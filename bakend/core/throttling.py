# API限流
from rest_framework.throttling import SimpleRateThrottle

class BurstRateThrottle(SimpleRateThrottle):
    """突发限流"""
    scope = 'burst'
    
    def get_cache_key(self, request, view):
        if not request.user.is_authenticated:
            return None
        return f"throttle_burst_{request.user.id}"


class SustainedRateThrottle(SimpleRateThrottle):
    """持续限流"""
    scope = 'sustained'
    
    def get_cache_key(self, request, view):
        if not request.user.is_authenticated:
            return None
        return f"throttle_sustained_{request.user.id}"