# 统一响应格式
from django.http import JsonResponse

class APIResponse:
    """统一API响应格式"""
    
    @staticmethod
    def success(data=None, message="success", status=200):
        return JsonResponse({
            'code': 0,
            'message': message,
            'data': data
        }, status=status)
    
    @staticmethod
    def error(message, code=400, details=None, status=400):
        return JsonResponse({
            'code': code,
            'message': message,
            'details': details
        }, status=status)
    
    @staticmethod
    def paginated(data, page, page_size, total, total_pages):
        """分页响应"""
        return JsonResponse({
            'code': 0,
            'message': 'success',
            'data': data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': total_pages
            }
        })