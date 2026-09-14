"""Per-user model transport. Never expose provider responses or keys in errors."""
import base64
import hashlib
import os
from urllib.parse import urlsplit
import requests
from cryptography.fernet import Fernet
from django.conf import settings
from langchain_core.language_models.llms import LLM
from pydantic import SecretStr


def cipher():
    secret = getattr(settings, "MODEL_KEY_SECRET", settings.SECRET_KEY)
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest()))


def encrypt_key(value):
    return cipher().encrypt(value.encode()).decode() if value else ""


def decrypt_key(value):
    return cipher().decrypt(value.encode()).decode() if value else ""


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
        base = validate_base_url(self.base_url)
        endpoint = "/api/chat" if self.protocol == "ollama" else "/chat/completions"
        body = {"model": self.model, "messages": messages, "stream": False}
        headers = {"Content-Type": "application/json"}
        if self.api_key.get_secret_value():
            headers["Authorization"] = "Bearer " + self.api_key.get_secret_value()
        try:
            response = requests.post(base + endpoint, json=body, headers=headers, timeout=(10, timeout), allow_redirects=False)
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
