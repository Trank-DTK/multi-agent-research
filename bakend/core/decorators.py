# 查询优化装饰器
from django.db import connection
import time
import logging

logger = logging.getLogger(__name__)

def query_debugger(func):
    """查询调试装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_queries = len(connection.queries) # 记录执行前SQL查询数量
        
        result = func(*args, **kwargs)
        
        end_queries = len(connection.queries) # 记录执行后SQL查询数量
        end_time = time.time()
        
        logger.debug(
            f"Function {func.__name__} executed {end_queries - start_queries} queries "
            f"in {end_time - start_time:.2f} seconds"
        )
        
        return result
    return wrapper


def cache_result(timeout=3600):
    """结果缓存装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            from agents.cache_service import CacheService
            
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            cached = CacheService.get_llm_response(
                model="cache",
                prompt=cache_key,
                temperature=0
            )
            
            if cached:
                return cached
            
            result = func(*args, **kwargs)
            CacheService.set_llm_response(
                model="cache",
                prompt=cache_key,
                temperature=0,
                response=str(result)[:5000], # 限制缓存大小
                ttl=timeout  # 过期时间
            )
            
            return result
        return wrapper
    return decorator