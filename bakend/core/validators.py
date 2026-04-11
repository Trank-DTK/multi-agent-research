# 验证增强
import re
from django.core.exceptions import ValidationError

def validate_safe_string(value):
    """验证安全的字符串（防止XSS）"""
    dangerous_patterns = [
        r'<script', r'javascript:', r'onclick=', r'onload=',
        r'<iframe', r'<object', r'<embed'
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValidationError(f'包含不安全字符: {pattern}')
    
    return value


def validate_file_extension(value):
    """验证文件扩展名"""
    import os
    ext = os.path.splitext(value.name)[1].lower()
    allowed_extensions = ['.pdf', '.csv', '.xlsx', '.xls', '.txt']
    
    if ext not in allowed_extensions:
        raise ValidationError(f'不支持的文件类型，仅支持: {", ".join(allowed_extensions)}')


def validate_file_size(value, max_size=50*1024*1024):
    """验证文件大小（默认50MB）"""
    if value.size > max_size:
        raise ValidationError(f'文件大小不能超过{max_size // (1024*1024)}MB')