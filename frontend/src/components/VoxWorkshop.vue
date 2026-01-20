<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const props = defineProps<{
  apiBaseUrl: string
}>()

// Voice Library Types
interface Voice {
  id: string
  name: string
  audio_url: string
}

// State
const files = ref<File[]>([])
const isDragging = ref(false)
const isGenerating = ref(false)
const result = ref<any>(null)
const error = ref<string | null>(null)
const progress = ref(0)
const currentStep = ref('')

// Voice Library State
const voices = ref<Voice[]>([])
const selectedVoiceId = ref<string | null>(null)
const voiceLoading = ref(false)
const voiceError = ref<string | null>(null)
const currentAudio = ref<HTMLAudioElement | null>(null)

// Progress Steps Definition
const progressSteps = [
  "文档获取与预处理",
  "结构化解析与噪音过滤", 
  "智能分块与覆盖率保障",
  "CBIT-LLM 语义分析",
  "深度理解与事实提取",
  "证据一致性校验",
  "幻觉过滤与可信度评估",
  "摘要生成与风格对齐",
  "准备输送结果"
]

// Options
const options = ref({
  speaker_name: '研究员',
  speaker_affiliation: 'VoxChina',
  topic_hint: '',
  duration_target_sec: 150,
  include_figure_placeholders: true
})

// Drag & Drop
const onDragOver = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = true
}

const onDragLeave = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = false
}

const onDrop = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = false
  if (e.dataTransfer?.files) {
    handleFiles(e.dataTransfer.files)
  }
}

const onFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files) {
    handleFiles(target.files)
  }
}

const handleFiles = (fileList: FileList) => {
  // Append new files
  for (let i = 0; i < fileList.length; i++) {
    files.value.push(fileList[i])
  }
}

const removeFile = (index: number) => {
  files.value.splice(index, 1)
}

