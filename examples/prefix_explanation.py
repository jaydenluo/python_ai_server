"""
Prefix 参数详解
解释 prefix 参数的作用和路由系统的工作原理
"""

from app.api.decorators.route_decorators import (
    api_controller, get, post, put, delete
)
from app.api.controllers.base import ResourceController
from app.core.middleware.base import Request, Response


# 示例1: 不使用 prefix 的控制器
@api_controller(version="v1", middleware=["auth"])
class SimpleController(ResourceController):
    """简单控制器 - 不使用 prefix"""
    
    def __init__(self):
        super().__init__(None)
    
    # 路由: GET /user/list
    @get("/user/list")
    async def user_list(self, request: Request) -> Response:
        """用户列表 - 不使用 prefix"""
        return self._create_response(
            self.success_response(
                data={"users": []},
                message="获取用户列表成功"
            )
        )
    
    # 路由: GET /user/profile
    @get("/user/profile")
    async def user_profile(self, request: Request) -> Response:
        """用户资料 - 不使用 prefix"""
        return self._create_response(
            self.success_response(
                data={"user": {}},
                message="获取用户资料成功"
            )
        )


# 示例2: 使用 prefix 的控制器
@api_controller(prefix="/api", version="v1", middleware=["auth"])
class PrefixedController(ResourceController):
    """带前缀的控制器 - 使用 prefix"""
    
    def __init__(self):
        super().__init__(None)
    
    # 路由: GET /api/user/list
    @get("/user/list")
    async def user_list(self, request: Request) -> Response:
        """用户列表 - 使用 prefix"""
        return self._create_response(
            self.success_response(
                data={"users": []},
                message="获取用户列表成功"
            )
        )
    
    # 路由: GET /api/user/profile
    @get("/user/profile")
    async def user_profile(self, request: Request) -> Response:
        """用户资料 - 使用 prefix"""
        return self._create_response(
            self.success_response(
                data={"user": {}},
                message="获取用户资料成功"
            )
        )


# 示例3: 多层 prefix 的控制器
@api_controller(prefix="/api/v1", version="v1", middleware=["auth"])
class MultiLevelController(ResourceController):
    """多层前缀控制器 - 使用多层 prefix"""
    
    def __init__(self):
        super().__init__(None)
    
    # 路由: GET /api/v1/user/list
    @get("/user/list")
    async def user_list(self, request: Request) -> Response:
        """用户列表 - 多层 prefix"""
        return self._create_response(
            self.success_response(
                data={"users": []},
                message="获取用户列表成功"
            )
        )
    
    # 路由: GET /api/v1/user/profile
    @get("/user/profile")
    async def user_profile(self, request: Request) -> Response:
        """用户资料 - 多层 prefix"""
        return self._create_response(
            self.success_response(
                data={"user": {}},
                message="获取用户资料成功"
            )
        )


# 示例4: 混合使用 prefix
@api_controller(prefix="/api", version="v1", middleware=["auth"])
class MixedController(ResourceController):
    """混合使用控制器 - 展示 prefix 的灵活性"""
    
    def __init__(self):
        super().__init__(None)
    
    # 路由: GET /api/user/list (使用控制器 prefix)
    @get("/user/list")
    async def user_list(self, request: Request) -> Response:
        """用户列表 - 使用控制器 prefix"""
        return self._create_response(
            self.success_response(
                data={"users": []},
                message="获取用户列表成功"
            )
        )
    
    # 路由: GET /admin/user/list (使用路由 prefix)
    @get("/user/list", prefix="/admin")
    async def admin_user_list(self, request: Request) -> Response:
        """管理员用户列表 - 使用路由 prefix"""
        return self._create_response(
            self.success_response(
                data={"admin_users": []},
                message="获取管理员用户列表成功"
            )
        )
    
    # 路由: GET /public/user/list (使用路由 prefix)
    @get("/user/list", prefix="/public")
    async def public_user_list(self, request: Request) -> Response:
        """公开用户列表 - 使用路由 prefix"""
        return self._create_response(
            self.success_response(
                data={"public_users": []},
                message="获取公开用户列表成功"
            )
        )


