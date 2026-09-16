"""Per-user model transport. Never expose provider responses or keys in errors."""
import base64
import hashlib
import os
import json
from urllib.parse import urlsplit, urlunsplit
import requests
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from langchain_core.language_models.llms import LLM
from pydantic import SecretStr


def cipher():
    secret = getattr(settings, "MODEL_KEY_SECRET", None) or settings.SECRET_KEY
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest()))


def encrypt_key(value):
    return cipher().encrypt(value.encode()).decode() if value else ""


def decrypt_key(value):
    try:
        return cipher().decrypt(value.encode()).decode() if value else ""
    except InvalidToken:
        raise ValueError("已保存的密钥无法解密，请在设置中重新填写 API Key 并保存") from None


def validate_base_url(value):
    parts = urlsplit(value)
    try:
        port = parts.port
    except ValueError:
        raise ValueError("Base URL 端口无效")
    if parts.scheme not in ("http", "https") or not parts.hostname or parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError("请输入完整的 HTTP/HTTPS Base URL，不要包含密钥、查询参数或账号密码")
    # Local model servers are intentional; block cloud metadata and non-host addresses.
    import ipaddress
    try:
        address = ipaddress.ip_address(parts.hostname)
    except ValueError:
        address = None
    if parts.hostname in ("metadata.google.internal", "metadata.azure.internal") or (address and (address.is_link_local or address.is_unspecified or address.is_multicast)):
        raise ValueError("该地址不能用于模型服务")
    return value.rstrip("/")


def model_endpoint(base_url, protocol):
    base = validate_base_url(base_url.strip())
    parts = urlsplit(base)
    # A local service runs on the host, rather than inside the application container.
    if os.path.exists('/.dockerenv') and parts.hostname in ('localhost', '127.0.0.1', '::1'):
        host = 'host.docker.internal' + (f':{parts.port}' if parts.port else '')
        base = urlunsplit((parts.scheme, host, parts.path, '', ''))
    if protocol == 'ollama':
        for suffix in ('/api/chat', '/v1/chat/completions', '/v1', '/api'):
            if base.endswith(suffix):
                base = base[:-len(suffix)]
                break
        return base + '/api/chat'
    if base.endswith('/chat/completions'):
        return base
    if not urlsplit(base).path:
        base += '/v1'
    return base + '/chat/completions'


class ProviderLLM(LLM):
    base_url: str
    model: str
    protocol: str = "openai"
    api_key: SecretStr = SecretStr("")

    @property
    def _llm_type(self):
        return "configured-provider"

    @property
    def _identifying_params(self):
        return {"model": self.model, "protocol": self.protocol}

    def chat(self, messages, timeout=120):
        endpoint = model_endpoint(self.base_url, self.protocol)
        body = {"model": self.model, "messages": messages, "stream": False}
        headers = {"Content-Type": "application/json"}
        if self.api_key.get_secret_value():
            headers["Authorization"] = "Bearer " + self.api_key.get_secret_value()
        try:
            response = requests.post(endpoint, json=body, headers=headers, timeout=(10, timeout), allow_redirects=False)
            if response.status_code >= 300:
                raise ValueError(f"模型服务返回 HTTP {response.status_code}，请检查地址、密钥、模型 ID 和额度")
            data = response.json()
            content = data["message"]["content"] if self.protocol == "ollama" else data["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("模型未返回文本，请确认选择的是支持对话的模型")
            return content
        except requests.Timeout:
            raise ValueError("模型请求超时，请检查模型服务或稍后重试") from None
        except requests.RequestException:
            raise ValueError("无法连接模型服务，请检查 Base URL 和服务状态") from None
        except (KeyError, IndexError, TypeError):
            raise ValueError("模型响应格式不兼容，请选择正确的接口协议") from None

    def stream_chat(self, messages, timeout=180):
        headers = {"Content-Type": "application/json"}
        if self.api_key.get_secret_value():
            headers["Authorization"] = "Bearer " + self.api_key.get_secret_value()
        response = None
        emitted = False
        completed = False
        try:
            response = requests.post(model_endpoint(self.base_url, self.protocol),
                json={"model": self.model, "messages": messages, "stream": True},
                headers=headers, timeout=(10, timeout), allow_redirects=False, stream=True)
            if response.status_code >= 300:
                raise ValueError(f"模型服务返回 HTTP {response.status_code}，请检查地址、密钥、模型 ID 和额度")
            for raw in response.iter_lines(chunk_size=1):
                line = raw.decode('utf-8') if isinstance(raw, bytes) else raw
                if not line or line.startswith(':'):
                    continue
                if self.protocol == 'openai':
                    if not line.startswith('data:'):
                        continue
                    line = line[5:].strip()
                    if line == '[DONE]':
                        completed = True
                        break
                data = json.loads(line)
                if data.get('error'):
                    raise ValueError("模型生成失败，请检查模型 ID、服务状态与额度")
                if self.protocol == 'ollama':
                    token = data.get('message', {}).get('content', '')
                    completed = bool(data.get('done'))
                else:
                    choices = data.get('choices', [])
                    if not choices:
                        continue
                    token = choices[0].get('delta', {}).get('content') or ''
                    completed = choices[0].get('finish_reason') is not None
                if token:
                    if not isinstance(token, str):
                        raise ValueError("模型响应格式不兼容")
                    emitted = True
                    yield token
                if completed:
                    break
            if not completed:
                raise ValueError("模型连接中断，回复尚未完成，请重试")
            if not emitted:
                raise ValueError("模型未返回文本，请确认选择的是支持对话的模型")
        except requests.Timeout:
            raise ValueError("模型请求超时，请检查模型服务或稍后重试") from None
        except requests.RequestException:
            raise ValueError("模型连接中断或无法连接，请检查 Base URL 和服务状态") from None
        except (KeyError, IndexError, TypeError, json.JSONDecodeError, UnicodeDecodeError):
            raise ValueError("模型响应格式不兼容，请选择正确的接口协议") from None
        finally:
            if response is not None:
                response.close()

    def _call(self, prompt, stop=None, run_manager=None, **kwargs):
        text = self.chat([{"role": "user", "content": prompt}])
        for token in stop or []:
            text = text.split(token)[0]
        return text


def build_llm(user=None, provider=None):
    if provider is None and user is not None:
        from .models import ModelProvider
        provider = ModelProvider.objects.filter(user=user, is_default=True).first()
    if provider:
        return ProviderLLM(base_url=provider.base_url, model=provider.model, protocol=provider.protocol, api_key=decrypt_key(provider.encrypted_api_key))
    return ProviderLLM(base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"), model=os.environ.get("OLLAMA_MODEL", "qwen2.5:7b"), protocol="ollama")
