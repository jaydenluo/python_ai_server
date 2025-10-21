"""
图像处理工具
提供图片处理、压缩、水印等功能
"""

from PIL import Image, ImageDraw, ImageFont
import os
from typing import Tuple, Optional, Dict, Any
import base64
from io import BytesIO


def resize_image(image_path: str, width: int, height: int, 
                output_path: Optional[str] = None, maintain_aspect: bool = True) -> str:
    """
    调整图片尺寸
    
    Args:
        image_path: 输入图片路径
        width: 目标宽度
        height: 目标高度
        output_path: 输出路径，None时覆盖原文件
        maintain_aspect: 是否保持宽高比
        
    Returns:
        str: 输出文件路径
    """
    try:
        with Image.open(image_path) as img:
            if maintain_aspect:
                img.thumbnail((width, height), Image.Resampling.LANCZOS)
            else:
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            if output_path is None:
                output_path = image_path
            
            img.save(output_path, optimize=True)
            return output_path
    except Exception as e:
        raise ValueError(f"图片调整失败: {str(e)}")


def compress_image(image_path: str, quality: int = 80, 
                  output_path: Optional[str] = None) -> str:
    """
    压缩图片
    
    Args:
        image_path: 输入图片路径
        quality: 压缩质量 (1-100)
        output_path: 输出路径，None时覆盖原文件
        
    Returns:
        str: 输出文件路径
    """
    try:
        with Image.open(image_path) as img:
            # 转换为RGB模式（如果需要）
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            if output_path is None:
                output_path = image_path
            
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            return output_path
    except Exception as e:
        raise ValueError(f"图片压缩失败: {str(e)}")


def generate_thumbnail(image_path: str, size: Tuple[int, int], 
                      output_path: Optional[str] = None) -> str:
    """
    生成缩略图
    
    Args:
        image_path: 输入图片路径
        size: 缩略图尺寸 (width, height)
        output_path: 输出路径
        
    Returns:
        str: 缩略图路径
    """
    try:
        with Image.open(image_path) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            if output_path is None:
                name, ext = os.path.splitext(image_path)
                output_path = f"{name}_thumb{ext}"
            
            img.save(output_path, optimize=True)
            return output_path
    except Exception as e:
        raise ValueError(f"缩略图生成失败: {str(e)}")


def add_watermark(image_path: str, watermark_text: str, 
                 output_path: Optional[str] = None, 
                 position: str = 'bottom-right',
                 font_size: int = 20, opacity: int = 128) -> str:
    """
    添加文字水印
    
    Args:
        image_path: 输入图片路径
        watermark_text: 水印文字
        output_path: 输出路径
        position: 水印位置 ('top-left', 'top-right', 'bottom-left', 'bottom-right', 'center')
        font_size: 字体大小
        opacity: 透明度 (0-255)
        
    Returns:
        str: 输出文件路径
    """
    try:
        with Image.open(image_path) as img:
            # 创建透明图层
            watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            
            # 尝试加载字体
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except OSError:
                font = ImageFont.load_default()
            
            # 获取文字尺寸
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 计算位置
            margin = 10
            if position == 'top-left':
                x, y = margin, margin
            elif position == 'top-right':
                x, y = img.width - text_width - margin, margin
            elif position == 'bottom-left':
                x, y = margin, img.height - text_height - margin
            elif position == 'bottom-right':
                x, y = img.width - text_width - margin, img.height - text_height - margin
            elif position == 'center':
                x, y = (img.width - text_width) // 2, (img.height - text_height) // 2
            else:
                x, y = img.width - text_width - margin, img.height - text_height - margin
            
            # 绘制水印
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, opacity))
            
            # 合并图像
            watermarked = Image.alpha_composite(img.convert('RGBA'), watermark)
            
            if output_path is None:
                name, ext = os.path.splitext(image_path)
                output_path = f"{name}_watermarked{ext}"
            
            # 保存时转换回原格式
            if img.mode != 'RGBA':
                watermarked = watermarked.convert(img.mode)
            
            watermarked.save(output_path)
            return output_path
    except Exception as e:
        raise ValueError(f"水印添加失败: {str(e)}")


def get_image_info(image_path: str) -> Dict[str, Any]:
    """
    获取图片信息
    
    Args:
        image_path: 图片路径
        
    Returns:
        Dict: 图片信息
    """
    try:
        with Image.open(image_path) as img:
            file_size = os.path.getsize(image_path)
            
            return {
                'filename': os.path.basename(image_path),
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.width,
                'height': img.height,
                'file_size': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
            }
    except Exception as e:
        raise ValueError(f"获取图片信息失败: {str(e)}")


def is_valid_image(file_path: str) -> bool:
    """
    检查是否为有效图片
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 是否为有效图片
    """
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False