# 示例5: 简称参数使用 prefix
@api_controller(p="/api", v="v1", m=["auth"])
class ShortPrefixController(ResourceController):
    """简称参数控制器 - 使用简称参数"""
    
    def __init__(self):
        super().__init__(None)
    
    # 路由: GET /api/user/list (使用简称参数)
    @get("/user/list")
    async def user_list(self, request: Request) -> Response:
        """用户列表 - 使用简称参数"""
        return self._create_response(
            self.success_response(
                data={"users": []},
                message="获取用户列表成功"
            )
        )
    
    # 路由: GET /admin/user/list (使用简称参数)
    @get("/user/list", p="/admin")
    async def admin_user_list(self, request: Request) -> Response:
        """管理员用户列表 - 使用简称参数"""
        return self._create_response(
            self.success_response(
                data={"admin_users": []},
                message="获取管理员用户列表成功"
            )
        )


def explain_prefix():
    """解释 prefix 参数的作用"""
    print("🔍 Prefix 参数详解")
    print("=" * 60)
    
    print("\n📋 什么是 Prefix？")
    print("-" * 60)
    print("Prefix 是路由前缀，用于为所有路由添加统一的前缀路径。")
    print("它可以帮助组织路由结构，实现 API 版本控制和路径分组。")
    
    print("\n🎯 Prefix 的作用")
    print("-" * 60)
    print("1. 路径组织 - 将相关路由组织在一起")
    print("2. 版本控制 - 实现 API 版本管理")
    print("3. 路径分组 - 按功能模块分组路由")
    print("4. 统一管理 - 为所有路由添加统一前缀")
    
    print("\n📊 路由生成规则")
    print("-" * 60)
    print("最终路由 = 控制器 prefix + 路由 prefix + 路由路径")
    print()
    print("示例:")
    print("控制器: @api_controller(prefix='/api')")
    print("路由:   @get('/user/list')")
    print("结果:   GET /api/user/list")
    print()
    print("控制器: @api_controller(prefix='/api')")
    print("路由:   @get('/user/list', prefix='/admin')")
    print("结果:   GET /admin/user/list")
    
    print("\n🔗 实际应用示例")
    print("-" * 60)
    print("1. 不使用 prefix:")
    print("   @get('/user/list')")
    print("   → GET /user/list")
    print()
    print("2. 使用控制器 prefix:")
    print("   @api_controller(prefix='/api')")
    print("   @get('/user/list')")
    print("   → GET /api/user/list")
    print()
    print("3. 使用路由 prefix:")
    print("   @get('/user/list', prefix='/admin')")
    print("   → GET /admin/user/list")
    print()
    print("4. 多层 prefix:")
    print("   @api_controller(prefix='/api/v1')")
    print("   @get('/user/list')")
    print("   → GET /api/v1/user/list")
    
    print("\n💡 最佳实践")
    print("-" * 60)
    print("1. 控制器级别 prefix - 用于 API 版本控制")
    print("   @api_controller(prefix='/api/v1')")
    print()
    print("2. 路由级别 prefix - 用于功能模块分组")
    print("   @get('/user/list', prefix='/admin')")
    print()
    print("3. 简称参数 - 提高开发效率")
    print("   @api_controller(p='/api', v='v1', m=['auth'])")
    print("   @get('/user/list', p='/admin')")
    
    print("\n🚨 注意事项")
    print("-" * 60)
    print("1. 路由 prefix 优先级高于控制器 prefix")
    print("2. 避免重复的 prefix 设置")
    print("3. 保持 prefix 的一致性和可读性")
    print("4. 使用简称参数提高开发效率")
    
    print("\n🎯 总结")
    print("-" * 60)
    print("Prefix 是路由系统的重要组成部分，它帮助:")
    print("✅ 组织路由结构")
    print("✅ 实现版本控制")
    print("✅ 分组相关功能")
    print("✅ 提高代码可维护性")
    print("✅ 支持简称参数提高开发效率")


if __name__ == "__main__":
    explain_prefix()