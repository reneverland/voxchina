# Integrated Voiceover Feature (整合口播稿件策划功能)

## 功能概述

VoxChina 多文献整合口播稿件策划（Evidence-based Scriptwriter）是一个基于多篇文献自动生成符合VOXCHINA规范的短视频口播稿的功能。

## 核心特性

### 1. 硬性证据规则（R1-R5）
- **R1**: 只允许使用 Evidence Ledger / Visual Asset Ledger 中存在的事实与数字，禁止外推、常识补充、主观推断
- **R2**: 任何数字必须带单位与时间口径，禁止自行换算/推导
- **R3**: 每个自然段末尾必须加证据标注
- **R4**: 每条证据标注类型：研究发现/数据描述/作者观点/政策信息等
- **R5**: 图表必须来自文档，禁止虚构图号/表号/趋势解释

### 2. 图表精准提取与匹配（V1-V5）
- **V1**: 识别Word表格、文本中的图/表标记、图注/表题
- **V2**: 为无编号的图表创建内部编号（D{doc_id}-FIG-1 / D{doc_id}-TAB-1）
- **V3**: 提取图表的完整字段（asset_id, asset_type, caption, key_numbers, takeaway_claim等）
- **V4**: 图表匹配到正文段落必须满足数字一致、主题一致或机制一致
- **V5**: 支持两种图表呈现风格（独立行 / 正文内嵌）

### 3. 六步输出流程

#### Step 0: Style Profile（风格配置）
- 确定是否启用VOXCHINA片头
- 选择主结构（S1-S4）
- 确定图表呈现风格（A/B）
- 输出3-6条规则

#### Step A: Evidence Ledger（文字证据台账）
- 对每篇文档提取3-10条最小事实单元
- 每条finding包含：type, claim, numbers, linked_assets

#### Step A2: Visual Asset Ledger（图表证据台账）
- 扫描所有文档，提取全部可用图/表
- 为每个asset添加剪辑指令

#### Step B: Structure Selector（结构选择器）
- S1: 三维度/三主线
- S2: 时间线/阶段推进
- S3: 现状—机制—对策
- S4: 机制链条
- 输出3-6个一级小标题

#### Step C: Script Review（审阅版口播稿）
- 带证据标注【证据：...】
- 带图表提示【图表：asset_id】
- 包含完整的标题、片头、正文、结尾

#### Step D: Script Final（上屏版口播稿）
- 删除所有证据标注
- 保留图表提示
- 最终可直接录制的版本

## 技术架构

### 后端

#### 1. 数据模型 (`backend/app/models/schemas.py`)
- `IntegratedVoiceoverRequest`: 请求参数
- `IntegratedVoiceoverResponse`: 完整响应
- `IntegratedVoiceoverStatus`: 任务状态
- `EvidenceLedger`: 证据台账
- `VisualAssetLedger`: 图表台账
- `StyleProfile`: 风格配置

#### 2. 服务层 (`backend/app/services/integrated_voiceover_service.py`)
- `IntegratedVoiceoverService`: 核心服务类
- 文档解析与证据提取
- 图表识别与匹配
- LLM驱动的内容生成
- 异步任务处理

#### 3. API端点 (`backend/app/api/v1/endpoints/integrated_voiceover.py`)
- `POST /api/v1/integrated-voiceover/create`: 创建任务
- `GET /api/v1/integrated-voiceover/status/{task_id}`: 查询状态
- `GET /api/v1/integrated-voiceover/result/{task_id}`: 获取结果
- `GET /api/v1/integrated-voiceover/list`: 列出所有任务
- `DELETE /api/v1/integrated-voiceover/delete/{task_id}`: 删除任务

### 前端

#### 1. 页面组件 (`frontend/src/views/IntegratedVoiceoverPage.vue`)
- 文档上传界面（支持拖拽）
- 参数配置表单
- 实时进度显示
- 结果展示（6个Tab）

#### 2. 路由配置 (`frontend/src/router/index.ts`)
- 路径: `/integrated-voiceover`
- 需要认证

#### 3. 导航集成 (`frontend/src/views/MainPage.vue`)
- 添加"整合口播稿件"导航项
- 使用FileVideo图标
- 点击跳转到专用页面

## 使用方法

### 1. 准备文档
- 支持格式：.docx, .doc, .pdf
- 文档应包含：文字内容、表格、图表
- 建议：每个文档包含清晰的标题和结构

### 2. 配置参数
- **主题/问题**（必填）：一句话描述主题
- **主播机构**（可选）：如"VoxChina"
- **主播姓名**（可选）：如"张三"
- **包含VOXCHINA片头**：默认启用
- **结构偏好**：可选择S1-S4或自动选择

### 3. 上传文档
- 点击上传区域或拖拽文件
- 支持多文件上传
- 查看文件列表，可删除不需要的文件

### 4. 生成口播稿
- 点击"开始生成"按钮
- 系统自动进行6步处理
- 实时显示进度和当前步骤

### 5. 查看结果
- **风格配置**：查看自动推断的风格规则
- **证据台账**：浏览所有提取的证据
- **图表台账**：查看识别的图表及剪辑指令
- **结构设计**：查看选定的结构和小标题
- **审阅版**：带证据标注的完整稿件
- **上屏版**：最终可录制的稿件

### 6. 复制使用
- 点击"复制"按钮将内容复制到剪贴板
- 可直接用于录制或进一步编辑

## API使用示例

### 创建任务

```bash
curl -X POST "http://localhost:8300/api/v1/integrated-voiceover/create" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "topic_hint=中国数字经济发展现状与挑战" \
  -F "speaker_affiliation=VoxChina" \
  -F "speaker_name=张三" \
  -F "include_vox_intro=true" \
  -F "style_preference=S1" \
  -F "files=@document1.docx" \
  -F "files=@document2.pdf"
```

### 查询状态

```bash
curl -X GET "http://localhost:8300/api/v1/integrated-voiceover/status/{task_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 获取结果

```bash
curl -X GET "http://localhost:8300/api/v1/integrated-voiceover/result/{task_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 注意事项

1. **文档质量**：文档质量直接影响生成效果，建议使用结构清晰、数据完整的文档
2. **处理时间**：根据文档数量和长度，处理时间可能需要1-5分钟
3. **LLM配置**：确保LLM服务配置正确，建议使用GPT-4或更高版本
4. **图表提取**：PDF中的图表提取效果可能不如Word文档
5. **证据验证**：生成后建议人工审核证据标注的准确性

## 未来改进

- [ ] 支持更多文档格式（如Markdown、HTML）
- [ ] 增强图表OCR识别能力
- [ ] 支持视频脚本导出（含时间轴）
- [ ] 添加人工审核和编辑功能
- [ ] 支持多语言口播稿生成
- [ ] 集成TTS自动生成音频
- [ ] 支持批量任务处理

## 故障排查

### 任务失败
- 检查文档格式是否支持
- 查看后端日志获取详细错误信息
- 确认LLM服务是否正常

### 图表未识别
- 确保文档中图表有明确标注
- Word文档效果优于PDF
- 检查图表是否为嵌入式图片

### 证据不准确
- 调整LLM temperature参数
- 使用更高质量的文档
- 人工审核并修正

## 开发者信息

- **开发时间**: 2026-01-17
- **版本**: 1.0.0
- **依赖**:
  - FastAPI
  - python-docx
  - pypdf
  - OpenAI API
  - Vue 3
  - TypeScript

## 许可证

Copyright © 2026 VoxChina. All rights reserved.
