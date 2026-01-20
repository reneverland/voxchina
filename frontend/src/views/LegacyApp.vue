<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

import VoxWorkshop from '../components/VoxWorkshop.vue'

// Configuration
// 根据访问域名动态选择API地址（支持前后端分离部署）
const API_BASE_URL = (() => {
  const hostname = window.location.hostname;
  // 如果是通过 llmhi.com 或 localhost 访问（前后端同服务器），使用内部代理
  if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === 'llmhi.com') {
    return ''; // 使用Vite proxy，避免NAT问题
  }
  // 如果是从其他域名访问（前端部署在其他服务器），使用外部IP
  return 'http://113.106.62.42:8300';
})()

// -- Types --
interface Article {
  id: string
  title: string
  summary: string
}

interface SearchSource {
  id: string
  title: string
  summary: string
  score: number
}

interface Voice {
  id: string
  name: string
  audio_url: string
}

// -- i18n --
type Locale = 'zh' | 'en'
const currentLocale = ref<Locale>('zh')

const translations = {
  zh: {
    title: "VoxChina 智能平台",
    tabs: {
      workshop: "内容工坊",
      extract: "文章提取",
      script: "口播稿生成",
      search: "AI 搜索",
      trending: "热点响应",
      voices: "声音库"
    },
    headers: {
      workshop: "VoxChina 内容工坊",
      extract: "文章智能提取",
      script: "口播稿生成",
      search: "智能搜索",
      trending: "热点与脚本",
      voices: "声音克隆库"
    },
    descriptions: {
      workshop: "统一入口：自动识别单篇摘要与多篇口播，支持现代化创作体验。",
      extract: "上传学术文章（DOCX/PDF），提取高密集、零幻觉、可追溯的研究摘要。",
      script: "上传3-N篇文章（DOCX），AI归纳生成零幻觉、证据约束的专题口播稿（可下载DOCX）。",
      search: "基于您的知识库提出问题并获得答案。",
      trending: "生成针对热点话题的快速响应推文及视频脚本。",
      voices: "上传音频样本以克隆声音，并将其用于您的内容生成。"
    },
    script: {
      upload_title: "上传文档",
      upload_hint: "支持DOCX格式，最多10个文件",
      params_title: "参数设置",
      speaker_name: "主播姓名",
      speaker_affiliation: "主播机构",
      episode_topic: "期数主题（可选）",
      duration: "目标时长（秒）",
      generate_btn: "生成口播稿",
      generating: "生成中...",
      progress_title: "生成进度",
      result_title: "生成结果",
      download_docx: "下载DOCX",
      download_ledgers: "下载证据台账",
      download_audit: "下载审计报告",
      error_upload: "请至少上传1个文档。",
      stage_parsing: "文档解析",
      stage_chunking: "智能分块",
      stage_extracting: "证据提取",
      stage_outlining: "大纲规划",
      stage_writing: "成稿写作",
      stage_verifying: "事实核验",
      stage_exporting: "导出DOCX"
    },
    search: {
      empty_state: "询问任何关于您文章的问题",
      input_placeholder: "输入问题...",
      response_title: "AI 回答",
      sources_title: "引用来源",
      score: "相关度"
    },
    trending: {
      topic_label: "热点话题 / 新闻事件",
      topic_placeholder: "例如：最新发布的AI监管政策...",
      script_toggle: "同时生成视频脚本 (Markdown)",
      generate_btn: "生成内容",
      generating: "生成中...",
      post_title: "快速响应推文",
      script_title: "视频脚本"
    },
    voices: {
      clone_title: "克隆新声音",
      name_label: "声音名称",
      name_placeholder: "例如：我的克隆声音",
      file_label: "参考音频",
      file_hint: "上传清晰的语音录音（建议10-30秒）。",
      clone_btn: "克隆声音",
      cloning: "克隆中...",
      library_title: "我的声音库",
      empty_lib: "暂无自定义声音。上传一个开始吧！",
      delete_confirm: "确定要删除这个声音吗？",
      preview_btn: "试听",
      preview_text_placeholder: "输入试听文本...", 
      previewing: "生成中...",
      preview_error: "试听生成失败"
    },
    extract: {
      upload_title: "上传文章",
      file_label: "选择文件",
      file_hint: "支持 .docx, .doc, .pdf 格式",
      batch_hint: "可一次上传多个文件（最多10个）",
      extract_btn: "开始提取",
      extracting: "提取中...",
      batch_extract_btn: "批量提取",
      result_title: "提取结果",
      summary_zh_title: "中文摘要",
      summary_en_title: "英文摘要",
      fact_table_title: "结构化事实表",
      audit_title: "审计报告",
      coverage: "覆盖率",
      validation: "校验结果",
      expand: "展开",
      collapse: "收起",
      authors: "作者/机构",
      research_question: "研究问题",
      data_sample: "数据与样本",
      method: "方法",
      key_findings: "核心发现",
      mechanism: "机制解释",
      implications: "政策含义",
      limits: "局限性",
      evidence: "证据引用",
      no_files: "未选择文件",
      history_title: "历史提取",
      view_detail: "查看详情",
      no_history: "暂无历史提取记录"
    },
    auth: {
      welcome: "欢迎回来",
      subtitle: "请登录以访问 VoxChina 智能平台",
      username: "账号",
      password: "密码",
      login_btn: "安全登录",
      logging_in: "验证中...",
      logout: "退出登录",
      error_login: "账号或密码错误，请重试"
    },
    footer: {
      branding: "2026 CBIT & VoxChina 合作研发",
      cbit_link: "CBIT 官网"
    }
  },
  en: {
    title: "VoxChina AI Platform",
    tabs: {
      extract: "Extract",
      script: "Script",
      search: "Search",
      trending: "Trending",
      voices: "Voice Lib"
    },
    headers: {
      extract: "Intelligent Article Extract",
      script: "Script Generation",
      search: "Intelligent Search",
      trending: "Trending & Scripts",
      voices: "Voice Cloning Library"
    },
    descriptions: {
      extract: "Upload academic articles (DOCX/PDF) to extract high-density, zero-hallucination, traceable research summaries.",
      script: "Upload 3-N articles (DOCX), AI generates zero-hallucination, evidence-constrained broadcast scripts (downloadable DOCX).",
      search: "Ask questions and get answers based on your knowledge base.",
      trending: "Generate rapid response posts and video scripts for trending topics.",
      voices: "Upload audio samples to clone voices and use them in your content."
    },
    script: {
      upload_title: "Upload Documents",
      upload_hint: "Supports DOCX format, max 10 files",
      params_title: "Parameters",
      speaker_name: "Speaker Name",
      speaker_affiliation: "Speaker Affiliation",
      episode_topic: "Episode Topic (Optional)",
      duration: "Target Duration (seconds)",
      generate_btn: "Generate Script",
      generating: "Generating...",
      progress_title: "Progress",
      result_title: "Result",
      download_docx: "Download DOCX",
      download_ledgers: "Download Evidence Ledgers",
      download_audit: "Download Audit Report",
      error_upload: "Please upload at least 1 document.",
      stage_parsing: "Parsing",
      stage_chunking: "Chunking",
      stage_extracting: "Extracting",
      stage_outlining: "Outlining",
      stage_writing: "Writing",
      stage_verifying: "Verifying",
      stage_exporting: "Exporting"
    },
    search: {
      empty_state: "Ask anything about your articles",
      input_placeholder: "Ask a question...",
      response_title: "AI Response",
      sources_title: "Sources Used",
      score: "Score"
    },
    trending: {
      topic_label: "Trending Topic / News Event",
      topic_placeholder: "e.g. New AI Regulation Policy released...",
      script_toggle: "Also generate Video Script (Markdown)",
      generate_btn: "Generate Content",
      generating: "Generating...",
      post_title: "Rapid Response Post",
      script_title: "Video Script"
    },
    voices: {
      clone_title: "Clone a New Voice",
      name_label: "Voice Name",
      name_placeholder: "e.g. My Clone Voice",
      file_label: "Reference Audio",
      file_hint: "Upload a clear voice recording (10-30s recommended).",
      clone_btn: "Clone Voice",
      cloning: "Cloning...",
      library_title: "My Voice Library",
      empty_lib: "No custom voices yet. Upload one to get started!",
      delete_confirm: "Are you sure you want to delete this voice?",
      preview_btn: "Audition",
      preview_text_placeholder: "Preview text...",
      previewing: "Generating...",
      preview_error: "Preview failed"
    },
    extract: {
      upload_title: "Upload Articles",
      file_label: "Select Files",
      file_hint: "Support .docx, .doc, .pdf formats",
      batch_hint: "Upload multiple files at once (max 10)",
      extract_btn: "Start Extract",
      extracting: "Extracting...",
      batch_extract_btn: "Batch Extract",
      result_title: "Extract Results",
      summary_zh_title: "Chinese Summary",
      summary_en_title: "English Summary",
      fact_table_title: "Structured Fact Table",
      audit_title: "Audit Report",
      coverage: "Coverage",
      validation: "Validation",
      expand: "Expand",
      collapse: "Collapse",
      authors: "Authors/Institutions",
      research_question: "Research Question",
      data_sample: "Data & Sample",
      method: "Method",
      key_findings: "Key Findings",
      mechanism: "Mechanism",
      implications: "Implications",
      limits: "Limitations",
      evidence: "Evidence",
      no_files: "No files selected",
      history_title: "Extract History",
      view_detail: "View Detail",
      no_history: "No extract history"
    },
    auth: {
      welcome: "Welcome Back",
      subtitle: "Sign in to access VoxChina AI Platform",
      username: "Username",
      password: "Password",
      login_btn: "Secure Login",
      logging_in: "Verifying...",
      logout: "Logout",
      error_login: "Invalid username or password"
    },
    footer: {
      branding: "Co-developed by CBIT & VoxChina 2026",
      cbit_link: "CBIT Official"
    }
  }
}

