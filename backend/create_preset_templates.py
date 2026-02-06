#!/usr/bin/env python3
"""
创建预设邮件模板（包含 VoxChina Logo）
"""
import sys
sys.path.append('/www/wwwroot/voxchina/backend')

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.email import EmailTemplate

# VoxChina Logo HTML
LOGO_HTML = '''<div style="text-align: center; margin-bottom: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px;">
  <img src="http://llmhi.com:8400/voxchinalogo1.jpg" alt="VoxChina Logo" style="width: 150px; height: auto; background: white; padding: 10px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
</div>'''

# 预设模板
PRESET_TEMPLATES = [
    {
        "name": "📰 每周文章推送",
        "subject": "VoxChina 本周新文章 ({{date_range}})",
        "content": f"""<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f4f4;">
{LOGO_HTML}
<div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
  <div style="padding: 40px 30px;">
    <h1 style="color: #2563eb; margin: 0 0 10px 0; font-size: 28px;">本周新文章</h1>
    <p style="color: #666; margin: 0 0 30px 0; font-size: 14px;">{{date_range}}</p>
    
    <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); padding: 25px; border-radius: 8px; border-left: 4px solid #2563eb; margin-bottom: 30px;">
      <h2 style="margin: 0 0 15px 0; color: #1e293b; font-size: 22px;">
        <a href="{{article_url}}" style="color: #2563eb; text-decoration: none;">{{article_title}}</a>
      </h2>
      <p style="margin: 0 0 12px 0; color: #64748b; font-size: 14px;">
        <strong>作者：</strong>
        <a href="{{author_bio_url}}" style="color: #2563eb; text-decoration: none;">{{author_name}}</a>
      </p>
      <p style="margin: 0 0 15px 0; color: #64748b; font-size: 14px;">
        <strong>发布日期：</strong> {{article_date}}
      </p>
      <p style="margin: 0; color: #475569; font-size: 15px; line-height: 1.6;">
        {{article_description}}
      </p>
    </div>
    
    <div style="text-align: center; margin: 35px 0;">
      <a href="{{article_url}}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 35px; text-decoration: none; border-radius: 25px; font-weight: 600; font-size: 15px; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);">
        阅读全文 →
      </a>
    </div>
    
    <p style="margin: 30px 0 0 0; color: #64748b; font-size: 14px; line-height: 1.6;">
      访问 <a href="https://www.voxchina.org" style="color: #2563eb; text-decoration: none; font-weight: 600;">www.voxchina.org</a> 查看更多精彩内容
    </p>
  </div>
  
  <div style="background-color: #f8fafc; padding: 25px 30px; border-top: 1px solid #e2e8f0;">
    <p style="margin: 0; font-size: 12px; color: #94a3b8; text-align: center; line-height: 1.6;">
      您收到此邮件是因为您订阅了 VoxChina 的更新推送<br>
      <a href="{{unsubscribe_url}}" style="color: #94a3b8; text-decoration: underline;">取消订阅</a> | 
      <a href="mailto:info@voxchina.org" style="color: #94a3b8; text-decoration: underline;">联系我们</a>
    </p>
  </div>
</div>
</body>
</html>"""
    },
    {
        "name": "📧 月度通讯",
        "subject": "VoxChina 月度通讯 - {{month_year}}",
        "content": f"""<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f4f4;">
{LOGO_HTML}
<div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
  <div style="padding: 40px 30px;">
    <div style="text-align: center; margin-bottom: 35px;">
      <h1 style="color: #2563eb; margin: 0 0 8px 0; font-size: 32px;">月度通讯</h1>
      <p style="color: #666; margin: 0; font-size: 16px; font-weight: 500;">{{month_year}}</p>
    </div>
    
    <p style="margin: 0 0 25px 0; color: #475569; font-size: 15px; line-height: 1.6;">
      亲爱的读者，
    </p>
    
    <p style="margin: 0 0 30px 0; color: #475569; font-size: 15px; line-height: 1.6;">
      欢迎阅读本月的 VoxChina 通讯！本月我们为您带来了多篇精彩文章和深度分析。
    </p>
    
    <h3 style="color: #1e293b; margin: 0 0 20px 0; font-size: 20px; border-bottom: 3px solid #2563eb; padding-bottom: 10px; display: inline-block;">
      📚 本月精选文章
    </h3>
    
    <div style="margin-bottom: 30px;">
      {{article_list_html}}
    </div>
    
    <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); padding: 25px; border-radius: 8px; margin: 30px 0;">
      <h3 style="margin: 0 0 15px 0; color: #92400e; font-size: 18px;">💡 本月数据洞察</h3>
      <p style="margin: 0; color: #78350f; font-size: 14px; line-height: 1.6;">
        {{monthly_insights}}
      </p>
    </div>
    
    <h3 style="color: #1e293b; margin: 35px 0 20px 0; font-size: 20px; border-bottom: 3px solid #2563eb; padding-bottom: 10px; display: inline-block;">
      🔜 下月预告
    </h3>
    
    <p style="margin: 0 0 30px 0; color: #475569; font-size: 15px; line-height: 1.6;">
      {{upcoming_content}}
    </p>
    
    <div style="background-color: #f0f9ff; padding: 25px; border-radius: 8px; text-align: center; margin: 35px 0;">
      <p style="margin: 0 0 15px 0; color: #1e293b; font-size: 16px; font-weight: 600;">
        📱 关注我们的社交媒体
      </p>
      <p style="margin: 0; color: #64748b; font-size: 14px;">
        获取每日更新和最新资讯
      </p>
    </div>
    
    <p style="margin: 30px 0 0 0; color: #475569; font-size: 15px; line-height: 1.6;">
      此致，<br>
      <strong style="color: #1e293b;">VoxChina 团队</strong>
    </p>
  </div>
  
  <div style="background-color: #f8fafc; padding: 25px 30px; border-top: 1px solid #e2e8f0;">
    <p style="margin: 0; font-size: 12px; color: #94a3b8; text-align: center; line-height: 1.6;">
      VoxChina | <a href="https://www.voxchina.org" style="color: #2563eb; text-decoration: none;">www.voxchina.org</a><br>
      <a href="{{unsubscribe_url}}" style="color: #94a3b8; text-decoration: underline;">取消订阅</a>
    </p>
  </div>
</div>
</body>
</html>"""
    },
    {
        "name": "👋 欢迎新订阅者",
        "subject": "欢迎加入 VoxChina！",
        "content": f"""<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f4f4;">
{LOGO_HTML}
<div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
  <div style="padding: 40px 30px;">
    <div style="text-align: center; margin-bottom: 35px;">
      <h1 style="color: #2563eb; margin: 0 0 15px 0; font-size: 36px;">欢迎加入！🎉</h1>
      <p style="color: #64748b; margin: 0; font-size: 16px;">感谢您订阅 VoxChina</p>
    </div>
    
    <p style="margin: 0 0 20px 0; color: #475569; font-size: 15px; line-height: 1.6;">
      {{subscriber_name}}，您好！
    </p>
    
    <p style="margin: 0 0 30px 0; color: #475569; font-size: 15px; line-height: 1.6;">
      感谢您订阅 <strong style="color: #2563eb;">VoxChina</strong>！我们很高兴您加入我们的读者社区，一起关注中国经济、政策和发展动态。
    </p>
    
    <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 30px; border-radius: 10px; margin: 30px 0;">
      <h3 style="margin: 0 0 20px 0; color: #0c4a6e; font-size: 20px; text-align: center;">
        📬 您将收到什么？
      </h3>
      <div style="margin-bottom: 15px;">
        <p style="margin: 0; color: #0c4a6e; font-size: 15px; line-height: 1.8;">
          📚 <strong>每周更新：</strong>最新文章和研究成果<br>
          🔍 <strong>深度分析：</strong>基于证据的经济洞察<br>
          🎯 <strong>专家评论：</strong>来自顶尖学者的分析<br>
          📊 <strong>数据研究：</strong>原创研究和数据可视化
        </p>
      </div>
    </div>
    
    <div style="background-color: #fef3c7; padding: 25px; border-radius: 8px; margin: 30px 0;">
      <h3 style="margin: 0 0 15px 0; color: #92400e; font-size: 18px;">💡 推荐阅读</h3>
      <p style="margin: 0 0 15px 0; color: #78350f; font-size: 14px; line-height: 1.6;">
        从我们的热门文章开始了解 VoxChina：
      </p>
      <ul style="margin: 0; padding-left: 20px; color: #78350f; font-size: 14px; line-height: 1.8;">
        <li>中国经济增长趋势分析</li>
        <li>政策改革与市场影响</li>
        <li>区域发展与城市化进程</li>
      </ul>
    </div>
    
    <div style="text-align: center; margin: 35px 0;">
      <a href="https://www.voxchina.org" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 16px 40px; text-decoration: none; border-radius: 25px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);">
        开始探索 VoxChina →
      </a>
    </div>
    
    <p style="margin: 30px 0 0 0; color: #475569; font-size: 14px; line-height: 1.6;">
      如果您有任何问题或反馈，请随时联系我们：
      <a href="mailto:info@voxchina.org" style="color: #2563eb; text-decoration: none; font-weight: 600;">info@voxchina.org</a>
    </p>
    
    <p style="margin: 25px 0 0 0; color: #475569; font-size: 15px; line-height: 1.6;">
      此致，<br>
      <strong style="color: #1e293b;">VoxChina 团队</strong>
    </p>
  </div>
  
  <div style="background-color: #f8fafc; padding: 25px 30px; border-top: 1px solid #e2e8f0;">
    <p style="margin: 0; font-size: 12px; color: #94a3b8; text-align: center; line-height: 1.6;">
      VoxChina | <a href="https://www.voxchina.org" style="color: #2563eb; text-decoration: none;">www.voxchina.org</a><br>
      <a href="{{preferences_url}}" style="color: #94a3b8; text-decoration: underline;">管理订阅偏好</a>
    </p>
  </div>
</div>
</body>
</html>"""
    },
    {
        "name": "🎯 活动邀请",
        "subject": "VoxChina 活动邀请：{{event_title}}",
        "content": f"""<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f4f4;">
{LOGO_HTML}
<div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
  <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
    <h1 style="margin: 0; color: white; font-size: 32px; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">
      {{event_title}}
    </h1>
    <p style="margin: 15px 0 0 0; color: rgba(255,255,255,0.9); font-size: 18px; font-weight: 500;">
      📅 {{event_date}}
    </p>
  </div>
  
  <div style="padding: 40px 30px;">
    <p style="margin: 0 0 25px 0; color: #475569; font-size: 15px; line-height: 1.6;">
      尊敬的 {{subscriber_name}}，
    </p>
    
    <p style="margin: 0 0 30px 0; color: #475569; font-size: 15px; line-height: 1.6;">
      {{event_description}}
    </p>
    
    <div style="background-color: #f8fafc; padding: 30px; border-radius: 10px; border: 2px solid #e2e8f0; margin: 30px 0;">
      <h3 style="margin: 0 0 20px 0; color: #2563eb; font-size: 20px; text-align: center;">
        📋 活动详情
      </h3>
      
      <div style="margin-bottom: 15px; padding: 12px; background-color: white; border-radius: 6px;">
        <p style="margin: 0; color: #64748b; font-size: 14px; font-weight: 600;">📅 日期</p>
        <p style="margin: 5px 0 0 0; color: #1e293b; font-size: 15px;">{{event_date}}</p>
      </div>
      
      <div style="margin-bottom: 15px; padding: 12px; background-color: white; border-radius: 6px;">
        <p style="margin: 0; color: #64748b; font-size: 14px; font-weight: 600;">🕐 时间</p>
        <p style="margin: 5px 0 0 0; color: #1e293b; font-size: 15px;">{{event_time}}</p>
      </div>
      
      <div style="margin-bottom: 15px; padding: 12px; background-color: white; border-radius: 6px;">
        <p style="margin: 0; color: #64748b; font-size: 14px; font-weight: 600;">📍 地点</p>
        <p style="margin: 5px 0 0 0; color: #1e293b; font-size: 15px;">{{event_location}}</p>
      </div>
      
      <div style="padding: 12px; background-color: white; border-radius: 6px;">
        <p style="margin: 0; color: #64748b; font-size: 14px; font-weight: 600;">🎤 演讲嘉宾</p>
        <p style="margin: 5px 0 0 0; color: #1e293b; font-size: 15px;">{{event_speakers}}</p>
      </div>
    </div>
    
    <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); padding: 20px; border-radius: 8px; margin: 30px 0; text-align: center;">
      <p style="margin: 0; color: #92400e; font-size: 14px; font-weight: 600;">
        ⏰ 名额有限，请尽快报名！
      </p>
    </div>
    
    <div style="text-align: center; margin: 35px 0;">
      <a href="{{registration_url}}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 16px 45px; text-decoration: none; border-radius: 25px; font-weight: 700; font-size: 17px; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5); text-transform: uppercase; letter-spacing: 0.5px;">
        立即报名 →
      </a>
    </div>
    
    <p style="margin: 30px 0 0 0; color: #475569; font-size: 15px; line-height: 1.6; text-align: center;">
      期待与您见面！
    </p>
    
    <p style="margin: 20px 0 0 0; color: #475569; font-size: 15px; line-height: 1.6; text-align: center;">
      <strong style="color: #1e293b;">VoxChina 团队</strong>
    </p>
  </div>
  
  <div style="background-color: #f8fafc; padding: 25px 30px; border-top: 1px solid #e2e8f0;">
    <p style="margin: 0; font-size: 12px; color: #94a3b8; text-align: center; line-height: 1.6;">
      VoxChina | <a href="https://www.voxchina.org" style="color: #2563eb; text-decoration: none;">www.voxchina.org</a><br>
      <a href="mailto:info@voxchina.org" style="color: #94a3b8; text-decoration: underline;">联系我们</a>
    </p>
  </div>
</div>
</body>
</html>"""
    },
    {
        "name": "📊 研究报告发布",
        "subject": "新研究报告：{{report_title}}",
        "content": f"""<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f4f4;">
{LOGO_HTML}
<div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
  <div style="padding: 40px 30px;">
    <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 25px; border-radius: 10px; border-left: 5px solid #2563eb; margin-bottom: 30px;">
      <p style="margin: 0 0 8px 0; color: #0369a1; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
        📊 最新研究
      </p>
      <h1 style="margin: 0; color: #0c4a6e; font-size: 28px; line-height: 1.3;">
        {{report_title}}
      </h1>
    </div>
    
    <p style="margin: 0 0 20px 0; color: #475569; font-size: 15px; line-height: 1.6;">
      亲爱的读者，
    </p>
    
    <p style="margin: 0 0 25px 0; color: #475569; font-size: 15px; line-height: 1.6;">
      我们很高兴地宣布，VoxChina 最新研究报告现已发布。本报告深入分析了 {{research_topic}}，为您提供基于数据的深度洞察。
    </p>
    
    <div style="background-color: #f8fafc; padding: 25px; border-radius: 8px; margin: 25px 0;">
      <h3 style="margin: 0 0 18px 0; color: #1e293b; font-size: 18px;">📌 报告要点</h3>
      <ul style="margin: 0; padding-left: 20px; color: #475569; font-size: 14px; line-height: 1.9;">
        <li><strong>研究主题：</strong>{{research_topic}}</li>
        <li><strong>数据来源：</strong>{{data_sources}}</li>
        <li><strong>研究方法：</strong>{{methodology}}</li>
        <li><strong>发布日期：</strong>{{report_date}}</li>
      </ul>
    </div>
    
    <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); padding: 25px; border-radius: 8px; margin: 30px 0;">
      <h3 style="margin: 0 0 15px 0; color: #92400e; font-size: 18px;">💡 核心发现</h3>
      <p style="margin: 0; color: #78350f; font-size: 15px; line-height: 1.7;">
        {{key_findings}}
      </p>
    </div>
    
    <div style="background-color: #f0fdf4; padding: 25px; border-radius: 8px; border-left: 4px solid #16a34a; margin: 30px 0;">
      <h3 style="margin: 0 0 15px 0; color: #166534; font-size: 18px;">🎯 政策建议</h3>
      <p style="margin: 0; color: #15803d; font-size: 14px; line-height: 1.7;">
        {{policy_recommendations}}
      </p>
    </div>
    
    <div style="text-align: center; margin: 35px 0;">
      <a href="{{report_url}}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 16px 40px; text-decoration: none; border-radius: 25px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);">
        下载完整报告 (PDF) →
      </a>
    </div>
    
    <p style="margin: 30px 0 0 0; color: #64748b; font-size: 14px; line-height: 1.6; text-align: center;">
      引用本报告：{{citation}}
    </p>
    
    <p style="margin: 25px 0 0 0; color: #475569; font-size: 15px; line-height: 1.6;">
      感谢您对 VoxChina 研究的关注！<br>
      <strong style="color: #1e293b;">VoxChina 研究团队</strong>
    </p>
  </div>
  
  <div style="background-color: #f8fafc; padding: 25px 30px; border-top: 1px solid #e2e8f0;">
    <p style="margin: 0; font-size: 12px; color: #94a3b8; text-align: center; line-height: 1.6;">
      VoxChina | <a href="https://www.voxchina.org" style="color: #2563eb; text-decoration: none;">www.voxchina.org</a><br>
      <a href="{{unsubscribe_url}}" style="color: #94a3b8; text-decoration: underline;">取消订阅</a>
    </p>
  </div>
</div>
</body>
</html>"""
    },
    {
        "name": "⚡ 重要新闻快讯",
        "subject": "【快讯】{{news_title}}",
        "content": f"""<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f4f4;">
{LOGO_HTML}
<div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
  <div style="background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); padding: 20px 30px;">
    <p style="margin: 0; color: white; font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px;">
      ⚡ 重要快讯
    </p>
  </div>
  
  <div style="padding: 40px 30px;">
    <div style="background-color: #fef2f2; border-left: 5px solid #dc2626; padding: 25px; border-radius: 8px; margin-bottom: 30px;">
      <h1 style="margin: 0 0 12px 0; color: #991b1b; font-size: 26px; line-height: 1.3;">
        {{news_title}}
      </h1>
      <p style="margin: 0; color: #b91c1c; font-size: 13px; font-weight: 600;">
        ⏰ {{news_time}}
      </p>
    </div>
    
    <p style="margin: 0 0 25px 0; color: #475569; font-size: 16px; line-height: 1.7; font-weight: 500;">
      {{news_summary}}
    </p>
    
    <div style="background-color: #f8fafc; padding: 25px; border-radius: 8px; margin: 25px 0;">
      <h3 style="margin: 0 0 18px 0; color: #1e293b; font-size: 18px;">📰 详细内容</h3>
      <p style="margin: 0 0 15px 0; color: #475569; font-size: 15px; line-height: 1.7;">
        {{news_content}}
      </p>
    </div>
    
    <div style="background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); padding: 20px; border-radius: 8px; margin: 25px 0;">
      <h3 style="margin: 0 0 12px 0; color: #1e40af; font-size: 16px;">🔍 市场影响分析</h3>
      <p style="margin: 0; color: #1e3a8a; font-size: 14px; line-height: 1.6;">
        {{market_impact}}
      </p>
    </div>
    
    <div style="background-color: #f0fdf4; padding: 20px; border-radius: 8px; border-left: 4px solid #16a34a; margin: 25px 0;">
      <h3 style="margin: 0 0 12px 0; color: #166534; font-size: 16px;">📊 关键数据</h3>
      <p style="margin: 0; color: #15803d; font-size: 14px; line-height: 1.6;">
        {{key_data}}
      </p>
    </div>
    
    <div style="text-align: center; margin: 35px 0;">
      <a href="{{news_url}}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 35px; text-decoration: none; border-radius: 25px; font-weight: 600; font-size: 15px; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);">
        阅读完整分析 →
      </a>
    </div>
    
    <p style="margin: 30px 0 0 0; color: #64748b; font-size: 13px; line-height: 1.6; font-style: italic; text-align: center;">
      本快讯由 VoxChina 编辑团队整理发布
    </p>
  </div>
  
  <div style="background-color: #f8fafc; padding: 25px 30px; border-top: 1px solid #e2e8f0;">
    <p style="margin: 0; font-size: 12px; color: #94a3b8; text-align: center; line-height: 1.6;">
      VoxChina 快讯 | <a href="https://www.voxchina.org" style="color: #2563eb; text-decoration: none;">www.voxchina.org</a><br>
      <a href="{{unsubscribe_url}}" style="color: #94a3b8; text-decoration: underline;">管理订阅</a>
    </p>
  </div>
</div>
</body>
</html>"""
    }
]

def create_preset_templates():
    db: Session = SessionLocal()
    try:
        # 删除所有现有模板
        print("🗑️  删除现有模板...")
        db.query(EmailTemplate).delete()
        db.commit()
        print("✅ 已删除所有现有模板\n")
        
        # 创建新的预设模板
        print("📝 创建新的预设模板...")
        for i, template_data in enumerate(PRESET_TEMPLATES, 1):
            template = EmailTemplate(**template_data)
            db.add(template)
            print(f"   {i}. ✅ {template_data['name']}")
        
        db.commit()
        
        print(f"\n🎉 成功创建 {len(PRESET_TEMPLATES)} 个预设模板！")
        print("\n所有模板都包含专业设计的 VoxChina Logo")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_preset_templates()
