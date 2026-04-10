from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Conversation(models.Model):
    """对话会话（用于分组连续对话）"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=200, blank=True, verbose_name="对话标题")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间") #自动设置为当前时间
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间") 

    class Meta:
        ordering = ['-updated_at']  #默认按更新时间降序排列
        verbose_name = "对话会话"
        verbose_name_plural = "对话会话"

    def __str__(self):
        return self.title or f"对话 {self.id}"
    
    def save(self, *args, **kwargs):
        #如果没有标题，使用第一条消息的前20个字符作为标题
        if not self.title and hasattr(self, 'messages') and self.messages.exists():
            first_message = self.messages.filter(role='user').first()  #获取第一条用户消息
            if first_message:
                self.title = first_message.content[:20] + '...' if len(first_message.content) > 20 else first_message.content
        super().save(*args, **kwargs)


class Message(models.Model):
    """单条消息（用于会话内的消息）"""
    ROLE_CHOICES = (
        ('user', '用户'),
        ('assistant', '助手'),
        ( 'system', '系统'),
    )
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name="角色")
    content = models.TextField(verbose_name="消息内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发送时间")

    class Meta:
        ordering = ['created_at']  #默认按发送时间升序排列
        verbose_name = "消息"
        verbose_name_plural = "消息"
        indexes = [
            # 索引1：按对话ID查询消息
            models.Index(fields=['conversation'], name='idx_message_conversation'),
            
            # 索引2：按对话+角色查询
            models.Index(fields=['conversation', 'role'], name='idx_message_conversation_role'),
            
            # 索引3：按创建时间排序
            models.Index(fields=['-created_at'], name='idx_message_created_at'),
        ]

    def __str__(self):
        return f"{self.get_role_display()}: {self.content[:30]}..."  #显示角色和消息内容的前30个字符
    

class ChatHistory(models.Model):
    """对话历史记录（兼容旧版，后续可迁移）"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_histories')
    message = models.TextField(verbose_name="用户消息")
    response = models.TextField(verbose_name="AI回复")
    model_name = models.CharField(max_length=50, default="qwen2.5:7b",verbose_name="模型名称")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        ordering = ['created_at']  
        verbose_name = "对话历史"
        verbose_name_plural = "对话历史"

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
   




