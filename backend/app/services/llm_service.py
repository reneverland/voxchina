import httpx
import json
import os
from loguru import logger
from app.core.config import settings
from openai import AsyncOpenAI

PROMPTS = {
    "zh": {
        "summary": """
        请为以下文章生成一个精炼的摘要，字数控制在{max_words}字以内。
        摘要应保留核心观点，适合作为音频播报的文案。
        
        文章内容：
        {content}
        """,
        "integrate": """
        请阅读以下多篇文章的内容，并将它们整合成一篇连贯、有深度的文章。
        
        要求：
        1. 字数控制在 {max_words} 字左右。
        2. {focus_prompt}
        3. 语言流畅，逻辑清晰，避免简单的拼接。
        4. 适合作为音频播报的文案。
        
        文章内容：
        {combined_content}
        """,
        "focus_default": "综合所有文章的关键点。",
        "focus_prefix": "重点关注：",
        "answer": """
        请根据提供的参考资料回答用户的问题。
        如果参考资料中没有相关信息，请诚实地说明无法回答。
        
        参考资料：
        {context_block}
        
        用户问题：
        {query}
        
        请用专业、连贯的语言回答：
        """,
        "trending": """
        你是一个专业的社交媒体运营专家。请根据以下信息，针对话题“{topic}”写一篇快速响应推文。
        
        最新网络资讯：
        {web_text}
        
        相关背景知识（自有库）：
        {local_text}
        
        要求：
        1. 标题吸引眼球。
        2. 内容结合时事热点和深度背景。
        3. 语气专业、客观但有观点。
        4. 适合微信公众号或今日头条发布。
        """,
        "script": """
        请将以下文章内容改编为短视频分镜脚本。
        
        文章内容：
        {content}
        
        输出格式要求（Markdown表格）：
        | 镜号 | 画面描述 (Visual) | 口播文案 (Audio) | 备注 |
        |---|---|---|---|
        | 1 | [场景描述] | [对应台词] | [音效/贴图建议] |
        
        要求：
        1. 节奏紧凑，适合1-3分钟短视频。
        2. 画面描述要具体，包含运镜建议。
        3. 口播文案要口语化。
        """
    },
    "en": {
        "summary": """
        Please generate a concise summary for the following article, keeping it under {max_words} words.
        The summary should retain core points and be suitable for audio broadcasting.
        
        Article Content:
        {content}
        """,
        "integrate": """
        Please read the contents of the following multiple articles and integrate them into a coherent, in-depth article.
        
        Requirements:
        1. Keep the word count around {max_words} words.
        2. {focus_prompt}
        3. Ensure fluent language and clear logic; avoid simple splicing.
        4. Suitable for audio broadcasting.
        
        Article Contents:
        {combined_content}
        """,
        "focus_default": "Synthesize the key points from all articles.",
        "focus_prefix": "Focus on: ",
        "answer": """
        Please answer the user's question based on the provided reference materials.
        If there is no relevant information in the references, honestly state that you cannot answer.
        
        Reference Materials:
        {context_block}
        
        User Question:
        {query}
        
        Please answer in professional and coherent language:
        """,
        "trending": """
        You are a professional social media operations expert. Please write a quick response post for the topic "{topic}" based on the following information.
        
        Latest Web Info:
        {web_text}
        
        Relevant Background (Local Knowledge Base):
        {local_text}
        
        Requirements:
        1. Catchy title.
        2. Combine current events with deep background.
        3. Professional, objective tone but with a viewpoint.
        4. Suitable for posting on Twitter or LinkedIn.
        """,
        "script": """
        Please adapt the following article content into a short video storyboard script.
        
        Article Content:
        {content}
        
        Output Format Requirement (Markdown Table):
        | Shot | Visual Description | Audio Script | Notes |
        |---|---|---|---|
        | 1 | [Scene Description] | [Lines] | [SFX/Sticker Suggestions] |
        
        Requirements:
        1. Fast-paced, suitable for a 1-3 minute short video.
        2. Visual descriptions should be specific, including camera movement suggestions.
        3. Audio script should be colloquial.
        """
    }
}

