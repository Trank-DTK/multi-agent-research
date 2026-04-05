# 缓存服务模块
import hashlib
import json
from django.core.cache import cache
from typing import Optional, Any

class CacheService:
    """缓存服务"""
    
    @staticmethod
    def _make_key(prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = str(args) + str(sorted(kwargs.items()))
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:16]
        return f"{prefix}:{key_hash}"
    
    @staticmethod
    def get_llm_response(model: str, prompt: str, temperature: float = 0.7) -> Optional[str]:
        """获取缓存的LLM响应"""
        key = CacheService._make_key("llm", model, prompt, temperature)
        return cache.get(key)
    
    @staticmethod
    def set_llm_response(model: str, prompt: str, temperature: float, response: str, ttl: int = 3600):
        """缓存LLM响应"""
        key = CacheService._make_key("llm", model, prompt, temperature)
        cache.set(key, response, ttl)
    
    @staticmethod
    def get_embedding(text: str) -> Optional[list]:
        """获取缓存的向量"""
        key = CacheService._make_key("embedding", text)
        return cache.get(key)
    
    @staticmethod
    def set_embedding(text: str, embedding: list, ttl: int = 86400):
        """缓存向量"""
        key = CacheService._make_key("embedding", text)
        cache.set(key, embedding, ttl)
    
    @staticmethod
    def get_search_result(query: str, user_id: int, top_k: int = 5) -> Optional[list]:
        """获取缓存的检索结果"""
        key = CacheService._make_key("search", query, user_id, top_k)
        return cache.get(key)
    
    @staticmethod
    def set_search_result(query: str, user_id: int, top_k: int, results: list, ttl: int = 1800):
        """缓存检索结果"""
        key = CacheService._make_key("search", query, user_id, top_k)
        cache.set(key, results, ttl)
    
    @staticmethod
    def invalidate_user_cache(user_id: int):
        """清除用户相关缓存"""
        pattern = f"*:{user_id}:*"
        # 注意：需要根据实际Redis客户端实现
        pass


class CachedLLM:
    """带缓存的LLM包装器"""
    
    def __init__(self, llm_instance):
        self.llm = llm_instance
    
    def invoke(self, prompt: str, use_cache: bool = True, **kwargs):
        """调用LLM（带缓存）"""
        if use_cache:
            cached = CacheService.get_llm_response(
                model=self.llm.model,
                prompt=prompt,
                temperature=getattr(self.llm, 'temperature', 0.7)
            )
            if cached:
                return cached
        
        response = self.llm.invoke(prompt, **kwargs)
        
        if use_cache:
            CacheService.set_llm_response(
                model=self.llm.model,
                prompt=prompt,
                temperature=getattr(self.llm, 'temperature', 0.7),
                response=response
            )
        
        return response