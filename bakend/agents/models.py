from django.db import models
from django.contrib.auth.models import User
from chat.models import Conversation, Message

# Create your models here.
class Task(models.Model):
    """任务模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=500)
    description = models.TextField()
    status = models.CharField(max_length=20, default='pending',
                              choices=[('pending', '等待'), ('running', '执行中'), 
                                       ('completed', '已完成'), ('failed', '失败')])
    result = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']


class TaskStep(models.Model):
    """任务步骤"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='steps')
    agent_name = models.CharField(max_length=100)
    action = models.CharField(max_length=200)
    input_data = models.TextField()
    output_data = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='pending')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)


# 审计日志模型
class AuditLog(models.Model):
    """审计日志模型"""
    
    ACTION_CHOICES = [
        ('user_input', '用户输入'),
        ('agent_call', '智能体调用'),
        ('tool_use', '工具使用'),
        ('critic_evaluation', '评审评估'),
        ('workflow_execution', '工作流执行'),
        ('error', '错误'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs', null=True)
    session_id = models.CharField(max_length=100, blank=True)
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    action_name = models.CharField(max_length=200)
    input_data = models.TextField(blank=True)
    output_data = models.TextField(blank=True)
    duration_ms = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='success')
    error_message = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['session_id']),
            models.Index(fields=['action_type']),
        ]
    
    def __str__(self):
        return f"{self.created_at} - {self.user} - {self.action_type}"


class PerformanceMetric(models.Model):
    """性能指标模型"""
    
    METRIC_TYPES = [
        ('api_latency', 'API延迟'),
        ('llm_latency', 'LLM延迟'),
        ('vector_search_latency', '向量检索延迟'),
        ('agent_response_time', '智能体响应时间'),
    ]
    
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    value_ms = models.IntegerField()
    endpoint = models.CharField(max_length=200, blank=True)
    extra_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class FeedbackRecord(models.Model):
    """用户反馈记录"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    content = models.TextField()
    rating = models.IntegerField(choices=[(i, f"{i}星") for i in range(1, 6)], null=True, blank=True)
    context = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']