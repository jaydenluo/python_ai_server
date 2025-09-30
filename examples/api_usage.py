"""
API使用示例
展示如何使用API框架
"""

import requests
import json
from typing import Dict, Any


class APIClient:
    """API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
    
    def set_token(self, token: str):
        """设置认证令牌"""
        self.token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        response = self.session.post(
            f"{self.base_url}/api/v1/auth/login",
            json={"username": username, "password": password}
        )
        data = response.json()
        
        if data.get("success"):
            self.set_token(data["data"]["token"])
            return data
        
        raise Exception(f"登录失败: {data.get('message', '未知错误')}")
    
    def register(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """用户注册"""
        response = self.session.post(
            f"{self.base_url}/api/v1/auth/register",
            json=user_data
        )
        return response.json()
    
    def get_users(self, page: int = 1, per_page: int = 15, **filters) -> Dict[str, Any]:
        """获取用户列表"""
        params = {"page": page, "per_page": per_page, **filters}
        response = self.session.get(f"{self.base_url}/api/v1/users", params=params)
        return response.json()
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """获取单个用户"""
        response = self.session.get(f"{self.base_url}/api/v1/users/{user_id}")
        return response.json()
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建用户"""
        response = self.session.post(f"{self.base_url}/api/v1/users", json=user_data)
        return response.json()
    
    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新用户"""
        response = self.session.put(f"{self.base_url}/api/v1/users/{user_id}", json=user_data)
        return response.json()
    
    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """删除用户"""
        response = self.session.delete(f"{self.base_url}/api/v1/users/{user_id}")
        return response.json()
    
    def get_models(self, page: int = 1, per_page: int = 15, **filters) -> Dict[str, Any]:
        """获取AI模型列表"""
        params = {"page": page, "per_page": per_page, **filters}
        response = self.session.get(f"{self.base_url}/api/v1/models", params=params)
        return response.json()
    
    def get_model(self, model_id: int) -> Dict[str, Any]:
        """获取单个AI模型"""
        response = self.session.get(f"{self.base_url}/api/v1/models/{model_id}")
        return response.json()
    
    def create_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建AI模型"""
        response = self.session.post(f"{self.base_url}/api/v1/models", json=model_data)
        return response.json()
    
    def update_model(self, model_id: int, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新AI模型"""
        response = self.session.put(f"{self.base_url}/api/v1/models/{model_id}", json=model_data)
        return response.json()
    
    def delete_model(self, model_id: int) -> Dict[str, Any]:
        """删除AI模型"""
        response = self.session.delete(f"{self.base_url}/api/v1/models/{model_id}")
        return response.json()
    
    def predict_model(self, model_id: int, input_data: list) -> Dict[str, Any]:
        """模型预测"""
        response = self.session.post(
            f"{self.base_url}/api/v1/models/{model_id}/predict",
            json={"input": input_data}
        )
        return response.json()
    
    def deploy_model(self, model_id: int) -> Dict[str, Any]:
        """部署模型"""
        response = self.session.post(f"{self.base_url}/api/v1/models/{model_id}/deploy")
        return response.json()
    
    def get_health(self) -> Dict[str, Any]:
        """健康检查"""
        response = self.session.get(f"{self.base_url}/health")
        return response.json()
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取API指标"""
        response = self.session.get(f"{self.base_url}/metrics")
        return response.json()


def example_usage():
    """使用示例"""
    
    # 创建API客户端
    client = APIClient("http://localhost:8000")
    
    try:
        # 1. 健康检查
        print("=== 健康检查 ===")
        health = client.get_health()
        print(f"服务状态: {health}")
        
        # 2. 用户注册
        print("\n=== 用户注册 ===")
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User"
        }
        register_result = client.register(user_data)
        print(f"注册结果: {register_result}")
        
        # 3. 用户登录
        print("\n=== 用户登录 ===")
        login_result = client.login("testuser", "password123")
        print(f"登录结果: {login_result}")
        
        # 4. 获取用户列表
        print("\n=== 获取用户列表 ===")
        users = client.get_users(page=1, per_page=10)
        print(f"用户列表: {users}")
        
        # 5. 创建AI模型
        print("\n=== 创建AI模型 ===")
        model_data = {
            "name": "test_model",
            "description": "测试模型",
            "type": "classification",
            "framework": "pytorch"
        }
        model_result = client.create_model(model_data)
        print(f"模型创建结果: {model_result}")
        
        # 6. 获取AI模型列表
        print("\n=== 获取AI模型列表 ===")
        models = client.get_models(page=1, per_page=10)
        print(f"模型列表: {models}")
        
        # 7. 模型预测
        print("\n=== 模型预测 ===")
        if models.get("data") and len(models["data"]) > 0:
            model_id = models["data"][0]["id"]
            prediction = client.predict_model(model_id, [{"feature1": 1.0, "feature2": 2.0}])
            print(f"预测结果: {prediction}")
        
        # 8. 获取API指标
        print("\n=== API指标 ===")
        metrics = client.get_metrics()
        print(f"API指标: {metrics}")
        
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    example_usage()