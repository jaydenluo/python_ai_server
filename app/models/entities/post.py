"""
文章实体
提供文章相关的数据模型和关系
"""

from typing import List, Optional
from datetime import datetime
from app.core.orm.models import Model
from app.core.orm.query import ModelQuery


class Post(Model):
    """文章模型"""
    
    __table__ = "posts"
    __fillable__ = [
        "user_id", "title", "content", "excerpt", "status", "featured_image",
        "tags", "category", "view_count", "like_count", "comment_count"
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @property
    def is_published(self) -> bool:
        """是否已发布"""
        return self.status == "published"
    
    @property
    def is_draft(self) -> bool:
        """是否为草稿"""
        return self.status == "draft"
    
    @property
    def word_count(self) -> int:
        """字数统计"""
        if hasattr(self, 'content') and self.content:
            return len(self.content)
        return 0
    
    @property
    def reading_time(self) -> int:
        """阅读时间（分钟）"""
        # 假设每分钟阅读200字
        return max(1, self.word_count // 200)
    
    def get_user(self) -> 'User':
        """获取文章作者"""
        # 这里应该实现关系查询
        # 实际实现需要数据库连接
        print(f"获取文章 {self.title} 的作者")
        return None
    
    def get_comments(self) -> List['Comment']:
        """获取文章评论"""
        # 这里应该实现关系查询
        # 实际实现需要数据库连接
        print(f"获取文章 {self.title} 的评论")
        return []
    
    def get_tags(self) -> List[str]:
        """获取文章标签"""
        if hasattr(self, 'tags') and self.tags:
            return self.tags.split(',') if isinstance(self.tags, str) else self.tags
        return []
    
    def publish(self):
        """发布文章"""
        self.status = "published"
        self.save()
    
    def unpublish(self):
        """取消发布"""
        self.status = "draft"
        self.save()
    
    def increment_view(self):
        """增加浏览量"""
        self.view_count = getattr(self, 'view_count', 0) + 1
        self.save()
    
    def increment_like(self):
        """增加点赞数"""
        self.like_count = getattr(self, 'like_count', 0) + 1
        self.save()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'excerpt': self.excerpt,
            'status': self.status,
            'featured_image': self.featured_image,
            'tags': self.get_tags(),
            'category': self.category,
            'view_count': getattr(self, 'view_count', 0),
            'like_count': getattr(self, 'like_count', 0),
            'comment_count': getattr(self, 'comment_count', 0),
            'word_count': self.word_count,
            'reading_time': self.reading_time,
            'is_published': self.is_published,
            'is_draft': self.is_draft,
            'created_at': self.created_at.isoformat() if hasattr(self, 'created_at') and self.created_at else None,
            'updated_at': self.updated_at.isoformat() if hasattr(self, 'updated_at') and self.updated_at else None
        }