const t = computed(() => translations[currentLocale.value])

// 过滤后的模型列表
const filteredModels = computed(() => {
  if (!modelSearchQuery.value) {
    return availableModels.value
  }
  const query = modelSearchQuery.value.toLowerCase()
  return availableModels.value.filter(model => 
    model.id.toLowerCase().includes(query) || 
    model.name.toLowerCase().includes(query)
  )
})

const toggleLocale = () => {
  currentLocale.value = currentLocale.value === 'zh' ? 'en' : 'zh'
}

// -- State --
const isAuthenticated = ref(false) // Auth state
const loginUsername = ref('')
const loginPassword = ref('')
const loginLoading = ref(false)
const loginError = ref('')
const token = ref('')
const userRole = ref('user') // 'superadmin' or 'user'
const userDisplayName = ref('')
const currentUsername = ref('')

const activeTab = ref<'workshop' | 'extract' | 'script' | 'search' | 'trending' | 'voices'>('workshop')

// LLM Config State
const showLLMConfig = ref(false)
const llmConfig = ref({
  provider: 'openai',
  model: 'gpt-4o-mini',
  display_name: 'CBIT CBIT-Elite',
  api_key_set: false
})
const availableModels = ref<Array<{id: string, name: string, provider: string}>>([])
const selectedModel = ref('')
const llmConfigLoading = ref(false)
const llmConfigError = ref('')
const modelSearchQuery = ref('')

// Shared State
const error = ref('')
const selectedVoiceId = ref<string>('')

// Multi Article State
const loading = ref(false)
const articles = ref<Article[]>([])
// Script Generation State
const scriptFiles = ref<File[]>([])
const scriptSpeakerName = ref('VoxChina主播')
const scriptSpeakerAffiliation = ref('VoxChina团队')
const scriptEpisodeTopic = ref('')
const scriptDuration = ref(150)
const scriptLoading = ref(false)
const scriptTaskId = ref('')
const scriptStatus = ref<any>(null)
const scriptResult = ref<any>(null)

// Search State
const searchQuery = ref('')
const searchLoading = ref(false)
const searchAnswer = ref('')
const searchSources = ref<SearchSource[]>([])

// Trending State
const trendingTopic = ref('')
const trendingGenerateVideoScript = ref(true)
const trendingLoading = ref(false)
const trendingPost = ref('')
const trendingScript = ref('')

// Voice Library State
const voices = ref<Voice[]>([])
const uploadVoiceName = ref('')
const uploadVoiceFile = ref<File | null>(null)
const voiceUploading = ref(false)
const uploadError = ref('')
const previewLoading = ref<string | null>(null) // track voice id being previewed
const previewAudioUrl = ref<Record<string, string>>({}) // map voice id to audio url
const voicePreviewTexts = ref<Record<string, string>>({}) // map voice id to custom text

// Extract State
const extractFiles = ref<File[]>([])
const extractLoading = ref(false)
const extractError = ref('')
const extractResult = ref<any>(null)
const batchExtractResults = ref<any[]>([])
const extractHistory = ref<any[]>([])
const showFactTable = ref(false)
const showAuditReport = ref(false)
// 提取进度状态
const extractProgress = ref(0)
const extractStage = ref('')
const extractStages = [
  { name: '文档获取与预处理', progress: 10 },
  { name: '结构化解析与噪音过滤', progress: 20 },
  { name: '智能分块与覆盖率保障', progress: 30 },
  { name: 'CBIT-LLM 语义分析', progress: 50 },
  { name: '深度理解与事实提取', progress: 65 },
  { name: '证据一致性校验', progress: 80 },
  { name: '幻觉过滤与可信度评估', progress: 90 },
  { name: '摘要生成与风格对齐', progress: 95 },
  { name: '准备输送结果', progress: 98 },
  { name: '质量审计与最终验证', progress: 100 }
]

// 音频播放状态
const playingAudio = ref<string | null>(null) // 'zh' | 'en' | null
const audioUrls = ref<{zh: string, en: string}>({ zh: '', en: '' })
const generatingAudio = ref<{zh: boolean, en: boolean}>({ zh: false, en: false })

// -- Helper: Fetch with Auth --
const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  const headers = new Headers(options.headers)
  if (token.value) {
    headers.append('Authorization', `Bearer ${token.value}`)
  }
  
  const response = await fetch(url, { ...options, headers })
  
  if (response.status === 401) {
    logout()
    throw new Error("Unauthorized")
  }
  
  return response
}

// -- Actions --

const login = async () => {
  if (!loginUsername.value || !loginPassword.value) return
  
  loginLoading.value = true
  loginError.value = ''
  
  try {
    const formData = new FormData()
    formData.append('username', loginUsername.value)
    formData.append('password', loginPassword.value)
    
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) throw new Error("Login failed")
    
    const data = await response.json()
    token.value = data.access_token
    userRole.value = data.role || 'user'
    currentUsername.value = data.username || loginUsername.value
    userDisplayName.value = data.display_name || loginUsername.value
    isAuthenticated.value = true
    localStorage.setItem('vox_token', token.value)
    localStorage.setItem('vox_role', userRole.value)
    localStorage.setItem('vox_username', currentUsername.value)
    localStorage.setItem('vox_display_name', userDisplayName.value)
    
    // Initial fetch
    fetchArticles()
    fetchVoices()
    fetchExtractHistory()
    
  } catch (e) {
    loginError.value = t.value.auth.error_login
  } finally {
    loginLoading.value = false
  }
}

const logout = () => {
  token.value = ''
  isAuthenticated.value = false
  userRole.value = 'user'
  currentUsername.value = ''
  userDisplayName.value = ''
  localStorage.removeItem('vox_token')
  localStorage.removeItem('vox_role')
  localStorage.removeItem('vox_username')
  localStorage.removeItem('vox_display_name')
  loginUsername.value = ''
  loginPassword.value = ''
}

const fetchArticles = async () => {
  try {
    // Public endpoint, but we can use auth if needed later
    const response = await fetch(`${API_BASE_URL}/api/v1/articles/?limit=20`)
    if (response.ok) {
      articles.value = await response.json()
    }
  } catch (e) {
    console.error("Failed to fetch articles", e)
  }
}

// Script Generation Functions
const handleScriptFilesUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    scriptFiles.value = Array.from(target.files).filter(file => 
      file.name.toLowerCase().endsWith('.docx') || 
      file.name.toLowerCase().endsWith('.doc')
    )
  }
}

const removeScriptFile = (index: number) => {
  scriptFiles.value.splice(index, 1)
}

const generateScript = async () => {
  if (scriptFiles.value.length < 1) {
    error.value = t.value.script.error_upload
    return
  }

  scriptLoading.value = true
  error.value = ''
  scriptTaskId.value = ''
  scriptStatus.value = null
  scriptResult.value = null

  try {
    const formData = new FormData()
    scriptFiles.value.forEach(file => {
      formData.append('files', file)
    })
    formData.append('speaker_name', scriptSpeakerName.value)
    formData.append('speaker_affiliation', scriptSpeakerAffiliation.value)
    if (scriptEpisodeTopic.value) {
      formData.append('episode_topic', scriptEpisodeTopic.value)
    }
    formData.append('duration_target_sec', scriptDuration.value.toString())
    formData.append('language', currentLocale.value)

    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/script/generate`, {
      method: 'POST',
      body: formData
    })

    if (!response.ok) throw new Error("Script generation failed")

    const data = await response.json()
    scriptTaskId.value = data.task_id
    pollScriptStatus()

  } catch (e: any) {
    error.value = e.message
    scriptLoading.value = false
  }
}

const pollScriptStatus = async () => {
  if (!scriptTaskId.value) return

  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/script/tasks/${scriptTaskId.value}`)
    if (!response.ok) throw new Error("Failed to fetch task status")

    const data = await response.json()
    scriptStatus.value = data

    if (data.status === 'completed') {
      scriptResult.value = data.result
      scriptLoading.value = false
    } else if (data.status === 'failed') {
      error.value = data.error || 'Generation failed'
      scriptLoading.value = false
    } else {
      setTimeout(pollScriptStatus, 2000)
    }
  } catch (e: any) {
    error.value = e.message
    scriptLoading.value = false
  }
}

const downloadScriptDocx = () => {
  if (scriptResult.value && scriptResult.value.download_url) {
    window.open(`${API_BASE_URL}${scriptResult.value.download_url}`, '_blank')
  }
}

const downloadScriptLedgers = async () => {
  if (!scriptTaskId.value) return
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/script/tasks/${scriptTaskId.value}/ledgers`)
    const data = await response.json()
    const blob = new Blob([JSON.stringify(data.evidence_ledgers, null, 2)], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `evidence_ledgers_${scriptTaskId.value.slice(0, 8)}.json`
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (e: any) {
    error.value = e.message
  }
}

const downloadScriptAudit = async () => {
  if (!scriptTaskId.value) return
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/script/tasks/${scriptTaskId.value}/ledgers`)
    const data = await response.json()
    const blob = new Blob([JSON.stringify(data.audit_report, null, 2)], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `audit_report_${scriptTaskId.value.slice(0, 8)}.json`
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (e: any) {
    error.value = e.message
  }
}

const performSearch = async () => {
  if (!searchQuery.value) return
  
  searchLoading.value = true
  searchAnswer.value = ''
  searchSources.value = []
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/search/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: searchQuery.value,
        limit: 3,
        language: currentLocale.value
      })
    })
    
    if (!response.ok) throw new Error("Search failed")
    
    const data = await response.json()
    searchAnswer.value = data.answer
    searchSources.value = data.sources
    
  } catch (e: any) {
    console.error(e)
  } finally {
    searchLoading.value = false
  }
}

