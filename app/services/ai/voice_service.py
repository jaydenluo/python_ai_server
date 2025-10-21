"""
语音服务管理
提供语音提供商和音色信息管理
"""

from typing import Dict, List, Optional, Any


class VoiceService:
    """语音服务管理 - 纯内存数据服务，不涉及数据库操作"""
    
    def __init__(self):
        """初始化语音服务"""
        self._providers = self._init_providers()
        self._voices = self._init_voices()
    
    def _init_providers(self) -> List[Dict[str, Any]]:
        """初始化提供商列表"""
        return [
            {
                "id": "xunfei",
                "name": "讯飞语音",
                "english_name": "iFLYTEK",
                "description": "科大讯飞超拟人语音合成服务，支持高质量中文语音合成",
                "enabled": True,
                "icon_url": None,
                "metadata": {
                    "version": "v3.5",
                    "supported_languages": ["zh_CN"],
                    "features": ["tts", "super_tts"],
                    "pricing": {
                        "tts": "2元/万字符",
                        "clone": "5元/个",
                        "long_text": "3元/万字符（10万字超长文本）"
                    }
                }
            }
        ]
    
    def _init_voices(self) -> Dict[str, List[Dict[str, Any]]]:
        """初始化音色列表"""
        return {
            "xunfei": [
                {
                    "id": "x5_lingfeiyi_flow",
                    "name": "凌飞易",
                    "provider_id": "xunfei",
                    "language": "zh_CN",
                    "gender": "male",
                    "description": "流畅自然的男声，适合新闻播报、有声读物",
                    "category": "超拟人",
                    "tags": ["流畅", "自然", "专业", "标准"],
                    "preview_url": None,
                    "is_premium": True,
                    "voice_params": {
                        "vcn": "x5_lingfeiyi_flow",
                        "speed": 50,
                        "volume": 50,
                        "pitch": 50,
                        "oral_level": "mid"
                    },
                    "metadata": {
                        "version": "x5系列",
                        "recommended_scenarios": ["新闻播报", "有声读物", "教育培训"],
                        "sample_rate": 24000,
                        "audio_format": "MP3"
                    }
                },
                {
                    "id": "x5_lingfeiyi",
                    "name": "凌飞易（情感版）",
                    "provider_id": "xunfei",
                    "language": "zh_CN",
                    "gender": "male",
                    "description": "富有情感的男声，适合情感类内容、故事讲述",
                    "category": "超拟人",
                    "tags": ["情感", "生动", "表现力强"],
                    "preview_url": None,
                    "is_premium": True,
                    "voice_params": {
                        "vcn": "x5_lingfeiyi",
                        "speed": 50,
                        "volume": 50,
                        "pitch": 50,
                        "oral_level": "high"
                    },
                    "metadata": {
                        "version": "x5系列",
                        "recommended_scenarios": ["情感故事", "戏剧朗读", "角色配音"],
                        "sample_rate": 24000,
                        "audio_format": "MP3"
                    }
                },
                {
                    "id": "x5_xiaoyan_flow",
                    "name": "小研",
                    "provider_id": "xunfei",
                    "language": "zh_CN",
                    "gender": "female",
                    "description": "流畅自然的女声，温柔清晰，适合客服、讲解",
                    "category": "超拟人",
                    "tags": ["温柔", "清晰", "亲和", "标准"],
                    "preview_url": None,
                    "is_premium": True,
                    "voice_params": {
                        "vcn": "x5_xiaoyan_flow",
                        "speed": 50,
                        "volume": 50,
                        "pitch": 50,
                        "oral_level": "mid"
                    },
                    "metadata": {
                        "version": "x5系列",
                        "recommended_scenarios": ["客服语音", "产品讲解", "导航提示"],
                        "sample_rate": 24000,
                        "audio_format": "MP3"
                    }
                },
                {
                    "id": "x5_xiaoyan",
                    "name": "小研（情感版）",
                    "provider_id": "xunfei",
                    "language": "zh_CN",
                    "gender": "female",
                    "description": "富有情感的女声，声音甜美温暖，适合情感表达",
                    "category": "超拟人",
                    "tags": ["情感", "甜美", "温暖", "生动"],
                    "preview_url": None,
                    "is_premium": True,
                    "voice_params": {
                        "vcn": "x5_xiaoyan",
                        "speed": 50,
                        "volume": 50,
                        "pitch": 50,
                        "oral_level": "high"
                    },
                    "metadata": {
                        "version": "x5系列",
                        "recommended_scenarios": ["情感文章", "儿童故事", "广告配音"],
                        "sample_rate": 24000,
                        "audio_format": "MP3"
                    }
                },
                {
                    "id": "x5_xiaoyu_flow",
                    "name": "小雨",
                    "provider_id": "xunfei",
                    "language": "zh_CN",
                    "gender": "female",
                    "description": "清新温柔的女声，声音柔和舒适，适合睡前故事",
                    "category": "超拟人",
                    "tags": ["清新", "温柔", "柔和", "舒适"],
                    "preview_url": None,
                    "is_premium": True,
                    "voice_params": {
                        "vcn": "x5_xiaoyu_flow",
                        "speed": 50,
                        "volume": 50,
                        "pitch": 50,
                        "oral_level": "mid"
                    },
                    "metadata": {
                        "version": "x5系列",
                        "recommended_scenarios": ["睡前故事", "冥想引导", "轻音乐解说"],
                        "sample_rate": 24000,
                        "audio_format": "MP3"
                    }
                },
                {
                    "id": "x5_xiaoyu",
                    "name": "小雨（情感版）",
                    "provider_id": "xunfei",
                    "language": "zh_CN",
                    "gender": "female",
                    "description": "活泼生动的女声，充满活力，适合活力内容",
                    "category": "超拟人",
                    "tags": ["活泼", "生动", "活力", "青春"],
                    "preview_url": None,
                    "is_premium": True,
                    "voice_params": {
                        "vcn": "x5_xiaoyu",
                        "speed": 50,
                        "volume": 50,
                        "pitch": 50,
                        "oral_level": "high"
                    },
                    "metadata": {
                        "version": "x5系列",
                        "recommended_scenarios": ["青春文学", "活力广告", "运动解说"],
                        "sample_rate": 24000,
                        "audio_format": "MP3"
                    }
                },
                {
                    "id": "x5_xiaochen_flow",
                    "name": "晓辰",
                    "provider_id": "xunfei",
                    "language": "zh_CN",
                    "gender": "female",
                    "description": "知性优雅的女声，成熟稳重，适合专业内容",
                    "category": "超拟人",
                    "tags": ["知性", "优雅", "成熟", "专业"],
                    "preview_url": None,
                    "is_premium": True,
                    "voice_params": {
                        "vcn": "x5_xiaochen_flow",
                        "speed": 50,
                        "volume": 50,
                        "pitch": 50,
                        "oral_level": "mid"
                    },
                    "metadata": {
                        "version": "x5系列",
                        "recommended_scenarios": ["商务演讲", "专业讲座", "财经资讯"],
                        "sample_rate": 24000,
                        "audio_format": "MP3"
                    }
                },
                {
                    "id": "x5_xiaochen",
                    "name": "晓辰（情感版）",
                    "provider_id": "xunfei",
                    "language": "zh_CN",
                    "gender": "female",
                    "description": "温暖亲切的女声，富有感染力，适合心灵内容",
                    "category": "超拟人",
                    "tags": ["温暖", "亲切", "感染力", "治愈"],
                    "preview_url": None,
                    "is_premium": True,
                    "voice_params": {
                        "vcn": "x5_xiaochen",
                        "speed": 50,
                        "volume": 50,
                        "pitch": 50,
                        "oral_level": "high"
                    },
                    "metadata": {
                        "version": "x5系列",
                        "recommended_scenarios": ["心灵鸡汤", "情感电台", "心理咨询"],
                        "sample_rate": 24000,
                        "audio_format": "MP3"
                    }
                }
            ]
        }
    
    def get_providers(self) -> List[Dict[str, Any]]:
        """
        获取所有语音服务提供商列表
        
        Returns:
            List[Dict]: 提供商列表
        """
        return self._providers
    
    def get_voice_list(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定提供商的音色列表
        
        Args:
            provider_id: 提供商ID
            
        Returns:
            Dict: 包含音色列表和元数据的字典，如果提供商不存在则返回None
        """
        # 检查提供商是否存在
        provider = next((p for p in self._providers if p['id'] == provider_id), None)
        if not provider:
            return None
        
        # 检查提供商是否启用
        if not provider.get('enabled', False):
            return None
        
        # 获取音色列表
        voices = self._voices.get(provider_id, [])
        
        # 统计信息
        categories = list(set(v['category'] for v in voices if 'category' in v))
        languages = list(set(v['language'] for v in voices if 'language' in v))
        premium_count = sum(1 for v in voices if v.get('is_premium', False))
        free_count = len(voices) - premium_count
        
        return {
            "provider_id": provider_id,
            "voices": voices,
            "total": len(voices),
            "metadata": {
                "categories": categories,
                "languages": languages,
                "premium_count": premium_count,
                "free_count": free_count
            }
        }
    
    def get_voice_detail(self, voice_id: str, provider_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        获取音色详情
        
        Args:
            voice_id: 音色ID
            provider_id: 提供商ID（可选，如果不提供则搜索所有提供商）
            
        Returns:
            Dict: 音色详情，如果不存在则返回None
        """
        if provider_id:
            # 在指定提供商中查找
            voices = self._voices.get(provider_id, [])
            return next((v for v in voices if v['id'] == voice_id), None)
        else:
            # 在所有提供商中查找
            for voices in self._voices.values():
                voice = next((v for v in voices if v['id'] == voice_id), None)
                if voice:
                    return voice
            return None
    
    def get_provider_by_id(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取提供商信息
        
        Args:
            provider_id: 提供商ID
            
        Returns:
            Dict: 提供商信息，如果不存在则返回None
        """
        return next((p for p in self._providers if p['id'] == provider_id), None)
    
    def search_voices(
        self,
        provider_id: Optional[str] = None,
        language: Optional[str] = None,
        gender: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索音色
        
        Args:
            provider_id: 提供商ID
            language: 语言
            gender: 性别
            category: 类别
            tags: 标签列表
            
        Returns:
            List[Dict]: 符合条件的音色列表
        """
        # 确定搜索范围
        if provider_id:
            all_voices = self._voices.get(provider_id, [])
        else:
            all_voices = []
            for voices in self._voices.values():
                all_voices.extend(voices)
        
        # 应用过滤条件
        filtered_voices = all_voices
        
        if language:
            filtered_voices = [v for v in filtered_voices if v.get('language') == language]
        
        if gender:
            filtered_voices = [v for v in filtered_voices if v.get('gender') == gender]
        
        if category:
            filtered_voices = [v for v in filtered_voices if v.get('category') == category]
        
        if tags:
            filtered_voices = [
                v for v in filtered_voices
                if any(tag in v.get('tags', []) for tag in tags)
            ]
        
        return filtered_voices

