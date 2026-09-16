"""Shared SSE envelope. Errors never masquerade as successfully completed answers."""
import json
import logging
from django.http import StreamingHttpResponse

logger = logging.getLogger(__name__)

def event(data):
    return 'data: ' + json.dumps(data, ensure_ascii=False) + '\n\n'

def stream_response(llm, messages, metadata=None, on_complete=None):
    def generate():
        source = None
        try:
            yield event(metadata or {"ready": True})
            source = llm.stream_chat(messages)
            chunks = []
            for token in source:
                chunks.append(token)
                yield event({"token": token})
            if on_complete:
                result = on_complete(''.join(chunks))
                if result:
                    yield event(result)
            yield 'data: [DONE]\n\n'
        except ValueError as exc:
            yield event({"error": str(exc)})
        except Exception:
            logger.exception('Streaming response failed')
            yield event({"error": "回复处理失败，请稍后重试；已显示的内容可能不完整"})
        finally:
            if source is not None and hasattr(source, 'close'):
                source.close()
    response = StreamingHttpResponse(generate(), content_type='text/event-stream; charset=utf-8')
    response['Cache-Control'] = 'no-cache, no-transform'
    response['X-Accel-Buffering'] = 'no'
    return response