const generateTrending = async () => {
  if (!trendingTopic.value) return
  
  trendingLoading.value = true
  trendingPost.value = ''
  trendingScript.value = ''
  error.value = ''
  
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/trending/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: trendingTopic.value,
        generate_script: trendingGenerateVideoScript.value,
        language: currentLocale.value
      })
    })
    
    if (!response.ok) throw new Error("Generation failed")
    
    const data = await response.json()
    trendingPost.value = data.post_content
    trendingScript.value = data.script_content
    
  } catch (e: any) {
    error.value = e.message
  } finally {
    trendingLoading.value = false
  }
}

// Voice Actions
const fetchVoices = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/voices/`)
    if (response.ok) {
      voices.value = await response.json()
    }
  } catch (e) {
    console.error("Failed to fetch voices", e)
  }
}

const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    uploadVoiceFile.value = target.files[0]
  }
}

const uploadVoice = async () => {
  if (!uploadVoiceName.value || !uploadVoiceFile.value) return
  
  voiceUploading.value = true
  uploadError.value = ''
  
  const formData = new FormData()
  formData.append('name', uploadVoiceName.value)
  formData.append('file', uploadVoiceFile.value)
  
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/voices/upload`, {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) throw new Error("Upload failed")
    
    // Reset form
    uploadVoiceName.value = ''
    uploadVoiceFile.value = null
    const fileInput = document.getElementById('voice-upload') as HTMLInputElement
    if (fileInput) fileInput.value = ''
    
    fetchVoices()
    
  } catch (e: any) {
    uploadError.value = e.message
  } finally {
    voiceUploading.value = false
  }
}

const deleteVoice = async (id: string) => {
  if (!confirm(t.value.voices.delete_confirm)) return
  try {
    await fetchWithAuth(`${API_BASE_URL}/api/v1/voices/${id}`, { method: 'DELETE' })
    fetchVoices()
  } catch (e) {
    console.error(e)
  }
}

const previewVoice = async (id: string) => {
  previewLoading.value = id
  
  const text = voicePreviewTexts.value[id] || null
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/voices/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        voice_id: id,
        text: text,
        language: currentLocale.value
      })
    })
    
    if (!response.ok) throw new Error("Preview failed")
    
    const data = await response.json()
    previewAudioUrl.value = { ...previewAudioUrl.value, [id]: `${API_BASE_URL}${data.audio_url}` }
    
  } catch (e) {
    console.error(e)
    alert(t.value.voices.preview_error)
  } finally {
    previewLoading.value = null
  }
}

// Extract Actions
const handleExtractFiles = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    extractFiles.value = Array.from(target.files)
  }
}

const triggerFileInput = () => {
  const fileInput = document.getElementById('extract-file-input') as HTMLInputElement
  if (fileInput) {
    fileInput.click()
  }
}

const extractArticle = async () => {
  if (extractFiles.value.length === 0) {
    extractError.value = t.value.extract.no_files
    return
  }
  
  extractLoading.value = true
  extractError.value = ''
  extractResult.value = null
  batchExtractResults.value = []
  extractProgress.value = 0
  extractStage.value = ''
  
  // 智能进度更新 - 匹配实际5分钟处理时间
  let updateCount = 0
  const progressInterval = setInterval(() => {
    updateCount++
    const elapsedSeconds = updateCount * 5 // 每5秒更新一次
    
    // 基于实际5分钟（300秒）的进度策略
    let targetProgress = 0
    if (elapsedSeconds <= 30) {
      // 0-30秒：10% (文档获取与预处理)
      targetProgress = Math.floor((elapsedSeconds / 30) * 10)
    } else if (elapsedSeconds <= 60) {
      // 30-60秒：10-20% (结构化解析)
      targetProgress = 10 + Math.floor(((elapsedSeconds - 30) / 30) * 10)
    } else if (elapsedSeconds <= 90) {
      // 60-90秒：20-30% (智能分块)
      targetProgress = 20 + Math.floor(((elapsedSeconds - 60) / 30) * 10)
    } else if (elapsedSeconds <= 150) {
      // 90-150秒：30-50% (CBIT-LLM语义分析 - 最耗时)
      targetProgress = 30 + Math.floor(((elapsedSeconds - 90) / 60) * 20)
    } else if (elapsedSeconds <= 210) {
      // 150-210秒：50-70% (深度理解与事实提取)
      targetProgress = 50 + Math.floor(((elapsedSeconds - 150) / 60) * 20)
    } else if (elapsedSeconds <= 240) {
      // 210-240秒：70-80% (证据一致性校验)
      targetProgress = 70 + Math.floor(((elapsedSeconds - 210) / 30) * 10)
    } else if (elapsedSeconds <= 270) {
      // 240-270秒：80-90% (幻觉过滤)
      targetProgress = 80 + Math.floor(((elapsedSeconds - 240) / 30) * 10)
    } else if (elapsedSeconds <= 300) {
      // 270-300秒：90-95% (摘要生成)
      targetProgress = 90 + Math.floor(((elapsedSeconds - 270) / 30) * 5)
    } else if (elapsedSeconds <= 310) {
      // 300-310秒：95-98% (准备输送结果)
      targetProgress = 95 + Math.floor(((elapsedSeconds - 300) / 10) * 3)
    } else {
      // 310秒后：保持在98%等待完成
      targetProgress = 98
    }
    
    if (extractProgress.value < targetProgress && extractProgress.value < 98) {
      extractProgress.value = targetProgress
      
      // 更新阶段文字
      const currentStage = extractStages.find(s => s.progress >= extractProgress.value)
      if (currentStage) {
        extractStage.value = currentStage.name
      }
    }
  }, 5000) // 每5秒更新一次
  
  try {
    if (extractFiles.value.length === 1) {
      // 单文件提取
      const formData = new FormData()
      formData.append('file', extractFiles.value[0])
      
      extractStage.value = extractStages[0].name
      extractProgress.value = extractStages[0].progress
      
      const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/article-extract/extract`, {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) throw new Error('Extract failed')
      
      const data = await response.json()
      
      // 完成所有阶段
      extractProgress.value = 100
      extractStage.value = extractStages[extractStages.length - 1].name
      
      // 延迟一下显示完成状态
      await new Promise(resolve => setTimeout(resolve, 500))
      
      extractResult.value = data
      
      // 刷新历史
      fetchExtractHistory()
      
    } else {
      // 批量提取
      const formData = new FormData()
      extractFiles.value.forEach(file => {
        formData.append('files', file)
      })
      
      extractStage.value = extractStages[0].name
      extractProgress.value = extractStages[0].progress
      
      const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/article-extract/extract/batch`, {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) throw new Error('Batch extract failed')
      
      const data = await response.json()
      
      extractProgress.value = 100
      extractStage.value = extractStages[extractStages.length - 1].name
      await new Promise(resolve => setTimeout(resolve, 500))
      
      batchExtractResults.value = data.results || []
      
      // 刷新历史
      fetchExtractHistory()
    }
    
  } catch (e: any) {
    extractError.value = e.message
  } finally {
    clearInterval(progressInterval)
    extractLoading.value = false
  }
}

const fetchExtractHistory = async () => {
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/article-extract/extracts?limit=10`)
    if (response.ok) {
      extractHistory.value = await response.json()
    }
  } catch (e) {
    console.error("Failed to fetch extract history", e)
  }
}

const viewExtractDetail = async (extractId: string) => {
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/article-extract/extracts/${extractId}`)
    if (response.ok) {
      const data = await response.json()
      extractResult.value = data
      // 滚动到结果区域
      setTimeout(() => {
        document.getElementById('extract-result')?.scrollIntoView({ behavior: 'smooth' })
      }, 100)
    }
  } catch (e) {
    console.error("Failed to fetch extract detail", e)
  }
}

const generateAudioForSummary = async (text: string, lang: 'zh' | 'en') => {
  if (!text) return
  
  // 如果没有选择声音，提示用户
  if (!selectedVoiceId.value && voices.value.length > 0) {
    const confirmed = confirm('未选择声音。\n\n如果继续，将使用默认声音（可能音质不佳）。\n建议先在"Voices"标签页上传参考音频进行声音克隆。\n\n是否继续使用默认声音？')
    if (!confirmed) return
  }
  
  generatingAudio.value[lang] = true
  
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/voices/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        voice_id: selectedVoiceId.value || '', // 空字符串表示使用基础声音
        text: text,
        language: lang
      })
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || "Audio generation failed")
    }
    
    const data = await response.json()
    audioUrls.value[lang] = `${API_BASE_URL}${data.audio_url}`
    
  } catch (e: any) {
    console.error('Audio generation error:', e)
    const errorMsg = e.message || '未知错误'
    alert(`音频生成失败：${errorMsg}\n\n提示：\n1. 请先在"Voices"标签页上传参考音频\n2. 确保后端TTS服务正常运行\n3. 查看浏览器控制台了解详细错误`)
  } finally {
    generatingAudio.value[lang] = false
  }
}

// LLM Config Actions
const fetchLLMConfig = async () => {
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/llm/config`)
    if (response.ok) {
      const data = await response.json()
      llmConfig.value = data
      selectedModel.value = data.model
    }
  } catch (e) {
    console.error("Failed to fetch LLM config", e)
  }
}

const fetchAvailableModels = async () => {
  llmConfigLoading.value = true
  llmConfigError.value = ''
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/llm/models`)
    if (response.ok) {
      const data = await response.json()
      availableModels.value = data.models || []
      llmConfig.value.display_name = data.display_name
      console.log(`✅ 成功获取 ${availableModels.value.length} 个模型`)
    } else {
      llmConfigError.value = `获取模型失败: ${response.status}`
    }
  } catch (e: any) {
    console.error("Failed to fetch models", e)
    llmConfigError.value = `获取模型失败: ${e.message}`
  } finally {
    llmConfigLoading.value = false
  }
}

