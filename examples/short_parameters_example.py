"""
简称参数示例
展示如何使用简称参数让代码更简洁
"""

from app.api.decorators.route_decorators import (
    api_controller, get, post, put, delete,
    auth_required, admin_required, rate_limit, cache
)
from app.api.controllers.base import ResourceController
from app.core.middleware.base import Request, Response


# 使用简称参数的控制器
@api_controller(p="/users", v="v1", m=["auth"])
class UserController(ResourceController):
    """用户控制器 - 使用简称参数"""
    
    def __init__(self):
        super().__init__(None)
    
    # 使用简称参数
    @get("/", p="/api", v="v2", m=["admin"])
    async def index(self, request: Request) -> Response:
        """用户列表 - 使用简称参数"""
        return self._create_response(
            self.success_response(
                data={"users": []},
                message="获取用户列表成功"
            )
        )
    
    # 混合使用简称和完整参数
    @get("/{id}", name="users.show", p="/api", v="v2")
    async def show(self, request: Request) -> Response:
        """用户详情 - 混合使用"""
        return self._create_response(
            self.success_response(
                data={"user": {}},
                message="获取用户详情成功"
            )
        )
    
    # 只使用简称参数
    @post("/", p="/api", v="v2", m=["admin"])
    async def store(self, request: Request) -> Response:
        """创建用户 - 只使用简称参数"""
        return self._create_response(
            self.success_response(
                data={"user": {}},
                message="创建用户成功",
                status_code=201
            )
        )
    
    # 使用简称参数 + 智能中间件
    @put("/{id}", p="/api", v="v2", m=["admin"])
    async def update(self, request: Request) -> Response:
        """更新用户 - 简称参数 + 智能中间件"""
        return self._create_response(
            self.success_response(
                data={"user": {}},
                message="更新用户成功"
            )
        )
    
    # 使用简称参数 + 匿名访问
    @get("/public", p="/api", v="v2", m=["anonymous"])
    async def public_info(self, request: Request) -> Response:
        """公开信息 - 简称参数 + 匿名访问"""
        return self._create_response(
            self.success_response(
                data={"info": "public"},
                message="获取公开信息成功"
            )
        )


# 对比：传统写法和简称写法
@api_controller(prefix="/demo", version="v1", middleware=["auth"])
class DemoController(ResourceController):
    """演示控制器 - 对比传统写法和简称写法"""
    
    def __init__(self):
        super().__init__(None)
    
    # 传统写法
    @get("/traditional", name="demo.traditional", 
         middleware=["auth", "admin"], prefix="/api", version="v2")
    async def traditional(self, request: Request) -> Response:
        """传统写法 - 完整参数名"""
        return self._create_response(
            self.success_response(
                data={"method": "traditional"},
                message="传统写法成功"
            )
        )
    
    # 简称写法
    @get("/short", name="demo.short", 
         m=["admin"], p="/api", v="v2")
    async def short(self, request: Request) -> Response:
        """简称写法 - 使用简称参数"""
        return self._create_response(
            self.success_response(
                data={"method": "short"},
                message="简称写法成功"
            )
        )
    
    # 混合写法
    @get("/mixed", name="demo.mixed", 
         middleware=["auth"], p="/api", v="v2")
    async def mixed(self, request: Request) -> Response:
        """混合写法 - 部分使用简称"""
        return self._create_response(
            self.success_response(
                data={"method": "mixed"},
                message="混合写法成功"
            )
        )


