"""
评论实体
提供评论相关的数据模型和关系
"""

from typing import List, Optional
from datetime import datetime
from app.core.orm.models import Model
from app.core.orm.query import ModelQuery


class Comment(Model):
    """评论模型"""
    
    __table__ = "comments"
    __fillable__ = [
        "user_id", "post_id", "parent_id", "content", "status", "like_count"
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @property
    def is_approved(self) -> bool:
        """是否已审核"""
        return self.status == "approved"
    
    @property
    def is_pending(self) -> bool:
        """是否待审核"""
        return self.status == "pending"
    
    @property
    def is_reply(self) -> bool:
        """是否为回复"""
        return hasattr(self, 'parent_id') and self.parent_id is not None
    
    def get_user(self) -> 'User':
        """获取评论作者"""
        # 这里应该实现关系查询
        # 实际实现需要数据库连接
        print(f"获取评论的作者")
        return None
    
    def get_post(self) -> 'Post':
        """获取评论所属文章"""
        # 这里应该实现关系查询
        # 实际实现需要数据库连接
        print(f"获取评论所属文章")
        return None
    
    def get_parent(self) -> Optional['Comment']:
        """获取父评论"""
        if self.is_reply:
            # 这里应该实现关系查询
            # 实际实现需要数据库连接
            print(f"获取父评论")
            return None
        return None
    
    def get_replies(self) -> List['Comment']:
        """获取子评论"""
        # 这里应该实现关系查询
        # 实际实现需要数据库连接
        print(f"获取子评论")
        return []
    
    def approve(self):
        """审核通过"""
        self.status = "approved"
        self.save()
    
    def reject(self):
        """审核拒绝"""
        self.status = "rejected"
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
            'post_id': self.post_id,
            'parent_id': getattr(self, 'parent_id', None),
            'content': self.content,
            'status': self.status,
            'like_count': getattr(self, 'like_count', 0),
            'is_approved': self.is_approved,
            'is_pending': self.is_pending,
            'is_reply': self.is_reply,
            'created_at': self.created_at.isoformat() if hasattr(self, 'created_at') and self.created_at else None,
            'updated_at': self.updated_at.isoformat() if hasattr(self, 'updated_at') and self.updated_at else None
        }