const saveLLMConfig = async () => {
  if (!selectedModel.value) {
    llmConfigError.value = '请先选择一个模型'
    return
  }
  
  llmConfigLoading.value = true
  llmConfigError.value = ''
  console.log('🔄 保存配置，选择的模型:', selectedModel.value)
  
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/llm/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: selectedModel.value
      })
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`保存失败 (${response.status}): ${errorText}`)
    }
    
    const data = await response.json()
    llmConfig.value = data.config
    console.log('✅ 配置保存成功:', data.config)
    showLLMConfig.value = false
    
    // 显示成功提示
    alert(currentLocale.value === 'zh' ? '配置保存成功！' : 'Configuration saved successfully!')
    
  } catch (e: any) {
    console.error('❌ 保存配置失败:', e)
    llmConfigError.value = e.message || '保存配置失败'
  } finally {
    llmConfigLoading.value = false
  }
}

const openLLMConfig = async () => {
  showLLMConfig.value = true
  
  // 只有超级管理员才获取配置和模型列表
  if (userRole.value === 'superadmin') {
    await fetchLLMConfig()
    await fetchAvailableModels()
  }
  // 普通用户不需要额外获取信息，直接显示预设文案即可
}

onMounted(() => {
  const storedToken = localStorage.getItem('vox_token')
  if (storedToken) {
    token.value = storedToken
    userRole.value = localStorage.getItem('vox_role') || 'user'
    currentUsername.value = localStorage.getItem('vox_username') || ''
    userDisplayName.value = localStorage.getItem('vox_display_name') || ''
    isAuthenticated.value = true
    fetchArticles()
    fetchVoices()
    fetchExtractHistory()
  }
})
</script>