class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.config_file = "llm_config.json"
        
        # Load persisted config if exists
        self._load_config_from_file()
        
        # Ollama config
        self.ollama_base_url = settings.OLLAMA_HOST
        self.ollama_model = settings.OLLAMA_MODEL
        
        # OpenAI config
        if self.provider == "openai":
            if not settings.OPENAI_API_KEY:
                logger.error("⚠️  OPENAI_API_KEY 未配置！请在 .env 文件中设置或通过管理界面配置")
            self.openai_client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY or "dummy-key",  # 防止初始化失败
                base_url=settings.OPENAI_API_BASE,
                timeout=300.0  # 5分钟超时，适配gpt-4o的长响应时间
            )
        else:
            self.openai_client = None

    def _load_config_from_file(self):
        """Load configuration from local file (including API key)."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    if config.get('provider'):
                        self.provider = config['provider']
                        settings.LLM_PROVIDER = config['provider']
                    if config.get('model'):
                        self.model = config['model']
                        settings.LLM_MODEL = config['model']
                    # Load API key if exists
                    if config.get('api_key') and config.get('provider') == 'openai':
                        settings.OPENAI_API_KEY = config['api_key']
                        logger.info("✅ 已从配置文件加载 API Key")
                        settings.LLM_MODEL = config['model']
                logger.info(f"Loaded LLM config from file: {self.provider}/{self.model}")
        except Exception as e:
            logger.error(f"Failed to load LLM config file: {e}")

    def _save_config_to_file(self):
        """Save configuration to local file (including API key)."""
        try:
            config = {
                "provider": self.provider,
                "model": self.model
            }
            # Save API key if set (for openai provider)
            if self.provider == "openai" and settings.OPENAI_API_KEY:
                config["api_key"] = settings.OPENAI_API_KEY
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"✅ 已保存 LLM 配置到文件: {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save LLM config file: {e}")

    def _get_prompt(self, key: str, language: str = "zh") -> str:
        lang = language if language in ["zh", "en"] else "zh"
        return PROMPTS[lang][key]
    
    async def _generate_with_provider(self, prompt: str, timeout: float = 60.0, model: str = None, system_prompt: str = None) -> str:
        """
        Generate text using the configured LLM provider (OpenAI or Ollama).
        
        Args:
            prompt: User prompt
            timeout: Request timeout in seconds
            model: Optional model override
            system_prompt: Optional system prompt (defaults to generic assistant prompt)
        """
        if self.provider == "openai":
            # 检查 API Key
            if not settings.OPENAI_API_KEY:
                raise Exception("❌ LLM API Key 未配置！请联系管理员在【LLM设置】中配置 API 密钥")
            
            try:
                # Use custom system prompt if provided, otherwise use default
                sys_content = system_prompt if system_prompt else "You are a helpful AI assistant that provides professional and accurate responses."
                
                response = await self.openai_client.chat.completions.create(
                    model=model or self.model,
                    messages=[
                        {"role": "system", "content": sys_content},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    timeout=timeout
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error generating with OpenAI: {error_msg}")
                
                # 检查具体错误类型
                if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                    raise Exception("LLM响应超时，请稍后重试")
                elif "rate limit" in error_msg.lower() or "429" in error_msg:
                    raise Exception("API调用频率限制，请稍后重试")
                elif "401" in error_msg or "unauthorized" in error_msg.lower():
                    raise Exception("LLM API认证失败，请检查配置")
                elif "connection" in error_msg.lower() or "connect" in error_msg.lower():
                    raise Exception(f"无法连接到LLM服务: {error_msg}")
                else:
                    raise Exception(f"LLM处理失败: {error_msg[:200]}")
        else:  # ollama
            try:
                # For Ollama, prepend system prompt to user prompt if provided
                full_prompt = prompt
                if system_prompt:
                    full_prompt = f"{system_prompt}\n\n{prompt}"
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.ollama_base_url}/api/generate",
                        json={
                            "model": self.ollama_model,
                            "prompt": full_prompt,
                            "stream": False
                        },
                        timeout=timeout
                    )
                    response.raise_for_status()
                    result = response.json()
                    return result.get("response", "").strip()
            except Exception as e:
                logger.error(f"Error generating with Ollama: {str(e)}")
                raise Exception("Failed to generate with Ollama")

    async def generate_summary(self, content: str, max_words: int = 200, language: str = "zh") -> str:
        """
        Generates a summary of the provided content using configured LLM.
        """
        prompt_template = self._get_prompt("summary", language)
        prompt = prompt_template.format(max_words=max_words, content=content)
        return await self._generate_with_provider(prompt, timeout=60.0)

    async def integrate_articles(self, contents: list[str], max_words: int = 500, focus: str = None, language: str = "zh") -> str:
        """
        Integrates multiple articles into a single coherent narrative.
        """
        combined_content = "\n\n--- ARTICLE SEPARATOR ---\n\n".join(contents)
        
        lang_config = PROMPTS.get(language, PROMPTS["zh"])
        focus_default = lang_config["focus_default"]
        focus_prefix = lang_config["focus_prefix"]
        
        focus_prompt = f"{focus_prefix}{focus}" if focus else focus_default
        
        prompt_template = self._get_prompt("integrate", language)
        prompt = prompt_template.format(max_words=max_words, focus_prompt=focus_prompt, combined_content=combined_content)
        return await self._generate_with_provider(prompt, timeout=120.0)

    async def answer_query(self, query: str, context_texts: list[str], language: str = "zh") -> str:
        """
        Answers a user query based on the provided context (RAG).
        """
        # Combine context
        context_block = "\n\n---\n\n".join(context_texts)
        
        prompt_template = self._get_prompt("answer", language)
        prompt = prompt_template.format(context_block=context_block, query=query)
        return await self._generate_with_provider(prompt, timeout=60.0)

    async def generate_trending_post(self, topic: str, web_context: list[dict], local_context: list[str], language: str = "zh") -> str:
        """
        Generates a trending response post combining web and local info.
        """
        web_text = "\n".join([f"- {r.get('title')}: {r.get('body')}" for r in web_context])
        local_text = "\n".join(local_context)
        
        prompt_template = self._get_prompt("trending", language)
        prompt = prompt_template.format(topic=topic, web_text=web_text, local_text=local_text)
        return await self._generate_with_provider(prompt, timeout=60.0)

    async def generate_video_script(self, content: str, language: str = "zh") -> str:
        """
        Generates a video script with visual cues based on content.
        """
        prompt_template = self._get_prompt("script", language)
        prompt = prompt_template.format(content=content)
        return await self._generate_with_provider(prompt, timeout=90.0)
    
    async def generate_completion(self, prompt: str, system_prompt: str = None, model: str = None, timeout: float = 60.0) -> str:
        """
        通用的文本生成方法，用于自定义prompt
        """
        return await self._generate_with_provider(prompt, timeout=timeout, model=model, system_prompt=system_prompt)
    
    async def fetch_available_models(self) -> list[dict]:
        """
        Fetch available models from the configured LLM provider.
        """
        if self.provider == "openai":
            try:
                # Check if API key is configured
                if not settings.OPENAI_API_KEY:
                    logger.warning("⚠️  API Key 未配置，返回默认模型列表")
                    raise Exception("API Key not configured")
                
                # Use a longer timeout for listing models
                logger.info("🔄 正在从 API 获取模型列表...")
                models = await self.openai_client.models.list(timeout=15.0)
                
                # 获取所有模型，不进行过滤
                model_list = []
                logger.info(f"📊 API 返回了 {len(models.data)} 个模型")
                
                for model in models.data:
                    model_list.append({
                        "id": model.id,
                        "name": model.id,
                        "provider": "openai"
                    })
                    logger.debug(f"   - {model.id}")
                
                # 按名称排序
                model_list = sorted(model_list, key=lambda x: x["id"])
                logger.info(f"✅ 成功获取并返回 {len(model_list)} 个模型")
                return model_list
                
            except Exception as e:
                logger.error(f"❌ 获取模型列表失败: {str(e)}")
                logger.info("📋 返回默认模型列表（18个）")
                # Return Comprehensive default models if API call fails
                return [
                    {"id": "gpt-4o", "name": "gpt-4o", "provider": "openai"},
                    {"id": "gpt-4o-2024-05-13", "name": "gpt-4o-2024-05-13", "provider": "openai"},
                    {"id": "gpt-4o-mini", "name": "gpt-4o-mini", "provider": "openai"},
                    {"id": "gpt-4o-mini-2024-07-18", "name": "gpt-4o-mini-2024-07-18", "provider": "openai"},
                    {"id": "gpt-4-turbo", "name": "gpt-4-turbo", "provider": "openai"},
                    {"id": "gpt-4-turbo-2024-04-09", "name": "gpt-4-turbo-2024-04-09", "provider": "openai"},
                    {"id": "gpt-4-turbo-preview", "name": "gpt-4-turbo-preview", "provider": "openai"},
                    {"id": "gpt-4-0125-preview", "name": "gpt-4-0125-preview", "provider": "openai"},
                    {"id": "gpt-4-1106-preview", "name": "gpt-4-1106-preview", "provider": "openai"},
                    {"id": "gpt-4", "name": "gpt-4", "provider": "openai"},
                    {"id": "gpt-4-0613", "name": "gpt-4-0613", "provider": "openai"},
                    {"id": "gpt-3.5-turbo", "name": "gpt-3.5-turbo", "provider": "openai"},
                    {"id": "gpt-3.5-turbo-0125", "name": "gpt-3.5-turbo-0125", "provider": "openai"},
                    {"id": "gpt-3.5-turbo-1106", "name": "gpt-3.5-turbo-1106", "provider": "openai"},
                    {"id": "o1-preview", "name": "o1-preview", "provider": "openai"},
                    {"id": "o1-preview-2024-09-12", "name": "o1-preview-2024-09-12", "provider": "openai"},
                    {"id": "o1-mini", "name": "o1-mini", "provider": "openai"},
                    {"id": "o1-mini-2024-09-12", "name": "o1-mini-2024-09-12", "provider": "openai"}
                ]
        else:  # ollama
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{self.ollama_base_url}/api/tags", timeout=5.0)
                    response.raise_for_status()
                    data = response.json()
                    models = data.get("models", [])
                    return [{"id": m["name"], "name": m["name"], "provider": "ollama"} for m in models]
            except Exception as e:
                logger.error(f"Error fetching Ollama models: {str(e)}")
                return []
    
    def update_config(self, provider: str = None, model: str = None, api_key: str = None):
        """
        Update LLM configuration at runtime.
        """
        if provider:
            self.provider = provider
            settings.LLM_PROVIDER = provider
        
        if model:
            self.model = model
            settings.LLM_MODEL = model
        
        if api_key and provider == "openai":
            settings.OPENAI_API_KEY = api_key
            self.openai_client = AsyncOpenAI(
                api_key=api_key,
                base_url=settings.OPENAI_API_BASE,
                timeout=300.0  # 5分钟超时
            )
        
        # Save to file
        self._save_config_to_file()
        
        logger.info(f"LLM config updated: provider={self.provider}, model={self.model}")
    
    def get_current_config(self) -> dict:
        """
        Get current LLM configuration.
        """
        return {
            "provider": self.provider,
            "model": self.model,
            "display_name": "CBIT CBIT-Elite",  # Display name for UI
            "api_key_set": bool(settings.OPENAI_API_KEY) if self.provider == "openai" else None
        }

llm_service = LLMService()
