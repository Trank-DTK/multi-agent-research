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
