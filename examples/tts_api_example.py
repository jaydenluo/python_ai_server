"""
TTS API使用示例
演示如何使用语音合成API接口
"""

import asyncio
import aiohttp
import json
import base64
from typing import Dict, Any, Optional


class TTSAPIClient:
    """TTS API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def generate_speech(
        self,
        text: str,
        provider: str = "openai",
        voice: str = "alloy",
        format: str = "mp3",
        speed: float = 1.0,
        pitch: float = 1.0,
        volume: float = 1.0,
        save_to_server: bool = True
    ) -> Dict[str, Any]:
        """
        生成语音
        
        Args:
            text: 要合成的文本
            provider: TTS服务提供商
            voice: 音色选择
            format: 音频格式
            speed: 语速
            pitch: 音调
            volume: 音量
            save_to_server: 是否保存到服务器
            
        Returns:
            Dict: 生成结果
        """
        url = f"{self.base_url}/api/tts/generate"
        
        payload = {
            "text": text,
            "provider": provider,
            "voice": voice,
            "format": format,
            "speed": speed,
            "pitch": pitch,
            "volume": volume,
            "save_to_server": save_to_server
        }
        
        async with self.session.post(url, json=payload, headers=self._get_headers()) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"生成语音失败: {response.status} - {error_text}")
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 任务状态
        """
        url = f"{self.base_url}/api/tts/status/{task_id}"
        
        async with self.session.get(url, headers=self._get_headers()) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"获取任务状态失败: {response.status} - {error_text}")
    
    async def download_audio(self, task_id: str) -> bytes:
        """
        下载音频文件
        
        Args:
            task_id: 任务ID
            
        Returns:
            bytes: 音频文件数据
        """
        url = f"{self.base_url}/api/tts/download/{task_id}"
        
        async with self.session.get(url, headers=self._get_headers()) as response:
            if response.status == 200:
                return await response.read()
            else:
                error_text = await response.text()
                raise Exception(f"下载音频失败: {response.status} - {error_text}")
    
    async def list_tasks(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        获取任务列表
        
        Args:
            user_id: 用户ID
            status: 任务状态
            page: 页码
            per_page: 每页数量
            
        Returns:
            Dict: 任务列表
        """
        url = f"{self.base_url}/api/tts/tasks"
        params = {
            "page": page,
            "per_page": per_page
        }
        
        if user_id:
            params["user_id"] = user_id
        if status:
            params["status"] = status
        
        async with self.session.get(url, params=params, headers=self._get_headers()) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"获取任务列表失败: {response.status} - {error_text}")
    
    async def get_providers(self) -> Dict[str, Any]:
        """
        获取支持的提供商列表
        
        Returns:
            Dict: 提供商列表
        """
        url = f"{self.base_url}/api/tts/providers"
        
        async with self.session.get(url, headers=self._get_headers()) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"获取提供商列表失败: {response.status} - {error_text}")
    
    async def get_voices(self, provider: str) -> Dict[str, Any]:
        """
        获取指定提供商的音色列表
        
        Args:
            provider: 服务提供商
            
        Returns:
            Dict: 音色列表
        """
        url = f"{self.base_url}/api/tts/voices"
        params = {"provider": provider}
        
        async with self.session.get(url, params=params, headers=self._get_headers()) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"获取音色列表失败: {response.status} - {error_text}")
    
    async def batch_generate(
        self,
        texts: list,
        provider: str = "openai",
        voice: str = "alloy",
        format: str = "mp3",
        speed: float = 1.0,
        pitch: float = 1.0,
        volume: float = 1.0,
        save_to_server: bool = True
    ) -> Dict[str, Any]:
        """
        批量生成语音
        
        Args:
            texts: 文本列表
            provider: TTS服务提供商
            voice: 音色选择
            format: 音频格式
            speed: 语速
            pitch: 音调
            volume: 音量
            save_to_server: 是否保存到服务器
            
        Returns:
            Dict: 批量生成结果
        """
        url = f"{self.base_url}/api/tts/batch"
        
        payload = {
            "texts": texts,
            "provider": provider,
            "voice": voice,
            "format": format,
            "speed": speed,
            "pitch": pitch,
            "volume": volume,
            "save_to_server": save_to_server
        }
        
        async with self.session.post(url, json=payload, headers=self._get_headers()) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"批量生成语音失败: {response.status} - {error_text}")


async def example_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    async with TTSAPIClient() as client:
        # 1. 获取支持的提供商
        print("1. 获取支持的提供商:")
        providers = await client.get_providers()
        print(json.dumps(providers, indent=2, ensure_ascii=False))
        
        # 2. 获取OpenAI的音色列表
        print("\n2. 获取OpenAI的音色列表:")
        voices = await client.get_voices("openai")
        print(json.dumps(voices, indent=2, ensure_ascii=False))
        
        # 3. 生成语音
        print("\n3. 生成语音:")
        result = await client.generate_speech(
            text="你好，这是一个语音合成测试。",
            provider="openai",
            voice="alloy",
            format="mp3",
            speed=1.0
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 4. 检查任务状态
        if result.get("task_id"):
            print(f"\n4. 检查任务状态: {result['task_id']}")
            status = await client.get_task_status(result["task_id"])
            print(json.dumps(status, indent=2, ensure_ascii=False))
            
            # 5. 下载音频文件（如果任务完成）
            if status.get("status") == "completed":
                print(f"\n5. 下载音频文件:")
                audio_data = await client.download_audio(result["task_id"])
                print(f"音频文件大小: {len(audio_data)} 字节")
                
                # 保存到本地文件
                with open(f"speech_{result['task_id']}.mp3", "wb") as f:
                    f.write(audio_data)
                print(f"音频文件已保存为: speech_{result['task_id']}.mp3")


async def example_batch_generation():
    """批量生成示例"""
    print("\n=== 批量生成示例 ===")
    
    async with TTSAPIClient() as client:
        texts = [
            "这是第一段文本。",
            "这是第二段文本。",
            "这是第三段文本。"
        ]
        
        result = await client.batch_generate(
            texts=texts,
            provider="openai",
            voice="alloy",
            format="mp3"
        )
        
        print("批量生成结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def example_different_providers():
    """不同提供商示例"""
    print("\n=== 不同提供商示例 ===")
    
    async with TTSAPIClient() as client:
        providers = ["openai", "baidu", "step", "minimax"]
        
        for provider in providers:
            try:
                print(f"\n使用 {provider} 提供商:")
                
                # 获取音色列表
                voices = await client.get_voices(provider)
                print(f"支持的音色: {voices.get('voices', [])}")
                
                # 生成语音
                result = await client.generate_speech(
                    text="测试不同提供商的语音合成效果。",
                    provider=provider,
                    voice=voices.get('voices', ['default'])[0] if voices.get('voices') else 'default',
                    format="mp3"
                )
                print(f"生成结果: {result.get('status')}")
                
            except Exception as e:
                print(f"{provider} 提供商测试失败: {e}")


async def example_parameter_tuning():
    """参数调优示例"""
    print("\n=== 参数调优示例 ===")
    
    async with TTSAPIClient() as client:
        # 测试不同的语速
        speeds = [0.5, 1.0, 1.5, 2.0]
        
        for speed in speeds:
            try:
                print(f"\n测试语速: {speed}")
                result = await client.generate_speech(
                    text="这是语速测试，请听一下效果。",
                    provider="openai",
                    voice="alloy",
                    speed=speed
                )
                print(f"语速 {speed} 生成结果: {result.get('status')}")
                
            except Exception as e:
                print(f"语速 {speed} 测试失败: {e}")


async def example_task_management():
    """任务管理示例"""
    print("\n=== 任务管理示例 ===")
    
    async with TTSAPIClient() as client:
        # 1. 获取任务列表
        print("1. 获取任务列表:")
        tasks = await client.list_tasks(page=1, per_page=10)
        print(json.dumps(tasks, indent=2, ensure_ascii=False))
        
        # 2. 创建多个任务
        print("\n2. 创建多个任务:")
        task_ids = []
        for i in range(3):
            result = await client.generate_speech(
                text=f"这是第{i+1}个测试任务。",
                provider="openai",
                voice="alloy"
            )
            if result.get("task_id"):
                task_ids.append(result["task_id"])
                print(f"任务 {i+1} ID: {result['task_id']}")
        
        # 3. 监控任务状态
        print("\n3. 监控任务状态:")
        for task_id in task_ids:
            status = await client.get_task_status(task_id)
            print(f"任务 {task_id}: {status.get('status')}")


async def main():
    """主函数"""
    print("TTS API 使用示例")
    print("=" * 50)
    
    try:
        # 运行各种示例
        await example_basic_usage()
        await example_batch_generation()
        await example_different_providers()
        await example_parameter_tuning()
        await example_task_management()
        
        print("\n所有示例运行完成！")
        
    except Exception as e:
        print(f"示例运行失败: {e}")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())
