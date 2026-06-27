"""插件管理器 - 管理搜索插件的加载和调用"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod


class SearchPlugin(ABC):
    """搜索插件基类"""
    
    name: str = ""
    description: str = ""
    version: str = ""
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查插件是否可用"""
        pass
    
    @abstractmethod
    def search(self, query: str, **kwargs) -> dict:
        """执行搜索"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """获取插件能力列表"""
        pass


class PluginManager:
    """插件管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.plugins: Dict[str, SearchPlugin] = {}
        self.config_path = config_path or self._default_config_path()
        self.config = self._load_config()
    
    def _default_config_path(self) -> str:
        """获取默认配置文件路径"""
        return str(Path(__file__).parent.parent.parent / "config" / "plugins.json")
    
    def _load_config(self) -> dict:
        """加载插件配置"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"plugins": {}}
    
    def register_plugin(self, plugin: SearchPlugin) -> bool:
        """注册插件"""
        if not plugin.name:
            return False
        
        # 检查配置中是否启用
        plugin_config = self.config.get("plugins", {}).get(plugin.name, {})
        if not plugin_config.get("enabled", True):
            return False
        
        # 检查插件是否可用
        if not plugin.is_available():
            return False
        
        self.plugins[plugin.name] = plugin
        return True
    
    def get_plugin(self, name: str) -> Optional[SearchPlugin]:
        """获取插件"""
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[dict]:
        """列出所有插件"""
        result = []
        for name, plugin in self.plugins.items():
            result.append({
                "name": name,
                "description": plugin.description,
                "version": plugin.version,
                "capabilities": plugin.get_capabilities(),
                "available": plugin.is_available()
            })
        return result
    
    def search(self, plugin_name: str, query: str, **kwargs) -> dict:
        """使用指定插件搜索"""
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            return {"ok": False, "error": f"Plugin {plugin_name} not found"}
        
        if not plugin.is_available():
            return {"ok": False, "error": f"Plugin {plugin_name} not available"}
        
        return plugin.search(query, **kwargs)


# 插件示例：AnySearch 插件
class AnySearchPlugin(SearchPlugin):
    """AnySearch 垂直搜索插件"""
    
    name = "anysearch"
    description = "垂直领域搜索（金融、学术、代码等）"
    version = "2.1.0"
    
    def __init__(self, api_endpoint: str = "https://api.anysearch.com/mcp", api_key: str = ""):
        self.api_endpoint = api_endpoint
        self.api_key = api_key
    
    def is_available(self) -> bool:
        """检查插件是否可用"""
        # 检查 API 是否可访问
        try:
            import requests
            response = requests.get(self.api_endpoint, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def search(self, query: str, **kwargs) -> dict:
        """执行搜索"""
        import requests
        
        domain = kwargs.get("domain", "general")
        sub_domain = kwargs.get("sub_domain", "")
        max_results = kwargs.get("max_results", 5)
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "search",
                "arguments": {
                    "query": query,
                    "max_results": max_results
                }
            }
        }
        
        if domain and domain != "general":
            payload["params"]["arguments"]["domain"] = domain
        if sub_domain:
            payload["params"]["arguments"]["sub_domain"] = sub_domain
        
        try:
            response = requests.post(self.api_endpoint, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return {"ok": True, "results": response.json()}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        """获取插件能力列表"""
        return [
            "general", "finance", "academic", "legal", "health",
            "business", "security", "ip", "code", "energy",
            "environment", "agriculture", "travel", "film", "gaming"
        ]


# 插件示例：DuckDuckGo 插件（内置）
class DuckDuckGoPlugin(SearchPlugin):
    """DuckDuckGo 搜索插件（内置）"""
    
    name = "duckduckgo"
    description = "DuckDuckGo 搜索（内置，零依赖）"
    version = "1.0.0"
    
    def is_available(self) -> bool:
        """检查插件是否可用"""
        return True  # 内置插件始终可用
    
    def search(self, query: str, **kwargs) -> dict:
        """执行搜索"""
        # 这里实现 DuckDuckGo 搜索逻辑
        return {"ok": True, "results": [], "note": "DuckDuckGo search placeholder"}
    
    def get_capabilities(self) -> List[str]:
        """获取插件能力列表"""
        return ["web_search"]


# 全局插件管理器实例
_plugin_manager = None


def get_plugin_manager() -> PluginManager:
    """获取全局插件管理器实例"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
        # 注册内置插件
        _plugin_manager.register_plugin(DuckDuckGoPlugin())
    return _plugin_manager
