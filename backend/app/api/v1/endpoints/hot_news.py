"""
VoxChina 热点新闻API端点
提供新闻抓取、话题搜索和推文生成功能
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from loguru import logger

from app.models.schemas import (
    HotNewsRequest,
    HotNewsResponse,
    NewsArticle,
    HotTopicSearchRequest,
    HotTopicSearchResponse,
    GeneratePostRequest,
    GeneratePostResponse,
    TrendingTopicsResponse,
    TrendingTopic,
    NewsSourceInfo,
    SaveNewsToKBRequest
)
from app.services.hot_news_service import hot_news_service
from app.services.knowledge_service import knowledge_service
from app.api.v1.endpoints.auth import get_current_user


router = APIRouter()


@router.post("/fetch", response_model=HotNewsResponse)
async def fetch_latest_news(
    request: HotNewsRequest,
    user: str = Depends(get_current_user)
):
    """
    获取最新新闻
    
    从配置的多个新闻源抓取最新热点新闻
    """
    try:
        logger.info(f"用户 {user} 请求获取最新新闻")
        
        news_list = await hot_news_service.fetch_latest_news(
            source_filter=request.source_filter,
            max_items=request.max_items or 50
        )
        
        # 转换为响应模型
        news_articles = [
            NewsArticle(
                title=news.get("title", ""),
                description=news.get("description", ""),
                link=news.get("link", ""),
                published_date=news.get("published_date", ""),
                source=news.get("source", ""),
                source_type=news.get("source_type", "")
            )
            for news in news_list
        ]
        
        return HotNewsResponse(
            news_list=news_articles,
            total_count=len(news_articles),
            last_update=news_list[0].get("published_date", "") if news_list else None
        )
        
    except Exception as e:
        logger.error(f"获取最新新闻失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取新闻失败: {str(e)}")


@router.post("/search", response_model=HotTopicSearchResponse)
async def search_hot_topic(
    request: HotTopicSearchRequest,
    user: str = Depends(get_current_user)
):
    """
    搜索特定热点话题
    
    整合新闻抓取、Tavily AI搜索和本地知识库
    """
    try:
        logger.info(f"用户 {user} 搜索话题: {request.topic}")
        
        search_results = await hot_news_service.search_hot_topic(
            topic=request.topic,
            use_tavily=request.use_tavily
        )
        
        # 转换新闻文章
        news_articles = [
            NewsArticle(
                title=news.get("title", ""),
                description=news.get("description", ""),
                link=news.get("link", ""),
                published_date=news.get("published_date", ""),
                source=news.get("source", ""),
                source_type=news.get("source_type", "")
            )
            for news in search_results.get("news_articles", [])
        ]
        
        # 提取Tavily摘要
        tavily_summary = None
        tavily_results = search_results.get("tavily_results")
        if tavily_results and tavily_results.get("answer"):
            tavily_summary = tavily_results["answer"]
        
        # 提取信息源
        sources = []
        for news in search_results.get("news_articles", [])[:5]:
            sources.append(NewsSourceInfo(
                title=news.get("title", ""),
                url=news.get("link", ""),
                source=news.get("source", "")
            ))
        
        return HotTopicSearchResponse(
            topic=request.topic,
            news_articles=news_articles,
            tavily_summary=tavily_summary,
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"搜索话题失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.post("/generate", response_model=GeneratePostResponse)
async def generate_post(
    request: GeneratePostRequest,
    user: str = Depends(get_current_user)
):
    """
    生成热点推文
    
    基于话题生成高质量推文，可选生成视频脚本
    """
    try:
        logger.info(f"用户 {user} 生成推文: {request.topic}")
        
        # 根据是否需要脚本选择不同的生成方法
        if request.generate_script:
            result = await hot_news_service.generate_post_with_script(
                topic=request.topic,
                style=request.style or "professional",
                language=request.language or "zh"
            )
        else:
            result = await hot_news_service.generate_post(
                topic=request.topic,
                style=request.style or "professional",
                length=request.length or "medium",
                language=request.language or "zh"
            )
        
        # 检查是否有错误
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        # 转换信息源
        sources = [
            NewsSourceInfo(
                title=src.get("title", ""),
                url=src.get("url", ""),
                source=src.get("source", "")
            )
            for src in result.get("sources", [])
        ]
        
        return GeneratePostResponse(
            topic=result.get("topic", request.topic),
            post_content=result.get("post_content", ""),
            script_content=result.get("script_content"),
            tags=result.get("tags", []),
            sources=sources,
            generated_at=result.get("generated_at", ""),
            style=result.get("style", request.style or "professional"),
            length=result.get("length", request.length or "medium")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成推文失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.get("/trending", response_model=TrendingTopicsResponse)
async def get_trending_topics(
    limit: int = 10,
    user: str = Depends(get_current_user)
):
    """
    获取当前热门话题
    
    使用Tavily AI获取实时热点话题
    """
    try:
        logger.info(f"用户 {user} 获取热门话题")
        
        trending_list = await hot_news_service.get_trending_topics(limit=limit)
        
        # 转换为响应模型
        topics = [
            TrendingTopic(
                title=topic.get("title", ""),
                url=topic.get("url", ""),
                description=topic.get("description", ""),
                score=topic.get("score", 0),
                published_date=topic.get("published_date", "")
            )
            for topic in trending_list
        ]
        
        return TrendingTopicsResponse(
            topics=topics,
            total_count=len(topics),
            last_update=trending_list[0].get("published_date", "") if trending_list else None
        )
        
    except Exception as e:
        logger.error(f"获取热门话题失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取热门话题失败: {str(e)}")


@router.get("/sources")
async def get_news_sources(user: str = Depends(get_current_user)):
    """
    获取可用的新闻源列表
    """
    try:
        from app.services.news_crawler_service import news_crawler_service
        
        sources = [
            {
                "name": source.name,
                "url": source.url,
                "type": source.source_type
            }
            for source in news_crawler_service.news_sources
        ]
        
        return {
            "sources": sources,
            "total_count": len(sources)
        }
        
    except Exception as e:
        logger.error(f"获取新闻源列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取新闻源失败: {str(e)}")


@router.post("/fetch-content")
async def fetch_news_content(
    data: dict,
    user: str = Depends(get_current_user)
):
    """
    获取新闻全文内容
    
    通过URL抓取新闻页面的正文内容
    """
    try:
        import httpx
        from bs4 import BeautifulSoup
        
        url = data.get("url", "")
        if not url:
            raise HTTPException(status_code=400, detail="缺少 url 参数")
        
        logger.info(f"用户 {user} 请求获取新闻全文: {url}")
        
        # 设置请求头模拟浏览器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            
            # 尝试检测编码
            content_type = response.headers.get('content-type', '')
            if 'gb2312' in content_type.lower() or 'gbk' in content_type.lower():
                response.encoding = 'gb2312'
            elif 'utf-8' in content_type.lower():
                response.encoding = 'utf-8'
            else:
                # 尝试自动检测
                response.encoding = response.charset_encoding or 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除脚本和样式
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
            # 尝试多种方式提取正文
            content = ""
            
            # 方法1: 查找常见的文章容器
            article_selectors = [
                'article', '.article', '#article',
                '.article-content', '.article-body', '.article_content',
                '.content', '#content', '.main-content',
                '.post-content', '.entry-content', '.text',
                '.news-content', '.news_content', '.newstext',
                '.TRS_Editor', '.article_txt', '.art_content'
            ]
            
            for selector in article_selectors:
                article = soup.select_one(selector)
                if article:
                    # 获取所有段落文本
                    paragraphs = article.find_all(['p', 'div'])
                    texts = []
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if text and len(text) > 20:  # 过滤太短的文本
                            texts.append(text)
                    if texts:
                        content = '\n\n'.join(texts)
                        break
            
            # 方法2: 如果上面没找到，尝试获取所有段落
            if not content:
                paragraphs = soup.find_all('p')
                texts = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 30:
                        texts.append(text)
                if texts:
                    content = '\n\n'.join(texts)
            
            # 清理内容
            if content:
                # 移除多余的空白
                import re
                content = re.sub(r'\n{3,}', '\n\n', content)
                content = re.sub(r' {2,}', ' ', content)
                content = content.strip()
            
            if content and len(content) > 100:
                logger.info(f"成功获取新闻全文，长度: {len(content)} 字符")
                return {"content": content, "success": True}
            else:
                logger.warning(f"无法提取有效内容: {url}")
                return {"content": None, "success": False, "message": "无法提取文章内容"}
                
    except httpx.TimeoutException:
        logger.error(f"获取新闻全文超时: {url}")
        raise HTTPException(status_code=504, detail="请求超时，请稍后重试")
    except Exception as e:
        logger.error(f"获取新闻全文失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取内容失败: {str(e)}")


@router.post("/save-to-kb")
async def save_news_to_knowledge_base(
    request: SaveNewsToKBRequest,
    user: str = Depends(get_current_user)
):
    """
    保存新闻到知识库
    
    将热点新闻或最新新闻保存到向量数据库，方便后续搜索和引用
    """
    try:
        logger.info(f"用户 {user} 保存新闻到知识库: {request.title}")
        
        # 准备元数据
        metadata = {
            "title": request.title,
            "url": request.url,
            "source": request.source or "热点新闻",
            "published_date": request.published_date or "",
            "type": "news",
            "saved_by": user
        }
        
        # 保存到知识库
        doc_id = await knowledge_service.add_document(
            content=request.content,
            metadata=metadata
        )
        
        logger.info(f"新闻已保存到知识库: {doc_id}")
        
        return {
            "success": True,
            "message": "新闻已成功保存到知识库",
            "doc_id": doc_id
        }
        
    except Exception as e:
        logger.error(f"保存新闻到知识库失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")
