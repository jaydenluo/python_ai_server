"""
自动发现系统
提供 Models、Services、Controllers 的自动发现和注册功能
支持智能导入和模块钩子
"""

from .auto_discovery import (
    AutoDiscovery,
    DiscoveredItem,
    get_auto_discovery,
    discover_all_components,
    get_models,
    get_services, 
    get_controllers,
    get_model_by_name,
    get_service_by_name,
    print_discovery_report
)

from .smart_importer import (
    SmartImporter,
    smart_import,
    get_available_exports,
    create_module_hooks
)

from .module_hooks import (
    setup_smart_import,
    create_smart_init
)

from .stub_generator import (
    StubGenerator,
    generate_stub_for_package,
    generate_all_stubs,
    update_stub_if_needed
)

__all__ = [
    # 原有的自动发现功能
    "AutoDiscovery",
    "DiscoveredItem", 
    "get_auto_discovery",
    "discover_all_components",
    "get_models",
    "get_services",
    "get_controllers", 
    "get_model_by_name",
    "get_service_by_name",
    "print_discovery_report",
    
    # 新的智能导入功能
    "SmartImporter",
    "smart_import",
    "get_available_exports",
    "create_module_hooks",
    "setup_smart_import",
    "create_smart_init",
    
    # 类型存根生成功能
    "StubGenerator",
    "generate_stub_for_package",
    "generate_all_stubs",
    "update_stub_if_needed"
]