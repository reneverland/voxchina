from pydantic import BaseModel
from typing import Optional, List

class ArticleRequest(BaseModel):
    content: str
    title: Optional[str] = None
    voice_id: Optional[str] = None
    language: str = "zh"

class ArticleResponse(BaseModel):
    summary: str
    audio_url: str
    message: str

class ArticleListItem(BaseModel):
    id: str
    title: str
    summary: str
    # content: str # Omitted for list view to save bandwidth

class IntegrationRequest(BaseModel):
    article_ids: List[str]
    max_words: Optional[int] = 500
    focus: Optional[str] = None
    voice_id: Optional[str] = None
    language: str = "zh"

class IntegrationResponse(BaseModel):
    integrated_content: str
    audio_url: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 3
    language: str = "zh"

class SearchResultItem(BaseModel):
    id: str
    title: str
    summary: str
    score: float

class SearchResponse(BaseModel):
    answer: str
    sources: List[SearchResultItem]

class TrendingRequest(BaseModel):
    topic: str
    generate_script: bool = False
    language: str = "zh"

class TrendingResponse(BaseModel):
    post_content: str
    script_content: Optional[str] = None

class VoiceResponse(BaseModel):
    id: str
    name: str
    audio_url: str
    created_at: Optional[str] = None

# Integrated Voiceover Schemas
class IntegratedVoiceoverRequest(BaseModel):
    topic_hint: str
    speaker_affiliation: Optional[str] = None
    speaker_name: Optional[str] = None
    include_vox_intro: bool = True
    style_preference: Optional[str] = None  # S1/S2/S3/S4
    language: str = "zh"

class EvidenceFinding(BaseModel):
    finding_index: int
    type: str  # 研究发现/数据描述/作者观点/政策信息
    claim: str
    numbers: Optional[List[str]] = []
    linked_assets: Optional[List[str]] = []
    source_doc_id: str

class VisualAsset(BaseModel):
    asset_id: str
    asset_type: str  # FIG|TAB
    original_label: Optional[str] = None
    caption_or_title: Optional[str] = None
    location_anchor: Optional[str] = None
    key_numbers: List[str] = []
    takeaway_claim: Optional[str] = None
    linked_findings: List[int] = []
    editing_instruction: Optional[str] = None

class EvidenceLedger(BaseModel):
    doc_id: str
    title: str
    time_range: Optional[str] = None
    findings: List[EvidenceFinding]

class VisualAssetLedger(BaseModel):
    assets: List[VisualAsset]

class StyleProfile(BaseModel):
    enable_vox_intro: bool
    main_structure: str  # S1/S2/S3/S4
    figure_style: str  # A/B
    rules: List[str]

class ScriptSection(BaseModel):
    section_title: str
    paragraphs: List[str]
    assets_used: List[str] = []

class IntegratedVoiceoverResponse(BaseModel):
    task_id: str
    status: str  # processing/completed/failed
    style_profile: Optional[StyleProfile] = None
    evidence_ledger: Optional[List[EvidenceLedger]] = None
    visual_asset_ledger: Optional[VisualAssetLedger] = None
    structure: Optional[dict] = None
    script_review: Optional[str] = None
    script_final: Optional[str] = None
    created_at: str
    updated_at: str

class IntegratedVoiceoverStatus(BaseModel):
    task_id: str
    status: str
    progress: int  # 0-100
    current_step: str  # Step0/StepA/StepA2/StepB/StepC/StepD
    result: Optional[IntegratedVoiceoverResponse] = None
    error: Optional[str] = None  # 错误信息（仅在failed时）
