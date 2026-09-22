"""配置管理器 - 多级配置加载"""
import os
import json
import shutil
from pathlib import Path
from typing import Optional
from .models import Config

# 默认配置
DEFAULT_CONFIG = {
    "llm": {
        "provider": "ollama",
        "model": "qwen2:7b",
        "api_key": "",
        "base_url": "http://localhost:11434/v1",
        "temperature": 0.7,
        "max_tokens": 4096,
        "timeout": 60,
    },
    "ocr": {
        "engine": "paddle",
        "lang": "ch",
        "dpi": 200,
        "use_gpu": False,
    },
    "vector_db": {
        "type": "chromadb",
        "path": "./data/chroma_db",
        "collection": "documents",
        "host": "localhost",
        "port": 5432,
        "username": "",
        "password": "",
    },
    "analysis": {
        "sample_pages": 50,
        "chunk_size": 800,
        "chunk_overlap": 150,
    },
}


class ConfigManager:
    """配置管理器
    
    加载优先级（高→低）：
    1. 环境变量 DOC_ROUTER_CONFIG
    2. ~/.doc-router/config.json (用户配置)
    3. ./config.json (项目本地配置)
    4. 包内默认配置
    """

    # 用户目录名称
    USER_DIR_NAME = ".doc-router"

    def __init__(self, config_path: Optional[str] = None):
        """
        Args:
            config_path: 自定义配置文件路径，优先级最高
        """
        self._config: Optional[Config] = None
        self._config_path = config_path
        self._user_dir = self._get_user_dir()
        self._project_dir = Path.cwd()

    def _get_user_dir(self) -> Path:
        """获取用户配置目录"""
        home = Path.home()
        user_dir = home / self.USER_DIR_NAME
        
        # 如果目录不存在，创建它
        if not user_dir.exists():
            user_dir.mkdir(parents=True, exist_ok=True)
        
        return user_dir

    def _get_default_config_path(self) -> Path:
        """获取包内默认配置路径"""
        return Path(__file__).parent / "defaults.json"

    def _load_json(self, path: Path) -> Optional[dict]:
        """加载JSON配置文件"""
        try:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"警告: 加载配置文件失败 {path}: {e}")
        return None

    def _save_json(self, path: Path, data: dict) -> bool:
        """保存JSON配置文件"""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"错误: 保存配置文件失败 {path}: {e}")
            return False

    def _merge_dict(self, base: dict, override: dict) -> dict:
        """合并两个字典，override覆盖base"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dict(result[key], value)
            else:
                result[key] = value
        return result

    def _apply_env_vars(self, config: dict) -> dict:
        """应用环境变量覆盖"""
        # LLM配置
        if os.environ.get("DOC_ROUTER_LLM_PROVIDER"):
            config["llm"]["provider"] = os.environ["DOC_ROUTER_LLM_PROVIDER"]
        if os.environ.get("DOC_ROUTER_LLM_MODEL"):
            config["llm"]["model"] = os.environ["DOC_ROUTER_LLM_MODEL"]
        if os.environ.get("DOC_ROUTER_LLM_API_KEY"):
            config["llm"]["api_key"] = os.environ["DOC_ROUTER_LLM_API_KEY"]
        if os.environ.get("DOC_ROUTER_LLM_BASE_URL"):
            config["llm"]["base_url"] = os.environ["DOC_ROUTER_LLM_BASE_URL"]
        
        # OCR配置
        if os.environ.get("DOC_ROUTER_OCR_ENGINE"):
            config["ocr"]["engine"] = os.environ["DOC_ROUTER_OCR_ENGINE"]
        
        # 向量库配置
        if os.environ.get("DOC_ROUTER_VECTOR_DB_TYPE"):
            config["vector_db"]["type"] = os.environ["DOC_ROUTER_VECTOR_DB_TYPE"]
        
        return config

    def load(self, force_reload: bool = False) -> Config:
        """加载配置
        
        Args:
            force_reload: 是否强制重新加载
            
        Returns:
            Config对象
        """
        if self._config is not None and not force_reload:
            return self._config

        # 1. 从默认配置开始
        config_data = DEFAULT_CONFIG.copy()

        # 2. 加载包内默认配置文件（如果存在）
        default_path = self._get_default_config_path()
        default_data = self._load_json(default_path)
        if default_data:
            config_data = self._merge_dict(config_data, default_data)

        # 3. 加载用户配置
        user_config_path = self._user_dir / "config.json"
        user_data = self._load_json(user_config_path)
        if user_data:
            config_data = self._merge_dict(config_data, user_data)

        # 4. 加载项目本地配置
        local_config_path = self._project_dir / "config.json"
        local_data = self._load_json(local_config_path)
        if local_data:
            config_data = self._merge_dict(config_data, local_data)

        # 5. 加载自定义配置文件（优先级最高）
        if self._config_path:
            custom_path = Path(self._config_path)
            custom_data = self._load_json(custom_path)
            if custom_data:
                config_data = self._merge_dict(config_data, custom_data)

        # 6. 应用环境变量
        config_data = self._apply_env_vars(config_data)

        # 7. 创建Config对象
        self._config = Config.from_dict(config_data)
        
        return self._config

    def save(self, config: Optional[Config] = None, target: str = "user") -> bool:
        """保存配置
        
        Args:
            config: 要保存的配置，None则保存当前配置
            target: 保存目标 (user / local / custom)
            
        Returns:
            是否保存成功
        """
        if config is None:
            config = self._config
        if config is None:
            print("错误: 没有配置可保存")
            return False

        data = config.to_dict()

        if target == "user":
            path = self._user_dir / "config.json"
        elif target == "local":
            path = self._project_dir / "config.json"
        elif target == "custom" and self._config_path:
            path = Path(self._config_path)
        else:
            print(f"错误: 未知的保存目标 {target}")
            return False

        return self._save_json(path, data)

    def reset(self, target: str = "user") -> bool:
        """重置配置文件为默认值
        
        Args:
            target: 重置目标 (user / local)
            
        Returns:
            是否重置成功
        """
        if target == "user":
            path = self._user_dir / "config.json"
        elif target == "local":
            path = self._project_dir / "config.json"
        else:
            print(f"错误: 未知的重置目标 {target}")
            return False

        return self._save_json(path, DEFAULT_CONFIG)

    def get_user_dir(self) -> Path:
        """获取用户配置目录路径"""
        return self._user_dir

    def get_structures_dir(self) -> Path:
        """获取用户结构模板目录"""
        structures_dir = self._user_dir / "structures"
        if not structures_dir.exists():
            structures_dir.mkdir(parents=True, exist_ok=True)
        return structures_dir

    def get_config_info(self) -> dict:
        """获取配置加载信息"""
        return {
            "user_dir": str(self._user_dir),
            "project_dir": str(self._project_dir),
            "config_path": self._config_path,
            "env_vars": {
                "DOC_ROUTER_CONFIG": os.environ.get("DOC_ROUTER_CONFIG", ""),
                "DOC_ROUTER_LLM_PROVIDER": os.environ.get("DOC_ROUTER_LLM_PROVIDER", ""),
            },
        }
