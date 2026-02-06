"""
VoxChina 新闻抓取服务
支持从多个中国主流新闻网站抓取最新热点新闻
"""
import asyncio
import httpx
import feedparser
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger
from bs4 import BeautifulSoup


class NewsSource:
    """新闻源配置"""
    def __init__(self, name: str, url: str, source_type: str = "rss", parser_func: Optional[callable] = None):
        self.name = name
        self.url = url
        self.source_type = source_type  # rss 或 html
        self.parser_func = parser_func


class NewsCrawlerService:
    """新闻抓取服务"""
    
    def __init__(self):
        # 配置各大新闻源 - 更新为用户提供的完整列表
        self.news_sources = [
            # AI 相关
            NewsSource("AI-人工智能(IT之家)", "https://next.ithome.com/ai", "html", self._parse_ithome_ai),
            NewsSource("AI新闻资讯(AIBase)", "https://news.aibase.com/zh/news", "html", self._parse_aibase),
            # 热搜
            NewsSource("微博热搜榜", "https://weibo.com/ajax/side/hotSearch", "json"),
            # 财经新闻
            NewsSource("产业市场(中国经济网)", "http://www.ce.cn/cysc/", "html", self._parse_ce_cn),
            NewsSource("财经板块(新华网)", "https://www.news.cn/fortune/index.htm", "html", self._parse_xinhua_fortune),
            NewsSource("要闻-经济科技(人民网)", "http://finance.people.com.cn/", "html", self._parse_people_finance),
            NewsSource("经济频道(央视网)", "https://jingji.cctv.com/", "html", self._parse_cctv_jingji),
            NewsSource("财经频道(中国新闻网)", "https://www.chinanews.com.cn/finance/", "html", self._parse_chinanews_finance),
            NewsSource("财经(环球网)", "https://finance.huanqiu.com/", "html", self._parse_huanqiu_finance),
            NewsSource("腾讯财经", "https://news.qq.com/ch/finance/", "html", self._parse_qq_finance),
            NewsSource("凤凰网财经", "https://finance.ifeng.com/", "html", self._parse_ifeng_finance),
            NewsSource("新浪财经-国内", "https://finance.sina.com.cn/china/", "html", self._parse_sina_finance),
            NewsSource("企业出海-财智(国际在线)", "https://gr.cri.cn/", "html", self._parse_cri_gr),
            NewsSource("网易财经", "https://money.163.com/", "html", self._parse_163_money),
        ]
        
        # 缓存的新闻数据
        self.cached_news = []
        self.last_fetch_time = None
    
    def get_available_sources(self) -> List[Dict[str, str]]:
        """获取所有可用的新闻源列表"""
        return [
            {
                "name": source.name,
                "url": source.url,
                "type": source.source_type
            }
            for source in self.news_sources
        ]
    
    async def fetch_all_news(self, max_items_per_source: int = 10) -> List[Dict[str, Any]]:
        """
        从所有新闻源获取最新新闻
        
        Args:
            max_items_per_source: 每个源最多获取的新闻数量
            
        Returns:
            新闻列表
        """
        logger.info("开始抓取新闻...")
        all_news = []
        
        # 并发抓取所有新闻源
        tasks = [
            self._fetch_from_source(source, max_items_per_source)
            for source in self.news_sources
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"抓取 {self.news_sources[i].name} 失败: {result}")
            else:
                all_news.extend(result)
        
        # 按时间排序
        all_news.sort(key=lambda x: x.get('published_date', ''), reverse=True)
        
        # 更新缓存
        self.cached_news = all_news
        self.last_fetch_time = datetime.now()
        
        logger.info(f"成功抓取 {len(all_news)} 条新闻")
        return all_news
    
    async def _fetch_from_source(self, source: NewsSource, max_items: int) -> List[Dict[str, Any]]:
        """从单个新闻源获取新闻"""
        try:
            if source.source_type == "rss":
                return await self._fetch_rss(source, max_items)
            elif source.source_type == "html" and source.parser_func:
                return await source.parser_func(source, max_items)
            elif source.source_type == "json":
                return await self._fetch_json(source, max_items)
            else:
                logger.warning(f"不支持的新闻源类型: {source.source_type}")
                return []
        except Exception as e:
            logger.error(f"抓取 {source.name} 时出错: {e}")
            return []
    
    async def _fetch_rss(self, source: NewsSource, max_items: int) -> List[Dict[str, Any]]:
        """从RSS源获取新闻"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(source.url)
                # 确保正确的编码
                response.encoding = response.charset_encoding or 'utf-8'
                feed = feedparser.parse(response.text)
                
                news_items = []
                for entry in feed.entries[:max_items]:
                    news_items.append({
                        'title': entry.get('title', ''),
                        'description': entry.get('summary', entry.get('description', '')),
                        'link': entry.get('link', ''),
                        'published_date': entry.get('published', entry.get('updated', '')),
                        'source': source.name,
                        'source_type': 'rss'
                    })
                
                return news_items
        except Exception as e:
            logger.error(f"RSS抓取失败 ({source.name}): {e}")
            return []
    
    async def _fetch_json(self, source: NewsSource, max_items: int) -> List[Dict[str, Any]]:
        """从JSON API获取新闻（如央视网）"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(source.url)
                # 确保正确的编码
                response.encoding = response.charset_encoding or 'utf-8'
                # 央视网返回JSONP格式，需要处理
                text = response.text
                
                # 解析JSON数据
                try:
                    if text.startswith('news_') or '(' in text[:20]:
                        # JSONP格式
                        start_idx = text.index('(') + 1
                        end_idx = text.rindex(')')
                        json_text = text[start_idx:end_idx]
                        data = json.loads(json_text)
                    else:
                        data = json.loads(text)
                except (ValueError, json.JSONDecodeError) as je:
                    logger.error(f"JSON解析失败 ({source.name}): {je}")
                    return []
                
                news_items = []
                items = data.get('data', {}).get('list', []) if isinstance(data, dict) else []
                
                for item in items[:max_items]:
                    if not isinstance(item, dict):
                        continue
                    news_items.append({
                        'title': item.get('title', ''),
                        'description': item.get('brief', ''),
                        'link': item.get('url', ''),
                        'published_date': item.get('focus_date', ''),
                        'source': source.name,
                        'source_type': 'json'
                    })
                
                return news_items
        except Exception as e:
            logger.error(f"JSON抓取失败 ({source.name}): {e}")
            return []
    
    async def _parse_huanqiu(self, source: NewsSource, max_items: int) -> List[Dict[str, Any]]:
        """解析环球网HTML页面"""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(source.url)
                # 确保正确的编码
                response.encoding = response.charset_encoding or 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')
                
                news_items = []
                articles = soup.select('.list-items li')[:max_items]
                
                for article in articles:
                    title_tag = article.select_one('a')
                    if title_tag:
                        news_items.append({
                            'title': title_tag.get_text(strip=True),
                            'description': '',
                            'link': title_tag.get('href', ''),
                            'published_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'source': source.name,
                            'source_type': 'html'
                        })
                
                return news_items
        except Exception as e:
            logger.error(f"环球网解析失败: {e}")
            return []
    
    async def _parse_sina_finance(self, source: NewsSource, max_items: int) -> List[Dict[str, Any]]:
        """解析新浪财经HTML页面"""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(source.url)
                # 确保正确的编码
                response.encoding = response.charset_encoding or 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')
                
                news_items = []
                articles = soup.select('.feed-card-item')[:max_items]
                
                for article in articles:
                    title_tag = article.select_one('h2 a, .feed-card-title a')
                    desc_tag = article.select_one('.feed-card-txt, .feed-card-summary')
                    
                    if title_tag:
                        news_items.append({
                            'title': title_tag.get_text(strip=True),
                            'description': desc_tag.get_text(strip=True) if desc_tag else '',
                            'link': title_tag.get('href', ''),
                            'published_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'source': source.name,
                            'source_type': 'html'
                        })
                
                return news_items
        except Exception as e:
            logger.error(f"新浪财经解析失败: {e}")
            return []
    
    async def _parse_163(self, source: NewsSource, max_items: int) -> List[Dict[str, Any]]:
        """解析网易新闻HTML页面"""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(source.url)
                # 确保正确的编码
                response.encoding = response.charset_encoding or 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')
                
                news_items = []
                articles = soup.select('.news_title')[:max_items]
                
                for article in articles:
                    title_tag = article.select_one('a')
                    if title_tag:
                        news_items.append({
                            'title': title_tag.get_text(strip=True),
                            'description': '',
                            'link': title_tag.get('href', ''),
                            'published_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'source': source.name,
                            'source_type': 'html'
                        })
                
                return news_items
        except Exception as e:
            logger.error(f"网易新闻解析失败: {e}")
            return []
    
    async def _parse_ithome_ai(self, source: NewsSource, max_items: int) -> List[Dict[str, Any]]:
        """解析IT之家AI频道"""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(source.url)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')
                
                news_items = []
                articles = soup.select('.news-item, .item, .card')[:max_items]
                
                for article in articles:
                    title_tag = article.select_one('a.title, h2 a, .title a')
                    if title_tag:
                        link = title_tag.get('href', '')
                        if link and not link.startswith('http'):
                            link = 'https://next.ithome.com' + link
                        news_items.append({
                            'title': title_tag.get_text(strip=True),
                            'description': '',
                            'link': link,
                            'published_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'source': source.name,
                            'source_type': 'html'
                        })
                
                return news_items
        except Exception as e:
            logger.error(f"IT之家AI解析失败: {e}")
            return []
    
    async def _parse_aibase(self, source: NewsSource, max_items: int) -> List[Dict[str, Any]]:
        """解析AIBase新闻"""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(source.url)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')
                
                news_items = []
                articles = soup.select('.news-item, .article-item, .list-item')[:max_items]
                
                for article in articles:
                    title_tag = article.select_one('a, h3 a, .title a')
                    if title_tag:
                        link = title_tag.get('href', '')
                        if link and not link.startswith('http'):
                            link = 'https://news.aibase.com' + link
                        news_items.append({
                            'title': title_tag.get_text(strip=True),
                            'description': '',
                            'link': link,
                            'published_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'source': source.name,
                            'source_type': 'html'
                        })
                
                return news_items
        except Exception as e:
            logger.error(f"AIBase解析失败: {e}")
            return []
    
    async def _parse_ce_cn(self, source: NewsSource, max_items: int) -> List[Dict[str, Any]]:
        """解析中国经济网"""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(source.url)
                response.encoding = 'gb2312'
                soup = BeautifulSoup(response.text, 'html.parser')
                
                news_items = []
                articles = soup.select('.list li a, .news-list a')[:max_items]
                
                for article in articles:
                    title = article.get_text(strip=True)
                    if title and len(title) > 5:
                        link = article.get('href', '')
                        if link and not link.startswith('http'):
                            link = 'http://www.ce.cn' + link
                        news_items.append({
                            'title': title,
                            'description': '',
                            'link': link,
                            'published_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'source': source.name,
                            'source_type': 'html'
                        })
                
                return news_items
        except Exception as e:
            logger.error(f"中国经济网解析失败: {e}")
            return []
    
    async def _parse_xinhua_fortune(self, source: NewsSource, max_items: int) -> List[Dict[str, Any]]:
        """解析新华网财经"""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(source.url)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')
                
                news_items = []
                articles = soup.select('.domPC a, .news-list a, .list a')[:max_items]
                
                for article in articles:
                    title = article.get_text(strip=True)
                    if title and len(title) > 5:
                        link = article.get('href', '')
                        if link and not link.startswith('http'):
                            link = 'https://www.news.cn' + link
                        news_items.append({
                            'title': title,
                            'description': '',
                            'link': link,
                            'published_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'source': source.name,
                            'source_type': 'html'
                        })
                
                return news_items
        except Exception as e:
            logger.error(f"新华网财经解析失败: {e}")
            return []
    
    async def _parse_people_finance(self, source: NewsSource, max_items: int) -> List[Dict[str, Any]]:
        """解析人民网财经"""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(source.url)
                response.encoding = 'gb2312'
                soup = BeautifulSoup(response.text, 'html.parser')
                
                news_items = []
                articles = soup.select('.p2j_list a, .ej_list_box a')[:max_items]
                
                for article in articles:
                    title = article.get_text(strip=True)
                    if title and len(title) > 5:
                        link = article.get('href', '')
                        if link and not link.startswith('http'):
                            link = 'http://finance.people.com.cn' + link
                        news_items.append({
                            'title': title,
                            'description': '',
                            'link': link,
                            'published_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'source': source.name,
                            'source_type': 'html'
                        })
                
                return news_items
        except Exception as e:
            logger.error(f"人民网财经解析失败: {e}")
            return []
    
    async def _parse_cctv_jingji(self, source: NewsSource, max_items: int) -> List[Dict[str, Any]]:
        """解析央视网经济频道"""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(source.url)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')
                
                news_items = []
                articles = soup.select('.text a, .news_list a')[:max_items]
                
                for article in articles:
                    title = article.get_text(strip=True)
                    if title and len(title) > 5:
                        link = article.get('href', '')
                        if link and not link.startswith('http'):
                            link = 'https://jingji.cctv.com' + link
                        news_items.append({
                            'title': title,
                            'description': '',
                            'link': link,
                            'published_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'source': source.name,
                            'source_type': 'html'
                        })
                
                return news_items
        except Exception as e:
            logger.error(f"央视网经济解析失败: {e}")
            return []
    
    async def _parse_chinanews_finance(self, source: NewsSource, max_items: int) -> List[Dict[str, Any]]:
        """解析中国新闻网财经"""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(source.url)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')
                
                news_items = []
                articles = soup.select('.content_list a, .dd_bt a')[:max_items]
                
                for article in articles:
                    title = article.get_text(strip=True)
                    if title and len(title) > 5:
                        link = article.get('href', '')
                        if link and not link.startswith('http'):
                            link = 'https://www.chinanews.com.cn' + link
                        news_items.append({
                            'title': title,
                            'description': '',
                            'link': link,
                            'published_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'source': source.name,
                            'source_type': 'html'
                        })
                
                return news_items
        except Exception as e:
            logger.error(f"中国新闻网财经解析失败: {e}")
            return []
    
    async def _parse_huanqiu_finance(self, source: NewsSource, max_items: int) -> List[Dict[str, Any]]:
        """解析环球网财经"""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(source.url)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')
                
                news_items = []
                articles = soup.select('.list-items li a, .news-list a')[:max_items]
                
                for article in articles:
                    title = article.get_text(strip=True)
                    if title and len(title) > 5:
                        link = article.get('href', '')
                        if link and not link.startswith('http'):
                            link = 'https://finance.huanqiu.com' + link
                        news_items.append({
                            'title': title,
                            'description': '',
                            'link': link,
                            'published_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'source': source.name,
                            'source_type': 'html'
                        })
                
                return news_items
        except Exception as e:
            logger.error(f"环球网财经解析失败: {e}")
            return []
    
    async def _parse_qq_finance(self, source: NewsSource, max_items: int) -> List[Dict[str, Any]]:
        """解析腾讯财经"""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(source.url)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')
                
                news_items = []
                articles = soup.select('.list a, .news-item a')[:max_items]
                
                for article in articles:
                    title = article.get_text(strip=True)
                    if title and len(title) > 5:
                        link = article.get('href', '')
                        news_items.append({
                            'title': title,
                            'description': '',
                            'link': link,
                            'published_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'source': source.name,
                            'source_type': 'html'
                        })
                
                return news_items
        except Exception as e:
            logger.error(f"腾讯财经解析失败: {e}")
            return []
    
    async def _parse_ifeng_finance(self, source: NewsSource, max_items: int) -> List[Dict[str, Any]]:
        """解析凤凰网财经"""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(source.url)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')
                
                news_items = []
                articles = soup.select('.news-stream a, .index-news a')[:max_items]
                
                for article in articles:
                    title = article.get_text(strip=True)
                    if title and len(title) > 5:
                        link = article.get('href', '')
                        if link and not link.startswith('http'):
                            link = 'https://finance.ifeng.com' + link
                        news_items.append({
                            'title': title,
                            'description': '',
                            'link': link,
                            'published_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'source': source.name,
                            'source_type': 'html'
                        })
                
                return news_items
        except Exception as e:
            logger.error(f"凤凰网财经解析失败: {e}")
            return []
    
    async def _parse_cri_gr(self, source: NewsSource, max_items: int) -> List[Dict[str, Any]]:
        """解析国际在线企业出海"""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(source.url)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')
                
                news_items = []
                articles = soup.select('.list a, .news-list a')[:max_items]
                
                for article in articles:
                    title = article.get_text(strip=True)
                    if title and len(title) > 5:
                        link = article.get('href', '')
                        if link and not link.startswith('http'):
                            link = 'https://gr.cri.cn' + link
                        news_items.append({
                            'title': title,
                            'description': '',
                            'link': link,
                            'published_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'source': source.name,
                            'source_type': 'html'
                        })
                
                return news_items
        except Exception as e:
            logger.error(f"国际在线解析失败: {e}")
            return []
    
    async def _parse_163_money(self, source: NewsSource, max_items: int) -> List[Dict[str, Any]]:
        """解析网易财经"""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(source.url)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')
                
                news_items = []
                articles = soup.select('.news_title a, .data_row a')[:max_items]
                
                for article in articles:
                    title = article.get_text(strip=True)
                    if title and len(title) > 5:
                        link = article.get('href', '')
                        news_items.append({
                            'title': title,
                            'description': '',
                            'link': link,
                            'published_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'source': source.name,
                            'source_type': 'html'
                        })
                
                return news_items
        except Exception as e:
            logger.error(f"网易财经解析失败: {e}")
            return []
    
    def get_cached_news(self) -> List[Dict[str, Any]]:
        """获取缓存的新闻"""
        return self.cached_news
    
    def get_news_by_source(self, source_name: str) -> List[Dict[str, Any]]:
        """按新闻源筛选新闻"""
        return [news for news in self.cached_news if news.get('source') == source_name]


# 创建全局实例
news_crawler_service = NewsCrawlerService()