def convert_format(image_path: str, target_format: str, 
                  output_path: Optional[str] = None) -> str:
    """
    转换图片格式
    
    Args:
        image_path: 输入图片路径
        target_format: 目标格式 ('JPEG', 'PNG', 'WEBP', etc.)
        output_path: 输出路径
        
    Returns:
        str: 输出文件路径
    """
    try:
        with Image.open(image_path) as img:
            # 处理透明度
            if target_format.upper() == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                # JPEG不支持透明度，转换为RGB
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            if output_path is None:
                name, _ = os.path.splitext(image_path)
                ext = '.jpg' if target_format.upper() == 'JPEG' else f'.{target_format.lower()}'
                output_path = f"{name}{ext}"
            
            img.save(output_path, target_format.upper())
            return output_path
    except Exception as e:
        raise ValueError(f"格式转换失败: {str(e)}")


def crop_image(image_path: str, box: Tuple[int, int, int, int], 
              output_path: Optional[str] = None) -> str:
    """
    裁剪图片
    
    Args:
        image_path: 输入图片路径
        box: 裁剪区域 (left, top, right, bottom)
        output_path: 输出路径
        
    Returns:
        str: 输出文件路径
    """
    try:
        with Image.open(image_path) as img:
            cropped = img.crop(box)
            
            if output_path is None:
                name, ext = os.path.splitext(image_path)
                output_path = f"{name}_cropped{ext}"
            
            cropped.save(output_path)
            return output_path
    except Exception as e:
        raise ValueError(f"图片裁剪失败: {str(e)}")


def rotate_image(image_path: str, angle: float, 
                output_path: Optional[str] = None) -> str:
    """
    旋转图片
    
    Args:
        image_path: 输入图片路径
        angle: 旋转角度（逆时针）
        output_path: 输出路径
        
    Returns:
        str: 输出文件路径
    """
    try:
        with Image.open(image_path) as img:
            rotated = img.rotate(angle, expand=True)
            
            if output_path is None:
                name, ext = os.path.splitext(image_path)
                output_path = f"{name}_rotated{ext}"
            
            rotated.save(output_path)
            return output_path
    except Exception as e:
        raise ValueError(f"图片旋转失败: {str(e)}")


def image_to_base64(image_path: str) -> str:
    """
    图片转Base64编码
    
    Args:
        image_path: 图片路径
        
    Returns:
        str: Base64编码字符串
    """
    try:
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
            base64_str = base64.b64encode(img_data).decode('utf-8')
            
            # 获取MIME类型
            with Image.open(image_path) as img:
                format_lower = img.format.lower()
                mime_type = f"image/{format_lower}"
            
            return f"data:{mime_type};base64,{base64_str}"
    except Exception as e:
        raise ValueError(f"Base64转换失败: {str(e)}")


def base64_to_image(base64_str: str, output_path: str) -> str:
    """
    Base64编码转图片
    
    Args:
        base64_str: Base64编码字符串
        output_path: 输出路径
        
    Returns:
        str: 输出文件路径
    """
    try:
        # 移除data URL前缀
        if base64_str.startswith('data:'):
            base64_str = base64_str.split(',')[1]
        
        img_data = base64.b64decode(base64_str)
        
        with open(output_path, 'wb') as img_file:
            img_file.write(img_data)
        
        return output_path
    except Exception as e:
        raise ValueError(f"Base64解码失败: {str(e)}")


def create_image_grid(image_paths: list, grid_size: Tuple[int, int], 
                     cell_size: Tuple[int, int], output_path: str) -> str:
    """
    创建图片网格
    
    Args:
        image_paths: 图片路径列表
        grid_size: 网格尺寸 (cols, rows)
        cell_size: 单元格尺寸 (width, height)
        output_path: 输出路径
        
    Returns:
        str: 输出文件路径
    """
    try:
        cols, rows = grid_size
        cell_width, cell_height = cell_size
        
        # 创建空白画布
        canvas_width = cols * cell_width
        canvas_height = rows * cell_height
        canvas = Image.new('RGB', (canvas_width, canvas_height), (255, 255, 255))
        
        # 放置图片
        for i, img_path in enumerate(image_paths[:cols * rows]):
            if not os.path.exists(img_path):
                continue
            
            row = i // cols
            col = i % cols
            
            x = col * cell_width
            y = row * cell_height
            
            with Image.open(img_path) as img:
                # 调整图片尺寸
                img = img.resize((cell_width, cell_height), Image.Resampling.LANCZOS)
                canvas.paste(img, (x, y))
        
        canvas.save(output_path)
        return output_path
    except Exception as e:
        raise ValueError(f"图片网格创建失败: {str(e)}")