// Generate
const generateContent = async () => {
  if (files.value.length === 0) {
    error.value = "请先上传至少一个文档"
    return
  }

  isGenerating.value = true
  error.value = null
  result.value = null
  progress.value = 5
  currentStep.value = "文档上传中..."

  try {
    const formData = new FormData()
    files.value.forEach(file => {
      formData.append('files', file)
    })
    
    formData.append('speaker_name', options.value.speaker_name)
    formData.append('speaker_affiliation', options.value.speaker_affiliation)
    formData.append('topic_hint', options.value.topic_hint)
    formData.append('duration_target_sec', options.value.duration_target_sec.toString())
    formData.append('include_figure_placeholders', options.value.include_figure_placeholders.toString())
    
    // 注意：LLM配置由后端统一管理，不再从前端传入

    // 1. Start Task
    const response = await fetch(`${props.apiBaseUrl}/api/v1/vox/generate`, {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      const errText = await response.text()
      throw new Error(`请求失败: ${response.status} ${errText}`)
    }

    const data = await response.json()
    const taskId = data.task_id
    
    // 2. Poll Status
    await pollStatus(taskId)

  } catch (err: any) {
    error.value = err.message || "生成失败"
    console.error(err)
    isGenerating.value = false
  }
}

const pollStatus = async (taskId: string) => {
  let pollCount = 0
  const maxPolls = 900 // 15分钟超时 (900秒) - 增加超时时间以适配复杂文档
  
  // 智能进度模拟（更合理的时间分配）
  let simulatedProgress = 5  // 从5%开始（文档已上传）
  let lastBackendProgress = 0
  let stepIndex = 0
  let lastUpdateTime = Date.now()
  
  const progressInterval = setInterval(() => {
    const now = Date.now()
    const timeSinceLastUpdate = now - lastUpdateTime
    
    // 如果后端进度有更新，立即同步
    if (progress.value > lastBackendProgress) {
      simulatedProgress = progress.value
      lastBackendProgress = progress.value
      lastUpdateTime = now
      
      // 根据进度更新步骤
      stepIndex = Math.floor(progress.value / 11.1) // 9个步骤
      if (stepIndex < progressSteps.length && !currentStep.value.includes(progressSteps[stepIndex])) {
        currentStep.value = progressSteps[stepIndex]
      }
    } else if (timeSinceLastUpdate > 2000) {
      // 如果后端超过2秒没更新，使用智能模拟（避免卡住）
      // 前期快(5-30%): 每0.5秒+0.5%
      // 中期慢(30-80%): 每0.5秒+0.2% (LLM处理阶段)
      // 后期快(80-95%): 每0.5秒+0.4%
      let increment = 0
      if (simulatedProgress < 30) {
        increment = 0.5  // 前期：文档处理
      } else if (simulatedProgress < 80) {
        increment = 0.2  // 中期：LLM分析（最慢）
      } else {
        increment = 0.4  // 后期：结果整理
      }
      
      simulatedProgress = Math.min(95, simulatedProgress + increment)
      if (progress.value < simulatedProgress) {
        progress.value = Math.floor(simulatedProgress)
        
        // 自动切换步骤显示
        const newStepIndex = Math.floor(simulatedProgress / 11.1)
        if (newStepIndex !== stepIndex && newStepIndex < progressSteps.length) {
          stepIndex = newStepIndex
          currentStep.value = progressSteps[stepIndex]
        }
      }
    }
  }, 500) // 每0.5秒更新一次（更流畅）
  
  const intervalId = setInterval(async () => {
    pollCount++
    
    // 超时检查
    if (pollCount > maxPolls) {
      clearInterval(intervalId)
      clearInterval(progressInterval)
      error.value = "处理超时，请重试或联系管理员"
      isGenerating.value = false
      return
    }
    
    try {
      const res = await fetch(`${props.apiBaseUrl}/api/v1/vox/status/${taskId}`)
      
      if (!res.ok) {
        // 404表示任务不存在（可能服务重启了）
        if (res.status === 404) {
          throw new Error("任务不存在（服务可能已重启），请重新提交")
        }
        throw new Error(`状态查询失败: HTTP ${res.status}`)
      }
      
      const statusData = await res.json()
      
      // 使用后端返回的实际进度和步骤
      if (statusData.progress !== undefined && statusData.progress > progress.value) {
        progress.value = statusData.progress
        simulatedProgress = statusData.progress // 同步模拟进度
      }
      if (statusData.step) {
        currentStep.value = statusData.step
      }
      
      // 检查任务状态
      if (statusData.status === 'completed') {
        clearInterval(intervalId)
        clearInterval(progressInterval)
        progress.value = 100
        currentStep.value = '完成'
        
        // 确保result对象存在且包含必要字段
        if (statusData.result) {
          result.value = {
            ...statusData.result,
            // 确保关键字段存在，避免undefined错误
            summary_zh: statusData.result.summary_zh || statusData.result.content || '',
            summary_en: statusData.result.summary_en || '',
            title: statusData.result.title || '',
            structured_fact_table: statusData.result.structured_fact_table || {}
          }
        } else {
          throw new Error('服务器返回的结果格式不正确')
        }
        
        isGenerating.value = false
        
      } else if (statusData.status === 'failed') {
        clearInterval(intervalId)
        clearInterval(progressInterval)
        throw new Error(statusData.error || statusData.result?.error || "任务处理失败")
      }
      
    } catch (err: any) {
      clearInterval(intervalId)
      clearInterval(progressInterval)
      error.value = err.message || "状态查询失败"
      isGenerating.value = false
      console.error('[VoxWorkshop] Poll error:', err)
    }
  }, 1000) // 每秒轮询一次
}

// Helpers
const modeLabel = computed(() => {
  if (result.value?.mode === 'SINGLE_SUMMARY') return '单篇精读摘要'
  if (result.value?.mode === 'MULTI_SCRIPT') return '多篇整合口播'
  return result.value?.mode
})

const downloadUrl = computed(() => {
  if (!result.value?.docx_url) return '#'
  return `${props.apiBaseUrl}${result.value.docx_url}`
})

// Progress UI Helper
const getStepStatus = (stepName: string) => {
  const currentIndex = progressSteps.indexOf(currentStep.value)
  const stepIndex = progressSteps.indexOf(stepName)
  
  // Simple heuristic: if exact match or past it
  if (currentStep.value === stepName) return 'current'
  
  // If we can find indices, compare them
  if (currentIndex !== -1 && stepIndex !== -1) {
      if (stepIndex < currentIndex) return 'completed'
      return 'pending'
  }
  
  // Fallback based on progress bar % roughly mapping to steps
  const totalSteps = progressSteps.length
  const percentPerStep = 100 / totalSteps
  const estimatedStepIndex = Math.floor(progress.value / percentPerStep)
  
  if (stepIndex < estimatedStepIndex) return 'completed'
  if (stepIndex === estimatedStepIndex) return 'current'
  return 'pending'
}

// Voice Library Functions
const fetchVoices = async () => {
  voiceLoading.value = true
  voiceError.value = null
  try {
    const response = await fetch(`${props.apiBaseUrl}/api/v1/voices/`)
    if (!response.ok) {
      throw new Error(`获取声音库失败: ${response.status}`)
    }
    voices.value = await response.json()
  } catch (err: any) {
    voiceError.value = err.message || '无法连接到声音库'
    console.error('Failed to fetch voices:', err)
  } finally {
    voiceLoading.value = false
  }
}

const playVoicePreview = async (voiceId: string) => {
  try {
    // Stop any currently playing audio
    if (currentAudio.value) {
      currentAudio.value.pause()
      currentAudio.value = null
    }

    const response = await fetch(`${props.apiBaseUrl}/api/v1/voices/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        voice_id: voiceId,
        text: null,
        language: 'zh'
      })
    })

    if (!response.ok) {
      throw new Error('预览生成失败')
    }

    const data = await response.json()
    const audioUrl = `${props.apiBaseUrl}${data.audio_url}`
    
    // Play audio
    const audio = new Audio(audioUrl)
    currentAudio.value = audio
    audio.play()
    
    selectedVoiceId.value = voiceId
  } catch (err: any) {
    console.error('Failed to play voice preview:', err)
    alert('声音预览失败: ' + err.message)
  }
}

const downloadAudio = async (voiceId: string, voiceName: string) => {
  try {
    const response = await fetch(`${props.apiBaseUrl}/api/v1/voices/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        voice_id: voiceId,
        text: result.value?.summary_zh || '欢迎使用VoxChina声音库',
        language: 'zh'
      })
    })

    if (!response.ok) {
      throw new Error('音频生成失败')
    }

    const data = await response.json()
    const audioUrl = `${props.apiBaseUrl}${data.audio_url}`
    
    // Download as MP3 (though backend generates WAV, we'll convert filename)
    const link = document.createElement('a')
    link.href = audioUrl
    link.download = `${voiceName}_preview.wav`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (err: any) {
    console.error('Failed to download audio:', err)
    alert('音频下载失败: ' + err.message)
  }
}

