# 论文写作模型
from django.db import models
from django.contrib.auth.models import User

class Paper(models.Model):
    """论文模型"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('writing', '写作中'),
        ('review', '评审中'),
        ('completed', '已完成'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='papers')
    title = models.CharField(max_length=500, verbose_name='论文标题')
    abstract = models.TextField(blank=True, verbose_name='摘要')
    keywords = models.CharField(max_length=200, blank=True, verbose_name='关键词')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    content = models.TextField(blank=True, verbose_name='内容')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.title


class PaperSection(models.Model):
    """论文章节"""
    SECTION_TYPES = [
        ('introduction', '引言'),
        ('related_work', '相关工作'),
        ('methodology', '方法'),
        ('experiments', '实验'),
        ('results', '结果'),
        ('discussion', '讨论'),
        ('conclusion', '结论'),
        ('custom', '自定义'),
    ]
    
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='sections')
    section_type = models.CharField(max_length=50, choices=SECTION_TYPES)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']


class Citation(models.Model):
    """引用文献"""
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='citations')
    title = models.CharField(max_length=500)
    authors = models.CharField(max_length=500)
    journal = models.CharField(max_length=200, blank=True)
    year = models.IntegerField(null=True, blank=True)
    doi = models.CharField(max_length=100, blank=True)
    bibtex = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.authors} ({self.year}) {self.title[:50]}"


class WritingHistory(models.Model):
    """写作历史（版本控制）"""
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='history')
    content = models.TextField()
    version = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
