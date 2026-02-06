"""
VoxChina 热点新闻推文生成服务
整合新闻抓取、AI搜索和本地知识库，快速生成高质量推文
"""
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from loguru import logger

from app.services.news_crawler_service import news_crawler_service
from app.services.tavily_search_service import tavily_search_service
from app.services.llm_service import llm_service
from app.services.vector_service import vector_service


class HotNewsService:
    """热点新闻推文生成服务"""
    
    def __init__(self):
        # 缓存的热点话题
        self.hot_topics_cache = []
        self.last_update_time = None
    
    async def fetch_latest_news(
        self, 
        source_filter: Optional[str] = None,
        max_items: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取最新新闻
        
        Args:
            source_filter: 新闻源过滤（可选）
            max_items: 最大新闻数量
            
        Returns:
            新闻列表
        """
        try:
            logger.info("正在获取最新新闻...")
            
            # 从各新闻源抓取
            news_list = await news_crawler_service.fetch_all_news(max_items_per_source=10)
            
            # 如果指定了新闻源过滤
            if source_filter:
                news_list = [n for n in news_list if n.get('source') == source_filter]
            
            # 限制返回数量
            news_list = news_list[:max_items]
            
            logger.info(f"成功获取 {len(news_list)} 条新闻")
            return news_list
            
        except Exception as e:
            logger.error(f"获取新闻失败: {e}")
            return []
    
    async def search_hot_topic(
        self, 
        topic: str,
        use_tavily: bool = True
    ) -> Dict[str, Any]:
        """
        搜索特定热点话题
        
        Args:
            topic: 话题关键词
            use_tavily: 是否使用Tavily AI搜索
            
        Returns:
            话题搜索结果
        """
        try:
            logger.info(f"搜索热点话题: {topic}")
            
            result = {
                "topic": topic,
                "news_articles": [],
                "tavily_results": None,
                "local_context": []
            }
            
            # 1. 从新闻抓取服务获取相关新闻
            all_news = news_crawler_service.get_cached_news()
            if not all_news:
                all_news = await news_crawler_service.fetch_all_news()
            
            # 简单关键词匹配
            result["news_articles"] = [
                news for news in all_news 
                if topic.lower() in news.get('title', '').lower() 
                or topic.lower() in news.get('description', '').lower()
            ][:10]
            
            # 2. 使用Tavily AI搜索
            if use_tavily:
                tavily_results = await tavily_search_service.search_news(topic, max_results=5)
                result["tavily_results"] = tavily_results
            
            # 3. 搜索本地知识库
            try:
                local_results = await vector_service.search_similar(topic, limit=3)
                if local_results:
                    result["local_context"] = [
                        {
                            "title": r.payload.get("title", "") if hasattr(r, 'payload') else "",
                            "content": (r.payload.get("content", "")[:500] if hasattr(r, 'payload') else ""),
                            "score": r.score if hasattr(r, 'score') else 0
                        }
                        for r in local_results
                    ]
            except Exception as e:
                logger.warning(f"本地知识库搜索失败: {e}")
            
            logger.info(f"话题搜索完成: {len(result['news_articles'])} 条新闻, "
                       f"{len(result.get('tavily_results', {}).get('results', []))} 条Tavily结果")
            
            return result
            
        except Exception as e:
            logger.error(f"搜索热点话题失败: {e}")
            return {
                "topic": topic,
                "news_articles": [],
                "tavily_results": None,
                "local_context": [],
                "error": str(e)
            }
    
    async def generate_post(
        self,
        topic: str,
        style: str = "professional",
        length: str = "medium",
        language: str = "zh"
    ) -> Dict[str, Any]:
        """
        基于热点话题生成推文
        
        Args:
            topic: 话题关键词
            style: 风格（professional/casual/academic）
            length: 长度（short/medium/long）
            language: 语言
            
        Returns:
            生成的推文及相关信息
        """
        try:
            logger.info(f"生成推文: {topic}, 风格: {style}, 长度: {length}")
            
            # 1. 搜索话题相关内容
            search_results = await self.search_hot_topic(topic, use_tavily=True)
            
            # 2. 整合上下文
            context = self._build_context(search_results)
            
            # 3. 构建提示词
            prompt = self._build_post_prompt(topic, context, style, length, language)
            
            # 4. 调用LLM生成推文
            post_content = await llm_service.generate_completion(prompt)
            
            # 5. 提取关键信息和标签
            tags = await self._extract_tags(topic, post_content)
            
            result = {
                "topic": topic,
                "post_content": post_content,
                "tags": tags,
                "sources": self._extract_sources(search_results),
                "generated_at": datetime.now().isoformat(),
                "style": style,
                "length": length
            }
            
            logger.info(f"推文生成成功，长度: {len(post_content)} 字符")
            return result
            
        except Exception as e:
            logger.error(f"生成推文失败: {e}")
            return {
                "topic": topic,
                "post_content": f"抱歉，生成推文时出现错误：{str(e)}",
                "tags": [],
                "sources": [],
                "error": str(e)
            }
    
    async def generate_post_with_script(
        self,
        topic: str,
        style: str = "professional",
        language: str = "zh"
    ) -> Dict[str, Any]:
        """
        生成推文并附带视频脚本
        
        Args:
            topic: 话题关键词
            style: 风格
            language: 语言
            
        Returns:
            推文、脚本及相关信息
        """
        try:
            # 1. 生成推文
            post_result = await self.generate_post(topic, style, "medium", language)
            
            # 2. 基于推文生成视频脚本
            script_prompt = self._build_script_prompt(
                topic, 
                post_result["post_content"],
                language
            )
            
            script_content = await llm_service.generate_completion(script_prompt)
            
            post_result["script_content"] = script_content
            
            logger.info(f"推文和脚本生成完成")
            return post_result
            
        except Exception as e:
            logger.error(f"生成推文和脚本失败: {e}")
            return {
                "topic": topic,
                "post_content": "",
                "script_content": "",
                "error": str(e)
            }
    
    def _build_context(self, search_results: Dict[str, Any]) -> str:
        """构建上下文字符串"""
        context_parts = []
        
        # 添加新闻文章
        if search_results.get("news_articles"):
            context_parts.append("## 相关新闻\n")
            for news in search_results["news_articles"][:5]:
                context_parts.append(f"- {news.get('title', '')}")
                if news.get('description'):
                    context_parts.append(f"  {news['description'][:200]}")
            context_parts.append("")
        
        # 添加Tavily搜索结果
        if search_results.get("tavily_results") and search_results["tavily_results"].get("results"):
            context_parts.append("## 实时搜索\n")
            for result in search_results["tavily_results"]["results"][:3]:
                context_parts.append(f"- {result.get('title', '')}")
                context_parts.append(f"  {result.get('content', '')[:200]}")
            context_parts.append("")
        
        # 添加本地知识库内容
        if search_results.get("local_context"):
            context_parts.append("## 知识库参考\n")
            for ctx in search_results["local_context"]:
                context_parts.append(f"- {ctx.get('title', '')}")
                context_parts.append(f"  {ctx.get('content', '')[:200]}")
        
        return "\n".join(context_parts)
    
    def _build_post_prompt(
        self, 
        topic: str, 
        context: str, 
        style: str, 
        length: str,
        language: str
    ) -> str:
        """构建推文生成提示词"""
        
        style_descriptions = {
            "professional": "专业、客观、权威",
            "casual": "轻松、有趣、易懂",
            "academic": "学术、严谨、深度"
        }
        
        length_guide = {
            "short": "100-200字",
            "medium": "300-500字",
            "long": "500-800字"
        }
        
        if language == "zh":
            prompt = f"""你是VoxChina的专业内容创作者。请基于以下背景信息，创作一篇关于"{topic}"的推文。

【背景信息】
{context}

【创作要求】
- 风格：{style_descriptions.get(style, '专业')}
- 长度：{length_guide.get(length, '300-500字')}
- 要求：
  1. 内容准确，基于提供的背景信息
  2. 观点鲜明，有独特见解
  3. 语言流畅，易于理解
  4. 包含关键事实和数据
  5. 结尾有思考或行动号召

请直接输出推文内容，不要包含标题或其他说明。"""
        else:
            prompt = f"""You are a professional content creator for VoxChina. Create a social media post about "{topic}" based on the following context.

【Context】
{context}

【Requirements】
- Style: {style}
- Length: {length}
- Requirements:
  1. Accurate content based on provided context
  2. Clear viewpoint with unique insights
  3. Fluent and easy to understand
  4. Include key facts and data
  5. End with reflection or call to action

Output the post content directly without titles or explanations."""
        
        return prompt
    
    def _build_script_prompt(self, topic: str, post_content: str, language: str) -> str:
        """构建视频脚本生成提示词"""
        
        if language == "zh":
            prompt = f"""基于以下推文内容，创作一个1-2分钟的短视频口播脚本。

【推文内容】
{post_content}

【脚本要求】
1. 时长：60-120秒
2. 结构：开场白 → 核心内容 → 总结升华
3. 语言：口语化、适合口播
4. 包含停顿提示和语气标注
5. 适合配图或视频素材

请输出完整的视频脚本："""
        else:
            prompt = f"""Based on the following post content, create a 1-2 minute video voiceover script.

【Post Content】
{post_content}

【Script Requirements】
1. Duration: 60-120 seconds
2. Structure: Opening → Core Content → Conclusion
3. Language: Conversational, suitable for voiceover
4. Include pause and tone indicators
5. Suitable for images or video footage

Output the complete video script:"""
        
        return prompt
    
    async def _extract_tags(self, topic: str, content: str) -> List[str]:
        """提取内容标签"""
        try:
            prompt = f"""从以下内容中提取3-5个关键标签（hashtag）。

内容：{content[:500]}

要求：
- 标签简短有力
- 与主题相关
- 适合社交媒体传播

请以列表形式输出，每个标签一行，格式如：#标签名"""
            
            tags_text = await llm_service.generate_completion(prompt)
            
            # 解析标签
            tags = []
            for line in tags_text.split('\n'):
                line = line.strip()
                if line.startswith('#'):
                    tags.append(line)
            
            return tags[:5]
        except Exception as e:
            logger.error(f"提取标签失败: {e}")
            return [f"#{topic}"]
    
    def _extract_sources(self, search_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """提取信息源"""
        sources = []
        
        # 从新闻文章提取
        for news in search_results.get("news_articles", [])[:3]:
            sources.append({
                "title": news.get("title", ""),
                "url": news.get("link", ""),
                "source": news.get("source", "")
            })
        
        # 从Tavily结果提取
        tavily_results = search_results.get("tavily_results", {})
        if tavily_results and tavily_results.get("results"):
            for result in tavily_results["results"][:2]:
                sources.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "source": "CBIT Real-Time Search"
                })
        
        return sources
    
    async def get_trending_topics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取当前热门话题
        
        Args:
            limit: 返回话题数量
            
        Returns:
            热门话题列表
        """
        try:
            logger.info("获取热门话题...")
            
            # 使用Tavily搜索热点
            hot_topics = await tavily_search_service.search_hot_topics()
            
            # 格式化返回结果
            trending = []
            for topic in hot_topics[:limit]:
                trending.append({
                    "title": topic.get("title", ""),
                    "url": topic.get("url", ""),
                    "description": topic.get("content", "")[:200],
                    "score": topic.get("score", 0),
                    "published_date": topic.get("published_date", "")
                })
            
            self.hot_topics_cache = trending
            self.last_update_time = datetime.now()
            
            logger.info(f"获取到 {len(trending)} 个热门话题")
            return trending
            
        except Exception as e:
            logger.error(f"获取热门话题失败: {e}")
            return []


# 创建全局实例
hot_news_service = HotNewsService()
