"""
VoxChina 统一内容生成器配置文件
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class VoxConfig:
    """配置类"""
    
    # ===== LLM 配置 =====
    DEFAULT_LLM_PROVIDER = os.getenv('DEFAULT_LLM_PROVIDER', 'openai')
    DEFAULT_MODEL_NAME = os.getenv('DEFAULT_MODEL_NAME', 'gpt-4o-mini')
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Anthropic (Claude)
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    
    # Azure OpenAI
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY', '')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT', '')
    AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
    
    # ===== 生成配置 =====
    # 并行处理最大线程数
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', '5'))
    
    # 单篇摘要字数范围
    SINGLE_SUMMARY_MIN_CHARS = int(os.getenv('SINGLE_SUMMARY_MIN_CHARS', '120'))
    SINGLE_SUMMARY_MAX_CHARS = int(os.getenv('SINGLE_SUMMARY_MAX_CHARS', '260'))
    
    # 多篇口播默认时长（秒）
    MULTI_SCRIPT_DEFAULT_DURATION = int(os.getenv('MULTI_SCRIPT_DEFAULT_DURATION', '150'))
    
    # 文档截断模式
    # - 'aggressive': 激进截断（单篇摘要）
    # - 'moderate': 适度截断（多篇要点）
    # - 'none': 不截断
    TRUNCATE_MODE_SINGLE = os.getenv('TRUNCATE_MODE_SINGLE', 'aggressive')
    TRUNCATE_MODE_MULTI = os.getenv('TRUNCATE_MODE_MULTI', 'moderate')
    
    # ===== 输出配置 =====
    DEFAULT_OUTPUT_DIR = os.getenv('DEFAULT_OUTPUT_DIR', 'output')
    
    # ===== 调试配置 =====
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    MOCK_MODE = os.getenv('MOCK_MODE', 'false').lower() == 'true'
    
    @classmethod
    def validate(cls):
        """验证配置"""
        errors = []
        
        if cls.DEFAULT_LLM_PROVIDER == 'openai' and not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY 未设置")
        
        if cls.DEFAULT_LLM_PROVIDER == 'anthropic' and not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY 未设置")
        
        if cls.DEFAULT_LLM_PROVIDER == 'azure':
            if not cls.AZURE_OPENAI_API_KEY:
                errors.append("AZURE_OPENAI_API_KEY 未设置")
            if not cls.AZURE_OPENAI_ENDPOINT:
                errors.append("AZURE_OPENAI_ENDPOINT 未设置")
        
        if errors:
            print("⚠️  配置警告:")
            for error in errors:
                print(f"  - {error}")
            print("\n请创建 .env 文件或设置相应环境变量。")
            print("参考环境变量配置：")
            print("  export OPENAI_API_KEY='sk-your-key-here'")
        
        return len(errors) == 0
    
    @classmethod
    def print_config(cls):
        """打印当前配置（隐藏敏感信息）"""
        print("VoxChina 当前配置:")
        print(f"  LLM Provider: {cls.DEFAULT_LLM_PROVIDER}")
        print(f"  Model: {cls.DEFAULT_MODEL_NAME}")
        print(f"  Max Workers: {cls.MAX_WORKERS}")
        print(f"  Output Dir: {cls.DEFAULT_OUTPUT_DIR}")
        print(f"  Debug Mode: {cls.DEBUG}")
        print(f"  Mock Mode: {cls.MOCK_MODE}")
        
        # API Key 状态（隐藏实际值）
        if cls.OPENAI_API_KEY:
            print(f"  OpenAI API Key: {'*' * 10}...{cls.OPENAI_API_KEY[-4:]}")
        if cls.ANTHROPIC_API_KEY:
            print(f"  Anthropic API Key: {'*' * 10}...{cls.ANTHROPIC_API_KEY[-4:]}")
        if cls.AZURE_OPENAI_API_KEY:
            print(f"  Azure API Key: {'*' * 10}...{cls.AZURE_OPENAI_API_KEY[-4:]}")


# 环境变量示例（可复制到 .env 文件）
ENV_TEMPLATE = """
# VoxChina 统一内容生成器环境变量配置
# 复制此文件为 .env 并填入真实值

# ===== OpenAI 配置 =====
OPENAI_API_KEY=sk-your-openai-api-key-here

# ===== Anthropic (Claude) 配置（可选） =====
# ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# ===== Azure OpenAI 配置（可选） =====
# AZURE_OPENAI_API_KEY=your-azure-key-here
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
# AZURE_OPENAI_API_VERSION=2024-02-15-preview

# ===== 其他配置 =====
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL_NAME=gpt-4o-mini
MAX_WORKERS=5
DEFAULT_OUTPUT_DIR=output
DEBUG=false
MOCK_MODE=false
"""


if __name__ == "__main__":
    VoxConfig.validate()
    VoxConfig.print_config()
