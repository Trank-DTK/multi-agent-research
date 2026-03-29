# 审计中间件
import time
import uuid
from django.utils.deprecation import MiddlewareMixin
from .models import AuditLog, PerformanceMetric

class AuditMiddleware(MiddlewareMixin):
    """审计中间件"""
    
    def process_request(self, request):
        request.audit_session_id = str(uuid.uuid4())
        request.audit_start_time = time.time()
    
    def process_response(self, request, response):
        duration_ms = int((time.time() - getattr(request, 'audit_start_time', time.time())) * 1000)
        
        # 记录API性能
        if hasattr(request, 'path') and request.path.startswith('/api/'):
            PerformanceMetric.objects.create(
                metric_type='api_latency',
                value_ms=duration_ms,
                endpoint=request.path,
                extra_data={
                    'method': request.method,
                    'status_code': response.status_code
                }
            )
        
        return response


class AuditLogService:
    """审计日志服务"""
    
    @staticmethod
    def log(user, action_type, action_name, input_data='', output_data='',
            duration_ms=0, status='success', error_message='', request=None):
        
        log = AuditLog(
            user=user,
            action_type=action_type,
            action_name=action_name,
            input_data=input_data[:1000] if input_data else '',
            output_data=output_data[:1000] if output_data else '',
            duration_ms=duration_ms,
            status=status,
            error_message=error_message[:500] if error_message else ''
        )
        
        if request:
            log.session_id = getattr(request, 'audit_session_id', '')
            log.ip_address = AuditLogService._get_client_ip(request)
            log.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        log.save()
        return log
    
    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip