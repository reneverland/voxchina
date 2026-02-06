"""
VoxChina Tavily AI 搜索服务
提供实时热点搜索和新闻分析能力
"""
import httpx
from typing import List, Dict, Any, Optional
from loguru import logger


class TavilySearchService:
    """Tavily AI 搜索服务"""
    
    def __init__(self):
        # Tavily API配置
        self.api_key = "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"
        self.api_base_url = "https://api.tavily.com"
        self.search_endpoint = f"{self.api_base_url}/search"
    
    async def search(
        self, 
        query: str, 
        max_results: int = 5,
        search_depth: str = "basic",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        使用Tavily AI搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数量
            search_depth: 搜索深度 ("basic" 或 "advanced")
            include_domains: 包含的域名列表
            exclude_domains: 排除的域名列表
            
        Returns:
            搜索结果字典
        """
        try:
            logger.info(f"Tavily搜索: {query}")
            
            # 构建请求体
            payload = {
                "api_key": self.api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": search_depth,
                "include_answer": True,
                "include_raw_content": False,
            }
            
            # 添加域名过滤
            if include_domains:
                payload["include_domains"] = include_domains
            if exclude_domains:
                payload["exclude_domains"] = exclude_domains
            
            # 发送请求
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.search_endpoint,
                    json=payload,
                    headers={
                        "Content-Type": "application/json; charset=utf-8",
                        "Accept": "application/json; charset=utf-8"
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Tavily API错误: {response.status_code} - {response.text}")
                    return self._get_fallback_result(query)
                
                # 明确使用 UTF-8 解码
                response.encoding = 'utf-8'
                result = response.json()
                logger.info(f"Tavily返回 {len(result.get('results', []))} 条结果")
                return result
                
        except Exception as e:
            logger.error(f"Tavily搜索失败: {e}")
            return self._get_fallback_result(query)
    
    async def search_news(
        self, 
        query: str, 
        max_results: int = 5
    ) -> Dict[str, Any]:
        """
        搜索新闻（专注于新闻网站）
        
        Args:
            query: 搜索查询
            max_results: 最大结果数量
            
        Returns:
            搜索结果字典
        """
        # 定义中国主流新闻域名（包含财经类）
        news_domains = [
            "xinhuanet.com",
            "people.com.cn",
            "cctv.com",
            "chinanews.com",
            "huanqiu.com",
            "sina.com.cn",
            "163.com",
            "qq.com",
            "ifeng.com",
            "ce.cn",
            "caijing.com.cn",  # 财经网
            "caixin.com",      # 财新网
            "yicai.com",       # 第一财经
            "hexun.com",       # 和讯网
            "jrj.com.cn",      # 金融界
            "eastmoney.com",   # 东方财富网
            "wallstreetcn.com" # 华尔街见闻
        ]
        
        return await self.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",
            include_domains=news_domains
        )
    
    async def search_hot_topics(self, topic_hint: str = "中国") -> List[Dict[str, Any]]:
        """
        搜索当前热点话题（聚焦财经、政策、经济）
        
        Args:
            topic_hint: 话题提示词
            
        Returns:
            热点话题列表
        """
        try:
            # 构建热点搜索查询 - 聚焦财经、政策、经济领域
            queries = [
                f"{topic_hint} 财经 最新政策",
                f"{topic_hint} 经济 热点新闻",
                f"{topic_hint} 金融 政策动态",
                f"{topic_hint} 宏观经济 政策解读",
            ]
            
            hot_topics = []
            
            for query in queries:
                result = await self.search_news(query, max_results=5)
                
                if result and 'results' in result:
                    for item in result['results']:
                        hot_topics.append({
                            'title': item.get('title', ''),
                            'url': item.get('url', ''),
                            'content': item.get('content', ''),
                            'score': item.get('score', 0),
                            'published_date': item.get('published_date', ''),
                        })
            
            # 按评分排序
            hot_topics.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            # 去重
            seen_titles = set()
            unique_topics = []
            for topic in hot_topics:
                if topic['title'] not in seen_titles:
                    seen_titles.add(topic['title'])
                    unique_topics.append(topic)
            
            return unique_topics[:10]
            
        except Exception as e:
            logger.error(f"搜索热点话题失败: {e}")
            return []
    
    def _get_fallback_result(self, query: str) -> Dict[str, Any]:
        """返回降级结果（当API失败时）"""
        return {
            "query": query,
            "results": [],
            "answer": f"暂时无法获取关于'{query}'的搜索结果，请稍后再试。",
            "error": True
        }
    
    def format_search_results(self, results: Dict[str, Any]) -> str:
        """
        格式化搜索结果为文本
        
        Args:
            results: Tavily搜索结果
            
        Returns:
            格式化的文本字符串
        """
        if not results or 'results' not in results:
            return "无搜索结果"
        
        formatted = []
        
        # 添加AI答案（如果有）
        if results.get('answer'):
            formatted.append(f"## AI摘要\n{results['answer']}\n")
        
        # 添加搜索结果
        formatted.append("## 相关新闻\n")
        for i, item in enumerate(results['results'], 1):
            title = item.get('title', '无标题')
            content = item.get('content', '')[:200] + "..."
            url = item.get('url', '')
            
            formatted.append(f"{i}. **{title}**")
            formatted.append(f"   {content}")
            formatted.append(f"   来源: {url}\n")
        
        return "\n".join(formatted)


# 创建全局实例
tavily_search_service = TavilySearchService()
