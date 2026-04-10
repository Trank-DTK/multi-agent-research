# 统一异常处理器
import traceback
from django.http import JsonResponse
from rest_framework.views import exception_handler
from rest_framework import status

def custom_exception_handler(exc, context):
    """自定义异常处理器"""
    response = exception_handler(exc, context)
    
    if response is not None:
        return response
    
    # 记录异常日志，获取完整堆栈
    error_trace = traceback.format_exc()
    
    return JsonResponse({
        'error': {
            'message': str(exc), #错误信息
            'type': exc.__class__.__name__, #异常类型
            'traceback': error_trace if context.get('request').user.is_superuser else None    #堆栈（仅管理员可见）
        }
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class APIError(Exception):
    """API错误基类"""
    def __init__(self, message, code=400, details=None):
        self.message = message  #错误描述信息
        self.code = code   #HTTP状态码
        self.details = details  #额外详细信息
        super().__init__(message)


class ValidationError(APIError):
    """验证错误"""
    pass


class NotFoundError(APIError):
    """资源不存在错误"""
    def __init__(self, message="资源不存在"):
        super().__init__(message, code=404)


class PermissionDeniedError(APIError):
    """权限错误"""
    def __init__(self, message="权限不足"):
        super().__init__(message, code=403)


class RateLimitError(APIError):
    """限流错误"""
    def __init__(self, message="请求过于频繁，请稍后再试"):
        super().__init__(message, code=429)