// Load voices on mount
onMounted(() => {
  fetchVoices()
})

</script>

<template>
  <div class="h-full flex flex-col bg-slate-50 overflow-hidden">
    <!-- Header -->
    <header class="bg-white border-b px-6 py-4 flex items-center justify-between shrink-0">
      <div>
        <h2 class="text-xl font-bold text-slate-800 flex items-center gap-2">
          <span class="bg-indigo-600 text-white p-1 rounded-md">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd" />
            </svg>
          </span>
          VoxChina 内容工坊
        </h2>
        <p class="text-sm text-slate-500 mt-1">
          统一入口：自动识别单篇摘要 / 多篇整合口播
        </p>
      </div>
      <div class="flex items-center gap-3">
        <!-- Voice Library Selector -->
        <div v-if="voiceLoading" class="flex items-center gap-2 px-3 py-1 bg-slate-100 rounded-full text-xs text-slate-400">
          <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>声音库加载中...</span>
        </div>
        <div v-else-if="voiceError" class="flex items-center gap-2 px-3 py-1 bg-red-100 rounded-full text-xs text-red-600">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{{ voiceError }}</span>
        </div>
        <div v-else-if="voices.length > 0" class="hidden md:flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
          </svg>
          <select 
            v-model="selectedVoiceId" 
            @change="selectedVoiceId && playVoicePreview(selectedVoiceId)"
            class="text-xs border-slate-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 bg-white"
          >
            <option :value="null">选择声音</option>
            <option v-for="voice in voices" :key="voice.id" :value="voice.id">
              {{ voice.name }}
            </option>
          </select>
          <button 
            v-if="selectedVoiceId && result"
            @click="downloadAudio(selectedVoiceId, voices.find(v => v.id === selectedVoiceId)?.name || 'voice')"
            class="px-2 py-1 bg-indigo-600 hover:bg-indigo-700 text-white text-xs rounded-md flex items-center gap-1"
            title="下载音频"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
            MP3
          </button>
        </div>
        <div v-else class="hidden md:flex items-center gap-2 px-3 py-1 bg-slate-100 rounded-full text-xs text-slate-400">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
          <span>暂无声音</span>
        </div>
      </div>
    </header>

    <div class="flex-1 overflow-hidden flex flex-col md:flex-row">
      <!-- Left Panel: Input -->
      <div class="w-full md:w-1/3 bg-white border-r flex flex-col overflow-y-auto z-10 shadow-lg md:shadow-none">
        <div class="p-6 space-y-6">
          
          <!-- Drop Zone -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">上传文档 (PDF/DOCX)</label>
            <div 
              class="border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer"
              :class="isDragging ? 'border-indigo-500 bg-indigo-50' : 'border-slate-300 hover:border-indigo-400'"
              @dragover="onDragOver"
              @dragleave="onDragLeave"
              @drop="onDrop"
              @click="$refs.fileInput.click()"
            >
              <input type="file" ref="fileInput" class="hidden" multiple accept=".pdf,.docx,.doc" @change="onFileSelect" />
              <div class="flex flex-col items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-slate-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p class="text-sm text-slate-600">点击或拖拽文件到此处</p>
                <p class="text-xs text-slate-400 mt-1">支持自动判断模式</p>
              </div>
            </div>

            <!-- File List -->
            <ul v-if="files.length > 0" class="mt-4 space-y-2">
              <li v-for="(file, index) in files" :key="index" class="flex items-center justify-between p-2 bg-slate-50 rounded text-sm group">
                <span class="truncate max-w-[200px] text-slate-700">{{ file.name }}</span>
                <button @click.stop="removeFile(index)" class="text-slate-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                </button>
              </li>
            </ul>
          </div>

          <!-- Options -->
          <div class="space-y-4 pt-4 border-t">
            <h3 class="text-sm font-semibold text-slate-900">生成参数</h3>
            
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-medium text-slate-600 mb-1">主播姓名</label>
                <input v-model="options.speaker_name" type="text" class="w-full text-sm border-slate-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500" />
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-600 mb-1">所属机构</label>
                <input v-model="options.speaker_affiliation" type="text" class="w-full text-sm border-slate-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500" />
              </div>
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-600 mb-1">话题提示 (可选)</label>
              <input v-model="options.topic_hint" type="text" placeholder="例如：经济政策、科技创新..." class="w-full text-sm border-slate-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500" />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-medium text-slate-600 mb-1">目标时长 (秒)</label>
                <input v-model.number="options.duration_target_sec" type="number" class="w-full text-sm border-slate-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500" />
              </div>
              <div class="flex items-center pt-5">
                <input v-model="options.include_figure_placeholders" type="checkbox" id="fig" class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded" />
                <label for="fig" class="ml-2 block text-xs text-slate-600">包含图表占位</label>
              </div>
            </div>
          </div>

          <!-- Action -->
          <button 
            @click="generateContent" 
            :disabled="isGenerating || files.length === 0"
            class="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <span v-if="isGenerating" class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              生成中...
            </span>
            <span v-else>立即生成内容</span>
          </button>
          
          <p v-if="error" class="text-sm text-red-600 text-center">{{ error }}</p>

        </div>
      </div>

      <!-- Right Panel: Result -->
      <div class="flex-1 bg-slate-50 flex flex-col h-full overflow-hidden">
        
        <!-- PROGRESS SCREEN -->
        <div v-if="isGenerating" class="h-full flex flex-col items-center justify-center p-10">
          <div class="bg-white p-8 rounded-2xl shadow-xl w-full max-w-2xl">
            <div class="flex items-center gap-4 mb-6">
               <div class="p-3 bg-indigo-100 rounded-lg">
                 <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                   <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                 </svg>
               </div>
               <div>
                 <h3 class="text-xl font-bold text-slate-800">CBIT 智能分析系统</h3>
                 <p class="text-sm text-slate-500">基于大语言模型的深度语义理解，结合多重证据校验机制，确保零幻觉、高精度的学术文章摘要提取。</p>
               </div>
            </div>

            <!-- Progress Bar with Gradient (参考文章提取样式) -->
            <div class="space-y-2 mb-6">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-semibold text-slate-700">{{ currentStep }}</span>
                <span class="text-sm font-bold text-indigo-600">{{ progress }}%</span>
              </div>
              <div class="w-full bg-slate-200 rounded-full h-3 overflow-hidden shadow-inner">
                <div 
                  class="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-full transition-all duration-500 ease-out relative overflow-hidden"
                  :style="{ width: progress + '%' }"
                >
                  <!-- 动画光效 -->
                  <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-shimmer"></div>
                </div>
              </div>
            </div>

            <!-- Status Card -->
            <div class="bg-gradient-to-br from-indigo-50 to-purple-50 p-4 rounded-xl border border-indigo-200 mb-4">
              <div class="flex items-start gap-3">
                <div class="flex-shrink-0">
                  <svg class="animate-spin h-5 w-5 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </div>
                <div class="flex-1">
                  <p class="text-sm text-indigo-900 font-medium">{{ currentStep }}</p>
                  <p class="text-xs text-indigo-600 mt-1">正在处理中，请稍候...</p>
                </div>
              </div>
              
              <!-- Stage Indicators -->
              <div class="mt-4 flex items-center gap-2 flex-wrap">
                <span 
                  v-for="(step, idx) in progressSteps.slice(0, 5)" 
                  :key="idx"
                  :class="[
                    'text-xs px-2 py-1 rounded-full transition-all duration-300',
                    progress >= (idx + 1) * 11 
                      ? 'bg-indigo-600 text-white font-semibold' 
                      : 'bg-slate-200 text-slate-500'
                  ]"
                >
                  {{ step.split('与')[0] }}
                </span>
              </div>
            </div>

          </div>
        </div>

        <!-- RESULT SCREEN -->
        <div v-else-if="result" class="h-full flex flex-col">
          <!-- Result Header -->
          <div class="bg-white border-b px-6 py-3 flex items-center justify-between shadow-sm">
            <div class="flex items-center gap-4">
              <div>
                <span class="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800 mr-2">
                  {{ modeLabel }}
                </span>
                <span class="text-sm text-slate-500">耗时 {{ result.processing_time }}s</span>
                <span v-if="result.api_version" class="ml-2 text-xs text-indigo-600 font-medium border border-indigo-200 rounded px-2 py-0.5">{{ result.api_version }}</span>
              </div>
            </div>
            <a 
              :href="downloadUrl" 
              class="inline-flex items-center px-3 py-1.5 border border-indigo-600 text-indigo-600 text-sm font-medium rounded-md hover:bg-indigo-50 focus:outline-none"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
              下载 DOCX
            </a>
          </div>

          <!-- Content Viewer -->
          <div class="flex-1 overflow-y-auto p-8 font-sans leading-relaxed text-slate-800 max-w-5xl mx-auto w-full">
            
            <h1 v-if="result.title" class="text-3xl font-bold mb-8 text-slate-900">{{ result.title }}</h1>
            
            <!-- Chinese & English Summaries -->
            <div v-if="result.summary_zh || result.summary_en" class="mb-10 space-y-6">
              <!-- Chinese Summary -->
              <div v-if="result.summary_zh" class="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-200">
                <div class="flex items-center gap-2 mb-3">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-600" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                  </svg>
                  <h3 class="text-lg font-bold text-blue-900">中文摘要</h3>
                </div>
                <p class="text-slate-800 leading-relaxed whitespace-pre-wrap">{{ result.summary_zh }}</p>
              </div>
              
              <!-- English Summary -->
              <div v-if="result.summary_en" class="bg-gradient-to-br from-purple-50 to-pink-50 p-6 rounded-xl border border-purple-200">
                <div class="flex items-center gap-2 mb-3">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-purple-600" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                  </svg>
                  <h3 class="text-lg font-bold text-purple-900">English Abstract</h3>
                </div>
                <p class="text-slate-800 leading-relaxed whitespace-pre-wrap">{{ result.summary_en }}</p>
              </div>
            </div>

            <!-- Structured Fact Table (if available) -->
            <div v-if="result.structured_fact_table && Object.keys(result.structured_fact_table).length > 0" class="mb-10 bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
               <div class="bg-slate-50 px-6 py-4 border-b border-slate-200">
                 <h3 class="text-lg font-bold text-slate-800">结构化事实表</h3>
               </div>
               <div class="divide-y divide-slate-100">
                 
                 <!-- Author / Affiliation -->
                 <div class="p-6 grid grid-cols-1 md:grid-cols-4 gap-4">
                   <div class="text-sm font-semibold text-slate-500 uppercase tracking-wider">作者/所属机构</div>
                   <div class="md:col-span-3 text-slate-900 font-medium">{{ result.structured_fact_table.author_affiliation || 'N/A' }}</div>
                 </div>

                 <!-- Research Question -->
                 <div class="p-6 grid grid-cols-1 md:grid-cols-4 gap-4 bg-slate-50/50">
                   <div class="text-sm font-semibold text-slate-500 uppercase tracking-wider">研究问题</div>
                   <div class="md:col-span-3 text-slate-900">
                     <!-- 如果是对象格式，展示详细信息 -->
                     <div v-if="typeof result.structured_fact_table.research_question === 'object' && result.structured_fact_table.research_question !== null" class="space-y-2">
                       <div v-if="result.structured_fact_table.research_question.question">
                         <span class="text-xs font-semibold text-indigo-600">研究问题：</span>
                         <p class="text-sm mt-1">{{ result.structured_fact_table.research_question.question }}</p>
                         <p v-if="result.structured_fact_table.research_question.evidence" class="text-xs text-slate-500 italic mt-1 pl-2 border-l-2 border-indigo-200">{{ result.structured_fact_table.research_question.evidence }}</p>
                       </div>
                       <div v-if="result.structured_fact_table.research_question.research_object">
                         <span class="text-xs font-semibold text-indigo-600">研究对象：</span>
                         <p class="text-sm mt-1">{{ result.structured_fact_table.research_question.research_object }}</p>
                       </div>
                       <div v-if="result.structured_fact_table.research_question.data_sample">
                         <span class="text-xs font-semibold text-indigo-600">数据与样本：</span>
                         <p class="text-sm mt-1">{{ result.structured_fact_table.research_question.data_sample }}</p>
                       </div>
                       <div v-if="result.structured_fact_table.research_question.method">
                         <span class="text-xs font-semibold text-indigo-600">研究方法：</span>
                         <p class="text-sm mt-1">{{ result.structured_fact_table.research_question.method }}</p>
                       </div>
                     </div>
                     <!-- 如果是字符串格式，直接显示 -->
                     <span v-else>{{ result.structured_fact_table.research_question || 'N/A' }}</span>
                   </div>
                 </div>

                 <!-- Core Findings -->
                 <div class="p-6 grid grid-cols-1 md:grid-cols-4 gap-4">
                   <div class="text-sm font-semibold text-slate-500 uppercase tracking-wider">核心发现</div>
                   <div class="md:col-span-3 space-y-4">
                     <template v-if="Array.isArray(result.structured_fact_table.core_findings)">
                        <div v-for="(item, idx) in result.structured_fact_table.core_findings" :key="idx" class="bg-amber-50 rounded-lg p-4 border border-amber-100">
                           <div class="text-slate-900 font-semibold mb-2">{{ item.finding }}</div>
                           <div v-if="item.data_points" class="text-sm text-amber-900 bg-amber-100/50 rounded px-2 py-1 mb-2 font-mono">
                             📊 关键数据: {{ item.data_points }}
                           </div>
                           <div v-if="item.source_snippet" class="text-xs text-amber-800/80 italic border-l-2 border-amber-300 pl-2">
                             原文片段: "{{ item.source_snippet }}"
                           </div>
                        </div>
                     </template>
                     <div v-else class="text-slate-500">N/A</div>
                   </div>
                 </div>

                 <!-- Mechanism -->
                 <div class="p-6 grid grid-cols-1 md:grid-cols-4 gap-4 bg-slate-50/50">
                   <div class="text-sm font-semibold text-slate-500 uppercase tracking-wider">机制解释</div>
                   <div class="md:col-span-3 text-slate-900">{{ result.structured_fact_table.mechanism_explanation || 'N/A' }}</div>
                 </div>

               </div>
            </div>

            <!-- Extracted Images -->
            <div v-if="result.images && result.images.length > 0" class="mb-10">
              <h3 class="text-lg font-bold mb-4 text-slate-900 flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                相关图表/配图
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div v-for="(img, idx) in result.images" :key="idx" class="bg-white rounded-xl shadow-sm border border-slate-200 p-2 hover:shadow-md transition-shadow">
                  <img :src="`${props.apiBaseUrl}${img.url}`" class="w-full h-auto rounded-lg object-contain max-h-[400px]" loading="lazy" />
                  <div class="mt-2 text-xs text-center text-slate-500 truncate">{{ img.filename }}</div>
                </div>
              </div>
            </div>

            <!-- AI Voice Broadcast Card -->
            <div class="mb-10 bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
              <div class="bg-gradient-to-r from-indigo-50 to-purple-50 px-6 py-4 border-b border-indigo-100 flex items-center justify-between">
                <div class="flex items-center gap-2">
                   <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                     <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                   </svg>
                   <h3 class="text-lg font-bold text-indigo-900">AI 语音播报</h3>
                </div>
              </div>
              
              <div class="p-8 flex items-center justify-center bg-white">
                 <div v-if="voiceLoading" class="flex items-center gap-2 px-4 py-2 bg-slate-100 rounded-full text-sm text-slate-500">
                   <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                     <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                     <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                   </svg>
                   <span>声音库加载中...</span>
                 </div>
                 
                 <div v-else-if="voiceError" class="flex items-center gap-2 px-4 py-2 bg-red-50 rounded-full text-sm text-red-600 border border-red-100">
                   <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                     <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                   </svg>
                   <span>{{ voiceError }}</span>
                 </div>
                 
                 <div v-else-if="voices.length > 0" class="flex flex-wrap items-center gap-6">
                    <!-- Voice Selector -->
                    <div class="flex items-center gap-3 bg-slate-50 px-4 py-2 rounded-lg border border-slate-200">
                       <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                       </svg>
                       <select 
                         v-model="selectedVoiceId" 
                         class="text-sm border-none bg-transparent focus:ring-0 text-slate-700 font-medium min-w-[120px]"
                       >
                         <option :value="null">请选择声音</option>
                         <option v-for="voice in voices" :key="voice.id" :value="voice.id">
                           {{ voice.name }}
                         </option>
                       </select>
                    </div>

                    <!-- Play Button -->
                    <button 
                      @click="selectedVoiceId && playVoicePreview(selectedVoiceId)"
                      :disabled="!selectedVoiceId"
                      class="flex items-center gap-2 px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium shadow-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
                      </svg>
                      播 放
                    </button>

                    <!-- Download Button -->
                    <button 
                      @click="selectedVoiceId && downloadAudio(selectedVoiceId, voices.find(v => v.id === selectedVoiceId)?.name || 'voice')"
                      :disabled="!selectedVoiceId"
                      class="flex items-center gap-2 px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium shadow-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
                      </svg>
                      MP3 下载
                    </button>
                 </div>
                 
                 <div v-else class="text-slate-400 flex items-center gap-2">
                   <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                     <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                   </svg>
                   <span>声音库暂无声音</span>
                 </div>
              </div>
            </div>

            <!-- Note: 完整内容已包含在摘要中，不再重复显示 -->
          </div>
          
          <!-- Footer -->
          <div class="bg-white border-t p-4 shrink-0">
             <div class="flex items-center justify-between text-slate-400 text-sm">
               <div class="flex items-center gap-2">
                 <div class="h-8 w-8 rounded-full bg-slate-200 flex items-center justify-center">
                   <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                     <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                   </svg>
                 </div>
                 <span>{{ options.speaker_name }} ({{ options.speaker_affiliation }})</span>
               </div>
               <div class="flex items-center gap-4">
                 <span class="text-indigo-600/70 text-xs font-medium">Generated with CBIT-Elite v4.2</span>
               </div>
             </div>
          </div>
        </div>

        <div v-else class="h-full flex flex-col items-center justify-center text-slate-400 p-8">
          <div class="text-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <p class="text-lg font-medium text-slate-500">准备就绪</p>
            <p class="text-sm mt-2">在左侧上传文档开始创作</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 进度条光效动画 */
@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.animate-shimmer {
  animation: shimmer 2s infinite;
}
</style>
