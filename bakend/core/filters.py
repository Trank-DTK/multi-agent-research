# 过滤敏感信息
import re

class SensitiveDataFilter:
    """敏感信息过滤器"""
    
    SENSITIVE_PATTERNS = [
        (r'\b\d{17}[\dXx]\b', '[身份证号已隐藏]'),  # 身份证
        (r'\b1[3-9]\d{9}\b', '[手机号已隐藏]'),     # 手机号
        (r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[邮箱已隐藏]'),  # 邮箱
    ]
    
    @classmethod
    def filter_text(cls, text):
        """过滤文本中的敏感信息"""
        if not text:
            return text
        
        for pattern, replacement in cls.SENSITIVE_PATTERNS:
            text = re.sub(pattern, replacement, text)
        
        return text
    
    @classmethod
    def filter_dict(cls, data):
        """过滤字典中的敏感信息"""
        if isinstance(data, dict):
            return {k: cls.filter_dict(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.filter_dict(item) for item in data]
        elif isinstance(data, str):
            return cls.filter_text(data)
        return data