<template>
  <div class="min-h-screen font-sans selection:bg-indigo-100">
    
    <!-- Modern Login Screen -->
    <div v-if="!isAuthenticated" class="min-h-screen flex items-center justify-center relative overflow-hidden bg-slate-900">
      <!-- Animated Gradient Background -->
      <div class="absolute inset-0 bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 opacity-20 animate-gradient"></div>
      
      <!-- Decorative Circles -->
      <div class="absolute top-[-10%] left-[-10%] w-96 h-96 bg-indigo-500/30 rounded-full blur-3xl"></div>
      <div class="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-pink-500/30 rounded-full blur-3xl"></div>

      <!-- Login Card -->
      <div class="relative w-full max-w-md p-8 mx-4 bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/20">
        <div class="text-center mb-10">
          <div class="w-20 h-20 mx-auto mb-6 overflow-hidden rounded-2xl shadow-lg shadow-indigo-500/30">
            <img src="/voxchinalogo2.jpg" alt="VoxChina Logo" class="w-full h-full object-cover" />
          </div>
          <h2 class="text-3xl font-bold text-white mb-2">{{ t.auth.welcome }}</h2>
          <p class="text-slate-300">{{ t.auth.subtitle }}</p>
        </div>
        
        <div class="space-y-6">
          <div class="group">
            <label class="block text-sm font-medium text-slate-300 mb-2">{{ t.auth.username }}</label>
            <div class="relative">
              <input 
                v-model="loginUsername" 
                type="text" 
                class="w-full bg-slate-800/50 border border-slate-600/50 rounded-xl px-5 py-3.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all pl-11"
                placeholder="admin"
              />
              <svg class="w-5 h-5 text-slate-400 absolute left-3.5 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
            </div>
          </div>
          
          <div class="group">
            <label class="block text-sm font-medium text-slate-300 mb-2">{{ t.auth.password }}</label>
            <div class="relative">
              <input 
                v-model="loginPassword" 
                type="password" 
                class="w-full bg-slate-800/50 border border-slate-600/50 rounded-xl px-5 py-3.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all pl-11"
                @keyup.enter="login"
                placeholder="••••••••"
              />
              <svg class="w-5 h-5 text-slate-400 absolute left-3.5 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
            </div>
          </div>
          
          <div v-if="loginError" class="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm text-center font-medium">
            {{ loginError }}
          </div>
          
          <button 
            @click="login" 
            :disabled="loginLoading" 
            class="w-full py-3.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-bold text-lg hover:from-indigo-500 hover:to-purple-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-indigo-500/30 transform hover:scale-[1.02] active:scale-[0.98]"
          >
            <span v-if="loginLoading" class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              {{ t.auth.logging_in }}
            </span>
            <span v-else>{{ t.auth.login_btn }}</span>
          </button>
          
          <div class="flex justify-center mt-6">
             <button @click="toggleLocale" class="text-sm text-slate-400 hover:text-white transition-colors flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"></path></svg>
                {{ currentLocale === 'zh' ? 'Switch to English' : '切换到中文' }}
             </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main App -->
    <div v-else class="bg-slate-50">
      <!-- Navbar -->
      <nav class="bg-white/80 backdrop-blur-md sticky top-0 z-50 border-b border-slate-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex justify-between h-16 items-center">
            <div class="flex items-center gap-2">
              <div class="w-10 h-10 overflow-hidden rounded-lg shadow-sm">
                <img src="/voxchinalogo2.jpg" alt="VoxChina Logo" class="w-full h-full object-cover" />
              </div>
              <span class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-violet-600">
                {{ t.title }}
              </span>
            </div>
            
            <div class="flex items-center gap-4">
              <!-- Tabs -->
              <div class="flex gap-1 sm:gap-2 overflow-x-auto">
                <button 
                  v-for="tab in ['extract', 'script', 'search', 'trending', 'voices']"
                  :key="tab"
                  @click="activeTab = tab as any"
                  :class="[activeTab === tab ? 'text-indigo-600 bg-indigo-50' : 'text-slate-600 hover:text-slate-900']"
                  class="px-3 py-2 rounded-md text-sm font-medium transition-colors capitalize whitespace-nowrap"
                >
                  {{ t.tabs[tab as keyof typeof t.tabs] }}
                </button>
              </div>
              
              <!-- Locale Toggle -->
              <button 
                @click="toggleLocale" 
                class="hidden sm:block ml-2 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-bold hover:bg-slate-200 transition-colors border border-slate-200"
              >
                {{ currentLocale === 'zh' ? 'En' : '中' }}
              </button>
              
              <!-- User Info -->
              <div class="ml-2 flex items-center gap-2 px-3 py-1 bg-slate-100 rounded-lg border border-slate-200">
                <div class="w-6 h-6 bg-indigo-600 rounded-full flex items-center justify-center">
                  <span class="text-white text-xs font-bold">{{ currentUsername.charAt(0).toUpperCase() }}</span>
                </div>
                <span class="text-xs font-medium text-slate-700">{{ userDisplayName || currentUsername }}</span>
                <span v-if="userRole === 'superadmin'" class="text-[10px] bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded font-bold">{{ currentLocale === 'zh' ? '超管' : 'ADMIN' }}</span>
              </div>
              
              <!-- LLM Config -->
              <button 
                @click="openLLMConfig" 
                class="ml-2 text-slate-500 hover:text-indigo-600 flex items-center gap-1 text-sm font-medium"
                :title="currentLocale === 'zh' ? 'LLM 配置' : 'LLM Config'"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
              </button>
              
              <!-- Logout -->
              <button @click="logout" class="ml-2 text-slate-500 hover:text-red-600 flex items-center gap-1 text-sm font-medium">
                <span>{{ t.auth.logout }}</span>
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
              </button>
            </div>
          </div>
        </div>
      </nav>

      <!-- LLM Config Modal -->
      <div v-if="showLLMConfig" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" @click.self="showLLMConfig = false">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl mx-4 overflow-hidden" @click.stop>
          <!-- Header -->
          <div class="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
              </div>
              <h2 class="text-xl font-bold text-white">{{ currentLocale === 'zh' ? 'LLM 配置' : 'LLM Configuration' }}</h2>
            </div>
            <button @click="showLLMConfig = false" class="text-white/80 hover:text-white transition-colors">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
          </div>

          <!-- Content -->
          <div class="p-6 space-y-6">
            <!-- Provider Display -->
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-2">
                {{ currentLocale === 'zh' ? 'LLM 提供商' : 'LLM Provider' }}
              </label>
              <div class="px-4 py-3 bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-xl">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
                    <span class="text-white font-bold text-sm">C</span>
                  </div>
                  <div>
                    <div class="font-bold text-slate-900">{{ llmConfig.display_name || 'CBIT CBIT-Elite' }}</div>
                    <div class="text-xs text-slate-500">{{ currentLocale === 'zh' ? '由 CBIT 提供的高性能 AI 服务' : 'High-performance AI service by CBIT' }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Model Selection - Only for superadmin -->
            <div v-if="userRole === 'superadmin'">
              <label class="block text-sm font-semibold text-slate-700 mb-2">
                {{ currentLocale === 'zh' ? '选择模型' : 'Select Model' }}
                <span class="text-xs font-normal text-slate-500 ml-2">({{ availableModels.length }} {{ currentLocale === 'zh' ? '个可用模型' : 'models available' }})</span>
              </label>
              
              <!-- 搜索框 -->
              <input 
                v-model="modelSearchQuery"
                type="text"
                :placeholder="currentLocale === 'zh' ? '搜索模型... (如: gpt-4o, gpt-3.5)' : 'Search models... (e.g. gpt-4o, gpt-3.5)'"
                class="w-full rounded-xl border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-indigo-500 focus:bg-white transition-all duration-200 mb-2"
              />
              
              <!-- 模型下拉框 -->
              <select 
                v-model="selectedModel" 
                class="w-full rounded-xl border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 focus:border-indigo-500 focus:ring-indigo-500 focus:bg-white transition-all duration-200 max-h-60"
                :disabled="llmConfigLoading"
                size="8"
              >
                <option value="" disabled>{{ currentLocale === 'zh' ? '选择一个模型...' : 'Choose a model...' }}</option>
                <optgroup v-if="filteredModels.filter(m => m.id.startsWith('gpt-4')).length > 0" label="GPT-4 系列">
                  <option v-for="model in filteredModels.filter(m => m.id.startsWith('gpt-4'))" :key="model.id" :value="model.id">
                    {{ model.name }}
                  </option>
                </optgroup>
                <optgroup v-if="filteredModels.filter(m => m.id.startsWith('gpt-3')).length > 0" label="GPT-3.5 系列">
                  <option v-for="model in filteredModels.filter(m => m.id.startsWith('gpt-3'))" :key="model.id" :value="model.id">
                    {{ model.name }}
                  </option>
                </optgroup>
                <optgroup v-if="filteredModels.filter(m => m.id.startsWith('gpt-5')).length > 0" label="GPT-5 系列">
                  <option v-for="model in filteredModels.filter(m => m.id.startsWith('gpt-5'))" :key="model.id" :value="model.id">
                    {{ model.name }}
                  </option>
                </optgroup>
                <optgroup v-if="filteredModels.filter(m => m.id.startsWith('o1')).length > 0" label="O1 系列">
                  <option v-for="model in filteredModels.filter(m => m.id.startsWith('o1'))" :key="model.id" :value="model.id">
                    {{ model.name }}
                  </option>
                </optgroup>
                <optgroup v-if="filteredModels.filter(m => m.id.startsWith('ft:')).length > 0" label="微调模型">
                  <option v-for="model in filteredModels.filter(m => m.id.startsWith('ft:'))" :key="model.id" :value="model.id">
                    {{ model.name }}
                  </option>
                </optgroup>
                <optgroup v-if="filteredModels.filter(m => !m.id.startsWith('gpt-') && !m.id.startsWith('o1') && !m.id.startsWith('ft:')).length > 0" label="其他模型">
                  <option v-for="model in filteredModels.filter(m => !m.id.startsWith('gpt-') && !m.id.startsWith('o1') && !m.id.startsWith('ft:'))" :key="model.id" :value="model.id">
                    {{ model.name }}
                  </option>
                </optgroup>
              </select>
              
              <p class="text-xs text-slate-500 mt-2">
                {{ currentLocale === 'zh' ? '当前使用：' : 'Currently using: ' }}<span class="font-semibold text-indigo-600">{{ llmConfig.model }}</span>
              </p>
              <p v-if="modelSearchQuery && filteredModels.length === 0" class="text-xs text-red-500 mt-1">
                {{ currentLocale === 'zh' ? '未找到匹配的模型' : 'No matching models found' }}
              </p>
            </div>

            <!-- User info message - for regular users -->
            <div v-if="userRole !== 'superadmin'" class="p-4 bg-blue-50 border border-blue-200 rounded-xl">
              <div class="flex items-start gap-3">
                <svg class="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <div>
                  <div class="font-medium text-blue-900 text-sm mb-1">
                    {{ currentLocale === 'zh' ? 'AI 模型信息' : 'AI Model Information' }}
                  </div>
                  <div class="text-sm text-blue-700 leading-relaxed">
                    {{ currentLocale === 'zh' ? '您正在使用 CBIT 提供的高性能AI 服务。该模型由CBIT基于Qwen3 和VoxChina提供的语料微调训练，确保精准性能和稳定性。' : 'You are using high-performance AI service provided by CBIT. The model is fine-tuned by CBIT based on Qwen3 and corpus provided by VoxChina, ensuring precision performance and stability.' }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Status - Only for superadmin -->
            <div v-if="userRole === 'superadmin' && llmConfig.api_key_set" class="flex items-center gap-2 text-sm">
              <div class="w-2 h-2 bg-green-500 rounded-full"></div>
              <span class="text-green-700 font-medium">{{ currentLocale === 'zh' ? 'API 密钥已配置' : 'API Key Configured' }}</span>
            </div>

            <!-- Error Message -->
            <div v-if="llmConfigError" class="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
              {{ llmConfigError }}
            </div>
          </div>

          <!-- Footer -->
          <div class="bg-slate-50 px-6 py-4 flex items-center justify-end gap-3 border-t border-slate-200">
            <button 
              @click="showLLMConfig = false" 
              class="px-4 py-2 text-slate-600 hover:text-slate-900 font-medium transition-colors"
            >
              {{ currentLocale === 'zh' ? userRole === 'superadmin' ? '取消' : '关闭' : userRole === 'superadmin' ? 'Cancel' : 'Close' }}
            </button>
            <!-- Save button only for superadmin -->
            <button 
              v-if="userRole === 'superadmin'"
              @click="saveLLMConfig" 
              :disabled="llmConfigLoading || !selectedModel"
              class="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors shadow-lg shadow-indigo-200"
            >
              <span v-if="llmConfigLoading">{{ currentLocale === 'zh' ? '保存中...' : 'Saving...' }}</span>
              <span v-else>{{ currentLocale === 'zh' ? '保存配置' : 'Save Config' }}</span>
            </button>
          </div>
        </div>
      </div>

      <main class="max-w-5xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <!-- Header -->
        <div class="text-center mb-12">
          <h1 class="text-4xl font-extrabold text-slate-900 sm:text-5xl tracking-tight mb-4 capitalize">
            {{ t.headers[activeTab] }}
          </h1>
          <p class="text-lg text-slate-600 max-w-2xl mx-auto">
            {{ t.descriptions[activeTab] }}
          </p>
        </div>
        
        <!-- Multi Article View -->
        <div v-if="activeTab === 'script'" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div class="lg:col-span-1 space-y-4">
            <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
              <h3 class="text-lg font-bold text-slate-900 mb-4">{{ t.script.upload_title }}</h3>
              <div class="mb-4">
                <input 
                  type="file" 
                  @change="handleScriptFilesUpload" 
                  accept=".docx,.doc"
                  multiple
                  class="w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                />
                <p class="mt-2 text-xs text-slate-500">{{ t.script.upload_hint }}</p>
              </div>
              <div v-if="scriptFiles.length > 0" class="space-y-2">
                <div v-for="(file, index) in scriptFiles" :key="index" class="flex items-center justify-between p-2 bg-slate-50 rounded-lg">
                  <span class="text-sm text-slate-700 truncate">{{ file.name }}</span>
                  <button @click="removeScriptFile(index)" class="text-red-500 hover:text-red-700">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                  </button>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
              <h3 class="text-lg font-bold text-slate-900 mb-4">{{ t.script.params_title }}</h3>
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-2">{{ t.script.speaker_name }}</label>
                  <input v-model="scriptSpeakerName" type="text" class="w-full rounded-lg border-slate-200 focus:ring-indigo-500 focus:border-indigo-500 text-sm" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-2">{{ t.script.speaker_affiliation }}</label>
                  <input v-model="scriptSpeakerAffiliation" type="text" class="w-full rounded-lg border-slate-200 focus:ring-indigo-500 focus:border-indigo-500 text-sm" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-2">{{ t.script.episode_topic }}</label>
                  <input v-model="scriptEpisodeTopic" type="text" class="w-full rounded-lg border-slate-200 focus:ring-indigo-500 focus:border-indigo-500 text-sm" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-2">{{ t.script.duration }}</label>
                  <input v-model="scriptDuration" type="number" min="60" max="600" class="w-full rounded-lg border-slate-200 focus:ring-indigo-500 focus:border-indigo-500 text-sm" />
                </div>
              </div>
              <div class="mt-6">
                <button 
                  @click="generateScript"
                  :disabled="scriptLoading || scriptFiles.length < 1"
                  class="w-full px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 font-medium transition-colors"
                >
                  {{ scriptLoading ? t.script.generating : t.script.generate_btn }}
                </button>
              </div>
              <div v-if="error" class="mt-4 text-red-600 text-sm">{{ error }}</div>
            </div>
          </div>

          <div class="lg:col-span-2 space-y-6">
            <div v-if="scriptLoading && scriptStatus" class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
              <h3 class="text-lg font-bold text-slate-900 mb-4">{{ t.script.progress_title }}</h3>
              <div class="space-y-4">
                <div class="flex justify-between items-center mb-2">
                  <span class="text-sm font-medium text-slate-700">{{ scriptStatus.stage }}</span>
                  <span class="text-sm text-slate-500">{{ scriptStatus.progress.percent }}%</span>
                </div>
                <div class="w-full bg-slate-200 rounded-full h-2.5">
                  <div class="bg-indigo-600 h-2.5 rounded-full transition-all duration-300" :style="{width: scriptStatus.progress.percent + '%'}"></div>
                </div>
                <p class="text-sm text-slate-600">{{ scriptStatus.detail }}</p>
                <div v-if="scriptStatus.progress.doc_total > 0" class="text-xs text-slate-500">
                  文档: {{ scriptStatus.progress.doc_current }}/{{ scriptStatus.progress.doc_total }} | 
                  文本块: {{ scriptStatus.progress.chunk_current }}/{{ scriptStatus.progress.chunk_total }}
                </div>
              </div>
            </div>

            <div v-if="scriptResult" class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 animate-fade-in">
              <h3 class="text-lg font-bold text-slate-900 mb-4">{{ t.script.result_title }}</h3>
              <div class="mb-6">
                <h4 class="text-xl font-bold text-slate-900 mb-3">{{ scriptResult.episode_title }}</h4>
                <div class="prose prose-slate max-w-none bg-slate-50 p-4 rounded-lg max-h-96 overflow-y-auto">
                  <pre class="whitespace-pre-wrap text-sm">{{ scriptResult.script_text }}</pre>
                </div>
              </div>
              <div class="flex flex-wrap gap-3">
                <button 
                  @click="downloadScriptDocx"
                  class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition-colors"
                >
                  {{ t.script.download_docx }}
                </button>
                <button 
                  @click="downloadScriptLedgers"
                  class="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 font-medium transition-colors"
                >
                  {{ t.script.download_ledgers }}
                </button>
                <button 
                  @click="downloadScriptAudit"
                  class="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 font-medium transition-colors"
                >
                  {{ t.script.download_audit }}
                </button>
              </div>
              <div class="mt-4 text-sm text-slate-600">
                <p>字数: {{ scriptResult.word_count }} | 核验: {{ scriptResult.verification.verdict }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Search View -->
        <div v-if="activeTab === 'search'" class="bg-white rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-100 min-h-[600px] flex flex-col">
          <!-- ... (Same content) ... -->
          <div class="flex-1 p-8 sm:p-10 overflow-y-auto">
            <div v-if="!searchAnswer && !searchLoading" class="h-full flex flex-col items-center justify-center text-center opacity-50">
               <div class="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4">
                 <svg class="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
               </div>
               <p class="text-lg font-medium text-slate-900">{{ t.search.empty_state }}</p>
            </div>

            <div v-else class="space-y-8">
               <!-- Answer -->
               <div v-if="searchAnswer" class="animate-fade-in">
                 <h3 class="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
                   <span class="w-6 h-6 bg-indigo-600 rounded-full flex items-center justify-center text-white text-xs">AI</span>
                   {{ t.search.response_title }}
                 </h3>
                 <div class="prose prose-slate max-w-none bg-slate-50 p-6 rounded-xl">
                   <p class="whitespace-pre-wrap">{{ searchAnswer }}</p>
                 </div>
               </div>

               <!-- Sources -->
               <div v-if="searchSources.length > 0" class="animate-fade-in delay-150">
                  <h3 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">{{ t.search.sources_title }}</h3>
                  <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    <div v-for="source in searchSources" :key="source.id" class="bg-white border border-slate-200 rounded-lg p-4 hover:border-indigo-300 transition-colors">
                      <h4 class="font-medium text-slate-900 text-sm mb-2 line-clamp-1">{{ source.title }}</h4>
                      <p class="text-xs text-slate-500 line-clamp-3">{{ source.summary }}</p>
                      <div class="mt-2 flex items-center gap-1">
                         <span class="text-[10px] bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full">{{ t.search.score }}: {{ source.score.toFixed(2) }}</span>
                      </div>
                    </div>
                  </div>
               </div>
            </div>
          </div>

          <!-- Input Area -->
          <div class="p-6 border-t border-slate-100 bg-slate-50 rounded-b-2xl">
            <div class="relative flex gap-4 max-w-3xl mx-auto">
              <input 
                v-model="searchQuery"
                @keyup.enter="performSearch"
                type="text" 
                :placeholder="t.search.input_placeholder" 
                class="w-full rounded-xl border-slate-200 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 py-3 pl-4 pr-12"
                :disabled="searchLoading"
              />
              <button 
                @click="performSearch"
                :disabled="searchLoading || !searchQuery"
                class="absolute right-2 top-2 bottom-2 px-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
              >
                <svg v-if="!searchLoading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                <svg v-else class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Trending View -->
        <div v-if="activeTab === 'trending'" class="bg-white rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-100">
           <!-- ... (Same content) ... -->
           <div class="p-8 sm:p-10">
             <div class="max-w-3xl mx-auto space-y-6">
                <div>
                  <label class="block text-sm font-semibold text-slate-700 mb-2">{{ t.trending.topic_label }}</label>
                  <input 
                    v-model="trendingTopic" 
                    type="text" 
                    :placeholder="t.trending.topic_placeholder" 
                    class="w-full rounded-xl border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 focus:border-indigo-500 focus:ring-indigo-500 focus:bg-white transition-all duration-200" 
                  />
                </div>
                
                <div class="flex items-center gap-3">
                  <input v-model="trendingGenerateVideoScript" id="script-toggle" type="checkbox" class="h-5 w-5 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                  <label for="script-toggle" class="text-sm font-medium text-slate-700">{{ t.trending.script_toggle }}</label>
                </div>

                <div class="pt-4 flex justify-end">
                  <button 
                    @click="generateTrending" 
                    :disabled="trendingLoading || !trendingTopic"
                    class="group relative inline-flex items-center justify-center px-8 py-3 text-base font-medium text-white transition-all duration-200 bg-indigo-600 rounded-xl hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 shadow-lg shadow-indigo-200"
                  >
                    <span v-if="trendingLoading">{{ t.trending.generating }}</span>
                    <span v-else>{{ t.trending.generate_btn }}</span>
                  </button>
                </div>
                <div v-if="error" class="text-red-600 text-sm font-medium text-center">{{ error }}</div>
             </div>
           </div>

           <div v-if="trendingPost" class="bg-slate-50/50 border-t border-slate-200 p-8 sm:p-10 space-y-8 animate-fade-in">
             <div>
               <div class="flex items-center gap-2 mb-4">
                 <div class="p-2 bg-blue-100 rounded-lg">
                   <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"></path></svg>
                 </div>
                 <h3 class="text-lg font-bold text-slate-900">{{ t.trending.post_title }}</h3>
               </div>
               <div class="prose prose-slate max-w-none bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                  <p class="whitespace-pre-wrap">{{ trendingPost }}</p>
               </div>
             </div>

             <div v-if="trendingScript">
               <div class="flex items-center gap-2 mb-4">
                 <div class="p-2 bg-purple-100 rounded-lg">
                   <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                 </div>
                 <h3 class="text-lg font-bold text-slate-900">{{ t.trending.script_title }}</h3>
               </div>
               <div class="prose prose-slate max-w-none bg-white p-6 rounded-xl shadow-sm border border-slate-100 overflow-x-auto">
                  <p class="whitespace-pre-wrap font-mono text-sm">{{ trendingScript }}</p>
               </div>
             </div>
           </div>
        </div>

        <!-- Voices View (New) -->
        <div v-if="activeTab === 'voices'" class="bg-white rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-100 p-8 sm:p-10">
           
           <div class="grid grid-cols-1 lg:grid-cols-3 gap-10">
              <!-- Upload Section -->
              <div class="lg:col-span-1">
                 <h3 class="text-lg font-bold text-slate-900 mb-6">{{ t.voices.clone_title }}</h3>
                 <div class="bg-slate-50 p-6 rounded-xl border border-slate-200 space-y-6">
                    <div>
                      <label class="block text-sm font-semibold text-slate-700 mb-2">{{ t.voices.name_label }}</label>
                      <input v-model="uploadVoiceName" type="text" :placeholder="t.voices.name_placeholder" class="w-full rounded-lg border-slate-200 focus:ring-indigo-500 focus:border-indigo-500" />
                    </div>
                    <div>
                      <label class="block text-sm font-semibold text-slate-700 mb-2">{{ t.voices.file_label }}</label>
                      <input id="voice-upload" type="file" accept="audio/*" @change="handleFileUpload" class="w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100" />
                      <p class="text-xs text-slate-500 mt-2">{{ t.voices.file_hint }}</p>
                    </div>
                    
                    <div v-if="uploadError" class="text-red-600 text-sm">{{ uploadError }}</div>
                    
                    <button @click="uploadVoice" :disabled="voiceUploading || !uploadVoiceName || !uploadVoiceFile" class="w-full py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 font-medium">
                      {{ voiceUploading ? t.voices.cloning : t.voices.clone_btn }}
                    </button>
                 </div>
              </div>

              <!-- Voice List -->
              <div class="lg:col-span-2">
                 <h3 class="text-lg font-bold text-slate-900 mb-6">{{ t.voices.library_title }}</h3>
                 <div v-if="voices.length === 0" class="text-center py-12 bg-slate-50 rounded-xl border border-dashed border-slate-300 text-slate-500">
                    {{ t.voices.empty_lib }}
                 </div>
                 <div class="grid gap-4 sm:grid-cols-2">
                    <div v-for="voice in voices" :key="voice.id" class="bg-white border border-slate-200 rounded-xl p-4 hover:border-indigo-300 transition-all group relative">
                       <div class="flex justify-between items-start mb-3">
                          <h4 class="font-bold text-slate-900">{{ voice.name }}</h4>
                          <button @click="deleteVoice(voice.id)" class="text-slate-400 hover:text-red-500"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg></button>
                       </div>
                       
                       <div class="space-y-3">
                          <!-- Original Audio -->
                          <div class="flex items-center gap-2">
                             <span class="text-[10px] text-slate-500 uppercase tracking-wider">Original</span>
                             <audio controls :src="`${API_BASE_URL}${voice.audio_url}`" class="w-full h-6"></audio>
                          </div>
                          
                          <!-- Preview Section (Inside Card) -->
                          <div class="border-t border-slate-100 pt-3 mt-2">
                             <div class="flex flex-col gap-2">
                                <div class="flex justify-between items-center">
                                  <span class="text-[10px] text-indigo-500 uppercase tracking-wider font-bold">Test Voice</span>
                                </div>
                                
                                <div class="flex items-center gap-2">
                                  <button 
                                     @click="previewVoice(voice.id)" 
                                     :disabled="previewLoading === voice.id"
                                     class="flex-shrink-0 text-xs bg-indigo-50 text-indigo-600 px-3 py-1.5 rounded hover:bg-indigo-100 disabled:opacity-50 font-medium transition-colors"
                                  >
                                     {{ previewLoading === voice.id ? t.voices.previewing : t.voices.preview_btn }}
                                  </button>
                                  
                                  <!-- Preview Player -->
                                  <audio v-if="previewAudioUrl[voice.id]" controls :src="previewAudioUrl[voice.id]" class="w-full h-6"></audio>
                                </div>
                             </div>
                          </div>
                       </div>
                    </div>
                 </div>
              </div>
           </div>
        </div>

        <!-- Vox Workshop View -->
        <div v-if="activeTab === 'workshop'" class="bg-white rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-100 h-[800px] overflow-hidden">
          <VoxWorkshop :api-base-url="API_BASE_URL" />
        </div>

        <!-- Extract View -->
        <div v-if="activeTab === 'extract'" class="space-y-6">
          <!-- Upload Section -->
          <div class="bg-white rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-100 p-8 sm:p-10">
            <h3 class="text-2xl font-bold text-slate-900 mb-2">{{ t.headers.extract }}</h3>
            <p class="text-slate-600 mb-8">{{ t.descriptions.extract }}</p>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <!-- File Upload Area -->
              <div>
                <label class="block text-sm font-semibold text-slate-700 mb-3">{{ t.extract.file_label }}</label>
                <div class="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center hover:border-indigo-400 transition-colors cursor-pointer bg-slate-50/50"
                     @click="triggerFileInput"
                     @drop.prevent="(e:any) => { extractFiles = Array.from(e.dataTransfer.files) }"
                     @dragover.prevent>
                  <div class="flex flex-col items-center gap-3">
                    <div class="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center">
                      <svg class="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                    </div>
                    <div>
                      <p class="text-sm font-medium text-slate-700">{{ extractFiles.length > 0 ? extractFiles.length + ' file(s) selected' : 'Click to upload or drag & drop' }}</p>
                      <p class="text-xs text-slate-500 mt-1">{{ t.extract.file_hint }}</p>
                      <p class="text-xs text-slate-400 mt-1">{{ t.extract.batch_hint }}</p>
                    </div>
                  </div>
                  <input 
                    id="extract-file-input" 
                    type="file" 
                    accept=".docx,.doc,.pdf" 
                    multiple
                    @change="handleExtractFiles"
                    class="hidden"
                  />
                </div>
                
                <!-- File List -->
                <div v-if="extractFiles.length > 0" class="mt-4 space-y-2">
                  <div v-for="(file, idx) in extractFiles" :key="idx" class="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-200">
                    <div class="flex items-center gap-2">
                      <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                      <span class="text-sm font-medium text-slate-700 truncate">{{ file.name }}</span>
                    </div>
                    <span class="text-xs text-slate-500">{{ (file.size / 1024).toFixed(1) }} KB</span>
                  </div>
                </div>
                
                <button 
                  @click="extractArticle"
                  :disabled="extractLoading || extractFiles.length === 0"
                  class="w-full mt-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 font-semibold transition-colors flex items-center justify-center gap-2"
                >
                  <svg v-if="extractLoading" class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                  <span>{{ extractLoading ? t.extract.extracting : (extractFiles.length > 1 ? t.extract.batch_extract_btn : t.extract.extract_btn) }}</span>
                </button>
                
                <!-- 进度条和状态显示 -->
                <div v-if="extractLoading" class="mt-6 space-y-4 animate-fade-in">
                  <!-- 进度条 -->
                  <div class="relative">
                    <div class="flex items-center justify-between mb-2">
                      <span class="text-sm font-semibold text-slate-700">{{ extractStage }}</span>
                      <span class="text-sm font-bold text-indigo-600">{{ extractProgress }}%</span>
                    </div>
                    <div class="w-full bg-slate-200 rounded-full h-3 overflow-hidden shadow-inner">
                      <div 
                        class="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-full transition-all duration-500 ease-out relative overflow-hidden"
                        :style="{ width: extractProgress + '%' }"
                      >
                        <!-- 动画光效 -->
                        <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-shimmer"></div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 状态详情卡片 -->
                  <div class="bg-gradient-to-br from-indigo-50 to-purple-50 p-4 rounded-xl border border-indigo-200">
                    <div class="flex items-start gap-3">
                      <div class="flex-shrink-0 mt-1">
                        <div class="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center animate-pulse">
                          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path></svg>
                        </div>
                      </div>
                      <div class="flex-1">
                        <p class="text-sm font-medium text-slate-900 mb-1">CBIT 智能分析系统</p>
                        <p class="text-xs text-slate-600 leading-relaxed">
                          基于大语言模型的深度语义理解，结合多重证据校验机制，确保零幻觉、高精度的学术文章摘要提取。
                        </p>
                      </div>
                    </div>
                    
                    <!-- 处理阶段指示器 -->
                    <div class="mt-4 flex items-center gap-2 flex-wrap">
                      <span 
                        v-for="(stage, idx) in extractStages.slice(0, 5)" 
                        :key="idx"
                        :class="[
                          'text-xs px-2 py-1 rounded-full transition-all duration-300',
                          extractProgress >= stage.progress 
                            ? 'bg-indigo-600 text-white font-semibold' 
                            : 'bg-slate-200 text-slate-500'
                        ]"
                      >
                        {{ stage.name.split('与')[0] }}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div v-if="extractError" class="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">{{ extractError }}</div>
              </div>
              
              <!-- History -->
              <div>
                <h4 class="text-sm font-semibold text-slate-700 mb-3">{{ t.extract.history_title }}</h4>
                <div class="space-y-2 max-h-[400px] overflow-y-auto custom-scrollbar">
                  <div v-if="extractHistory.length === 0" class="text-center py-8 text-slate-400 text-sm">{{ t.extract.no_history }}</div>
                  <div 
                    v-for="item in extractHistory" 
                    :key="item.id"
                    @click="viewExtractDetail(item.id)"
                    class="p-4 bg-slate-50 border border-slate-200 rounded-lg hover:border-indigo-300 cursor-pointer transition-all group"
                  >
                    <h5 class="font-semibold text-slate-900 text-sm mb-1 group-hover:text-indigo-600 line-clamp-1">{{ item.title }}</h5>
                    <p class="text-xs text-slate-500 line-clamp-2 mb-2">{{ item.summary_zh }}</p>
                    <div class="flex items-center justify-between">
                      <span class="text-[10px] text-slate-400">{{ new Date(item.created_at).toLocaleDateString() }}</span>
                      <span class="text-xs text-indigo-600 group-hover:underline">{{ t.extract.view_detail }} →</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Single Extract Result (Workbench Style) -->
          <div v-if="extractResult && !batchExtractResults.length" id="extract-result" class="animate-fade-in space-y-6">
            
            <!-- Header Metadata -->
            <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex justify-between items-start">
              <div>
                <h3 class="text-2xl font-bold text-slate-900 mb-2">{{ extractResult.title }}</h3>
                <div class="flex gap-4 text-sm text-slate-500">
                  <span class="flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                    {{ new Date().toLocaleDateString() }}
                  </span>
                  <span class="flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    {{ extractResult.metadata?.format?.toUpperCase() || 'DOC' }}
                  </span>
                </div>
              </div>
              <div class="flex items-center gap-2">
                 <div class="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-bold flex items-center gap-1">
                   <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                   Completed
                 </div>
              </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
              
              <!-- Left Column: Analysis (FactTable) -->
              <div class="lg:col-span-5 space-y-6">
                <!-- Fact Table -->
                <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden flex flex-col h-full">
                  <div class="px-6 py-4 border-b border-slate-100 bg-slate-50 flex justify-between items-center">
                    <h4 class="font-bold text-slate-800 flex items-center gap-2">
                      <svg class="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path></svg>
                      {{ t.extract.fact_table_title }}
                    </h4>
                  </div>
                  
                  <div class="p-6 space-y-6 overflow-y-auto max-h-[800px] custom-scrollbar">
                    <!-- Authors -->
                    <div v-if="extractResult.fact_table.authors_affiliations?.length">
                      <h5 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">{{ t.extract.authors }}</h5>
                      <ul class="space-y-2">
                        <li v-for="(auth, idx) in extractResult.fact_table.authors_affiliations" :key="idx" class="flex items-start gap-2 text-sm text-slate-700 bg-slate-50 p-2 rounded-lg">
                          <span class="w-1.5 h-1.5 bg-indigo-400 rounded-full mt-1.5 shrink-0"></span>
                          {{ auth }}
                        </li>
                      </ul>
                    </div>
                    
                    <!-- Research Question -->
                    <div v-if="extractResult.fact_table.research_question">
                      <h5 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">{{ t.extract.research_question }}</h5>
                      <div class="bg-slate-50 p-4 rounded-lg border-l-4 border-indigo-200 space-y-3">
                        <!-- 如果是对象格式，展示详细信息 -->
                        <div v-if="typeof extractResult.fact_table.research_question === 'object'">
                          <div v-if="extractResult.fact_table.research_question.question" class="mb-2">
                            <span class="text-xs font-semibold text-indigo-600">研究问题：</span>
                            <p class="text-sm text-slate-700 mt-1">{{ extractResult.fact_table.research_question.question }}</p>
                            <p v-if="extractResult.fact_table.research_question.evidence" class="text-xs text-slate-500 italic mt-1 pl-2 border-l-2 border-indigo-200">{{ extractResult.fact_table.research_question.evidence }}</p>
                          </div>
                          
                          <div v-if="extractResult.fact_table.research_question.research_object" class="mb-2">
                            <span class="text-xs font-semibold text-indigo-600">研究对象：</span>
                            <p class="text-sm text-slate-700 mt-1">{{ extractResult.fact_table.research_question.research_object }}</p>
                            <p v-if="extractResult.fact_table.research_question.research_object_evidence" class="text-xs text-slate-500 italic mt-1 pl-2 border-l-2 border-indigo-200">{{ extractResult.fact_table.research_question.research_object_evidence }}</p>
                          </div>
                          
                          <div v-if="extractResult.fact_table.research_question.data_sample" class="mb-2">
                            <span class="text-xs font-semibold text-indigo-600">数据与样本：</span>
                            <p class="text-sm text-slate-700 mt-1">{{ extractResult.fact_table.research_question.data_sample }}</p>
                            <p v-if="extractResult.fact_table.research_question.data_sample_evidence" class="text-xs text-slate-500 italic mt-1 pl-2 border-l-2 border-indigo-200">{{ extractResult.fact_table.research_question.data_sample_evidence }}</p>
                          </div>
                          
                          <div v-if="extractResult.fact_table.research_question.method">
                            <span class="text-xs font-semibold text-indigo-600">研究方法：</span>
                            <p class="text-sm text-slate-700 mt-1">{{ extractResult.fact_table.research_question.method }}</p>
                            <p v-if="extractResult.fact_table.research_question.method_evidence" class="text-xs text-slate-500 italic mt-1 pl-2 border-l-2 border-indigo-200">{{ extractResult.fact_table.research_question.method_evidence }}</p>
                          </div>
                        </div>
                        
                        <!-- 如果是字符串格式（兼容旧数据），直接显示 -->
                        <p v-else class="text-sm text-slate-700">
                          {{ extractResult.fact_table.research_question }}
                        </p>
                      </div>
                    </div>
                    
                    <!-- Key Findings -->
                    <div v-if="extractResult.fact_table.key_findings?.length">
                      <h5 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">{{ t.extract.key_findings }}</h5>
                      <div class="space-y-3">
                        <div v-for="(finding, idx) in extractResult.fact_table.key_findings" :key="idx" class="bg-amber-50 p-3 rounded-lg border border-amber-100 group hover:shadow-sm transition-shadow">
                          <div class="flex items-start gap-2">
                            <span class="text-amber-500 font-bold text-lg leading-none mt-0.5">•</span>
                            <div>
                              <p class="text-sm font-medium text-slate-900 mb-1">{{ finding.finding }}</p>
                              <div v-if="finding.effect_size" class="inline-block px-2 py-0.5 bg-white rounded text-xs text-amber-700 font-mono border border-amber-100 mb-1">
                                {{ finding.effect_size }}
                              </div>
                              <p v-if="finding.evidence_quote" class="text-xs text-slate-500 italic mt-1 pl-2 border-l-2 border-amber-200">
                                "{{ finding.evidence_quote }}"
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Mechanism -->
                    <div v-if="extractResult.fact_table.mechanism?.length">
                      <h5 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">{{ t.extract.mechanism }}</h5>
                      <div class="space-y-2">
                        <div v-for="(mech, idx) in extractResult.fact_table.mechanism" :key="idx" class="text-sm text-slate-700 bg-blue-50 p-3 rounded-lg border border-blue-100">
                          <p class="font-medium">{{ mech.claim }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Audit Report Footer -->
                  <div class="px-6 py-3 bg-slate-50 border-t border-slate-200 text-xs text-slate-500 flex justify-between">
                    <span>Coverage: {{ extractResult.audit_report.coverage.coverage_rate }}</span>
                    <span>Valid Facts: {{ extractResult.audit_report.validation.filter((v:any) => v.status === 'pass').length }}</span>
                  </div>
                </div>
              </div>

              <!-- Right Column: Creation (Summaries + Audio) -->
              <div class="lg:col-span-7 space-y-6">
                <!-- Chinese Summary Card -->
                <div class="bg-white rounded-2xl shadow-lg shadow-indigo-100/50 border border-indigo-100 overflow-hidden relative">
                  <div class="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-indigo-500 to-purple-500"></div>
                  
                  <div class="p-6">
                    <div class="flex justify-between items-center mb-4">
                      <h4 class="text-lg font-bold text-slate-900 flex items-center gap-2">
                        <span class="px-2 py-0.5 bg-indigo-600 text-white text-xs rounded shadow-sm shadow-indigo-200">中文摘要</span>
                        <span class="text-xs font-normal text-slate-400">Research Brief</span>
                      </h4>
                      <div class="flex items-center gap-2">
                        <select 
                          v-model="selectedVoiceId" 
                          class="text-xs border border-slate-300 rounded-lg px-2 py-1.5 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        >
                          <option value="">默认声音</option>
                          <option v-for="voice in voices" :key="voice.id" :value="voice.id">
                            {{ voice.name }}
                          </option>
                        </select>
                        <button 
                          @click="generateAudioForSummary(extractResult.summary_zh, 'zh')"
                          :disabled="generatingAudio.zh"
                          class="text-indigo-600 hover:text-indigo-700 text-sm font-medium flex items-center gap-1 px-3 py-1.5 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors whitespace-nowrap"
                        >
                          <svg v-if="generatingAudio.zh" class="animate-spin w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 714 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"></path></svg>
                          {{ audioUrls.zh ? '重新生成' : '生成音频' }}
                        </button>
                      </div>
                    </div>
                    
                    <div class="prose prose-slate max-w-none mb-6">
                      <p class="text-slate-700 leading-relaxed text-justify whitespace-pre-wrap font-serif">{{ extractResult.summary_zh }}</p>
                    </div>

                    <!-- Audio Player -->
                    <div v-if="audioUrls.zh" class="mt-4 p-3 bg-slate-50 rounded-xl border border-slate-100 flex items-center gap-3 animate-fade-in">
                      <audio controls :src="audioUrls.zh" class="w-full h-8"></audio>
                      <a :href="audioUrls.zh" download="summary_zh.wav" class="p-2 text-slate-400 hover:text-indigo-600 transition-colors" title="下载音频">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                      </a>
                    </div>
                  </div>
                </div>

                <!-- English Summary Card -->
                <div class="bg-white rounded-2xl shadow-lg shadow-purple-100/50 border border-purple-100 overflow-hidden relative">
                  <div class="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-purple-500 to-pink-500"></div>
                  
                  <div class="p-6">
                    <div class="flex justify-between items-center mb-4">
                      <h4 class="text-lg font-bold text-slate-900 flex items-center gap-2">
                        <span class="px-2 py-0.5 bg-purple-600 text-white text-xs rounded shadow-sm shadow-purple-200">English Summary</span>
                        <span class="text-xs font-normal text-slate-400">International Brief</span>
                      </h4>
                      <div class="flex items-center gap-2">
                        <select 
                          v-model="selectedVoiceId" 
                          class="text-xs border border-slate-300 rounded-lg px-2 py-1.5 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-purple-500"
                        >
                          <option value="">Default Voice</option>
                          <option v-for="voice in voices" :key="voice.id" :value="voice.id">
                            {{ voice.name }}
                          </option>
                        </select>
                        <button 
                          @click="generateAudioForSummary(extractResult.summary_en, 'en')"
                          :disabled="generatingAudio.en"
                          class="text-purple-600 hover:text-purple-700 text-sm font-medium flex items-center gap-1 px-3 py-1.5 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors whitespace-nowrap"
                        >
                          <svg v-if="generatingAudio.en" class="animate-spin w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 714 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"></path></svg>
                          {{ audioUrls.en ? 'Regenerate' : 'Generate Audio' }}
                        </button>
                      </div>
                    </div>
                    
                    <div class="prose prose-slate max-w-none mb-6">
                      <p class="text-slate-700 leading-relaxed text-justify whitespace-pre-wrap font-serif">{{ extractResult.summary_en }}</p>
                    </div>

                    <!-- Audio Player -->
                    <div v-if="audioUrls.en" class="mt-4 p-3 bg-slate-50 rounded-xl border border-slate-100 flex items-center gap-3 animate-fade-in">
                      <audio controls :src="audioUrls.en" class="w-full h-8"></audio>
                      <a :href="audioUrls.en" download="summary_en.wav" class="p-2 text-slate-400 hover:text-purple-600 transition-colors" title="Download Audio">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Batch Extract Results -->
          <div v-if="batchExtractResults.length > 0" class="bg-white rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-100 p-8 sm:p-10 animate-fade-in">
            <h3 class="text-2xl font-bold text-slate-900 mb-6">{{ t.extract.result_title }} ({{ batchExtractResults.filter((r:any) => r.status === 'success').length }}/{{ batchExtractResults.length }})</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div 
                v-for="(result, idx) in batchExtractResults" 
                :key="idx"
                :class="[result.status === 'success' ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50']"
                class="p-4 rounded-lg border"
              >
                <div class="flex items-start gap-2 mb-2">
                  <svg v-if="result.status === 'success'" class="w-5 h-5 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                  <svg v-else class="w-5 h-5 text-red-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                  <div class="flex-1">
                    <h5 class="font-semibold text-slate-900 text-sm mb-1 line-clamp-1">{{ result.filename }}</h5>
                    <p v-if="result.status === 'success'" class="text-xs text-slate-600 line-clamp-2">{{ result.summary_zh }}</p>
                    <p v-else class="text-xs text-red-600">{{ result.error }}</p>
                  </div>
                </div>
                <button 
                  v-if="result.status === 'success' && result.extract_id"
                  @click="viewExtractDetail(result.extract_id)"
                  class="mt-2 text-xs text-indigo-600 hover:underline"
                >
                  {{ t.extract.view_detail }} →
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <footer class="mt-16 border-t border-slate-200 pt-8 pb-12">
          <div class="flex flex-col items-center justify-center gap-6">
            <!-- Branding -->
            <div class="flex items-center gap-2 text-slate-900 font-bold">
              <span>© {{ t.footer.branding }}</span>
            </div>

            <!-- Links & Badges -->
            <div class="flex items-center gap-4 flex-wrap justify-center">
              <!-- CBIT Link -->
              <a 
                href="https://cbit.cuhk.edu.cn" 
                target="_blank" 
                class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-full text-sm font-medium text-slate-600 hover:text-indigo-600 hover:border-indigo-200 transition-colors shadow-sm group"
              >
                <img src="https://cbit.cuhk.edu.cn/favicon.ico" alt="CBIT Logo" class="w-4 h-4 rounded-full" />
                <span>{{ t.footer.cbit_link }}</span>
              </a>

              <!-- GitHub Link -->
              <a 
                href="https://github.com/reneverland" 
                target="_blank" 
                class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-full text-sm font-medium text-slate-600 hover:text-indigo-600 hover:border-indigo-200 transition-colors shadow-sm group"
              >
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.499.09.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.953 0-1.091.39-1.984 1.029-2.682-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.026 2.747-1.026.546 1.379.202 2.398.099 2.65.64.698 1.028 1.591 1.028 2.682 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2Z" clip-rule="evenodd"></path></svg>
              </a>
            </div>
          </div>
        </footer>

      </main>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: #f1f5f9; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
.animate-fade-in { animation: fadeIn 0.5s ease-out; }
.animate-gradient { animation: gradientMove 8s ease infinite; background-size: 200% 200%; }
.animate-shimmer { animation: shimmer 2s ease-in-out infinite; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes gradientMove { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
@keyframes shimmer { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }
</style>

