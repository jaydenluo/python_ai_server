"""
用户管理控制器 - 后台管理
基于Django-Vue3-Admin的用户管理功能
"""
from typing import List, Dict, Any, Optional
from app.core.controllers.base_controller import *
from app.models.entities.system.user_management import User, Role, Dept, Post
from app.core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import Depends


@api_controller(prefix="/admin/user", tags=["AdminAPI - 用户管理"])
class UserController(BaseController):
    """后台用户管理控制器"""
    
    @get("/list")
    async def get_users(
        self, 
        request: Request,
        page: int = 1, 
        limit: int = 20,
        db: Session = Depends(get_db)
    ) -> Response:
        """获取用户列表（分页）"""
        try:
            # 构建查询
            query = db.query(User)
            
            # 应用过滤条件
            filters = dict(request.query_params)
            if 'username' in filters:
                query = query.filter(User.username.like(f"%{filters['username']}%"))
            if 'email' in filters:
                query = query.filter(User.email.like(f"%{filters['email']}%"))
            if 'mobile' in filters:
                query = query.filter(User.mobile.like(f"%{filters['mobile']}%"))
            if 'status' in filters:
                query = query.filter(User.status == filters['status'])
            
            # 分页
            total = query.count()
            users = query.offset((page - 1) * limit).limit(limit).all()
            
            return self._create_response(
                self.success_response(
                    data={
                        "list": [user.to_dict() for user in users],
                        "total": total,
                        "page": page,
                        "limit": limit
                    }
                )
            )
        except Exception as e:
            return self._create_response(
                self.error_response(message=f"获取用户列表失败: {str(e)}", status_status_code=500)
            )
    
    @get("/{user_id}")
    async def get_user(
        self, 
        request: Request,
        user_id: int,
        db: Session = Depends(get_db)
    ) -> Response:
        """获取单个用户详情"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return self._create_response(
                    self.error_response(message="用户不存在", status_code=404)
                )
            
            return self._create_response(
                self.success_response(data=user.to_dict())
            )
        except Exception as e:
            return self._create_response(
                self.error_response(message=f"获取用户详情失败: {str(e)}", status_code=500)
            )
    
    @post("/create")
    async def create_user(
        self, 
        request: Request,
        db: Session = Depends(get_db)
    ) -> Response:
        """创建新用户"""
        try:
            data = await request.json()
            
            # 检查用户名是否存在
            if db.query(User).filter(User.username == data['username']).first():
                return self._create_response(
                    self.error_response(message="用户名已存在", status_code=400)
                )
            
            # 创建用户
            user = User(**data)
            db.add(user)
            db.commit()
            db.refresh(user)
            
            return self._create_response(
                self.success_response(data=user.to_dict(), message="用户创建成功")
            )
        except Exception as e:
            db.rollback()
            return self._create_response(
                self.error_response(message=f"创建用户失败: {str(e)}", status_code=500)
            )
    
    @put("/{user_id}")
    async def update_user(
        self, 
        request: Request,
        user_id: int,
        db: Session = Depends(get_db)
    ) -> Response:
        """更新用户信息"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return self._create_response(
                    self.error_response(message="用户不存在", status_code=404)
                )
            
            data = await request.json()
            for key, value in data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            db.commit()
            db.refresh(user)
            
            return self._create_response(
                self.success_response(data=user.to_dict(), message="用户更新成功")
            )
        except Exception as e:
            db.rollback()
            return self._create_response(
                self.error_response(message=f"更新用户失败: {str(e)}", status_code=500)
            )
    
    @delete("/{user_id}")
    async def delete_user(
        self, 
        request: Request,
        user_id: int,
        db: Session = Depends(get_db)
    ) -> Response:
        """删除用户"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return self._create_response(
                    self.error_response(message="用户不存在", status_code=404)
                )
            
            db.delete(user)
            db.commit()
            
            return self._create_response(
                self.success_response(message="用户删除成功")
            )
        except Exception as e:
            db.rollback()
            return self._create_response(
                self.error_response(message=f"删除用户失败: {str(e)}", status_code=500)
            )

