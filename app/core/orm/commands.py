"""
智能ORM命令系统
提供命令行工具来管理模型和数据库
"""

import sys
import argparse
from typing import List, Type, Dict, Any
from pathlib import Path
import importlib
import inspect

from app.core.orm.migration_system import migration_manager, ModelAnalyzer
from app.models.base import Model


class ORMCommands:
    """ORM命令系统"""
    
    def __init__(self):
        self.analyzer = ModelAnalyzer()
    
    def migrate(self, args):
        """执行迁移"""
        print("🔄 检测模型变更...")
        
        # 获取所有模型类
        model_classes = self._get_all_models()
        
        # 自动迁移
        result = migration_manager.auto_migrate(model_classes, dry_run=args.dry_run)
        
        print(f"📊 检测到 {len(result['detected_changes'])} 个变更")
        
        if result['detected_changes']:
            print("\n📋 检测到的变更:")
            for change in result['detected_changes']:
                print(f"  - {change}")
            
            print("\n🔧 生成的SQL语句:")
            for sql_info in result['sql_statements']:
                print(f"  {sql_info['migration']}:")
                print(f"    {sql_info['sql']}")
            
            if args.dry_run:
                print("\n⚠️  这是预览模式，没有实际执行迁移")
                print("使用 --execute 参数来执行迁移")
            else:
                print("\n✅ 迁移文件已生成")
                for file in result['generated_files']:
                    print(f"  - {file}")
        else:
            print("✅ 没有检测到模型变更")
    
    def status(self, args):
        """查看迁移状态"""
        print("📊 模型状态检查")
        print("=" * 50)
        
        model_classes = self._get_all_models()
        
        for model_class in model_classes:
            table_name = getattr(model_class, '__table__', model_class.__name__.lower())
            schema = self.analyzer.analyze_model(model_class)
            
            print(f"\n📋 模型: {model_class.__name__}")
            print(f"   表名: {table_name}")
            print(f"   列数: {len(schema.columns)}")
            print(f"   时间戳: {'是' if schema.timestamps else '否'}")
            
            print("   列信息:")
            for col in schema.columns:
                nullable = "可空" if col.nullable else "非空"
                pk = " (主键)" if col.primary_key else ""
                print(f"     - {col.name}: {col.type} ({nullable}){pk}")
    
    def generate_model(self, args):
        """生成模型"""
        model_name = args.name
        table_name = args.table or model_name.lower()
        
        print(f"🔧 生成模型: {model_name}")
        
        # 生成模型文件内容
        content = self._generate_model_content(model_name, table_name)
        
        # 保存文件
        model_file = Path(f"app/models/{model_name.lower()}.py")
        model_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(model_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 模型文件已生成: {model_file}")
    
    def analyze_models(self, args):
        """分析模型"""
        print("🔍 分析模型结构")
        print("=" * 50)
        
        model_classes = self._get_all_models()
        
        for model_class in model_classes:
            print(f"\n📋 模型: {model_class.__name__}")
            
            # 分析模型属性
            annotations = getattr(model_class, '__annotations__', {})
            print(f"   属性数量: {len(annotations)}")
            
            for name, annotation in annotations.items():
                if not name.startswith('_'):
                    print(f"     - {name}: {annotation}")
            
            # 分析关系
            relationships = getattr(model_class, '__relationships__', {})
            if relationships:
                print(f"   关系数量: {len(relationships)}")
                for name, rel in relationships.items():
                    print(f"     - {name}: {rel.type.value} -> {rel.model.__name__}")
    
    def _get_all_models(self) -> List[Type[Model]]:
        """获取所有模型类"""
        models = []
        
        # 扫描models目录
        models_dir = Path("app/models")
        if models_dir.exists():
            for file in models_dir.glob("*.py"):
                if file.name == "__init__.py":
                    continue
                
                try:
                    module_name = f"app.models.{file.stem}"
                    module = importlib.import_module(module_name)
                    
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, Model) and 
                            obj != Model):
                            models.append(obj)
                except ImportError as e:
                    print(f"⚠️  无法导入模块 {module_name}: {e}")
        
        return models
    
    def _generate_model_content(self, model_name: str, table_name: str) -> str:
        """生成模型文件内容"""
        return f'''"""
{model_name}模型
自动生成的模型文件
"""

from typing import Optional
from datetime import datetime
from .base import Model


class {model_name}(Model):
    """{model_name}模型"""
    
    __table__ = "{table_name}"
    __fillable__ = [
        # 在这里添加可填充字段
    ]
    __hidden__ = [
        # 在这里添加隐藏字段
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    # 在这里添加模型方法
'''
    
    def run(self):
        """运行命令"""
        parser = argparse.ArgumentParser(description="智能ORM命令系统")
        subparsers = parser.add_subparsers(dest="command", help="可用命令")
        
        # migrate命令
        migrate_parser = subparsers.add_parser("migrate", help="执行数据库迁移")
        migrate_parser.add_argument("--dry-run", action="store_true", help="预览模式，不执行迁移")
        migrate_parser.add_argument("--execute", action="store_true", help="执行迁移")
        
        # status命令
        status_parser = subparsers.add_parser("status", help="查看迁移状态")
        
        # generate命令
        generate_parser = subparsers.add_parser("generate", help="生成模型")
        generate_parser.add_argument("name", help="模型名称")
        generate_parser.add_argument("--table", help="表名")
        
        # analyze命令
        analyze_parser = subparsers.add_parser("analyze", help="分析模型")
        
        args = parser.parse_args()
        
        if args.command == "migrate":
            self.migrate(args)
        elif args.command == "status":
            self.status(args)
        elif args.command == "generate":
            self.generate_model(args)
        elif args.command == "analyze":
            self.analyze_models(args)
        else:
            parser.print_help()


def main():
    """主函数"""
    commands = ORMCommands()
    commands.run()


if __name__ == "__main__":
    main()