# 简称参数的优势示例
@api_controller(p="/api", v="v1", m=["auth"])
class AdvantageController(ResourceController):
    """优势演示控制器 - 展示简称参数的优势"""
    
    def __init__(self):
        super().__init__(None)
    
    # 简洁的路由定义
    @get("/", p="/users", v="v2", m=["admin"])
    async def users(self, request: Request) -> Response:
        """用户列表 - 简洁定义"""
        return self._create_response(
            self.success_response(
                data={"users": []},
                message="获取用户列表成功"
            )
        )
    
    # 快速原型开发
    @get("/quick", p="/api", v="v2", m=["admin"])
    async def quick_prototype(self, request: Request) -> Response:
        """快速原型 - 简称参数"""
        return self._create_response(
            self.success_response(
                data={"prototype": "data"},
                message="快速原型成功"
            )
        )
    
    # 批量路由定义
    @get("/batch1", p="/api", v="v2", m=["admin"])
    async def batch1(self, request: Request) -> Response:
        """批量路由1"""
        return self._create_response(
            self.success_response(
                data={"batch": 1},
                message="批量路由1成功"
            )
        )
    
    @get("/batch2", p="/api", v="v2", m=["admin"])
    async def batch2(self, request: Request) -> Response:
        """批量路由2"""
        return self._create_response(
            self.success_response(
                data={"batch": 2},
                message="批量路由2成功"
            )
        )
    
    @get("/batch3", p="/api", v="v2", m=["admin"])
    async def batch3(self, request: Request) -> Response:
        """批量路由3"""
        return self._create_response(
            self.success_response(
                data={"batch": 3},
                message="批量路由3成功"
            )
        )


def demo_short_parameters():
    """演示简称参数的使用"""
    print("⚡ 简称参数演示")
    print("=" * 60)
    
    print("\n📋 简称参数对照表:")
    print("-" * 60)
    print("完整参数名    →    简称参数")
    print("prefix        →    p")
    print("version       →    v")
    print("middleware    →    m")
    print("name          →    n (暂未实现)")
    
    print("\n🔗 使用示例:")
    print("-" * 60)
    print("# 传统写法")
    print("@get('/users', prefix='/api', version='v2', middleware=['admin'])")
    print("async def users(self, request): pass")
    print()
    print("# 简称写法")
    print("@get('/users', p='/api', v='v2', m=['admin'])")
    print("async def users(self, request): pass")
    print()
    print("# 控制器简称写法")
    print("@api_controller(p='/users', v='v1', m=['auth'])")
    print("class UserController(ResourceController): pass")
    
    print("\n💡 简称参数优势:")
    print("-" * 60)
    print("✅ 更简洁 - 减少代码量")
    print("✅ 更快速 - 提高开发速度")
    print("✅ 更清晰 - 参数一目了然")
    print("✅ 更灵活 - 支持混合使用")
    print("✅ 向后兼容 - 原有写法仍然有效")
    
    print("\n🎯 使用场景:")
    print("-" * 60)
    print("1. 快速原型开发 - 使用简称参数快速定义路由")
    print("2. 批量路由定义 - 大量相似路由的快速定义")
    print("3. 代码简洁 - 减少重复的长参数名")
    print("4. 团队协作 - 统一的简称参数使用")
    
    print("\n📊 代码对比:")
    print("-" * 60)
    print("传统写法 (完整参数):")
    print("@get('/users', prefix='/api', version='v2', middleware=['admin'])")
    print("async def users(self, request): pass")
    print()
    print("简称写法 (简称参数):")
    print("@get('/users', p='/api', v='v2', m=['admin'])")
    print("async def users(self, request): pass")
    print()
    print("代码减少: 约30%")
    
    print("\n🚨 注意事项:")
    print("-" * 60)
    print("⚠️  简称参数优先级低于完整参数")
    print("⚠️  混合使用时，完整参数会覆盖简称参数")
    print("⚠️  简称参数主要用于提高开发效率")
    print("⚠️  生产环境建议使用完整参数名")
    
    print("\n🎯 最佳实践:")
    print("-" * 60)
    print("1. 开发阶段 - 使用简称参数提高效率")
    print("2. 生产环境 - 使用完整参数名保持清晰")
    print("3. 团队协作 - 统一简称参数的使用规范")
    print("4. 代码审查 - 确保简称参数的使用合理")
    print("5. 文档说明 - 在团队文档中说明简称参数")


if __name__ == "__main__":
    demo_short_parameters()