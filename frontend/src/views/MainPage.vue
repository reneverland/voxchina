<template>
  <div class="flex h-screen w-full bg-slate-50 font-sans text-slate-800">
    <!-- Sidebar Navigation -->
    <aside class="w-20 lg:w-64 flex-shrink-0 bg-white/80 backdrop-blur-md border-r border-slate-100 flex flex-col justify-between transition-all duration-300 z-10">
      <!-- Logo Section -->
      <div class="h-20 flex items-center justify-center lg:justify-start lg:px-6 border-b border-slate-50">
        <img src="/voxchinalogo2.jpg" alt="VoxChina Logo" class="h-10 w-10 rounded-xl shadow-sm object-cover" />
        <span class="ml-3 font-semibold text-lg tracking-tight hidden lg:block bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">VoxChina</span>
      </div>

      <!-- Navigation Links -->
      <nav class="flex-1 py-8 px-2 space-y-2">
        <a 
          v-for="item in navItems" 
          :key="item.name"
          href="#"
          @click.prevent="setActiveTab(item.id)"
          :class="[
            'flex items-center px-4 py-3 rounded-xl transition-all duration-200 group',
            activeTab === item.id 
              ? 'bg-blue-50 text-blue-600 shadow-sm shadow-blue-100/50 translate-x-1' 
              : 'text-slate-500 hover:bg-slate-50 hover:text-slate-700 hover:shadow-sm'
          ]"
        >
          <component 
            :is="item.icon" 
            :class="[
              'w-5 h-5 transition-transform duration-300',
              activeTab === item.id ? 'scale-110' : 'group-hover:scale-110'
            ]" 
          />
          <span class="ml-3 font-medium hidden lg:block">{{ item.name }}</span>
          
          <!-- Active Indicator -->
          <div 
            v-if="activeTab === item.id"
            class="absolute left-0 w-1 h-8 bg-blue-500 rounded-r-full lg:hidden"
          ></div>
        </a>
      </nav>

      <!-- User Profile / Settings (Bottom Sidebar) -->
      <div class="p-4 border-t border-slate-50">
        <div 
          class="flex items-center justify-center lg:justify-start px-2 py-2 rounded-xl hover:bg-slate-50 cursor-pointer transition-colors"
          @click="handleLogout"
          title="Click to Logout"
        >
          <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-100 to-purple-100 flex items-center justify-center text-blue-600 font-bold text-xs shadow-inner">
            {{ userInitials }}
          </div>
          <div class="ml-3 hidden lg:block overflow-hidden">
            <p class="text-sm font-medium text-slate-700 truncate">{{ userDisplayName }}</p>
            <p class="text-xs text-slate-400">Log Out</p>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Workspace -->
    <main class="flex-1 flex flex-col overflow-hidden relative">
      <!-- Background Elements -->
      <div class="absolute top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
        <div class="absolute -top-[10%] -right-[5%] w-[40%] h-[40%] bg-blue-50/50 rounded-full blur-3xl opacity-60"></div>
        <div class="absolute top-[20%] left-[10%] w-[30%] h-[30%] bg-purple-50/30 rounded-full blur-3xl opacity-60"></div>
      </div>

      <!-- Header -->
      <header class="h-20 flex items-center justify-between px-8 bg-white/40 backdrop-blur-sm sticky top-0 z-10">
        <div>
          <h1 class="text-2xl font-light text-slate-800 tracking-tight">{{ activeItem?.name }}</h1>
          <p class="text-xs text-slate-400 mt-1">AI Workbench / {{ activeItem?.name }}</p>
        </div>
        <div class="flex items-center space-x-4">
          <!-- Language Switcher -->
          <button 
            @click="toggleLanguage"
            class="p-2 text-slate-400 hover:text-slate-600 transition-colors bg-white rounded-full shadow-sm border border-slate-100"
            :title="currentLanguage === 'en' ? 'Switch to Chinese' : '切换到英文'"
          >
            <Languages class="w-5 h-5" />
          </button>
          <button 
            @click="llmSettingsOpen = true"
            class="p-2 text-slate-400 hover:text-slate-600 transition-colors bg-white rounded-full shadow-sm border border-slate-100"
            :title="t('settings')"
          >
            <Settings class="w-5 h-5" />
          </button>
          <button class="p-2 text-slate-400 hover:text-slate-600 transition-colors bg-white rounded-full shadow-sm border border-slate-100">
            <Bell class="w-5 h-5" />
          </button>
          <button class="px-4 py-2 bg-slate-900 text-white text-sm font-medium rounded-lg shadow-lg shadow-slate-200/50 hover:bg-slate-800 transition-all hover:-translate-y-0.5 active:translate-y-0">
            {{ t('export') }}
          </button>
        </div>
      </header>

      <!-- Content Area -->
      <div class="flex-1 overflow-y-auto p-8">
        <div class="max-w-6xl mx-auto w-full">
          
          <!-- Dynamic Content based on active tab -->
          <div class="bg-white rounded-2xl shadow-xl shadow-slate-200/40 border border-slate-100 min-h-[600px] p-8 transition-all duration-300 animate-in fade-in slide-in-from-bottom-4">
            
            <!-- Voice Library Content -->
            <div v-if="activeTab === 'voices'" class="h-full flex flex-col">
              <div class="mb-8 border-b border-slate-50 pb-6 flex justify-between items-end">
                <div>
                  <h2 class="text-xl font-medium text-slate-700 mb-2">Voice Library</h2>
                  <p class="text-slate-500 font-light">
                    Manage your cloned voices and upload new samples for synthesis.
                  </p>
                </div>
              </div>

              <!-- Voice Library Layout -->
              <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                
                <!-- Upload / Clone Section -->
                <div class="lg:col-span-1 space-y-6">
                  <div class="bg-slate-50/50 rounded-xl border border-slate-100 p-6">
                    <h3 class="text-md font-semibold text-slate-800 mb-4 flex items-center">
                      <div class="p-1.5 bg-indigo-100 text-indigo-600 rounded-lg mr-2">
                        <Mic class="w-4 h-4" />
                      </div>
                      Clone New Voice
                    </h3>
                    
                    <div class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-slate-600 mb-1.5">Voice Name</label>
                        <input 
                          v-model="uploadVoiceName"
                          type="text" 
                          placeholder="e.g. My Narrator Voice"
                          class="w-full rounded-lg border-slate-200 bg-white text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                        />
                      </div>
                      
                      <div>
                        <label class="block text-sm font-medium text-slate-600 mb-1.5">Reference Audio</label>
                        <div class="relative group">
                          <input 
                            type="file" 
                            id="voice-upload"
                            @change="handleFileUpload"
                            accept="audio/*"
                            class="hidden"
                          />
                          <label 
                            for="voice-upload"
                            @dragover.prevent="isDraggingVoice = true"
                            @dragleave.prevent="isDraggingVoice = false"
                            @drop.prevent="onVoiceDrop"
                            :class="[
                              'flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer transition-all',
                              isDraggingVoice ? 'border-indigo-500 bg-indigo-50' : 'border-slate-300 bg-white hover:bg-slate-50 hover:border-indigo-400'
                            ]"
                          >
                            <div v-if="!uploadVoiceFile" class="flex flex-col items-center justify-center pt-5 pb-6">
                              <Upload class="w-8 h-8 text-slate-300 mb-2 group-hover:text-indigo-400 transition-colors" />
                              <p class="text-xs text-slate-500">Click to upload audio sample</p>
                              <p class="text-[10px] text-slate-400 mt-1">MP3, WAV (10-30s recommended)</p>
                            </div>
                            <div v-else class="flex flex-col items-center justify-center pt-5 pb-6 px-4 text-center">
                              <div class="w-8 h-8 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-2">
                                <Mic class="w-4 h-4" />
                              </div>
                              <p class="text-sm text-slate-700 font-medium truncate w-full max-w-[180px]">{{ uploadVoiceFile.name }}</p>
                              <p class="text-xs text-green-600 mt-1">Ready to clone</p>
                            </div>
                          </label>
                        </div>
                      </div>

                      <button 
                        @click="uploadVoice"
                        :disabled="!uploadVoiceName || !uploadVoiceFile || voiceUploading"
                        class="w-full py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-medium shadow-lg shadow-indigo-200 hover:bg-indigo-700 hover:shadow-indigo-300 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center"
                      >
                        <Loader2 v-if="voiceUploading" class="w-4 h-4 mr-2 animate-spin" />
                        {{ voiceUploading ? 'Cloning... (this may take a minute)' : 'Start Cloning' }}
                      </button>
                      
                      <p v-if="uploadError" class="text-xs text-red-500 text-center">{{ uploadError }}</p>
                    </div>
                  </div>
                  
                  <!-- Text to Speech Section -->
                  <div class="bg-gradient-to-br from-green-50/50 to-emerald-50/50 rounded-xl border border-green-100 p-6">
                    <h3 class="text-md font-semibold text-slate-800 mb-4 flex items-center">
                      <div class="p-1.5 bg-green-100 text-green-600 rounded-lg mr-2">
                        <Volume2 class="w-4 h-4" />
                      </div>
                      {{ currentLanguage === 'zh' ? '文本转语音' : 'Text to Speech' }}
                    </h3>
                    
                    <div class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-slate-600 mb-1.5">
                          {{ currentLanguage === 'zh' ? '输入文本' : 'Input Text' }}
                        </label>
                        <textarea 
                          v-model="ttsInputText"
                          :placeholder="currentLanguage === 'zh' ? '输入您想要转换为语音的文本内容...' : 'Enter the text you want to convert to speech...'"
                          class="w-full rounded-lg border-slate-200 bg-white text-sm focus:ring-2 focus:ring-green-500/20 focus:border-green-500 transition-all resize-none"
                          rows="4"
                        ></textarea>
                        <div class="text-xs text-slate-400 mt-1 text-right">
                          {{ ttsInputText.length }} {{ currentLanguage === 'zh' ? '字符' : 'characters' }}
                        </div>
                      </div>
                      
                      <div>
                        <label class="block text-xs font-medium text-slate-500 mb-1">
                          {{ currentLanguage === 'zh' ? '选择声音' : 'Select Voice' }}
                        </label>
                        <select 
                          v-model="ttsSelectedVoiceId"
                          class="w-full rounded-lg border-slate-200 bg-white text-sm focus:ring-2 focus:ring-green-500/20 focus:border-green-500"
                        >
                          <option value="">{{ currentLanguage === 'zh' ? '-- 请选择声音 --' : '-- Select a voice --' }}</option>
                          <option v-for="voice in voices" :key="voice.id" :value="voice.id">
                            {{ voice.name }}
                          </option>
                        </select>
                        <p v-if="voices.length === 0" class="text-xs text-amber-600 mt-1">
                          {{ currentLanguage === 'zh' ? '请先克隆一个声音' : 'Please clone a voice first' }}
                        </p>
                      </div>

                      <button 
                        @click="generateTTSAudio"
                        :disabled="!ttsInputText.trim() || !ttsSelectedVoiceId || generatingTTSAudio"
                        class="w-full py-2.5 bg-green-500 text-white rounded-lg text-sm font-medium shadow-lg shadow-green-200 hover:bg-green-600 hover:shadow-green-300 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center"
                      >
                        <Loader2 v-if="generatingTTSAudio" class="w-4 h-4 mr-2 animate-spin" />
                        {{ generatingTTSAudio ? (currentLanguage === 'zh' ? '生成中...' : 'Generating...') : (currentLanguage === 'zh' ? '生成语音' : 'Generate Audio') }}
                      </button>
                    </div>
                    
                    <!-- Generated Audio Result -->
                    <div v-if="ttsGeneratedAudioUrl" class="mt-4 p-4 bg-white rounded-lg border border-green-200">
                      <div class="flex items-center justify-between mb-3">
                        <span class="text-sm font-medium text-slate-700">
                          {{ currentLanguage === 'zh' ? '生成的音频' : 'Generated Audio' }}
                        </span>
                        <button
                          @click="downloadTTSAudio"
                          class="px-3 py-1.5 bg-green-100 hover:bg-green-200 text-green-700 text-xs rounded-lg transition-colors flex items-center"
                        >
                          📥 {{ currentLanguage === 'zh' ? '下载' : 'Download' }}
                        </button>
                      </div>
                      <audio 
                        :src="ttsGeneratedAudioUrl" 
                        controls 
                        class="w-full"
                        style="height: 40px;"
                      ></audio>
                    </div>
                  </div>
                </div>

                <!-- Library List Section -->
                <div class="lg:col-span-2">
                  <h3 class="text-md font-semibold text-slate-800 mb-4 flex items-center justify-between">
                    <span class="flex items-center">
                      <div class="p-1.5 bg-purple-100 text-purple-600 rounded-lg mr-2">
                         <LayoutGrid class="w-4 h-4" />
                      </div>
                      My Voices
                    </span>
                    <span class="text-xs font-normal text-slate-400 bg-slate-100 px-2 py-1 rounded-full">{{ voices.length }} voices</span>
                  </h3>

                  <div v-if="voices.length === 0" class="text-center py-16 bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
                    <div class="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-3">
                       <Mic class="w-6 h-6 text-slate-300" />
                    </div>
                    <p class="text-slate-500 font-medium">No voices yet</p>
                    <p class="text-xs text-slate-400 mt-1">Upload a sample to create your first voice clone.</p>
                  </div>

                  <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div 
                      v-for="voice in voices" 
                      :key="voice.id" 
                      class="group bg-white border border-slate-100 rounded-xl p-4 hover:border-indigo-200 hover:shadow-md transition-all relative overflow-hidden"
                    >
                      <div class="flex justify-between items-start mb-3">
                        <div class="flex items-center">
                          <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-50 to-purple-50 flex items-center justify-center text-indigo-600 mr-3 border border-indigo-100/50">
                             <Volume2 class="w-5 h-5" />
                          </div>
                          <div>
                            <h4 class="font-semibold text-slate-800 text-sm">{{ voice.name }}</h4>
                            <p class="text-[10px] text-slate-400">ID: {{ voice.id.slice(0, 8) }}...</p>
                          </div>
                        </div>
                        <button 
                          @click="deleteVoice(voice.id)"
                          class="text-slate-300 hover:text-red-500 transition-colors p-1"
                          title="Delete Voice"
                        >
                          <Trash2 class="w-4 h-4" />
                        </button>
                      </div>

                      <div class="mt-4 space-y-2">
                         <!-- Generate Preview Button -->
                         <button 
                            @click="previewVoice(voice.id)"
                            :disabled="previewLoading === voice.id"
                            class="w-full py-1.5 bg-slate-50 hover:bg-slate-100 text-slate-600 text-xs font-medium rounded-lg border border-slate-200 transition-colors flex items-center justify-center"
                         >
                            <Loader2 v-if="previewLoading === voice.id" class="w-3.5 h-3.5 mr-1.5 animate-spin" />
                            <Play v-else class="w-3.5 h-3.5 mr-1.5 fill-current" />
                            {{ previewLoading === voice.id ? 'Generating...' : 'Generate Preview' }}
                         </button>
                         
                         <!-- Audio Player (显示音频控制器，无自动播放) -->
                         <audio 
                           v-if="previewAudioUrl[voice.id]" 
                           :src="previewAudioUrl[voice.id]" 
                           controls 
                           class="w-full"
                           @ended="previewLoading = null"
                           style="height: 32px;"
                         ></audio>
                      </div>
                    </div>
                  </div>
                </div>

              </div>
            </div>

            <!-- Academic Extract Content -->
            <div v-else-if="activeTab === 'academic'" class="h-full flex flex-col">
              <div class="mb-8 border-b border-slate-50 pb-6">
                <h2 class="text-xl font-medium text-slate-700 mb-2">{{ t('academicExtract') }}</h2>
                <p class="text-slate-500 font-light">
                  {{ currentLanguage === 'en' ? 'Upload academic papers (DOCX/PDF) to generate zero-hallucination, evidence-traceable bilingual summaries and structured fact tables.' : '上传学术论文（DOCX/PDF），生成零幻觉、证据可追溯的中英文摘要与结构化事实表。' }}
                </p>
              </div>

              <!-- Academic Extract Layout -->
              <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                
                <!-- Left: Upload Section -->
                <div class="lg:col-span-1 space-y-6">
                  <div class="bg-slate-50/50 rounded-xl border border-slate-100 p-6">
                    <h3 class="text-md font-semibold text-slate-800 mb-4 flex items-center">
                      <div class="p-1.5 bg-indigo-100 text-indigo-600 rounded-lg mr-2">
                        <FileText class="w-4 h-4" />
                      </div>
                      {{ t('uploadDocument') }}
                    </h3>
                    
                    <div class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-slate-600 mb-1.5">Select File</label>
                        <div class="relative group">
                          <input 
                            type="file" 
                            id="academic-upload"
                            @change="handleAcademicUpload"
                            accept=".docx,.doc,.pdf"
                            class="hidden"
                          />
                          <label 
                            for="academic-upload"
                            @dragover.prevent="isDraggingAcademic = true"
                            @dragleave.prevent="isDraggingAcademic = false"
                            @drop.prevent="onAcademicDrop"
                            :class="[
                              'flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer transition-all',
                              isDraggingAcademic ? 'border-indigo-500 bg-indigo-50' : 'border-slate-300 bg-white hover:bg-slate-50 hover:border-indigo-400'
                            ]"
                          >
                            <div v-if="!academicFile" class="flex flex-col items-center justify-center pt-5 pb-6">
                              <Upload class="w-8 h-8 text-slate-300 mb-2 group-hover:text-indigo-400 transition-colors" />
                              <p class="text-xs text-slate-500">Click to upload academic paper</p>
                              <p class="text-[10px] text-slate-400 mt-1">DOCX, DOC, PDF (Recommended < 10MB)</p>
                            </div>
                            <div v-else class="flex flex-col items-center justify-center pt-5 pb-6 px-4 text-center">
                              <div class="w-8 h-8 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-2">
                                <FileText class="w-4 h-4" />
                              </div>
                              <p class="text-sm text-slate-700 font-medium truncate w-full max-w-[180px]">{{ academicFile.name }}</p>
                              <p class="text-xs text-green-600 mt-1">Ready to Extract</p>
                            </div>
                          </label>
                        </div>
                      </div>

                      <button 
                        type="button"
                        @click="startAcademicExtraction"
                        :disabled="!academicFile || academicExtracting"
                        class="w-full py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-medium shadow-lg shadow-indigo-200 hover:bg-indigo-700 hover:shadow-indigo-300 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center"
                      >
                        <Loader2 v-if="academicExtracting" class="w-4 h-4 mr-2 animate-spin" />
                        {{ academicExtracting ? t('extracting') : t('startExtraction') }}
                      </button>

                      <!-- Progress Display -->
                      <div v-if="academicExtracting && currentStep" class="mt-4 p-4 bg-indigo-50 rounded-lg border border-indigo-100">
                        <div class="flex items-center mb-2">
                          <Loader2 class="w-4 h-4 text-indigo-600 animate-spin mr-2" />
                          <span class="text-sm font-medium text-indigo-900">{{ currentStep }}</span>
                        </div>
                        <div class="w-full bg-indigo-200 rounded-full h-2">
                          <div 
                            class="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                            :style="{ width: `${academicProgress}%` }"
                          ></div>
                        </div>
                        <p class="text-xs text-indigo-600 mt-1">{{ academicProgress }}%</p>
                      </div>
                      
                      <p v-if="academicError" class="text-xs text-red-500 text-center">{{ academicError }}</p>
                    </div>
                  </div>
                </div>

                <!-- Right: Result Display -->
                <div class="lg:col-span-2">
                  <div v-if="academicResult" class="bg-white rounded-xl border border-slate-100 p-6">
                    <div class="flex items-center justify-between mb-4">
                      <h3 class="text-md font-semibold text-slate-800 flex items-center">
                        <div class="p-1.5 bg-green-100 text-green-600 rounded-lg mr-2">
                          <FileText class="w-4 h-4" />
                        </div>
                        {{ t('extractionCompleted') }}
                      </h3>
                      <div class="flex space-x-2">
                        <button 
                          @click="saveAcademicToKB"
                          :disabled="isSavingAcademicToKB"
                          class="px-3 py-1.5 bg-green-100 hover:bg-green-200 text-green-700 text-xs font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <span v-if="isSavingAcademicToKB">⏳ {{ currentLanguage === 'zh' ? '保存中...' : 'Saving...' }}</span>
                          <span v-else>💾 {{ currentLanguage === 'zh' ? '存入知识库' : 'Save to KB' }}</span>
                        </button>
                        <button 
                          @click="copyAcademicResult"
                          class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-600 text-xs font-medium rounded-lg transition-colors"
                        >
                          {{ t('copyAll') }}
                        </button>
                        <button 
                          @click="downloadAcademicResult"
                          class="px-3 py-1.5 bg-indigo-100 hover:bg-indigo-200 text-indigo-600 text-xs font-medium rounded-lg transition-colors"
                        >
                          📄 TXT
                        </button>
                        <button 
                          @click="downloadAcademicWord"
                          class="px-3 py-1.5 bg-blue-100 hover:bg-blue-200 text-blue-600 text-xs font-medium rounded-lg transition-colors"
                        >
                          📄 Word
                        </button>
                      </div>
                    </div>

                    <!-- Recommended Tags with Selection -->
                    <div class="mb-4 p-3 bg-amber-50 rounded-lg border border-amber-200">
                      <div class="flex items-center justify-between mb-2">
                        <span class="text-sm font-medium text-amber-800 flex items-center">
                          <Tag class="w-4 h-4 mr-1.5" />
                          {{ currentLanguage === 'zh' ? '标签管理' : 'Tag Management' }}
                        </span>
                        <button
                          v-if="academicRecommendedTags.length === 0"
                          @click="fetchAcademicRecommendedTags"
                          :disabled="loadingAcademicTags"
                          class="text-xs text-amber-600 hover:text-amber-700 flex items-center"
                        >
                          <Loader2 v-if="loadingAcademicTags" class="w-3 h-3 mr-1 animate-spin" />
                          <RefreshCw v-else class="w-3 h-3 mr-1" />
                          {{ loadingAcademicTags ? (currentLanguage === 'zh' ? '生成中...' : 'Generating...') : (currentLanguage === 'zh' ? '生成推荐标签' : 'Generate Tags') }}
                        </button>
                        <button
                          v-else
                          @click="fetchAcademicRecommendedTags"
                          :disabled="loadingAcademicTags"
                          class="text-xs text-amber-600 hover:text-amber-700 flex items-center"
                        >
                          <RefreshCw class="w-3 h-3 mr-1" :class="{ 'animate-spin': loadingAcademicTags }" />
                          {{ currentLanguage === 'zh' ? '重新生成' : 'Regenerate' }}
                        </button>
                      </div>
                      
                      <!-- Selected Tags -->
                      <div v-if="academicSelectedTags.length > 0" class="mb-2">
                        <div class="text-xs text-amber-700 mb-1">{{ currentLanguage === 'zh' ? '已选标签:' : 'Selected:' }}</div>
                        <div class="flex flex-wrap gap-1.5">
                          <span 
                            v-for="tag in academicSelectedTags" 
                            :key="tag"
                            class="px-2 py-0.5 bg-green-100 text-green-800 text-xs rounded-full flex items-center cursor-pointer hover:bg-green-200"
                            @click="toggleAcademicTag(tag)"
                          >
                            {{ tag }}
                            <X class="w-3 h-3 ml-1" />
                          </span>
                        </div>
                      </div>
                      
                      <!-- Recommended Tags (clickable to select) -->
                      <div v-if="academicRecommendedTags.length > 0" class="mb-2">
                        <div class="text-xs text-amber-700 mb-1">{{ currentLanguage === 'zh' ? '推荐标签 (点击选择):' : 'Recommended (click to select):' }}</div>
                        <div class="flex flex-wrap gap-1.5">
                          <span 
                            v-for="tag in academicRecommendedTags.filter(t => !academicSelectedTags.includes(t))" 
                            :key="tag"
                            class="px-2 py-0.5 bg-amber-100 text-amber-800 text-xs rounded-full cursor-pointer hover:bg-amber-200 transition-colors"
                            @click="toggleAcademicTag(tag)"
                          >
                            + {{ tag }}
                          </span>
                        </div>
                      </div>
                      
                      <!-- Custom Tag Input -->
                      <div class="flex items-center gap-2 mt-2">
                        <input
                          v-model="academicCustomTag"
                          type="text"
                          :placeholder="currentLanguage === 'zh' ? '输入自定义标签...' : 'Enter custom tag...'"
                          class="flex-1 px-2 py-1 text-xs border border-amber-300 rounded focus:outline-none focus:ring-1 focus:ring-amber-500"
                          @keyup.enter="addAcademicCustomTag"
                        />
                        <button
                          @click="addAcademicCustomTag"
                          :disabled="!academicCustomTag.trim()"
                          class="px-2 py-1 text-xs bg-amber-500 text-white rounded hover:bg-amber-600 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {{ currentLanguage === 'zh' ? '添加' : 'Add' }}
                        </button>
                      </div>
                      
                      <p v-if="academicRecommendedTags.length === 0 && academicSelectedTags.length === 0" class="text-xs text-amber-600 mt-2">
                        {{ currentLanguage === 'zh' ? '点击"生成推荐标签"获取推荐，或直接输入自定义标签' : 'Click "Generate Tags" for recommendations, or enter custom tags' }}
                      </p>
                    </div>

                    <!-- Tab Switcher -->
                    <div class="flex space-x-1 mb-4 bg-slate-50 p-1 rounded-lg">
                      <button 
                        @click="academicResultTab = 'summary'"
                        :class="[
                          'flex-1 px-4 py-2 text-sm font-medium rounded-md transition-all',
                          academicResultTab === 'summary' 
                            ? 'bg-white text-indigo-600 shadow-sm' 
                            :                           'text-slate-500 hover:text-slate-700'
                        ]"
                      >
                        {{ t('summaryView') }}
                      </button>
                      <button 
                        @click="academicResultTab = 'facttable'"
                        :class="[
                          'flex-1 px-4 py-2 text-sm font-medium rounded-md transition-all',
                          academicResultTab === 'facttable' 
                            ? 'bg-white text-indigo-600 shadow-sm' 
                            : 'text-slate-500 hover:text-slate-700'
                        ]"
                      >
                        {{ t('factTableView') }}
                      </button>
                    </div>

                    <!-- Summary View -->
                    <div v-if="academicResultTab === 'summary'" class="space-y-4">
                      <!-- 编辑按钮 -->
                      <div class="flex justify-end space-x-2">
                        <button
                          v-if="!isEditingAcademicSummary"
                          @click="startEditAcademicSummary"
                          class="px-3 py-1.5 text-sm bg-amber-500 hover:bg-amber-600 text-white rounded-lg transition-colors font-medium"
                        >
                          ✏️ {{ currentLanguage === 'zh' ? '编辑' : 'Edit' }}
                        </button>
                        <template v-else>
                          <button
                            @click="saveEditAcademicSummary"
                            class="px-3 py-1.5 text-sm bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors font-medium"
                          >
                            ✅ {{ currentLanguage === 'zh' ? '保存' : 'Save' }}
                          </button>
                          <button
                            @click="cancelEditAcademicSummary"
                            class="px-3 py-1.5 text-sm bg-slate-400 hover:bg-slate-500 text-white rounded-lg transition-colors font-medium"
                          >
                            ❌ {{ currentLanguage === 'zh' ? '取消' : 'Cancel' }}
                          </button>
                        </template>
                      </div>
                      
                      <div class="border border-slate-100 rounded-lg overflow-hidden">
                        <div class="bg-slate-50 px-4 py-2 border-b border-slate-100">
                          <h4 class="text-sm font-semibold text-slate-700">{{ t('chineseSummary') }}</h4>
                        </div>
                        <div class="p-4 bg-white">
                          <textarea
                            v-if="isEditingAcademicSummary"
                            v-model="editedAcademicSummaryZh"
                            class="w-full h-32 p-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 text-sm resize-y"
                            :placeholder="currentLanguage === 'zh' ? '编辑中文摘要...' : 'Edit Chinese summary...'"
                          ></textarea>
                          <p v-else class="text-slate-700 leading-relaxed text-sm">{{ academicResult.summary_zh }}</p>
                        </div>
                      </div>

                      <div class="border border-slate-100 rounded-lg overflow-hidden">
                        <div class="bg-slate-50 px-4 py-2 border-b border-slate-100">
                          <h4 class="text-sm font-semibold text-slate-700">{{ t('englishSummary') }}</h4>
                        </div>
                        <div class="p-4 bg-white">
                          <textarea
                            v-if="isEditingAcademicSummary"
                            v-model="editedAcademicSummaryEn"
                            class="w-full h-32 p-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 text-sm resize-y"
                            :placeholder="currentLanguage === 'zh' ? '编辑英文摘要...' : 'Edit English summary...'"
                          ></textarea>
                          <p v-else class="text-slate-700 leading-relaxed text-sm">{{ academicResult.summary_en }}</p>
                        </div>
                      </div>
                    </div>

                    <!-- Fact Table View -->
                    <div v-if="academicResultTab === 'facttable'" class="space-y-6">
                      <!-- Basic Info -->
                      <div>
                        <h3 class="text-md font-semibold text-slate-800 mb-3">{{ t('basicInformation') }}</h3>
                        <div class="space-y-3">
                          <!-- Authors -->
                          <div v-if="academicResult.fact_table.basic_info?.authors">
                            <p class="text-xs text-slate-500 mb-1">Authors & Affiliation</p>
                            <div class="space-y-1">
                              <div 
                                v-for="(author, idx) in academicResult.fact_table.basic_info.authors" 
                                :key="idx"
                                class="text-sm text-slate-700"
                              >
                                <span class="font-medium">{{ author.name }}</span>
                                <span v-if="author.affiliation" class="text-slate-500"> ({{ author.affiliation }})</span>
                                <span v-if="author.evidence" class="text-xs text-indigo-600 ml-2">[{{ author.evidence }}]</span>
                              </div>
                            </div>
                          </div>

                          <!-- Research Question -->
                          <div v-if="academicResult.fact_table.basic_info?.research_question">
                            <p class="text-xs text-slate-500 mb-1">Research Question</p>
                            <p class="text-sm text-slate-700">
                              {{ academicResult.fact_table.basic_info.research_question.question }}
                              <span v-if="academicResult.fact_table.basic_info.research_question.evidence" class="text-xs text-indigo-600 ml-2">
                                [{{ academicResult.fact_table.basic_info.research_question.evidence }}]
                              </span>
                            </p>
                          </div>

                          <!-- Research Object -->
                          <div v-if="academicResult.fact_table.basic_info?.research_object">
                            <p class="text-xs text-slate-500 mb-1">Research Object / Scope</p>
                            <p class="text-sm text-slate-700">
                              {{ academicResult.fact_table.basic_info.research_object.description }}
                              <span v-if="academicResult.fact_table.basic_info.research_object.evidence" class="text-xs text-indigo-600 ml-2">
                                [{{ academicResult.fact_table.basic_info.research_object.evidence }}]
                              </span>
                            </p>
                          </div>

                          <!-- Data Sample -->
                          <div v-if="academicResult.fact_table.basic_info?.data_sample">
                            <p class="text-xs text-slate-500 mb-1">Data & Sample</p>
                            <div class="text-sm text-slate-700 space-y-1">
                              <p v-if="academicResult.fact_table.basic_info.data_sample.source">
                                <span class="font-medium">Source:</span> {{ academicResult.fact_table.basic_info.data_sample.source }}
                              </p>
                              <p v-if="academicResult.fact_table.basic_info.data_sample.sample_size">
                                <span class="font-medium">Sample Size:</span> {{ academicResult.fact_table.basic_info.data_sample.sample_size }}
                              </p>
                              <p v-if="academicResult.fact_table.basic_info.data_sample.time_span">
                                <span class="font-medium">Time Span:</span> {{ academicResult.fact_table.basic_info.data_sample.time_span }}
                              </p>
                              <p v-if="academicResult.fact_table.basic_info.data_sample.region">
                                <span class="font-medium">Region:</span> {{ academicResult.fact_table.basic_info.data_sample.region }}
                              </p>
                              <span v-if="academicResult.fact_table.basic_info.data_sample.evidence" class="text-xs text-indigo-600">
                                [{{ academicResult.fact_table.basic_info.data_sample.evidence }}]
                              </span>
                            </div>
                          </div>

                          <!-- Method -->
                          <div v-if="academicResult.fact_table.basic_info?.method">
                            <p class="text-xs text-slate-500 mb-1">Research Method</p>
                            <p class="text-sm text-slate-700">
                              {{ academicResult.fact_table.basic_info.method.description }}
                              <span v-if="academicResult.fact_table.basic_info.method.evidence" class="text-xs text-indigo-600 ml-2">
                                [{{ academicResult.fact_table.basic_info.method.evidence }}]
                              </span>
                            </p>
                          </div>
                        </div>
                      </div>

                      <!-- Key Findings -->
                      <div v-if="academicResult.fact_table.key_findings?.length > 0">
                        <h3 class="text-md font-semibold text-slate-800 mb-3">Key Findings</h3>
                        <div class="space-y-3">
                          <div 
                            v-for="(finding, idx) in academicResult.fact_table.key_findings" 
                            :key="idx"
                            class="p-4 bg-green-50 border border-green-200 rounded-lg"
                          >
                            <p class="text-sm font-medium text-slate-800 mb-2">{{ idx + 1 }}. {{ finding.finding }}</p>
                            <p v-if="finding.quantitative_data" class="text-sm text-green-700 mb-2">
                              <span class="font-medium">Quantitative Data:</span> {{ finding.quantitative_data }}
                            </p>
                            <p v-if="finding.evidence" class="text-xs text-indigo-600">
                              <span class="font-medium">Evidence:</span> {{ finding.evidence }}
                            </p>
                            <div v-if="finding.heterogeneity" class="mt-2 pt-2 border-t border-green-300">
                              <p class="text-xs text-slate-600">
                                <span class="font-medium">Heterogeneity:</span> {{ finding.heterogeneity }}
                              </p>
                              <p v-if="finding.heterogeneity_evidence" class="text-xs text-indigo-600 mt-1">
                                {{ finding.heterogeneity_evidence }}
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>

                      <!-- Mechanisms -->
                      <div v-if="academicResult.fact_table.mechanisms?.length > 0">
                        <h3 class="text-md font-semibold text-slate-800 mb-3">Mechanisms</h3>
                        <div class="space-y-3">
                          <div 
                            v-for="(mechanism, idx) in academicResult.fact_table.mechanisms" 
                            :key="idx"
                            class="p-4 bg-blue-50 border border-blue-200 rounded-lg"
                          >
                            <p class="text-sm text-slate-800 mb-2">{{ mechanism.description }}</p>
                            <p v-if="mechanism.type" class="text-xs text-blue-700 mb-2">
                              <span class="font-medium">Type:</span> {{ mechanism.type }}
                            </p>
                            <p v-if="mechanism.evidence" class="text-xs text-indigo-600">
                              <span class="font-medium">Evidence:</span> {{ mechanism.evidence }}
                            </p>
                          </div>
                        </div>
                      </div>

                      <!-- Policy Implications -->
                      <div v-if="academicResult.fact_table.policy_implications?.length > 0">
                        <h3 class="text-md font-semibold text-slate-800 mb-3">Policy Implications</h3>
                        <div class="space-y-3">
                          <div 
                            v-for="(policy, idx) in academicResult.fact_table.policy_implications" 
                            :key="idx"
                            class="p-4 bg-amber-50 border border-amber-200 rounded-lg"
                          >
                            <p class="text-sm text-slate-800 mb-2">{{ policy.implication }}</p>
                            <p v-if="policy.evidence" class="text-xs text-indigo-600">
                              <span class="font-medium">Evidence:</span> {{ policy.evidence }}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Oral Broadcast Section - Always visible below tabs -->
                    <div class="mt-8 pt-6 border-t border-slate-100">
                      <h4 class="text-sm font-semibold text-slate-700 mb-4 flex items-center">
                        <svg class="w-4 h-4 mr-2 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                        </svg>
                        {{ t('oralBroadcast') }}
                      </h4>
                      
                      <div class="bg-slate-50 rounded-xl p-4 border border-slate-100">
                        <div v-if="voices.length === 0" class="text-center py-4">
                          <p class="text-sm text-slate-500">{{ t('loadingVoices') }}</p>
                        </div>
                        <div v-else class="flex flex-col md:flex-row gap-4 items-end">
                          <div class="flex-1 w-full">
                            <label class="block text-xs font-medium text-slate-500 mb-1">{{ t('selectContent') }}</label>
                            <select v-model="selectedSummaryLang" class="w-full text-sm rounded-lg border-slate-200 focus:border-indigo-500 focus:ring-indigo-500">
                              <option value="zh">{{ t('chineseSummary') }}</option>
                              <option value="en">{{ t('englishSummary') }}</option>
                            </select>
                          </div>
                          
                          <div class="flex-1 w-full">
                            <label class="block text-xs font-medium text-slate-500 mb-1">{{ t('selectVoice') }}</label>
                            <select v-model="selectedVoiceId" class="w-full text-sm rounded-lg border-slate-200 focus:border-indigo-500 focus:ring-indigo-500">
                              <option v-for="voice in voices" :key="voice.id" :value="voice.id">
                                {{ voice.name }}
                              </option>
                            </select>
                          </div>
                          
                          <button 
                            @click="generateAcademicAudio"
                            :disabled="isGeneratingAudio || !selectedVoiceId"
                            class="w-full md:w-auto px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center whitespace-nowrap"
                          >
                            <Loader2 v-if="isGeneratingAudio" class="w-4 h-4 mr-2 animate-spin" />
                            <span v-else class="flex items-center">
                              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              {{ t('generateAndPlay') }}
                            </span>
                          </button>
                        </div>
                        
                        <!-- Player Section -->
                        <div v-if="audioUrl" class="mt-4 pt-4 border-t border-slate-200">
                          <div class="flex items-center gap-4">
                            <audio controls :src="audioUrl" class="flex-1 h-10 w-full"></audio>
                            <a 
                              :href="audioUrl" 
                              :download="`summary_broadcast_${Date.now()}.wav`"
                              class="flex-shrink-0 p-2 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                              :title="t('downloadAudio')"
                            >
                              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                              </svg>
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Empty State -->
                  <div v-else class="bg-slate-50/50 rounded-xl border border-dashed border-slate-200 p-12 text-center">
                    <div class="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-3">
                      <FileText class="w-6 h-6 text-slate-300" />
                    </div>
                    <p class="text-slate-500 font-medium">No results yet</p>
                    <p class="text-xs text-slate-400 mt-1">Upload academic paper and click "Start Extraction"</p>
                  </div>

                  <!-- History Section -->
                  <div class="mt-6 bg-white rounded-xl border border-slate-100 p-6">
                    <div class="flex items-center justify-between mb-4">
                      <h3 class="text-md font-semibold text-slate-800 flex items-center">
                        <div class="p-1.5 bg-purple-100 text-purple-600 rounded-lg mr-2">
                          <LayoutGrid class="w-4 h-4" />
                        </div>
                        {{ t('extractionHistory') }}
                      </h3>
                      <button 
                        @click="fetchAcademicHistory"
                        class="text-xs text-slate-500 hover:text-indigo-600 transition-colors flex items-center"
                      >
                        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                        </svg>
                        {{ t('refresh') }}
                      </button>
                    </div>

                    <!-- Search Bar -->
                    <div class="mb-4">
                      <div class="relative">
                        <input 
                          v-model="academicHistorySearch"
                          @input="searchAcademicHistory"
                          type="text" 
                          placeholder="Search by title or summary..." 
                          class="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                        />
                        <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                          <Search class="w-4 h-4 text-slate-400" />
                        </div>
                      </div>
                    </div>

                    <div v-if="academicHistory.length === 0" class="text-center py-8 text-slate-400 text-sm">
                      {{ academicHistorySearch ? 'No results found' : t('noHistory') }}
                    </div>

                    <div v-else class="space-y-3">
                      <div 
                        v-for="item in academicHistory" 
                        :key="item.id"
                        class="group p-4 bg-slate-50 rounded-lg border border-slate-100 hover:border-indigo-200 transition-all"
                      >
                        <div class="flex items-start justify-between">
                          <div 
                            class="flex-1 cursor-pointer"
                            @click="viewAcademicHistory(item.id)"
                          >
                            <h4 class="text-sm font-medium text-slate-800 group-hover:text-indigo-700 line-clamp-1">
                              {{ item.title || 'Untitled' }}
                            </h4>
                            <p class="text-xs text-slate-500 mt-1 line-clamp-2">
                              {{ item.summary_zh ? item.summary_zh.substring(0, 80) + '...' : 'No summary' }}
                            </p>
                            <p class="text-xs text-slate-400 mt-2">
                              {{ formatDate(item.created_at) }}
                            </p>
                          </div>
                          
                          <!-- Action Buttons -->
                          <div class="ml-3 flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button 
                              @click.stop="confirmDeleteAcademicHistory(item.id, item.title)"
                              class="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                              title="Delete"
                            >
                              <Trash2 class="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Pagination -->
                    <div v-if="academicHistoryTotal > academicHistoryPageSize" class="mt-4 flex items-center justify-between border-t border-slate-100 pt-4">
                      <div class="text-xs text-slate-500">
                        Showing {{ (academicHistoryPage - 1) * academicHistoryPageSize + 1 }} - {{ Math.min(academicHistoryPage * academicHistoryPageSize, academicHistoryTotal) }} of {{ academicHistoryTotal }}
                      </div>
                      <div class="flex items-center gap-2">
                        <button 
                          @click="academicHistoryPage--; fetchAcademicHistory()"
                          :disabled="academicHistoryPage === 1"
                          class="px-3 py-1 text-xs border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                          Previous
                        </button>
                        <div class="flex items-center gap-1">
                          <button 
                            v-for="page in paginationPages(academicHistoryTotal, academicHistoryPageSize, academicHistoryPage)"
                            :key="page"
                            @click="academicHistoryPage = page; fetchAcademicHistory()"
                            :class="[
                              'px-3 py-1 text-xs rounded-lg transition-colors',
                              page === academicHistoryPage 
                                ? 'bg-indigo-600 text-white' 
                                : 'border border-slate-200 hover:bg-slate-50'
                            ]"
                          >
                            {{ page }}
                          </button>
                        </div>
                        <button 
                          @click="academicHistoryPage++; fetchAcademicHistory()"
                          :disabled="academicHistoryPage >= Math.ceil(academicHistoryTotal / academicHistoryPageSize)"
                          class="px-3 py-1 text-xs border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                          Next
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

              </div>
            </div>

            <!-- Knowledge Database Content -->
            <div v-else-if="activeTab === 'knowledge'" class="h-full flex flex-col">
              <div class="mb-8 border-b border-slate-50 pb-6 flex justify-between items-end">
                <div>
                  <h2 class="text-xl font-medium text-slate-700 mb-2">Knowledge Database</h2>
                  <p class="text-slate-500 font-light">
                    Manage your vectorized knowledge assets for retrieval and analysis.
                  </p>
                </div>
                <div class="flex gap-3 items-center">
                  <!-- Upload Article Button -->
                  <button 
                    @click="openUploadArticleDialog"
                    class="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2"
                  >
                    <Upload class="w-4 h-4" />
                    {{ currentLanguage === 'zh' ? '上传文章' : 'Upload Article' }}
                  </button>
                  <!-- Tag Management Button -->
                  <button 
                    @click="showTagManagementDialog = true; fetchTags()"
                    class="p-2 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                    :title="currentLanguage === 'zh' ? '标签管理' : 'Manage Tags'"
                  >
                    <Tag class="w-5 h-5" />
                  </button>
                  <!-- Tag Filter Dropdown -->
                  <select 
                    v-model="selectedTagFilter"
                    @change="filterByTag"
                    class="px-3 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                  >
                    <option value="">{{ currentLanguage === 'zh' ? '所有标签' : 'All Tags' }}</option>
                    <option v-for="tag in availableTags" :key="tag" :value="tag">{{ tag }}</option>
                  </select>
                  <!-- Refresh Button -->
                  <button 
                    @click="fetchKnowledgeDocs"
                    :disabled="knowledgeLoading"
                    class="p-2 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors disabled:opacity-50"
                    title="Refresh"
                  >
                    <RefreshCw :class="['w-5 h-5', knowledgeLoading ? 'animate-spin' : '']" />
                  </button>
                  <!-- Search Bar -->
                  <div class="relative w-64">
                    <input 
                      v-model="knowledgeSearchQuery"
                      @keyup.enter="searchKnowledge"
                      type="text" 
                      placeholder="Search knowledge..." 
                      class="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                    />
                    <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                      <Search class="w-4 h-4 text-slate-400" />
                    </div>
                  </div>
                </div>
              </div>

              <!-- Knowledge List -->
              <div v-if="knowledgeLoading" class="flex-1 flex items-center justify-center">
                <Loader2 class="w-8 h-8 text-indigo-500 animate-spin" />
              </div>

              <div v-else-if="knowledgeDocs.length === 0" class="flex-1 flex flex-col items-center justify-center text-center p-12 bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
                <div class="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-3">
                   <Database class="w-6 h-6 text-slate-300" />
                </div>
                <p class="text-slate-500 font-medium">Database is empty</p>
                <p class="text-xs text-slate-400 mt-1">Extract articles to populate the knowledge base.</p>
              </div>

              <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 overflow-y-auto pb-6">
                <div 
                  v-for="doc in knowledgeDocs" 
                  :key="doc.id" 
                  class="group bg-white border border-slate-100 rounded-xl p-5 hover:border-indigo-200 hover:shadow-md transition-all relative flex flex-col h-[320px]"
                >
                  <!-- Card Header -->
                  <div class="flex justify-between items-start mb-3">
                    <div class="flex items-center">
                      <div class="p-1.5 bg-indigo-50 text-indigo-600 rounded-lg mr-2.5">
                        <FileText class="w-4 h-4" />
                      </div>
                      <span class="text-[10px] font-semibold tracking-wider text-indigo-500 uppercase bg-indigo-50 px-2 py-0.5 rounded-full">
                        {{ doc.payload.type || 'ARTICLE' }}
                      </span>
                    </div>
                    <button 
                      @click="deleteKnowledgeDoc(doc.id)"
                      class="text-slate-300 hover:text-red-500 transition-colors p-1 opacity-0 group-hover:opacity-100"
                      title="Delete from Database"
                    >
                      <Trash2 class="w-4 h-4" />
                    </button>
                  </div>

                  <!-- Card Content -->
                  <h3 class="font-semibold text-slate-800 text-sm mb-2 line-clamp-2 leading-relaxed">
                    {{ doc.payload.title || 'Untitled Document' }}
                  </h3>
                  
                  <!-- Tags Display -->
                  <div v-if="doc.payload.tags && doc.payload.tags.length > 0" class="flex flex-wrap gap-1.5 mb-2">
                    <span 
                      v-for="tag in doc.payload.tags.slice(0, 3)" 
                      :key="tag"
                      class="px-2 py-0.5 bg-slate-100 text-slate-600 text-[10px] rounded-full"
                    >
                      {{ tag }}
                    </span>
                    <span 
                      v-if="doc.payload.tags.length > 3"
                      class="px-2 py-0.5 bg-slate-50 text-slate-400 text-[10px] rounded-full"
                    >
                      +{{ doc.payload.tags.length - 3 }}
                    </span>
                  </div>
                  
                  <div class="flex-1 overflow-hidden relative mb-3">
                    <p class="text-xs text-slate-500 leading-relaxed line-clamp-4">
                      {{ doc.payload.summary_zh || doc.payload.content || 'No summary available.' }}
                    </p>
                    <div class="absolute bottom-0 left-0 w-full h-8 bg-gradient-to-t from-white to-transparent"></div>
                  </div>

                  <!-- Source Link (if from Academic Extract or Integrated Voiceover) -->
                  <div v-if="doc.payload.source_task_id" class="mb-2">
                    <button 
                      @click="navigateToSourceTask(doc.payload)"
                      class="text-[10px] text-amber-600 hover:text-amber-700 bg-amber-50 hover:bg-amber-100 px-2 py-1 rounded-full transition-colors flex items-center"
                    >
                      <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                      </svg>
                      {{ currentLanguage === 'zh' ? '查看原始任务' : 'View Source Task' }}
                    </button>
                  </div>
                  
                  <!-- Card Footer -->
                  <div class="pt-3 border-t border-slate-50 flex justify-between items-center mt-auto">
                    <span class="text-[10px] text-slate-400">
                      {{ formatDate(doc.payload.created_at) }}
                    </span>
                    <button 
                      @click="viewKnowledgeDetail(doc)"
                      class="text-xs font-medium text-indigo-600 hover:text-indigo-700 transition-colors flex items-center"
                    >
                      View Details
                      <svg class="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Pagination for Knowledge Database -->
              <div v-if="!knowledgeLoading && knowledgeDocs.length > 0 && knowledgeTotal > knowledgePageSize" class="mt-6 flex items-center justify-between border-t border-slate-100 pt-4">
                <div class="text-sm text-slate-500">
                  Showing {{ (knowledgePage - 1) * knowledgePageSize + 1 }} - {{ Math.min(knowledgePage * knowledgePageSize, knowledgeTotal) }} of {{ knowledgeTotal }}
                </div>
                <div class="flex items-center gap-2">
                  <button 
                    @click="knowledgePage--; fetchKnowledgeDocs()"
                    :disabled="knowledgePage === 1"
                    class="px-4 py-2 text-sm border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Previous
                  </button>
                  <div class="flex items-center gap-1">
                    <button 
                      v-for="page in paginationPages(knowledgeTotal, knowledgePageSize, knowledgePage)"
                      :key="page"
                      @click="knowledgePage = page; fetchKnowledgeDocs()"
                      :class="[
                        'px-3 py-2 text-sm rounded-lg transition-colors',
                        page === knowledgePage 
                          ? 'bg-indigo-600 text-white' 
                          : 'border border-slate-200 hover:bg-slate-50'
                      ]"
                    >
                      {{ page }}
                    </button>
                  </div>
                  <button 
                    @click="knowledgePage++; fetchKnowledgeDocs()"
                    :disabled="knowledgePage >= Math.ceil(knowledgeTotal / knowledgePageSize)"
                    class="px-4 py-2 text-sm border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Next
                  </button>
                </div>
              </div>
            </div>

            <!-- Image Management Content -->
            <div v-else-if="activeTab === 'images'" class="h-full flex flex-col">
              <div class="mb-8 border-b border-slate-50 pb-6 flex justify-between items-end">
                <div>
                  <h2 class="text-xl font-medium text-slate-700 mb-2">{{ t('imageManagement') }}</h2>
                  <p class="text-slate-500 font-light">
                    {{ currentLanguage === 'en' ? 'Manage extracted images from documents.' : '管理从文档中提取的图片。' }}
                  </p>
                </div>
                <div class="flex gap-3">
                  <button 
                    @click="fetchImages"
                    :disabled="loadingImages"
                    class="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors text-sm font-medium"
                  >
                    <RefreshCw :class="['w-4 h-4', loadingImages ? 'animate-spin' : '']" />
                    {{ t('refresh') }}
                  </button>
                  <button 
                    v-if="selectedImages.size > 0"
                    @click="deleteSelectedImages"
                    class="flex items-center gap-2 px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors text-sm font-medium"
                  >
                    <Trash2 class="w-4 h-4" />
                    {{ t('deleteSelected') }} ({{ selectedImages.size }})
                  </button>
                  <button 
                    @click="cleanupOldImages(30)"
                    class="flex items-center gap-2 px-4 py-2 bg-amber-50 text-amber-600 rounded-lg hover:bg-amber-100 transition-colors text-sm font-medium"
                  >
                    <AlertCircle class="w-4 h-4" />
                    {{ t('cleanupOld') }}
                  </button>
                </div>
              </div>

              <!-- Loading State -->
              <div v-if="loadingImages" class="flex-1 flex items-center justify-center">
                <Loader2 class="w-8 h-8 text-blue-500 animate-spin" />
              </div>

              <!-- Empty State -->
              <div v-else-if="imageList.length === 0" class="flex-1 flex flex-col items-center justify-center text-center p-12 bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
                <div class="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Image class="w-6 h-6 text-slate-300" />
                </div>
                <p class="text-slate-500 font-medium">No images yet</p>
                <p class="text-xs text-slate-400 mt-1">Images will appear here when you upload documents in Integrated Voiceover.</p>
              </div>

              <!-- Image Grid -->
              <div v-else class="flex-1 overflow-y-auto">
                <!-- Select All -->
                <div class="mb-4 flex items-center justify-between bg-slate-50 p-3 rounded-lg">
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input 
                      type="checkbox" 
                      :checked="selectedImages.size === imageList.length && imageList.length > 0"
                      @change="toggleSelectAll"
                      class="w-4 h-4 text-blue-600 bg-white border-slate-300 rounded focus:ring-blue-500 focus:ring-2"
                    />
                    <span class="text-sm font-medium text-slate-700">
                      {{ selectedImages.size === imageList.length && imageList.length > 0 ? t('clearAll') : t('selectAll') }}
                    </span>
                  </label>
                  <span class="text-sm text-slate-500">
                    {{ imageList.length }} {{ t('imageCount') }}
                  </span>
                </div>

                <!-- Image Grid -->
                <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                  <div 
                    v-for="img in imageList" 
                    :key="img.filename"
                    class="group relative bg-white border border-slate-200 rounded-lg overflow-hidden hover:border-blue-300 hover:shadow-md transition-all"
                  >
                    <!-- Checkbox -->
                    <div class="absolute top-2 left-2 z-10">
                      <input 
                        type="checkbox" 
                        :checked="selectedImages.has(img.filename)"
                        @change="toggleImageSelection(img.filename)"
                        class="w-5 h-5 text-blue-600 bg-white border-slate-300 rounded focus:ring-blue-500 focus:ring-2 shadow-sm"
                      />
                    </div>

                    <!-- Delete Button -->
                    <button 
                      @click="deleteImage(img.filename)"
                      class="absolute top-2 right-2 z-10 p-1.5 bg-red-500/90 text-white rounded-md opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
                    >
                      <Trash2 class="w-4 h-4" />
                    </button>

                    <!-- Image -->
                    <div class="aspect-square bg-slate-100 flex items-center justify-center p-2">
                      <img 
                        :src="`${API_BASE_URL}${img.url}`"
                        :alt="img.filename"
                        class="max-w-full max-h-full object-contain"
                        @error="(e) => (e.target as HTMLImageElement).src = 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22%3E%3Crect fill=%22%23f1f5f9%22 width=%22200%22 height=%22200%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23cbd5e1%22 font-size=%2216%22%3EImage%3C/text%3E%3C/svg%3E'"
                      />
                    </div>

                    <!-- Info -->
                    <div class="p-2 bg-white border-t border-slate-100">
                      <p class="text-xs text-slate-600 truncate font-medium" :title="img.filename">
                        {{ img.filename }}
                      </p>
                      <div class="flex items-center justify-between mt-1">
                        <span class="text-[10px] text-slate-400">
                          {{ (img.size_bytes / 1024).toFixed(1) }} KB
                        </span>
                        <span class="text-[10px] text-slate-400">
                          {{ new Date(img.created_at).toLocaleDateString() }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- AI Search Content -->
            <div v-else-if="activeTab === 'search'" class="h-full flex flex-col">
              <div class="mb-8 border-b border-slate-50 pb-6">
                <div>
                  <h2 class="text-xl font-medium text-slate-700 mb-2">{{ t('aiSearch') }}</h2>
                  <p class="text-slate-500 font-light">
                    {{ currentLanguage === 'en' ? 'Search knowledge base with AI-powered semantic search and get intelligent answers.' : '通过 AI 语义搜索知识库，获得智能回答和相关文章。' }}
                  </p>
                </div>
              </div>

              <div class="grid grid-cols-1 lg:grid-cols-5 gap-6 flex-1">
                <!-- Left Panel: Search Input -->
                <div class="lg:col-span-2 space-y-6">
                  <div class="bg-slate-50/50 rounded-xl border border-slate-100 p-6 h-full">
                    <h3 class="text-md font-semibold text-slate-800 mb-4 flex items-center">
                      <div class="p-1.5 bg-blue-100 text-blue-600 rounded-lg mr-2">
                        <Search class="w-4 h-4" />
                      </div>
                      {{ currentLanguage === 'en' ? 'Search Query' : '搜索查询' }}
                    </h3>
                    
                    <div class="space-y-4">
                      <!-- Search Input -->
                      <div>
                        <label class="block text-sm font-medium text-slate-600 mb-1.5">
                          {{ currentLanguage === 'en' ? 'Question / Keywords' : '问题 / 关键词' }}
                        </label>
                        <textarea 
                          v-model="searchQuery"
                          :placeholder="currentLanguage === 'en' ? 'e.g., What are the latest developments in China AI policy?' : '例如：中国人工智能政策的最新发展是什么？'"
                          class="w-full rounded-lg border-slate-200 bg-white text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all resize-none"
                          rows="4"
                          @keyup.ctrl.enter="performSearch"
                        ></textarea>
                        <p class="text-xs text-slate-400 mt-1">
                          {{ currentLanguage === 'en' ? 'Press Ctrl+Enter to search' : '按 Ctrl+Enter 快速搜索' }}
                        </p>
                      </div>
                      
                      <!-- Search Options -->
                      <div class="grid grid-cols-2 gap-3">
                        <div>
                          <label class="block text-sm font-medium text-slate-600 mb-1.5">
                            {{ currentLanguage === 'en' ? 'Search Type' : '搜索类型' }}
                          </label>
                          <select 
                            v-model="searchType"
                            class="w-full rounded-lg border-slate-200 bg-white text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                          >
                            <option value="ai_qa">{{ currentLanguage === 'en' ? 'AI Q&A' : 'AI 问答' }}</option>
                            <option value="knowledge">{{ currentLanguage === 'en' ? 'Knowledge Base' : '知识库搜索' }}</option>
                          </select>
                        </div>
                        <div>
                          <label class="block text-sm font-medium text-slate-600 mb-1.5">
                            {{ currentLanguage === 'en' ? 'Result Limit' : '结果数量' }}
                          </label>
                          <select 
                            v-model="searchLimit"
                            class="w-full rounded-lg border-slate-200 bg-white text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                          >
                            <option :value="5">5 {{ currentLanguage === 'en' ? 'results' : '条' }}</option>
                            <option :value="10">10 {{ currentLanguage === 'en' ? 'results' : '条' }}</option>
                            <option :value="15">15 {{ currentLanguage === 'en' ? 'results' : '条' }}</option>
                            <option :value="20">20 {{ currentLanguage === 'en' ? 'results' : '条' }}</option>
                          </select>
                        </div>
                      </div>
                      
                      <!-- Language Selection -->
                      <div>
                        <label class="block text-sm font-medium text-slate-600 mb-1.5">
                          {{ currentLanguage === 'en' ? 'Answer Language' : '回答语言' }}
                        </label>
                        <select 
                          v-model="searchLanguage"
                          class="w-full rounded-lg border-slate-200 bg-white text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                        >
                          <option value="zh">{{ currentLanguage === 'en' ? 'Chinese' : '中文' }}</option>
                          <option value="en">{{ currentLanguage === 'en' ? 'English' : '英文' }}</option>
                        </select>
                      </div>
                      
                      <!-- Search Button -->
                      <button
                        @click="performSearch"
                        :disabled="!searchQuery.trim() || isSearching"
                        :class="[
                          'w-full py-3 rounded-lg font-medium transition-all flex items-center justify-center',
                          searchQuery.trim() && !isSearching
                            ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white hover:shadow-lg hover:shadow-blue-200/50'
                            : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                        ]"
                      >
                        <Loader2 v-if="isSearching" class="w-4 h-4 mr-2 animate-spin" />
                        <Search v-else class="w-4 h-4 mr-2" />
                        {{ isSearching ? (currentLanguage === 'en' ? 'Searching...' : '搜索中...') : (currentLanguage === 'en' ? 'Search' : '开始搜索') }}
                      </button>

                      <!-- Search History -->
                      <div v-if="searchHistory.length > 0" class="pt-4 border-t border-slate-200">
                        <div class="flex items-center justify-between mb-2">
                          <label class="text-sm font-medium text-slate-600">
                            {{ currentLanguage === 'en' ? 'Recent Searches' : '最近搜索' }}
                          </label>
                          <button 
                            @click="clearSearchHistory"
                            class="text-xs text-slate-400 hover:text-red-500 transition-colors"
                          >
                            {{ currentLanguage === 'en' ? 'Clear' : '清空' }}
                          </button>
                        </div>
                        <div class="space-y-1 max-h-32 overflow-y-auto">
                          <button
                            v-for="(history, idx) in searchHistory.slice(0, 5)"
                            :key="idx"
                            @click="searchQuery = history; performSearch()"
                            class="w-full text-left text-xs text-slate-500 hover:text-blue-600 hover:bg-blue-50 px-2 py-1 rounded transition-colors truncate"
                          >
                            {{ history }}
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Right Panel: Search Results -->
                <div class="lg:col-span-3 space-y-6">
                  <!-- Results Container -->
                  <div v-if="searchResults || aiAnswer" class="space-y-6">
                    <!-- AI Answer Section -->
                    <div v-if="aiAnswer && searchType === 'ai_qa'" class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200 p-6">
                      <div class="flex items-start justify-between mb-4">
                        <h3 class="text-md font-semibold text-blue-900 flex items-center">
                          <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                          </svg>
                          {{ currentLanguage === 'en' ? 'AI Answer' : 'AI 回答' }}
                        </h3>
                        <div class="flex items-center space-x-2">
                          <button
                            @click="copyToClipboard(aiAnswer)"
                            class="p-1.5 text-blue-600 hover:bg-blue-100 rounded-lg transition-colors"
                            :title="currentLanguage === 'en' ? 'Copy' : '复制'"
                          >
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                          </button>
                        </div>
                      </div>
                      <div class="prose prose-sm max-w-none">
                        <p class="text-slate-700 leading-relaxed whitespace-pre-wrap">{{ aiAnswer }}</p>
                      </div>
                      <div v-if="searchDuration" class="mt-4 pt-4 border-t border-blue-200">
                        <p class="text-xs text-blue-600">
                          ⚡ {{ currentLanguage === 'en' ? 'Search completed in' : '搜索耗时' }} {{ searchDuration }}ms
                        </p>
                      </div>
                    </div>

                    <!-- Sources / Results List -->
                    <div class="bg-white rounded-xl border border-slate-100 p-6">
                      <h3 class="text-md font-semibold text-slate-800 mb-4 flex items-center">
                        <svg class="w-5 h-5 mr-2 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        {{ currentLanguage === 'en' ? 'Related Documents' : '相关文档' }}
                        <span class="ml-2 text-xs font-normal text-slate-500">({{ searchResultsList.length }} {{ currentLanguage === 'en' ? 'results' : '条结果' }})</span>
                      </h3>
                      
                      <div v-if="searchResultsList.length === 0" class="text-center py-8">
                        <div class="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-3">
                          <Search class="w-6 h-6 text-slate-300" />
                        </div>
                        <p class="text-slate-500 font-medium">{{ currentLanguage === 'en' ? 'No results found' : '未找到相关结果' }}</p>
                        <p class="text-xs text-slate-400 mt-1">{{ currentLanguage === 'en' ? 'Try different keywords or refine your query' : '尝试使用不同的关键词或优化您的查询' }}</p>
                      </div>

                      <div v-else class="space-y-3">
                        <div
                          v-for="(result, idx) in searchResultsList"
                          :key="idx"
                          class="p-4 bg-slate-50 hover:bg-slate-100 rounded-lg border border-slate-200 transition-all cursor-pointer"
                          @click="viewSearchResult(result)"
                        >
                          <div class="flex items-start justify-between mb-2">
                            <h4 class="text-sm font-semibold text-slate-800 flex-1">
                              {{ result.title || (currentLanguage === 'en' ? 'Untitled' : '无标题') }}
                            </h4>
                            <div class="flex items-center ml-2">
                              <span class="text-xs font-medium px-2 py-1 bg-blue-100 text-blue-700 rounded">
                                {{ (result.score * 100).toFixed(1) }}%
                              </span>
                            </div>
                          </div>
                          <p class="text-xs text-slate-600 line-clamp-2 leading-relaxed">
                            {{ result.summary || result.content || (currentLanguage === 'en' ? 'No description available' : '暂无描述') }}
                          </p>
                          <div class="flex items-center justify-between mt-3 pt-3 border-t border-slate-200">
                            <div class="flex items-center space-x-2 text-xs text-slate-400">
                              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                              </svg>
                              <span>ID: {{ result.id }}</span>
                            </div>
                            <button
                              class="text-xs text-blue-600 hover:text-blue-800 font-medium flex items-center"
                            >
                              {{ currentLanguage === 'en' ? 'View Details' : '查看详情' }}
                              <svg class="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                              </svg>
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Empty State -->
                  <div v-else class="bg-slate-50/50 rounded-xl border border-dashed border-slate-200 p-12 text-center">
                    <div class="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Search class="w-8 h-8 text-slate-300" />
                    </div>
                    <h3 class="text-lg font-medium text-slate-700 mb-2">{{ currentLanguage === 'en' ? 'Ready to Search' : '准备开始搜索' }}</h3>
                    <p class="text-sm text-slate-500 mb-4">{{ currentLanguage === 'en' ? 'Enter your question or keywords and click search to get AI-powered answers and relevant documents.' : '输入您的问题或关键词，点击搜索获取 AI 回答和相关文档。' }}</p>
                    <div class="flex flex-col items-center space-y-2 text-xs text-slate-400">
                      <div class="flex items-center">
                        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                        {{ currentLanguage === 'en' ? 'Tip: Use Ctrl+Enter for quick search' : '提示：使用 Ctrl+Enter 快速搜索' }}
                      </div>
                      <div class="flex items-center">
                        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                        {{ currentLanguage === 'en' ? 'AI Q&A mode provides intelligent summaries' : 'AI 问答模式提供智能总结' }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Hot Topics Content -->
            <div v-else-if="activeTab === 'trending'" class="h-full flex flex-col">
              <div class="mb-8 border-b border-slate-50 pb-6">
                <div>
                  <h2 class="text-xl font-medium text-slate-700 mb-2">{{ t('hotTopics') }}</h2>
                  <p class="text-slate-500 font-light">
                    {{ currentLanguage === 'en' ? 'Generate trending posts from real-time news and hot topics.' : '基于实时新闻和热点话题快速生成推文内容。' }}
                  </p>
                </div>
              </div>

              <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- Left Panel: Topic Search & Generation -->
                <div class="lg:col-span-2 space-y-6">
                  <!-- Search & Generate Card -->
                  <div class="bg-slate-50/50 rounded-xl border border-slate-100 p-6">
                    <h3 class="text-md font-semibold text-slate-800 mb-4 flex items-center">
                      <div class="p-1.5 bg-orange-100 text-orange-600 rounded-lg mr-2">
                        <Flame class="w-4 h-4" />
                      </div>
                      {{ currentLanguage === 'en' ? 'Generate Hot Post' : '生成热点推文' }}
                    </h3>
                    
                    <div class="space-y-4">
                      <!-- Topic Input -->
                      <div>
                        <label class="block text-sm font-medium text-slate-600 mb-1.5">
                          {{ currentLanguage === 'en' ? 'Topic / Keyword' : '话题 / 关键词' }}
                        </label>
                        <input 
                          v-model="hotNewsTopic"
                          type="text" 
                          :placeholder="currentLanguage === 'en' ? 'e.g., China AI Development' : '例如：中国人工智能发展'"
                          class="w-full rounded-lg border-slate-200 bg-white text-sm focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
                          @keyup.enter="generateHotPost"
                        />
                      </div>
                      
                      <!-- Style & Length -->
                      <div class="grid grid-cols-2 gap-3">
                        <div>
                          <label class="block text-sm font-medium text-slate-600 mb-1.5">
                            {{ currentLanguage === 'en' ? 'Style' : '风格' }}
                          </label>
                          <select 
                            v-model="hotNewsStyle"
                            class="w-full rounded-lg border-slate-200 bg-white text-sm focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500"
                          >
                            <option value="professional">{{ currentLanguage === 'en' ? 'Professional' : '专业' }}</option>
                            <option value="casual">{{ currentLanguage === 'en' ? 'Casual' : '轻松' }}</option>
                            <option value="academic">{{ currentLanguage === 'en' ? 'Academic' : '学术' }}</option>
                          </select>
                        </div>
                        <div>
                          <label class="block text-sm font-medium text-slate-600 mb-1.5">
                            {{ currentLanguage === 'en' ? 'Length' : '长度' }}
                          </label>
                          <select 
                            v-model="hotNewsLength"
                            class="w-full rounded-lg border-slate-200 bg-white text-sm focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500"
                          >
                            <option value="short">{{ currentLanguage === 'en' ? 'Short (100-200)' : '短 (100-200字)' }}</option>
                            <option value="medium">{{ currentLanguage === 'en' ? 'Medium (300-500)' : '中 (300-500字)' }}</option>
                            <option value="long">{{ currentLanguage === 'en' ? 'Long (500-800)' : '长 (500-800字)' }}</option>
                          </select>
                        </div>
                      </div>
                      
                      <!-- Options -->
                      <div class="flex items-center space-x-4">
                        <label class="flex items-center space-x-2 cursor-pointer">
                          <input
                            v-model="hotNewsGenerateScript"
                            type="checkbox"
                            class="w-4 h-4 text-orange-600 border-slate-300 rounded focus:ring-2 focus:ring-orange-500/20"
                          />
                          <span class="text-sm text-slate-700">
                            {{ currentLanguage === 'en' ? 'Generate video script' : '生成视频脚本' }}
                          </span>
                        </label>
                      </div>
                      
                      <!-- Generate Button -->
                      <button
                        @click="generateHotPost"
                        :disabled="!hotNewsTopic.trim() || hotNewsGenerating"
                        :class="[
                          'w-full py-3 rounded-lg font-medium transition-all flex items-center justify-center',
                          hotNewsTopic.trim() && !hotNewsGenerating
                            ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white hover:shadow-lg hover:shadow-orange-200/50'
                            : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                        ]"
                      >
                        <Zap v-if="!hotNewsGenerating" class="w-4 h-4 mr-2" />
                        <Loader2 v-else class="w-4 h-4 mr-2 animate-spin" />
                        {{ hotNewsGenerating 
                          ? (currentLanguage === 'en' ? 'Generating...' : '生成中...') 
                          : (currentLanguage === 'en' ? 'Generate Post' : '生成推文')
                        }}
                      </button>
                    </div>
                  </div>
                  
                  <!-- Generated Post Result -->
                  <div v-if="hotNewsResult" class="bg-white rounded-xl border border-slate-100 p-6">
                    <div class="flex items-center justify-between mb-4">
                      <h3 class="text-md font-semibold text-slate-800">
                        {{ currentLanguage === 'en' ? 'Generated Post' : '生成的推文' }}
                      </h3>
                      <button
                        @click="copyToClipboard(hotNewsResult.post_content)"
                        class="flex items-center gap-2 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm rounded-lg transition-colors"
                      >
                        <Copy class="w-4 h-4" />
                        {{ currentLanguage === 'en' ? 'Copy' : '复制' }}
                      </button>
                    </div>
                    
                    <div class="prose prose-sm max-w-none mb-4">
                      <div class="whitespace-pre-wrap text-slate-700 leading-relaxed">{{ hotNewsResult.post_content }}</div>
                    </div>
                    
                    <!-- Tags -->
                    <div v-if="hotNewsResult.tags && hotNewsResult.tags.length > 0" class="flex flex-wrap gap-2 mb-4">
                      <span 
                        v-for="tag in hotNewsResult.tags" 
                        :key="tag"
                        class="px-3 py-1 bg-blue-50 text-blue-600 rounded-full text-xs font-medium"
                      >
                        {{ tag }}
                      </span>
                    </div>
                    
                    <!-- Video Script (if generated) -->
                    <div v-if="hotNewsResult.script_content" class="mt-6 pt-6 border-t border-slate-100">
                      <div class="flex items-center justify-between mb-3">
                        <h4 class="text-sm font-semibold text-slate-800">
                          {{ currentLanguage === 'en' ? 'Video Script' : '视频脚本' }}
                        </h4>
                        <button
                          @click="copyToClipboard(hotNewsResult.script_content)"
                          class="flex items-center gap-2 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs rounded-lg transition-colors"
                        >
                          <Copy class="w-3 h-3" />
                          {{ currentLanguage === 'en' ? 'Copy' : '复制' }}
                        </button>
                      </div>
                      <div class="bg-slate-50 rounded-lg p-4">
                        <div class="whitespace-pre-wrap text-slate-700 text-sm leading-relaxed">{{ hotNewsResult.script_content }}</div>
                      </div>
                    </div>
                    
                    <!-- Sources -->
                    <div v-if="hotNewsResult.sources && hotNewsResult.sources.length > 0" class="mt-6 pt-6 border-t border-slate-100">
                      <h4 class="text-sm font-semibold text-slate-800 mb-3">
                        {{ currentLanguage === 'en' ? 'Sources' : '信息来源' }}
                      </h4>
                      <div class="space-y-2">
                        <a 
                          v-for="(source, idx) in hotNewsResult.sources" 
                          :key="idx"
                          :href="source.url"
                          target="_blank"
                          class="block p-3 bg-slate-50 hover:bg-slate-100 rounded-lg transition-colors group"
                        >
                          <div class="flex items-start justify-between">
                            <div class="flex-1">
                              <p class="text-sm font-medium text-slate-700 group-hover:text-blue-600 transition-colors">{{ source.title }}</p>
                              <p class="text-xs text-slate-500 mt-1">{{ source.source }}</p>
                            </div>
                            <ExternalLink class="w-4 h-4 text-slate-400 group-hover:text-blue-600 transition-colors flex-shrink-0 ml-2" />
                          </div>
                        </a>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Right Panel: Trending Topics & Latest News -->
                <div class="space-y-6">
                  <!-- Trending Topics -->
                  <div class="bg-white rounded-xl border border-slate-100 p-5">
                    <div class="flex items-center justify-between mb-4">
                      <h3 class="text-md font-semibold text-slate-800 flex items-center">
                        <TrendingUp class="w-4 h-4 mr-2 text-red-500" />
                        {{ currentLanguage === 'en' ? 'Trending Now' : '实时热点' }}
                      </h3>
                      <button
                        @click="fetchTrendingTopics"
                        :disabled="loadingTrending"
                        class="p-1.5 hover:bg-slate-100 rounded-lg transition-colors"
                      >
                        <RefreshCw :class="['w-4 h-4 text-slate-500', loadingTrending ? 'animate-spin' : '']" />
                      </button>
                    </div>
                    
                    <!-- Loading -->
                    <div v-if="loadingTrending" class="flex items-center justify-center py-8">
                      <Loader2 class="w-6 h-6 text-orange-500 animate-spin" />
                    </div>
                    
                    <!-- Trending List -->
                    <div v-else-if="trendingTopics.length > 0" class="space-y-3 max-h-[400px] overflow-y-auto">
                      <div 
                        v-for="(topic, idx) in trendingTopics" 
                        :key="idx"
                        class="p-3 bg-slate-50 hover:bg-orange-50 rounded-lg transition-all border border-transparent hover:border-orange-200 group"
                      >
                        <div class="flex items-start">
                          <span class="flex-shrink-0 w-6 h-6 bg-gradient-to-br from-orange-400 to-red-400 text-white text-xs font-bold rounded-full flex items-center justify-center mr-2">
                            {{ idx + 1 }}
                          </span>
                          <div class="flex-1 min-w-0 cursor-pointer" @click="generatePostFromTrending(topic)">
                            <p class="text-sm font-medium text-slate-700 group-hover:text-orange-600 transition-colors line-clamp-2">
                              {{ topic.title }}
                            </p>
                            <p class="text-xs text-slate-500 mt-1 line-clamp-1">{{ topic.description }}</p>
                          </div>
                          <div class="flex items-center gap-1 ml-2">
                            <button
                              @click.stop="viewTrendingDetail(topic)"
                              class="p-1.5 hover:bg-blue-100 rounded-lg transition-colors"
                              title="查看详情"
                            >
                              <ExternalLink class="w-3.5 h-3.5 text-slate-400 hover:text-blue-600" />
                            </button>
                            <button
                              @click.stop="saveTrendingToKB(topic)"
                              class="p-1.5 hover:bg-green-100 rounded-lg transition-colors"
                              title="保存到知识库"
                            >
                              <Save class="w-3.5 h-3.5 text-slate-400 hover:text-green-600" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Empty State -->
                    <div v-else class="text-center py-8">
                      <p class="text-sm text-slate-500">{{ currentLanguage === 'en' ? 'No trending topics' : '暂无热点话题' }}</p>
                    </div>
                  </div>
                  
                  <!-- Latest News -->
                  <div class="bg-white rounded-xl border border-slate-100 p-5">
                    <div class="flex items-center justify-between mb-4">
                      <h3 class="text-md font-semibold text-slate-800 flex items-center">
                        <Newspaper class="w-4 h-4 mr-2 text-blue-500" />
                        {{ currentLanguage === 'en' ? 'Latest News' : '最新新闻' }}
                      </h3>
                      <div class="flex items-center gap-2">
                        <button
                          @click="toggleNewsSourceSelector"
                          class="p-1.5 hover:bg-slate-100 rounded-lg transition-colors"
                          :title="currentLanguage === 'zh' ? '选择新闻源' : 'Select News Sources'"
                        >
                          <Settings class="w-4 h-4 text-slate-500" />
                        </button>
                        <button
                          @click="fetchLatestNews"
                          :disabled="loadingNews"
                          class="p-1.5 hover:bg-slate-100 rounded-lg transition-colors"
                        >
                          <RefreshCw :class="['w-4 h-4 text-slate-500', loadingNews ? 'animate-spin' : '']" />
                        </button>
                      </div>
                    </div>
                    
                    <!-- News Source Selector -->
                    <div v-if="showNewsSourceSelector" class="mb-4 p-3 bg-slate-50 rounded-lg border border-slate-200">
                      <div class="flex items-center justify-between mb-3">
                        <span class="text-sm font-medium text-slate-700">
                          {{ currentLanguage === 'zh' ? '选择新闻频道' : 'Select News Channels' }}
                        </span>
                        <button
                          @click="selectAllNewsSources"
                          class="text-xs text-indigo-600 hover:text-indigo-700"
                        >
                          {{ selectedNewsSources.length === availableNewsSources.length ? (currentLanguage === 'zh' ? '取消全选' : 'Deselect All') : (currentLanguage === 'zh' ? '全选' : 'Select All') }}
                        </button>
                      </div>
                      <div v-if="loadingNewsSources" class="flex items-center justify-center py-4">
                        <Loader2 class="w-5 h-5 text-slate-400 animate-spin" />
                      </div>
                      <div v-else class="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto">
                        <label 
                          v-for="source in availableNewsSources" 
                          :key="source.name"
                          class="flex items-center gap-2 p-2 rounded hover:bg-white cursor-pointer text-xs"
                        >
                          <input
                            type="checkbox"
                            :value="source.name"
                            v-model="selectedNewsSources"
                            class="w-3.5 h-3.5 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500"
                          />
                          <span class="text-slate-700 truncate" :title="source.name">{{ source.name }}</span>
                        </label>
                      </div>
                      <div class="mt-3 flex justify-end">
                        <button
                          @click="applyNewsSourceFilter"
                          class="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs rounded-lg transition-colors"
                        >
                          {{ currentLanguage === 'zh' ? '应用筛选' : 'Apply Filter' }}
                        </button>
                      </div>
                    </div>
                    
                    <!-- Loading -->
                    <div v-if="loadingNews" class="flex items-center justify-center py-8">
                      <Loader2 class="w-6 h-6 text-blue-500 animate-spin" />
                    </div>
                    
                    <!-- News List -->
                    <div v-else-if="latestNews.length > 0" class="space-y-3 max-h-[400px] overflow-y-auto">
                      <div 
                        v-for="(news, idx) in latestNews" 
                        :key="idx"
                        class="p-3 bg-slate-50 rounded-lg transition-all border border-slate-200 hover:border-blue-300 group"
                      >
                        <p class="text-sm font-medium text-slate-700 line-clamp-2 mb-1">
                          {{ news.title }}
                        </p>
                        <div class="flex items-center justify-between text-xs text-slate-500 mb-2">
                          <span>{{ news.source }}</span>
                          <span>{{ news.published_date ? new Date(news.published_date).toLocaleDateString() : '' }}</span>
                        </div>
                        <!-- Action Buttons -->
                        <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            @click="viewNewsDetail(news)"
                            class="flex-1 flex items-center justify-center gap-1 px-2 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded text-xs transition-colors"
                          >
                            <FileText class="w-3 h-3" />
                            {{ currentLanguage === 'en' ? 'View' : '查看' }}
                          </button>
                          <button
                            @click="generatePostFromNews(news)"
                            class="flex-1 flex items-center justify-center gap-1 px-2 py-1 bg-orange-100 hover:bg-orange-200 text-orange-700 rounded text-xs transition-colors"
                          >
                            <Zap class="w-3 h-3" />
                            {{ currentLanguage === 'en' ? 'Generate' : '生成' }}
                          </button>
                          <button
                            @click="saveNewsToKB(news)"
                            class="flex items-center justify-center gap-1 px-2 py-1 bg-green-100 hover:bg-green-200 text-green-700 rounded text-xs transition-colors"
                          >
                            <Database class="w-3 h-3" />
                            {{ currentLanguage === 'en' ? 'Save' : '存储' }}
                          </button>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Empty State -->
                    <div v-else class="text-center py-8">
                      <p class="text-sm text-slate-500">{{ currentLanguage === 'en' ? 'No news available' : '暂无新闻' }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- News Detail Modal -->
            <div 
              v-if="showNewsDetail" 
              class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
              @click.self="closeNewsDetail"
            >
              <div class="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[80vh] overflow-hidden flex flex-col">
                <!-- Header -->
                <div class="flex items-center justify-between p-6 border-b border-slate-100">
                  <h3 class="text-xl font-semibold text-slate-800">
                    {{ currentLanguage === 'en' ? 'News Detail' : '新闻详情' }}
                  </h3>
                  <button 
                    @click="closeNewsDetail"
                    class="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                  >
                    <X class="w-5 h-5 text-slate-500" />
                  </button>
                </div>
                
                <!-- Content -->
                <div v-if="selectedNewsDetail" class="flex-1 overflow-y-auto p-6">
                  <!-- Title -->
                  <h2 class="text-2xl font-bold text-slate-800 mb-4">
                    {{ selectedNewsDetail.title }}
                  </h2>
                  
                  <!-- Meta Info -->
                  <div class="flex items-center gap-4 text-sm text-slate-500 mb-6 pb-4 border-b border-slate-100">
                    <div class="flex items-center gap-1">
                      <Newspaper class="w-4 h-4" />
                      <span>{{ selectedNewsDetail.source }}</span>
                    </div>
                    <div class="flex items-center gap-1">
                      <Clock class="w-4 h-4" />
                      <span>{{ selectedNewsDetail.published_date ? new Date(selectedNewsDetail.published_date).toLocaleString() : 'N/A' }}</span>
                    </div>
                    <div v-if="selectedNewsDetail.score" class="flex items-center gap-1">
                      <TrendingUp class="w-4 h-4" />
                      <span>{{ (selectedNewsDetail.score * 100).toFixed(1) }}%</span>
                    </div>
                  </div>
                  
                  <!-- Description / Content -->
                  <div class="mb-6">
                    <div class="flex items-center justify-between mb-3">
                      <h4 class="text-sm font-semibold text-slate-700">
                        {{ currentLanguage === 'en' ? 'Content' : '内容' }}
                      </h4>
                      <button
                        v-if="!selectedNewsDetail.fullContent && (selectedNewsDetail.link || selectedNewsDetail.url)"
                        @click="fetchNewsFullContent"
                        :disabled="loadingNewsContent"
                        class="text-xs text-blue-600 hover:text-blue-700 flex items-center"
                      >
                        <Loader2 v-if="loadingNewsContent" class="w-3 h-3 mr-1 animate-spin" />
                        <RefreshCw v-else class="w-3 h-3 mr-1" />
                        {{ loadingNewsContent ? (currentLanguage === 'zh' ? '获取中...' : 'Fetching...') : (currentLanguage === 'zh' ? '获取全文' : 'Fetch Full Content') }}
                      </button>
                    </div>
                    <div v-if="selectedNewsDetail.fullContent || selectedNewsDetail.description" class="prose prose-slate max-w-none">
                      <p class="text-slate-600 leading-relaxed whitespace-pre-wrap">
                        {{ selectedNewsDetail.fullContent || selectedNewsDetail.description }}
                      </p>
                    </div>
                    <div v-else class="text-center py-8 bg-slate-50 rounded-lg">
                      <p class="text-sm text-slate-500">
                        {{ currentLanguage === 'zh' ? '暂无内容摘要，点击"获取全文"尝试抓取原文内容' : 'No content summary. Click "Fetch Full Content" to try fetching the original article.' }}
                      </p>
                    </div>
                  </div>
                  
                  <!-- Original Link -->
                  <div v-if="selectedNewsDetail.link || selectedNewsDetail.url" class="mb-6 p-4 bg-slate-50 rounded-lg">
                    <h4 class="text-sm font-semibold text-slate-700 mb-2">
                      {{ currentLanguage === 'en' ? 'Source Link' : '原文链接' }}
                    </h4>
                    <a 
                      :href="selectedNewsDetail.link || selectedNewsDetail.url" 
                      target="_blank"
                      class="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 hover:underline break-all"
                    >
                      <ExternalLink class="w-4 h-4 flex-shrink-0" />
                      <span class="text-sm">{{ selectedNewsDetail.link || selectedNewsDetail.url }}</span>
                    </a>
                  </div>
                </div>
                
                <!-- Footer Actions -->
                <div class="flex items-center justify-end gap-3 p-6 border-t border-slate-100 bg-slate-50">
                  <button
                    @click="saveNewsDetailToKB(); closeNewsDetail()"
                    :disabled="savingNewsToKB"
                    class="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50"
                  >
                    <Database class="w-4 h-4" />
                    {{ savingNewsToKB 
                      ? (currentLanguage === 'en' ? 'Saving...' : '保存中...') 
                      : (currentLanguage === 'en' ? 'Save to Knowledge Base' : '保存到知识库')
                    }}
                  </button>
                  <button
                    @click="generatePostFromDetail(); closeNewsDetail()"
                    class="flex items-center gap-2 px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-colors"
                  >
                    <Zap class="w-4 h-4" />
                    {{ currentLanguage === 'en' ? 'Generate Post' : '生成推文' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Email Marketing Content -->
            <div v-else-if="activeTab === 'email'" class="h-full flex flex-col">
              <div class="mb-8 border-b border-slate-50 pb-6">
                <h2 class="text-xl font-medium text-slate-700 mb-2">{{ t('emailMarketing') }}</h2>
                <p class="text-slate-500 font-light">
                  {{ currentLanguage === 'en' ? 'Manage email subscribers, templates, and send newsletters to engaged users.' : '管理邮件订阅者、模板，并向活跃用户发送新闻简报。' }}
                </p>
              </div>

              <!-- Email Marketing Tabs -->
              <div class="mb-6">
                <div class="border-b border-slate-200">
                  <nav class="-mb-px flex space-x-8" aria-label="Tabs">
                    <button 
                      v-for="tab in emailTabs" 
                      :key="tab.id"
                      @click="currentEmailTab = tab.id"
                      :class="[
                        currentEmailTab === tab.id
                          ? 'border-indigo-500 text-indigo-600'
                          : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300',
                        'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
                      ]"
                    >
                      {{ tab.name }}
                    </button>
                  </nav>
                </div>
              </div>

              <!-- Tab Content -->
              <div class="flex-1 overflow-y-auto">
                
                <!-- Subscribers Tab -->
                <div v-if="currentEmailTab === 'subscribers'">
                  <div class="flex justify-between items-center mb-6">
                    <h3 class="text-lg font-medium text-slate-900">{{ currentLanguage === 'zh' ? '订阅用户列表' : 'Subscriber List' }}</h3>
                    <div class="flex gap-2">
                      <input 
                        type="file" 
                        ref="emailFileInput" 
                        class="hidden" 
                        accept=".csv,.xlsx,.xls" 
                        @change="handleEmailFileUpload"
                      >
                      <button 
                        @click="$refs.emailFileInput.click()"
                        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
                      >
                        {{ currentLanguage === 'zh' ? '导入 Excel/CSV' : 'Import Excel/CSV' }}
                      </button>
                      <button 
                        @click="fetchEmailSubscribers"
                        class="inline-flex items-center px-4 py-2 border border-slate-300 text-sm font-medium rounded-md text-slate-700 bg-white hover:bg-slate-50"
                      >
                        {{ currentLanguage === 'zh' ? '刷新' : 'Refresh' }}
                      </button>
                    </div>
                  </div>

                  <div v-if="emailLoading" class="text-center py-10">{{ currentLanguage === 'zh' ? '加载中...' : 'Loading...' }}</div>
                  
                  <div v-else class="bg-white shadow overflow-hidden sm:rounded-lg">
                    <table class="min-w-full divide-y divide-slate-200">
                      <thead class="bg-slate-50">
                        <tr>
                          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">ID</th>
                          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">{{ currentLanguage === 'zh' ? '邮箱' : 'Email' }}</th>
                          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">{{ currentLanguage === 'zh' ? '姓名' : 'Name' }}</th>
                          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">{{ currentLanguage === 'zh' ? '状态' : 'Status' }}</th>
                          <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">{{ currentLanguage === 'zh' ? '操作' : 'Actions' }}</th>
                        </tr>
                      </thead>
                      <tbody class="bg-white divide-y divide-slate-200">
                        <tr v-for="sub in emailSubscribers" :key="sub.id">
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{{ sub.id }}</td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">{{ sub.email }}</td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{{ sub.name || '-' }}</td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                            <span :class="sub.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                              {{ sub.is_active ? (currentLanguage === 'zh' ? '活跃' : 'Active') : (currentLanguage === 'zh' ? '停用' : 'Inactive') }}
                            </span>
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <button @click="deleteEmailSubscriber(sub.id)" class="text-red-600 hover:text-red-900">{{ currentLanguage === 'zh' ? '删除' : 'Delete' }}</button>
                          </td>
                        </tr>
                        <tr v-if="emailSubscribers.length === 0">
                          <td colspan="5" class="px-6 py-4 text-center text-sm text-slate-500">{{ currentLanguage === 'zh' ? '暂无数据' : 'No data' }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <!-- Templates Tab -->
                <div v-else-if="currentEmailTab === 'templates'">
                  <div class="flex justify-between items-center mb-6">
                    <h3 class="text-lg font-medium text-slate-900">{{ currentLanguage === 'zh' ? '邮件模板管理' : 'Email Templates' }}</h3>
                    <button 
                      @click="openEmailTemplateModal()"
                      class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
                    >
                      {{ currentLanguage === 'zh' ? '新建模板' : 'New Template' }}
                    </button>
                  </div>

                  <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    <div 
                      v-for="tpl in emailTemplates" 
                      :key="tpl.id"
                      class="relative rounded-lg border border-slate-300 bg-white px-6 py-5 shadow-sm flex flex-col justify-between hover:border-indigo-500"
                    >
                      <div>
                        <h4 class="text-sm font-medium text-slate-900">{{ tpl.name }}</h4>
                        <p class="mt-1 text-sm text-slate-500 truncate">{{ currentLanguage === 'zh' ? '主题' : 'Subject' }}: {{ tpl.subject }}</p>
                        <div class="mt-2 text-xs text-slate-400">{{ currentLanguage === 'zh' ? '更新于' : 'Updated' }}: {{ new Date(tpl.updated_at || tpl.created_at).toLocaleString() }}</div>
                      </div>
                      <div class="mt-4 flex justify-end gap-2">
                        <button @click="openEmailTemplateModal(tpl)" class="text-indigo-600 hover:text-indigo-900 text-sm">{{ currentLanguage === 'zh' ? '编辑' : 'Edit' }}</button>
                        <button @click="deleteEmailTemplate(tpl.id)" class="text-red-600 hover:text-red-900 text-sm">{{ currentLanguage === 'zh' ? '删除' : 'Delete' }}</button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Send Tab -->
                <div v-else-if="currentEmailTab === 'send'">
                  <div class="max-w-2xl mx-auto">
                    <h3 class="text-lg font-medium text-slate-900 mb-6">{{ currentLanguage === 'zh' ? '发送邮件' : 'Send Email' }}</h3>
                    
                    <div class="space-y-6">
                      <div>
                        <label class="block text-sm font-medium text-slate-700">{{ currentLanguage === 'zh' ? '选择模板' : 'Select Template' }}</label>
                        <select v-model="emailSendForm.template_id" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-slate-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md">
                          <option v-for="tpl in emailTemplates" :key="tpl.id" :value="tpl.id">{{ tpl.name }} - {{ tpl.subject }}</option>
                        </select>
                      </div>

                      <div>
                        <label class="block text-sm font-medium text-slate-700">{{ currentLanguage === 'zh' ? '发送对象' : 'Send To' }}</label>
                        <div class="mt-2 space-y-2">
                          <div class="flex items-center">
                            <input id="send-all" name="send-type" type="radio" value="all" v-model="emailSendForm.type" class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-slate-300">
                            <label for="send-all" class="ml-3 block text-sm font-medium text-slate-700">
                              {{ currentLanguage === 'zh' ? '所有活跃订阅用户' : 'All Active Subscribers' }} ({{ emailSubscribers.length }} {{ currentLanguage === 'zh' ? '人' : 'users' }})
                            </label>
                          </div>
                          <div class="flex items-center">
                            <input id="send-test" name="send-type" type="radio" value="test" v-model="emailSendForm.type" class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-slate-300">
                            <label for="send-test" class="ml-3 block text-sm font-medium text-slate-700">
                              {{ currentLanguage === 'zh' ? '发送测试邮件' : 'Send Test Email' }}
                            </label>
                          </div>
                        </div>
                      </div>

                      <div v-if="emailSendForm.type === 'test'">
                        <label class="block text-sm font-medium text-slate-700">{{ currentLanguage === 'zh' ? '测试邮箱地址' : 'Test Email Address' }}</label>
                        <input type="email" v-model="emailSendForm.test_email" class="mt-1 block w-full border border-slate-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                      </div>

                      <div class="pt-4">
                        <button 
                          @click="sendEmail"
                          :disabled="emailSending || !emailSendForm.template_id"
                          class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-slate-400"
                        >
                          {{ emailSending ? (currentLanguage === 'zh' ? '发送中...' : 'Sending...') : (currentLanguage === 'zh' ? '确认发送' : 'Confirm Send') }}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Settings Tab -->
                <div v-else-if="currentEmailTab === 'settings'">
                  <div class="max-w-2xl mx-auto">
                    <h3 class="text-lg font-medium text-slate-900 mb-6">{{ currentLanguage === 'zh' ? 'SMTP 发件配置' : 'SMTP Configuration' }}</h3>
                    
                    <div class="space-y-4">
                      <!-- 预设配置选择器 -->
                      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <label class="block text-sm font-medium text-blue-900 mb-2">
                          {{ currentLanguage === 'zh' ? '📧 选择常用邮件服务商（可选）' : '📧 Choose Email Provider (Optional)' }}
                        </label>
                        <select 
                          @change="applySmtpPreset($event)"
                          class="block w-full border border-blue-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-white"
                        >
                          <option value="">{{ currentLanguage === 'zh' ? '-- 选择预设或手动配置 --' : '-- Select preset or configure manually --' }}</option>
                          <option value="gmail">Gmail (Google)</option>
                          <option value="outlook">Outlook / Hotmail (Microsoft)</option>
                          <option value="office365">Office 365 (Exchange)</option>
                          <option value="163">163.com (网易)</option>
                          <option value="qq">QQ Mail (腾讯)</option>
                          <option value="yahoo">Yahoo Mail</option>
                          <option value="icloud">iCloud Mail (Apple)</option>
                        </select>
                        <p class="mt-2 text-xs text-blue-700">
                          {{ currentLanguage === 'zh' ? '💡 选择后会自动填入服务器地址和端口，您只需填写用户名和密码' : '💡 Server and port will be auto-filled. Just enter your username and password' }}
                        </p>
                      </div>
                      
                      <div class="grid grid-cols-2 gap-4">
                        <div>
                          <label class="block text-sm font-medium text-slate-700">{{ currentLanguage === 'zh' ? 'SMTP 服务器' : 'SMTP Server' }}</label>
                          <input type="text" v-model="emailConfigForm.smtp_server" class="mt-1 block w-full border border-slate-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                        </div>
                        <div>
                          <label class="block text-sm font-medium text-slate-700">{{ currentLanguage === 'zh' ? '端口' : 'Port' }}</label>
                          <input type="number" v-model="emailConfigForm.smtp_port" class="mt-1 block w-full border border-slate-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                        </div>
                      </div>

                      <div>
                        <label class="block text-sm font-medium text-slate-700">{{ currentLanguage === 'zh' ? '用户名' : 'Username' }}</label>
                        <input type="text" v-model="emailConfigForm.smtp_username" class="mt-1 block w-full border border-slate-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                      </div>

                      <div>
                        <label class="block text-sm font-medium text-slate-700">{{ currentLanguage === 'zh' ? '密码' : 'Password' }}</label>
                        <input type="password" v-model="emailConfigForm.smtp_password" class="mt-1 block w-full border border-slate-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                      </div>

                      <div class="grid grid-cols-2 gap-4">
                        <div>
                          <label class="block text-sm font-medium text-slate-700">{{ currentLanguage === 'zh' ? '发件人邮箱' : 'Sender Email' }}</label>
                          <input type="email" v-model="emailConfigForm.sender_email" class="mt-1 block w-full border border-slate-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                        </div>
                        <div>
                          <label class="block text-sm font-medium text-slate-700">{{ currentLanguage === 'zh' ? '发件人名称' : 'Sender Name' }}</label>
                          <input type="text" v-model="emailConfigForm.sender_name" class="mt-1 block w-full border border-slate-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                        </div>
                      </div>

                      <div class="flex items-center">
                        <input id="use-tls" type="checkbox" v-model="emailConfigForm.use_tls" class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-slate-300 rounded">
                        <label for="use-tls" class="ml-2 block text-sm text-slate-900">{{ currentLanguage === 'zh' ? '使用 TLS' : 'Use TLS' }}</label>
                      </div>

                      <div class="pt-4 space-y-3">
                        <button 
                          @click="handleTestConnection"
                          :disabled="emailSending"
                          class="w-full flex justify-center items-center py-2 px-4 border border-slate-300 rounded-md shadow-sm text-sm font-medium text-slate-700 bg-white hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                        >
                          <svg v-if="!emailSending" class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <Loader2 v-else class="w-4 h-4 mr-2 animate-spin" />
                          {{ emailSending ? (currentLanguage === 'zh' ? '测试中...' : 'Testing...') : (currentLanguage === 'zh' ? '🧪 测试连接' : '🧪 Test Connection') }}
                        </button>
                        
                        <button 
                          @click="saveEmailConfig"
                          :disabled="emailSending"
                          class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                        >
                          {{ currentLanguage === 'zh' ? '💾 保存配置' : '💾 Save Configuration' }}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

              </div>
            </div>

            <!-- Integrated Voiceover Content -->
            <div v-else-if="activeTab === 'integrated'" class="h-full flex flex-col">
              <div class="mb-8 border-b border-slate-50 pb-6 flex justify-between items-end">
                <div>
                  <h2 class="text-xl font-medium text-slate-700 mb-2">{{ t('integratedVoiceover') }}</h2>
                  <p class="text-slate-500 font-light">
                    {{ t('integratedVoiceoverDesc') }}
                  </p>
                </div>
                <button
                  @click="showIntegratedHistory = true; fetchIntegratedHistory()"
                  class="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors text-sm font-medium"
                >
                  <Clock class="w-4 h-4" />
                  {{ t('viewHistory') }}
                </button>
              </div>

              <!-- Upload Form (if no task running) -->
              <div v-if="!integratedTaskId" class="space-y-6">
                <!-- Parameters Form -->
                <div class="bg-slate-50/50 rounded-xl border border-slate-100 p-6">
                  <div class="space-y-4">
                    <!-- Topic Hint -->
                    <div>
                      <label class="block text-sm font-medium text-slate-700 mb-2">
                        {{ t('topicHint') }} <span class="text-red-500">*</span>
                      </label>
                      <input
                        v-model="integratedForm.topic_hint"
                        type="text"
                        :placeholder="t('topicPlaceholder')"
                        class="w-full px-4 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-sm"
                      />
                    </div>

                    <!-- Speaker Info -->
                    <div class="grid grid-cols-2 gap-4">
                      <div>
                        <label class="block text-sm font-medium text-slate-700 mb-2">{{ t('speakerAffiliation') }}</label>
                        <input
                          v-model="integratedForm.speaker_affiliation"
                          type="text"
                          placeholder="VoxChina"
                          class="w-full px-4 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-sm"
                        />
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-slate-700 mb-2">{{ t('speakerName') }}</label>
                        <input
                          v-model="integratedForm.speaker_name"
                          type="text"
                          placeholder="Speaker"
                          class="w-full px-4 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-sm"
                        />
                      </div>
                    </div>

                    <!-- Structure & Options -->
                    <div class="grid grid-cols-3 gap-4">
                      <div>
                        <label class="block text-sm font-medium text-slate-700 mb-2">{{ t('structurePreference') }}</label>
                        <select
                          v-model="integratedForm.style_preference"
                          class="w-full px-4 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-sm"
                        >
                          <option value="">{{ t('autoSelect') }}</option>
                          <option value="S1">S1 - Three Dimensions</option>
                          <option value="S2">S2 - Timeline</option>
                          <option value="S3">S3 - Status-Mechanism-Strategy</option>
                          <option value="S4">S4 - Mechanism Chain</option>
                        </select>
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-slate-700 mb-2">
                          {{ currentLanguage === 'zh' ? '字数限制' : 'Word Limit' }}
                          <span class="text-xs text-slate-400 ml-1">({{ currentLanguage === 'zh' ? '可选' : 'Optional' }})</span>
                        </label>
                        <select
                          v-model="integratedForm.word_limit"
                          class="w-full px-4 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-sm"
                        >
                          <option :value="null">{{ currentLanguage === 'zh' ? '默认（推荐）' : 'Default (Recommended)' }}</option>
                          <option :value="2000">2000 {{ currentLanguage === 'zh' ? '字' : 'words' }}</option>
                          <option :value="3000">3000 {{ currentLanguage === 'zh' ? '字' : 'words' }}</option>
                          <option :value="4000">4000 {{ currentLanguage === 'zh' ? '字' : 'words' }}</option>
                        </select>
                      </div>
                      <div class="flex items-end">
                        <label class="flex items-center space-x-2 cursor-pointer">
                          <input
                            v-model="integratedForm.include_vox_intro"
                            type="checkbox"
                            class="w-4 h-4 text-indigo-600 border-slate-300 rounded focus:ring-2 focus:ring-indigo-500/20"
                          />
                          <span class="text-sm font-medium text-slate-700">{{ t('includeVoxIntro') }}</span>
                        </label>
                      </div>
                    </div>

                    <!-- File Upload -->
                    <div>
                      <label class="block text-sm font-medium text-slate-700 mb-2">
                        {{ t('uploadDocuments') }} <span class="text-red-500">*</span>
                        <span class="text-xs text-slate-500 ml-2">{{ t('supportedFormats') }}</span>
                      </label>
                      <div
                        @click="($refs.integratedFileInput as HTMLInputElement)?.click()"
                        @dragover.prevent="isDraggingIntegrated = true"
                        @dragleave.prevent="isDraggingIntegrated = false"
                        @drop.prevent="handleIntegratedFileDrop"
                        :class="[
                          'border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all',
                          isDraggingIntegrated ? 'border-indigo-500 bg-indigo-50' : 'border-slate-200 hover:border-indigo-400'
                        ]"
                      >
                        <Upload class="w-10 h-10 mx-auto text-slate-400 mb-3" />
                        <p class="text-sm text-slate-600 mb-1">{{ t('clickOrDrag') }}</p>
                        <p class="text-xs text-slate-400">{{ t('multipleFiles') }}</p>
                      </div>
                      <input
                        ref="integratedFileInput"
                        type="file"
                        multiple
                        accept=".docx,.doc,.pdf"
                        @change="handleIntegratedFileSelect"
                        class="hidden"
                      />

                      <!-- File List -->
                      <div v-if="integratedFiles.length > 0" class="mt-4 space-y-2">
                        <div
                          v-for="(file, index) in integratedFiles"
                          :key="index"
                          class="flex items-center justify-between p-3 bg-white rounded-lg border border-slate-200"
                        >
                          <div class="flex items-center space-x-3">
                            <FileText class="w-5 h-5 text-indigo-600" />
                            <span class="text-sm text-slate-700">{{ file.name }}</span>
                            <span class="text-xs text-slate-400">({{ formatFileSize(file.size) }})</span>
                          </div>
                          <button
                            @click="removeIntegratedFile(index)"
                            class="text-red-500 hover:text-red-700 transition-colors"
                          >
                            <Trash2 class="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>

                    <!-- Submit Buttons -->
                    <div class="flex justify-end space-x-3 pt-4">
                      <button
                        @click="resetIntegratedForm"
                        class="px-6 py-2.5 text-slate-600 hover:text-slate-800 transition-colors text-sm font-medium"
                      >
                        {{ t('reset') }}
                      </button>
                      <button
                        @click="submitIntegratedTask"
                        :disabled="integratedSubmitting || !integratedForm.topic_hint.trim() || integratedFiles.length === 0"
                        :class="[
                          'px-6 py-2.5 rounded-lg font-medium transition-all text-sm',
                          integratedForm.topic_hint.trim() && integratedFiles.length > 0 && !integratedSubmitting
                            ? 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-lg shadow-indigo-200/50'
                            : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                        ]"
                      >
                        <span v-if="!integratedSubmitting">{{ t('startGeneration') }}</span>
                        <span v-else class="flex items-center">
                          <Loader2 class="w-4 h-4 mr-2 animate-spin" />
                          {{ t('processing') }}
                        </span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Processing/Result View -->
              <div v-else class="space-y-6">
                <!-- Progress (if processing) -->
                <div v-if="integratedStatus && integratedStatus.status === 'processing'" class="bg-white rounded-xl border border-slate-100 p-8">
                  <div class="text-center">
                    <div class="inline-flex items-center justify-center w-16 h-16 bg-indigo-50 rounded-full mb-4">
                      <Loader2 class="w-8 h-8 text-indigo-600 animate-spin" />
                    </div>
                    <h3 class="text-lg font-semibold text-slate-800 mb-2">{{ t('generating') }}</h3>
                    <p class="text-sm text-slate-600 mb-2">{{ t('currentStep') }}: {{ getStepName(integratedStatus.current_step) }}</p>
                    <p class="text-xs text-slate-400 mb-6">Task ID: {{ integratedTaskId }}</p>
                    
                    <div class="w-full bg-slate-100 rounded-full h-3 mb-2">
                      <div
                        class="bg-indigo-600 h-3 rounded-full transition-all duration-500"
                        :style="{ width: integratedStatus.progress + '%' }"
                      ></div>
                    </div>
                    <p class="text-xs text-slate-500 mb-4">{{ integratedStatus.progress }}%</p>
                    
                    <!-- Manual Refresh Button -->
                    <button
                      @click="pollIntegratedStatus"
                      class="mt-4 px-4 py-2 text-sm bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-lg transition-colors inline-flex items-center"
                    >
                      <RefreshCw class="w-4 h-4 mr-2" />
                      Check Status Now
                    </button>
                  </div>
                </div>

                <!-- Results Tabs -->
                <div v-if="integratedResult && integratedStatus.status === 'completed'" class="bg-white rounded-xl border border-slate-100 overflow-hidden">
                  <!-- Tab Headers -->
                  <div class="flex border-b border-slate-100 bg-slate-50 overflow-x-auto">
                    <button
                      v-for="tab in [
                        { id: 'style', name: t('styleProfile') },
                        { id: 'evidence', name: t('evidenceLedger') },
                        { id: 'assets', name: t('visualAssets') },
                        { id: 'structure', name: t('structure') },
                        { id: 'review', name: t('reviewVersion') },
                        { id: 'final', name: t('finalVersion') }
                      ]"
                      :key="tab.id"
                      @click="integratedResultTab = tab.id"
                      :class="[
                        'px-6 py-4 text-sm font-medium transition-all whitespace-nowrap',
                        integratedResultTab === tab.id
                          ? 'text-indigo-600 border-b-2 border-indigo-600 bg-white'
                          : 'text-slate-600 hover:text-slate-800'
                      ]"
                    >
                      {{ tab.name }}
                    </button>
                  </div>

                  <!-- Tab Content -->
                  <div class="p-6 max-h-[600px] overflow-y-auto">
                    <!-- Style Profile -->
                    <div v-if="integratedResultTab === 'style'" class="space-y-4">
                      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <!-- VOX Intro -->
                        <div class="bg-white rounded-lg border border-slate-200 p-4">
                          <div class="text-xs font-medium text-slate-500 uppercase mb-2">{{ t('voxIntro') }}</div>
                          <div class="flex items-center space-x-2">
                            <span :class="[
                              'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium',
                              integratedResult.style_profile?.enable_vox_intro 
                                ? 'bg-green-100 text-green-700' 
                                : 'bg-slate-100 text-slate-600'
                            ]">
                              {{ integratedResult.style_profile?.enable_vox_intro ? '✓ ' + t('enabled') : '✗ ' + t('disabled') }}
                            </span>
                          </div>
                        </div>
                        
                        <!-- Main Structure -->
                        <div class="bg-white rounded-lg border border-slate-200 p-4">
                          <div class="text-xs font-medium text-slate-500 uppercase mb-2">{{ t('mainStructure') }}</div>
                          <div class="flex items-center space-x-2">
                            <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-700">
                              {{ integratedResult.style_profile?.main_structure || 'S3' }}
                            </span>
                            <span class="text-sm text-slate-600">
                              {{ getStructureName(integratedResult.style_profile?.main_structure) }}
                            </span>
                          </div>
                        </div>
                        
                        <!-- Figure Style -->
                        <div class="bg-white rounded-lg border border-slate-200 p-4">
                          <div class="text-xs font-medium text-slate-500 uppercase mb-2">{{ t('figureStyle') }}</div>
                          <div class="text-sm text-slate-700">
                            {{ integratedResult.style_profile?.figure_style || 'B' }}
                          </div>
                        </div>
                      </div>
                      
                      <!-- Rules Section -->
                      <div class="bg-white rounded-lg border border-slate-200 p-4">
                        <div class="text-xs font-medium text-slate-500 uppercase mb-3">{{ t('styleRules') }}</div>
                        <div class="space-y-2">
                          <div
                            v-for="(rule, index) in integratedResult.style_profile?.rules || []"
                            :key="index"
                            class="flex items-start space-x-3 p-3 bg-slate-50 rounded-lg"
                          >
                            <span class="flex-shrink-0 w-6 h-6 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center text-xs font-medium">
                              {{ index + 1 }}
                            </span>
                            <p class="text-sm text-slate-700 leading-relaxed flex-1">{{ rule }}</p>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Evidence Ledger -->
                    <div v-else-if="integratedResultTab === 'evidence'" class="space-y-4">
                      <div
                        v-for="(ledger, index) in integratedResult.evidence_ledger"
                        :key="index"
                        class="bg-slate-50 rounded-lg p-4"
                      >
                        <div class="flex items-center justify-between mb-3">
                          <h4 class="font-semibold text-slate-800">{{ ledger.doc_id }}: {{ ledger.title }}</h4>
                          <button
                            @click="openDocumentDetail(ledger.doc_id)"
                            class="text-xs px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                            :title="currentLanguage === 'zh' ? '查看原文' : 'View Source'"
                          >
                            {{ currentLanguage === 'zh' ? '📄 查看原文' : '📄 View Source' }}
                          </button>
                        </div>
                        <div class="space-y-2">
                          <div
                            v-for="finding in ledger.findings"
                            :key="finding.finding_index"
                            class="bg-white rounded-lg p-3 border border-slate-200 text-sm hover:border-indigo-300 transition-colors"
                          >
                            <div class="flex items-start justify-between mb-2">
                              <span class="text-xs font-medium text-indigo-600 bg-indigo-50 px-2 py-1 rounded">{{ finding.type }}</span>
                              <div class="flex items-center space-x-2">
                                <span class="text-xs text-slate-400">#{{ finding.finding_index }}</span>
                                <button
                                  @click="openDocumentDetail(finding.source_doc_id || ledger.doc_id)"
                                  class="text-xs text-blue-600 hover:text-blue-700 hover:underline"
                                  :title="currentLanguage === 'zh' ? '回溯原文' : 'Trace to source'"
                                >
                                  {{ currentLanguage === 'zh' ? '↗ 原文' : '↗ Source' }}
                                </button>
                              </div>
                            </div>
                            <p class="text-slate-700 mb-2">{{ finding.claim }}</p>
                            <div v-if="finding.numbers && finding.numbers.length > 0" class="flex flex-wrap gap-1 mt-2">
                              <span
                                v-for="(num, idx) in finding.numbers"
                                :key="idx"
                                class="text-xs px-2 py-0.5 bg-amber-50 text-amber-700 rounded border border-amber-200 font-mono"
                              >
                                {{ num }}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Visual Assets -->
                    <div v-else-if="integratedResultTab === 'assets'">
                      <div v-if="integratedResult.visual_asset_ledger" style="display:none">
                        {{ console.log('[Visual Assets] Ledger:', integratedResult.visual_asset_ledger) }}
                        {{ console.log('[Visual Assets] Assets count:', integratedResult.visual_asset_ledger.assets?.length) }}
                        {{ integratedResult.visual_asset_ledger.assets?.forEach((asset: any, idx: number) => {
                          console.log(`[Visual Assets] Asset ${idx}:`, asset.asset_id, 'image_url:', asset.image_url);
                        }) }}
                      </div>
                      <div v-if="!integratedResult.visual_asset_ledger?.assets || integratedResult.visual_asset_ledger.assets.length === 0" 
                        class="bg-slate-50 rounded-lg p-12 text-center border-2 border-dashed border-slate-200">
                        <div class="text-slate-400 mb-2">
                          <svg xmlns="http://www.w3.org/2000/svg" class="w-12 h-12 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                          <p class="text-sm">{{ t('noVisualAssets') }}</p>
                        </div>
                      </div>
                      
                      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div
                          v-for="asset in integratedResult.visual_asset_ledger.assets"
                          :key="asset.asset_id"
                          class="bg-white rounded-lg border border-slate-200 overflow-hidden hover:border-indigo-300 hover:shadow-md transition-all"
                        >
                          <!-- Asset Header -->
                          <div class="bg-gradient-to-r from-slate-50 to-slate-100 px-4 py-3 border-b border-slate-200">
                            <div class="flex items-center justify-between">
                              <span class="text-sm font-bold text-slate-800">{{ asset.asset_id }}</span>
                              <span
                                :class="[
                                  'text-xs px-2.5 py-1 rounded-full font-medium',
                                  asset.asset_type === 'FIG' ? 'bg-purple-100 text-purple-700' : 'bg-green-100 text-green-700'
                                ]"
                              >
                                {{ asset.asset_type }}
                              </span>
                            </div>
                          </div>
                          
                          <!-- Asset Content -->
                          <div class="p-4 space-y-3">
                            <!-- Image Preview (for FIG type) -->
                            <div v-if="asset.image_url && asset.asset_type === 'FIG'" class="mb-3">
                              <img 
                                :src="getImageUrl(asset.image_url)" 
                                :alt="asset.caption_or_title || 'Image'" 
                                class="w-full h-auto rounded-lg border border-slate-200 object-contain max-h-48"
                                @error="handleImageError"
                                loading="lazy"
                              />
                            </div>
                            <div v-else-if="asset.asset_type === 'FIG' && !asset.image_url" class="mb-3 bg-slate-100 rounded-lg p-8 text-center">
                              <svg xmlns="http://www.w3.org/2000/svg" class="w-16 h-16 mx-auto text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                              </svg>
                              <p class="text-xs text-slate-400 mt-2">{{ currentLanguage === 'zh' ? '图片未能提取' : 'Image not extracted' }}</p>
                            </div>
                            
                            <!-- Table Preview (for TAB type) -->
                            <div v-else-if="asset.asset_type === 'TAB'" class="mb-3">
                              <!-- If table has raw_text or content -->
                              <div v-if="asset.raw_text || asset.table_content" class="bg-slate-50 rounded-lg border border-slate-200 overflow-hidden">
                                <div class="bg-slate-100 px-3 py-2 border-b border-slate-200 flex items-center">
                                  <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 mr-2 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                  </svg>
                                  <span class="text-xs font-medium text-slate-600">{{ currentLanguage === 'zh' ? '表格内容' : 'Table Content' }}</span>
                                </div>
                                <div class="p-3 max-h-48 overflow-auto">
                                  <pre class="text-xs text-slate-600 whitespace-pre-wrap font-mono">{{ asset.raw_text || asset.table_content }}</pre>
                                </div>
                              </div>
                              <!-- If table has structured data -->
                              <div v-else-if="asset.table_data && asset.table_data.length > 0" class="overflow-x-auto">
                                <table class="min-w-full text-xs border border-slate-200 rounded-lg overflow-hidden">
                                  <thead class="bg-slate-100">
                                    <tr>
                                      <th v-for="(header, idx) in (asset.table_data[0] || [])" :key="idx" class="px-2 py-1.5 text-left font-medium text-slate-700 border-b border-slate-200">
                                        {{ header }}
                                      </th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    <tr v-for="(row, rowIdx) in asset.table_data.slice(1)" :key="rowIdx" class="hover:bg-slate-50">
                                      <td v-for="(cell, cellIdx) in row" :key="cellIdx" class="px-2 py-1.5 text-slate-600 border-b border-slate-100">
                                        {{ cell }}
                                      </td>
                                    </tr>
                                  </tbody>
                                </table>
                              </div>
                              <!-- If table has location_anchor (fallback for table content) -->
                              <div v-else-if="asset.location_anchor" class="bg-slate-50 rounded-lg border border-slate-200 overflow-hidden">
                                <div class="bg-slate-100 px-3 py-2 border-b border-slate-200 flex items-center">
                                  <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 mr-2 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                  </svg>
                                  <span class="text-xs font-medium text-slate-600">{{ currentLanguage === 'zh' ? '表格预览' : 'Table Preview' }}</span>
                                </div>
                                <div class="p-3 max-h-48 overflow-auto">
                                  <table v-if="asset.location_anchor.includes('|')" class="min-w-full text-xs border-collapse">
                                    <tbody>
                                      <tr v-for="(cell, idx) in asset.location_anchor.split('|').filter((c: string) => c.trim())" :key="idx" class="border-b border-slate-200">
                                        <td class="px-2 py-1.5 text-slate-600 font-mono">{{ cell.trim() }}</td>
                                      </tr>
                                    </tbody>
                                  </table>
                                  <pre v-else class="text-xs text-slate-600 whitespace-pre-wrap font-mono">{{ asset.location_anchor }}</pre>
                                </div>
                              </div>
                              <!-- Fallback: show placeholder -->
                              <div v-else class="bg-green-50 rounded-lg p-6 text-center border border-green-200">
                                <svg xmlns="http://www.w3.org/2000/svg" class="w-12 h-12 mx-auto text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                </svg>
                                <p class="text-xs text-green-600 mt-2">{{ currentLanguage === 'zh' ? '表格数据' : 'Table Data' }}</p>
                              </div>
                            </div>
                            
                            <!-- Caption/Title -->
                            <div>
                              <div class="text-xs font-medium text-slate-500 uppercase mb-1">{{ t('caption') }}</div>
                              <p class="text-sm text-slate-700 font-medium">{{ asset.caption_or_title || t('noCaption') }}</p>
                            </div>
                            
                            <!-- Key Numbers -->
                            <div v-if="filterValidKeyNumbers(asset.key_numbers).length > 0">
                              <div class="text-xs font-medium text-slate-500 uppercase mb-2">{{ t('keyNumbers') }}</div>
                              <div class="flex flex-wrap gap-2">
                                <span
                                  v-for="(num, idx) in filterValidKeyNumbers(asset.key_numbers)"
                                  :key="idx"
                                  class="inline-flex items-center px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs font-mono"
                                >
                                  {{ num }}
                                </span>
                              </div>
                            </div>
                            
                            <!-- Takeaway Claim -->
                            <div v-if="asset.takeaway_claim">
                              <div class="text-xs font-medium text-slate-500 uppercase mb-1">{{ t('takeaway') }}</div>
                              <p class="text-sm text-slate-600 italic">{{ asset.takeaway_claim }}</p>
                            </div>
                            
                            <!-- Editing Instruction -->
                            <div v-if="asset.editing_instruction" class="pt-3 border-t border-slate-100">
                              <div class="text-xs font-medium text-slate-500 uppercase mb-1">{{ t('editingInstruction') }}</div>
                              <p class="text-xs text-slate-600 bg-amber-50 border border-amber-200 rounded px-2 py-1">
                                💡 {{ asset.editing_instruction }}
                              </p>
                            </div>
                            
                            <!-- Linked Findings -->
                            <div v-if="asset.linked_findings && asset.linked_findings.length > 0" class="pt-3 border-t border-slate-100">
                              <div class="text-xs font-medium text-slate-500 uppercase mb-2">{{ t('linkedFindings') }}</div>
                              <div class="flex flex-wrap gap-1">
                                <span
                                  v-for="findingId in asset.linked_findings"
                                  :key="findingId"
                                  class="inline-flex items-center px-2 py-0.5 bg-indigo-50 text-indigo-600 rounded text-xs"
                                >
                                  #{{ findingId }}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Structure -->
                    <div v-else-if="integratedResultTab === 'structure'" class="space-y-4">
                      <!-- Structure Overview -->
                      <div class="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-100 p-4">
                        <div class="flex items-center justify-between">
                          <div>
                            <div class="text-xs font-medium text-indigo-600 uppercase mb-1">{{ t('scriptStructure') }}</div>
                            <div class="text-sm text-slate-700">
                              {{ t('totalSections') }}: <span class="font-semibold">{{ integratedResult.structure?.sections?.length || 0 }}</span>
                            </div>
                          </div>
                          <div class="text-right">
                            <div class="text-xs text-slate-500 mb-1">{{ t('structureType') }}</div>
                            <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-700">
                              {{ integratedResult.structure?.structure_type || integratedResult.structure?.main_structure || 'S3' }}
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      <!-- Sections -->
                      <div class="space-y-3">
                        <div
                          v-for="(section, index) in integratedResult.structure?.sections || []"
                          :key="index"
                          class="bg-white rounded-lg border border-slate-200 overflow-hidden hover:border-indigo-300 transition-colors"
                        >
                          <div class="bg-gradient-to-r from-slate-50 to-slate-100 px-4 py-3 border-b border-slate-200">
                            <div class="flex items-center justify-between">
                              <div class="flex items-center space-x-3">
                                <span class="flex-shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-lg flex items-center justify-center text-sm font-bold">
                                  {{ section.section_id || index + 1 }}
                                </span>
                                <h4 class="font-semibold text-slate-800">{{ section.title || section.section_title || t('untitled') }}</h4>
                              </div>
                              <div class="flex items-center space-x-2">
                                <span v-if="section.related_docs && section.related_docs.length > 0" class="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
                                  {{ section.related_docs.length }} {{ t('docs') }}
                                </span>
                                <span v-if="section.related_assets && section.related_assets.length > 0" class="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded">
                                  {{ section.related_assets.length }} {{ t('assets') }}
                                </span>
                              </div>
                            </div>
                          </div>
                          
                          <!-- Section Content -->
                          <div class="p-4 space-y-3">
                            <!-- Related Documents -->
                            <div v-if="section.related_docs && section.related_docs.length > 0">
                              <div class="text-xs font-medium text-slate-500 uppercase mb-2">{{ t('relatedDocs') }}</div>
                              <div class="flex flex-wrap gap-2">
                                <button
                                  v-for="docId in section.related_docs"
                                  :key="docId"
                                  @click="openDocumentDetail(docId)"
                                  class="inline-flex items-center px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs font-medium hover:bg-blue-100 hover:shadow-sm transition-all cursor-pointer"
                                  :title="currentLanguage === 'zh' ? '点击查看文档详情' : 'Click to view document details'"
                                >
                                  📄 {{ docId }}
                                </button>
                              </div>
                            </div>
                            
                            <!-- Related Assets -->
                            <div v-if="section.related_assets && section.related_assets.length > 0" class="pt-2">
                              <div class="text-xs font-medium text-slate-500 uppercase mb-2">{{ t('relatedAssets') }}</div>
                              <div class="flex flex-wrap gap-2">
                                <button
                                  v-for="assetId in section.related_assets"
                                  :key="assetId"
                                  @click="openAssetDetail(assetId)"
                                  class="inline-flex items-center px-2 py-1 bg-purple-50 text-purple-700 rounded text-xs font-medium hover:bg-purple-100 hover:shadow-sm transition-all cursor-pointer"
                                  :title="currentLanguage === 'zh' ? '点击查看资产详情' : 'Click to view asset details'"
                                >
                                  {{ assetId.includes('FIG') ? '📊' : '📋' }} {{ assetId }}
                                </button>
                              </div>
                            </div>
                            
                            <!-- Goal (if available) -->
                            <div v-if="section.goal" class="pt-2 border-t border-slate-100">
                              <div class="text-xs font-medium text-slate-500 uppercase mb-1">{{ t('sectionGoal') }}</div>
                              <p class="text-sm text-slate-600 italic">{{ section.goal }}</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Review Version -->
                    <div v-else-if="integratedResultTab === 'review'">
                      <div class="bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg border border-amber-200 p-4 mb-4">
                        <div class="flex items-center justify-between">
                          <div class="flex items-center space-x-3">
                            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            <div>
                              <div class="text-sm font-semibold text-amber-900">{{ t('reviewVersion') }}</div>
                              <div class="text-xs text-amber-700">{{ t('reviewVersionDesc') }}</div>
                            </div>
                          </div>
                          <button
                            @click="copyIntegratedContent(integratedResult.script_review)"
                            class="px-4 py-2 text-sm bg-white hover:bg-amber-50 text-amber-700 border border-amber-300 rounded-lg transition-colors font-medium"
                          >
                            📋 {{ t('copy') }}
                          </button>
                        </div>
                      </div>
                      <div class="bg-white rounded-lg border border-slate-200 p-8 shadow-sm">
                        <div class="script-content" v-html="formatScriptText(integratedResult.script_review)" @click="handleScriptContentClick"></div>
                      </div>
                    </div>

                    <!-- Final Version -->
                    <div v-else-if="integratedResultTab === 'final'">
                      <div class="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-200 p-4 mb-4">
                        <div class="flex items-center justify-between">
                          <div class="flex items-center space-x-3">
                            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <div>
                              <div class="text-sm font-semibold text-indigo-900">{{ t('finalVersion') }}</div>
                              <div class="text-xs text-indigo-700">{{ t('finalVersionDesc') }}</div>
                            </div>
                          </div>
                          <div class="flex items-center space-x-2">
                            <button
                              @click="openIntegratedTagModal"
                              :disabled="isSavingIntegratedToKB"
                              class="px-4 py-2 text-sm bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors font-medium shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              <span v-if="isSavingIntegratedToKB">⏳ {{ currentLanguage === 'zh' ? '保存中...' : 'Saving...' }}</span>
                              <span v-else>💾 {{ currentLanguage === 'zh' ? '存入知识库' : 'Save to KB' }}</span>
                            </button>
                            <button
                              @click="downloadIntegratedFinal"
                              class="px-4 py-2 text-sm bg-white hover:bg-indigo-50 text-indigo-700 border border-indigo-300 rounded-lg transition-colors font-medium shadow-sm"
                            >
                              📥 PDF
                            </button>
                            <button
                              @click="downloadIntegratedWord"
                              class="px-4 py-2 text-sm bg-white hover:bg-blue-50 text-blue-700 border border-blue-300 rounded-lg transition-colors font-medium shadow-sm"
                            >
                              📄 Word
                            </button>
                            <button
                              v-if="!isEditingIntegratedFinal"
                              @click="startEditIntegratedFinal"
                              class="px-4 py-2 text-sm bg-amber-500 hover:bg-amber-600 text-white rounded-lg transition-colors font-medium shadow-sm"
                            >
                              ✏️ {{ currentLanguage === 'zh' ? '编辑' : 'Edit' }}
                            </button>
                            <template v-else>
                              <button
                                @click="saveEditIntegratedFinal"
                                class="px-4 py-2 text-sm bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors font-medium shadow-sm"
                              >
                                ✅ {{ currentLanguage === 'zh' ? '保存' : 'Save' }}
                              </button>
                              <button
                                @click="cancelEditIntegratedFinal"
                                class="px-4 py-2 text-sm bg-slate-400 hover:bg-slate-500 text-white rounded-lg transition-colors font-medium shadow-sm"
                              >
                                ❌ {{ currentLanguage === 'zh' ? '取消' : 'Cancel' }}
                              </button>
                            </template>
                            <button
                              @click="copyIntegratedContent(integratedResult.script_final)"
                              class="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors font-medium shadow-sm"
                            >
                              📋 {{ t('copy') }}
                            </button>
                          </div>
                        </div>
                      </div>
                      <div class="bg-white rounded-lg border border-slate-200 p-8 shadow-sm">
                        <!-- 编辑模式 -->
                        <textarea
                          v-if="isEditingIntegratedFinal"
                          v-model="editedIntegratedFinal"
                          class="w-full h-96 p-4 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-mono text-sm resize-y"
                          :placeholder="currentLanguage === 'zh' ? '编辑口播稿内容...' : 'Edit script content...'"
                        ></textarea>
                        <!-- 显示模式 -->
                        <div v-else class="script-content" v-html="formatScriptText(integratedResult.script_final)" @click="handleScriptContentClick"></div>
                      </div>
                      
                      <!-- Oral Broadcast Section for Final Version -->
                      <div class="mt-8 pt-6 border-t border-slate-100">
                        <h4 class="text-sm font-semibold text-slate-700 mb-4 flex items-center">
                          <svg class="w-4 h-4 mr-2 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                          </svg>
                          {{ t('oralBroadcast') }}
                        </h4>
                        
                        <div class="bg-slate-50 rounded-xl p-4 border border-slate-100">
                          <div v-if="voices.length === 0" class="text-center py-4">
                            <p class="text-sm text-slate-500">{{ t('loadingVoices') }}</p>
                          </div>
                          <div v-else class="flex flex-col md:flex-row gap-4 items-end">
                            <div class="flex-1 w-full">
                              <label class="block text-xs font-medium text-slate-500 mb-1">{{ t('selectVoice') }}</label>
                              <select v-model="selectedIntegratedVoiceId" class="w-full text-sm rounded-lg border-slate-200 focus:border-indigo-500 focus:ring-indigo-500">
                                <option v-for="voice in voices" :key="voice.id" :value="voice.id">
                                  {{ voice.name }}
                                </option>
                              </select>
                            </div>
                            
                            <button 
                              @click="generateIntegratedAudio"
                              :disabled="isGeneratingIntegratedAudio || !selectedIntegratedVoiceId"
                              class="w-full md:w-auto px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center whitespace-nowrap"
                            >
                              <Loader2 v-if="isGeneratingIntegratedAudio" class="w-4 h-4 mr-2 animate-spin" />
                              <span v-else class="flex items-center">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                {{ t('generateAndPlay') }}
                              </span>
                            </button>
                          </div>
                          
                          <!-- Player Section -->
                          <div v-if="integratedAudioUrl" class="mt-4 pt-4 border-t border-slate-200">
                            <div class="flex items-center gap-4">
                              <audio controls :src="integratedAudioUrl" class="flex-1 h-10 w-full"></audio>
                              <a 
                                :href="integratedAudioUrl" 
                                :download="`integrated_broadcast_${Date.now()}.mp3`"
                                class="flex-shrink-0 p-2 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                                :title="t('downloadAudio')"
                              >
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                </svg>
                              </a>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Error Message -->
                <div v-if="integratedError" class="bg-gradient-to-br from-red-50 to-orange-50 border-2 border-red-200 rounded-xl p-6 shadow-sm">
                  <div class="flex items-start space-x-4">
                    <div class="flex-shrink-0">
                      <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div class="flex-1">
                      <h3 class="text-lg font-bold text-red-900 mb-2">{{ t('generationFailed') }}</h3>
                      <p class="text-sm text-red-800 mb-4 leading-relaxed">{{ integratedError }}</p>
                      
                      <!-- Helpful Tips -->
                      <div class="bg-white/60 rounded-lg p-4 mb-4 border border-red-200">
                        <div class="text-xs font-semibold text-red-900 mb-2">💡 {{ t('troubleshootingTips') }}</div>
                        <ul class="text-xs text-red-800 space-y-1.5 list-disc list-inside">
                          <li>{{ t('tip1') }}</li>
                          <li>{{ t('tip2') }}</li>
                          <li>{{ t('tip3') }}</li>
                        </ul>
                      </div>
                      
                      <!-- Action Buttons -->
                      <div class="flex space-x-3">
                        <button
                          @click="retryIntegratedGeneration"
                          class="px-5 py-2.5 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-all text-sm shadow-sm flex items-center space-x-2"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                          </svg>
                          <span>{{ t('retryGeneration') }}</span>
                        </button>
                        <button
                          @click="resetIntegratedForm"
                          class="px-5 py-2.5 bg-white border border-slate-300 text-slate-700 font-medium rounded-lg hover:bg-slate-50 transition-all text-sm"
                        >
                          {{ t('backToForm') }}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>

        </div>
      </div>
    </main>
    
    <!-- Integrated Voiceover Tag Selection Modal -->
    <div 
      v-if="showIntegratedTagModal" 
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showIntegratedTagModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden">
        <div class="p-6 border-b border-slate-200 bg-gradient-to-r from-green-50 to-emerald-50">
          <h3 class="text-lg font-semibold text-slate-800 flex items-center">
            <Tag class="w-5 h-5 mr-2 text-green-600" />
            {{ currentLanguage === 'zh' ? '选择标签后存入知识库' : 'Select Tags Before Saving' }}
          </h3>
          <p class="text-sm text-slate-500 mt-1">
            {{ currentLanguage === 'zh' ? '选择或添加标签，便于后续检索' : 'Select or add tags for easier retrieval' }}
          </p>
        </div>
        
        <div class="p-6 space-y-4">
          <!-- Generate Tags Button -->
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-slate-700">
              {{ currentLanguage === 'zh' ? '推荐标签' : 'Recommended Tags' }}
            </span>
            <button
              @click="fetchIntegratedRecommendedTags"
              :disabled="loadingIntegratedTags"
              class="text-xs text-green-600 hover:text-green-700 flex items-center"
            >
              <Loader2 v-if="loadingIntegratedTags" class="w-3 h-3 mr-1 animate-spin" />
              <RefreshCw v-else class="w-3 h-3 mr-1" />
              {{ loadingIntegratedTags ? (currentLanguage === 'zh' ? '生成中...' : 'Generating...') : (currentLanguage === 'zh' ? '生成推荐标签' : 'Generate Tags') }}
            </button>
          </div>
          
          <!-- Selected Tags -->
          <div v-if="integratedSelectedTags.length > 0" class="mb-3">
            <div class="text-xs text-slate-500 mb-2">{{ currentLanguage === 'zh' ? '已选标签:' : 'Selected:' }}</div>
            <div class="flex flex-wrap gap-2">
              <span 
                v-for="tag in integratedSelectedTags" 
                :key="tag"
                class="px-2.5 py-1 bg-green-100 text-green-800 text-xs rounded-full flex items-center cursor-pointer hover:bg-green-200"
                @click="toggleIntegratedTag(tag)"
              >
                {{ tag }}
                <X class="w-3 h-3 ml-1" />
              </span>
            </div>
          </div>
          
          <!-- Recommended Tags -->
          <div v-if="integratedRecommendedTags.length > 0">
            <div class="text-xs text-slate-500 mb-2">{{ currentLanguage === 'zh' ? '点击选择:' : 'Click to select:' }}</div>
            <div class="flex flex-wrap gap-2">
              <span 
                v-for="tag in integratedRecommendedTags.filter(t => !integratedSelectedTags.includes(t))" 
                :key="tag"
                class="px-2.5 py-1 bg-slate-100 text-slate-700 text-xs rounded-full cursor-pointer hover:bg-slate-200 transition-colors"
                @click="toggleIntegratedTag(tag)"
              >
                + {{ tag }}
              </span>
            </div>
          </div>
          
          <!-- Custom Tag Input -->
          <div class="flex items-center gap-2 pt-2 border-t border-slate-100">
            <input
              v-model="integratedCustomTag"
              type="text"
              :placeholder="currentLanguage === 'zh' ? '输入自定义标签...' : 'Enter custom tag...'"
              class="flex-1 px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/20 focus:border-green-500"
              @keyup.enter="addIntegratedCustomTag"
            />
            <button
              @click="addIntegratedCustomTag"
              :disabled="!integratedCustomTag.trim()"
              class="px-3 py-2 text-sm bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ currentLanguage === 'zh' ? '添加' : 'Add' }}
            </button>
          </div>
        </div>
        
        <!-- Footer -->
        <div class="p-6 border-t border-slate-200 bg-slate-50 flex items-center justify-end gap-3">
          <button
            @click="showIntegratedTagModal = false"
            class="px-4 py-2 text-sm text-slate-600 hover:text-slate-800 transition-colors"
          >
            {{ currentLanguage === 'zh' ? '取消' : 'Cancel' }}
          </button>
          <button
            @click="confirmSaveIntegratedToKB"
            :disabled="isSavingIntegratedToKB"
            class="px-4 py-2 text-sm bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            <span v-if="isSavingIntegratedToKB">{{ currentLanguage === 'zh' ? '保存中...' : 'Saving...' }}</span>
            <span v-else>{{ currentLanguage === 'zh' ? '确认保存' : 'Confirm Save' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Document Detail Modal -->
    <div 
      v-if="documentDetailOpen && selectedDocument" 
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="documentDetailOpen = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div class="p-6 border-b border-slate-200 flex items-center justify-between bg-gradient-to-r from-blue-50 to-indigo-50">
          <h3 class="text-lg font-semibold text-slate-800 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            {{ currentLanguage === 'zh' ? '文档详情' : 'Document Details' }}: {{ selectedDocument.doc_id }}
          </h3>
          <button 
            @click="documentDetailOpen = false"
            class="text-slate-400 hover:text-slate-600 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div class="flex-1 overflow-y-auto p-6 space-y-4">
          <!-- Document Title -->
          <div class="bg-gradient-to-r from-slate-50 to-slate-100 rounded-lg p-4 border border-slate-200">
            <div class="text-xs font-medium text-slate-500 uppercase mb-1">{{ currentLanguage === 'zh' ? '文档标题' : 'Document Title' }}</div>
            <h4 class="text-lg font-semibold text-slate-800">{{ selectedDocument.title || currentLanguage === 'zh' ? '无标题' : 'Untitled' }}</h4>
          </div>
          
          <!-- Document Stats -->
          <div class="grid grid-cols-3 gap-3">
            <div class="bg-blue-50 rounded-lg p-3 border border-blue-100">
              <div class="text-xs text-blue-600 mb-1">{{ currentLanguage === 'zh' ? '段落数' : 'Paragraphs' }}</div>
              <div class="text-xl font-bold text-blue-700">{{ selectedDocument.total_paragraphs || 0 }}</div>
            </div>
            <div class="bg-purple-50 rounded-lg p-3 border border-purple-100">
              <div class="text-xs text-purple-600 mb-1">{{ currentLanguage === 'zh' ? '表格数' : 'Tables' }}</div>
              <div class="text-xl font-bold text-purple-700">{{ selectedDocument.total_tables || 0 }}</div>
            </div>
            <div class="bg-green-50 rounded-lg p-3 border border-green-100">
              <div class="text-xs text-green-600 mb-1">{{ currentLanguage === 'zh' ? '图片数' : 'Images' }}</div>
              <div class="text-xl font-bold text-green-700">{{ selectedDocument.images?.length || 0 }}</div>
            </div>
          </div>
          
          <!-- Document Content Preview -->
          <div class="bg-white rounded-lg border border-slate-200">
            <div class="bg-gradient-to-r from-slate-50 to-slate-100 px-4 py-3 border-b border-slate-200">
              <h5 class="text-sm font-semibold text-slate-700">{{ currentLanguage === 'zh' ? '内容预览' : 'Content Preview' }}</h5>
            </div>
            <div class="p-4 max-h-96 overflow-y-auto space-y-3">
              <div 
                v-for="(para, idx) in selectedDocument.paragraphs?.slice(0, 10)" 
                :key="idx"
                class="p-3 bg-slate-50 rounded-lg border border-slate-100 hover:border-slate-300 transition-colors"
              >
                <div class="flex items-start justify-between mb-2">
                  <span class="text-xs font-medium text-slate-500">
                    {{ currentLanguage === 'zh' ? '段落' : 'Para' }} #{{ para.paragraph_id }}
                  </span>
                  <span 
                    v-if="para.type === 'heading'"
                    class="text-xs px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded"
                  >
                    {{ currentLanguage === 'zh' ? '标题' : 'Heading' }} {{ para.heading_level || '' }}
                  </span>
                </div>
                <p class="text-sm text-slate-700 leading-relaxed">{{ para.text }}</p>
              </div>
              <div v-if="selectedDocument.paragraphs?.length > 10" class="text-center text-xs text-slate-400 py-2">
                {{ currentLanguage === 'zh' ? `还有 ${selectedDocument.paragraphs.length - 10} 个段落...` : `${selectedDocument.paragraphs.length - 10} more paragraphs...` }}
              </div>
            </div>
          </div>
          
          <!-- Images Preview -->
          <div v-if="selectedDocument.images && selectedDocument.images.length > 0" class="bg-white rounded-lg border border-slate-200">
            <div class="bg-gradient-to-r from-slate-50 to-slate-100 px-4 py-3 border-b border-slate-200">
              <h5 class="text-sm font-semibold text-slate-700">{{ currentLanguage === 'zh' ? '文档图片' : 'Document Images' }}</h5>
            </div>
            <div class="p-4 grid grid-cols-2 md:grid-cols-3 gap-3">
              <div 
                v-for="(img, idx) in selectedDocument.images" 
                :key="idx"
                class="relative group"
              >
                <img 
                  :src="getImageUrl(img.url)" 
                  :alt="`Image ${idx + 1}`"
                  class="w-full h-32 object-cover rounded-lg border border-slate-200 group-hover:border-blue-300 transition-colors"
                  @error="handleImageError"
                />
                <div class="absolute bottom-2 right-2 bg-black bg-opacity-60 text-white text-xs px-2 py-1 rounded">
                  {{ idx + 1 }}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="p-4 border-t border-slate-200 bg-slate-50 flex justify-end">
          <button 
            @click="documentDetailOpen = false"
            class="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors text-sm font-medium"
          >
            {{ currentLanguage === 'zh' ? '关闭' : 'Close' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Asset Detail Modal -->
    <div 
      v-if="assetDetailOpen && selectedAsset" 
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="assetDetailOpen = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div class="p-6 border-b border-slate-200 flex items-center justify-between bg-gradient-to-r from-purple-50 to-indigo-50">
          <h3 class="text-lg font-semibold text-slate-800 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 mr-2 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            {{ currentLanguage === 'zh' ? '资产详情' : 'Asset Details' }}: {{ selectedAsset.asset_id }}
          </h3>
          <button 
            @click="assetDetailOpen = false"
            class="text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X class="w-6 h-6" />
          </button>
        </div>
        
        <div class="flex-1 overflow-y-auto p-6 space-y-4">
          <!-- Asset Type Badge -->
          <div class="flex items-center gap-3">
            <span
              :class="[
                'text-sm px-3 py-1.5 rounded-full font-medium',
                selectedAsset.asset_type === 'FIG' ? 'bg-purple-100 text-purple-700' : 'bg-green-100 text-green-700'
              ]"
            >
              {{ selectedAsset.asset_type === 'FIG' ? (currentLanguage === 'zh' ? '图表' : 'Figure') : (currentLanguage === 'zh' ? '表格' : 'Table') }}
            </span>
          </div>
          
          <!-- Image Preview (for FIG) -->
          <div v-if="selectedAsset.image_url && selectedAsset.asset_type === 'FIG'" class="bg-slate-50 rounded-lg p-4 border border-slate-200">
            <img 
              :src="getImageUrl(selectedAsset.image_url)" 
              :alt="selectedAsset.caption_or_title || 'Asset Image'" 
              class="max-w-full h-auto rounded-lg border border-slate-200 mx-auto"
              @error="handleImageError"
            />
          </div>
          
          <!-- Table Content (for TAB) -->
          <div v-else-if="selectedAsset.asset_type === 'TAB'" class="bg-slate-50 rounded-lg border border-slate-200 overflow-hidden">
            <div class="bg-slate-100 px-4 py-3 border-b border-slate-200">
              <h5 class="text-sm font-semibold text-slate-700">{{ currentLanguage === 'zh' ? '表格内容' : 'Table Content' }}</h5>
            </div>
            <div class="p-4 max-h-64 overflow-auto">
              <pre v-if="selectedAsset.raw_text || selectedAsset.table_content" class="text-sm text-slate-600 whitespace-pre-wrap font-mono">{{ selectedAsset.raw_text || selectedAsset.table_content }}</pre>
              <template v-else-if="selectedAsset.location_anchor">
                <table v-if="selectedAsset.location_anchor.includes('|')" class="min-w-full text-sm border-collapse">
                  <tbody>
                    <tr v-for="(cell, idx) in selectedAsset.location_anchor.split('|').filter((c: string) => c.trim())" :key="idx" class="border-b border-slate-200">
                      <td class="px-3 py-2 text-slate-600 font-mono">{{ cell.trim() }}</td>
                    </tr>
                  </tbody>
                </table>
                <pre v-else class="text-sm text-slate-600 whitespace-pre-wrap font-mono">{{ selectedAsset.location_anchor }}</pre>
              </template>
              <p v-else class="text-sm text-slate-500 italic">{{ currentLanguage === 'zh' ? '无表格内容数据' : 'No table content data' }}</p>
            </div>
          </div>
          
          <!-- Caption/Title -->
          <div v-if="selectedAsset.caption_or_title" class="bg-white rounded-lg border border-slate-200 p-4">
            <div class="text-xs font-medium text-slate-500 uppercase mb-2">{{ currentLanguage === 'zh' ? '标题/说明' : 'Caption/Title' }}</div>
            <p class="text-slate-700 font-medium">{{ selectedAsset.caption_or_title }}</p>
          </div>
          
          <!-- Key Numbers -->
          <div v-if="filterValidKeyNumbers(selectedAsset.key_numbers).length > 0" class="bg-blue-50 rounded-lg border border-blue-200 p-4">
            <div class="text-xs font-medium text-blue-600 uppercase mb-2">{{ currentLanguage === 'zh' ? '关键数字' : 'Key Numbers' }}</div>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="(num, idx) in filterValidKeyNumbers(selectedAsset.key_numbers)"
                :key="idx"
                class="inline-flex items-center px-3 py-1.5 bg-white text-blue-700 rounded-lg text-sm font-mono border border-blue-200"
              >
                {{ num }}
              </span>
            </div>
          </div>
          
          <!-- Takeaway Claim -->
          <div v-if="selectedAsset.takeaway_claim" class="bg-amber-50 rounded-lg border border-amber-200 p-4">
            <div class="text-xs font-medium text-amber-600 uppercase mb-2">{{ currentLanguage === 'zh' ? '要点' : 'Takeaway' }}</div>
            <p class="text-slate-700 italic">{{ selectedAsset.takeaway_claim }}</p>
          </div>
          
          <!-- Editing Instruction -->
          <div v-if="selectedAsset.editing_instruction" class="bg-indigo-50 rounded-lg border border-indigo-200 p-4">
            <div class="text-xs font-medium text-indigo-600 uppercase mb-2">{{ currentLanguage === 'zh' ? '剪辑指示' : 'Editing Instruction' }}</div>
            <p class="text-slate-700">💡 {{ selectedAsset.editing_instruction }}</p>
          </div>
          
          <!-- Linked Findings -->
          <div v-if="selectedAsset.linked_findings && selectedAsset.linked_findings.length > 0" class="bg-slate-50 rounded-lg border border-slate-200 p-4">
            <div class="text-xs font-medium text-slate-500 uppercase mb-2">{{ currentLanguage === 'zh' ? '关联证据' : 'Linked Findings' }}</div>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="findingId in selectedAsset.linked_findings"
                :key="findingId"
                class="inline-flex items-center px-2 py-1 bg-indigo-100 text-indigo-700 rounded text-xs"
              >
                #{{ findingId }}
              </span>
            </div>
          </div>
        </div>
        
        <div class="p-4 border-t border-slate-200 bg-slate-50 flex justify-end">
          <button 
            @click="assetDetailOpen = false"
            class="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors text-sm font-medium"
          >
            {{ currentLanguage === 'zh' ? '关闭' : 'Close' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- LLM Settings Modal -->
    <div 
      v-if="llmSettingsOpen" 
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="llmSettingsOpen = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] flex flex-col">
        <div class="p-6 border-b border-slate-200 flex items-center justify-between">
          <h3 class="text-lg font-semibold text-slate-800 flex items-center">
            <Settings class="w-5 h-5 mr-2 text-indigo-600" />
            LLM Configuration
          </h3>
          <button 
            @click="llmSettingsOpen = false"
            class="text-slate-400 hover:text-slate-600 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div class="p-6 space-y-6 overflow-y-auto flex-1">
          <!-- Provider Selection - Only for superadmin -->
          <div v-if="userRole === 'superadmin'">
            <label class="block text-sm font-semibold text-slate-700 mb-2">
              LLM 提供商 *
            </label>
            <div class="relative">
              <select 
                v-model="selectedProvider"
                class="w-full px-4 py-2.5 pr-10 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 text-sm appearance-none cursor-pointer transition-all"
              >
                <option value="openai">OpenAI Compatible (CBIT / OpenAI / Azure)</option>
                <option value="ollama">Ollama (本地部署)</option>
              </select>
              <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
                <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </div>
            </div>
            <p class="mt-1 text-xs text-slate-500">
              选择 LLM 服务提供商类型
            </p>
          </div>
          
          <!-- Provider Display - For regular users -->
          <div v-else>
            <label class="block text-sm font-semibold text-slate-700 mb-2">
              LLM 提供商
            </label>
            <div class="px-4 py-3 bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-xl">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
                  <span class="text-white font-bold text-sm">C</span>
                </div>
                <div>
                  <div class="font-bold text-slate-900">{{ llmConfig.display_name || 'CBIT CBIT-Elite' }}</div>
                  <div class="text-xs text-slate-500">由 CBIT 提供的高性能 AI 服务</div>
                </div>
              </div>
            </div>
          </div>

          <!-- API Key Input - Only for superadmin and openai provider -->
          <div v-if="userRole === 'superadmin' && selectedProvider === 'openai'">
            <label class="block text-sm font-semibold text-slate-700 mb-2">
              API Key *
            </label>
            <input 
              v-model="selectedApiKey"
              type="password"
              placeholder="输入您的 API Key（如 sk-...）"
              class="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 text-sm transition-all"
            />
            <p class="mt-1 text-xs text-slate-500">
              您的 API Key 将被安全加密存储
            </p>
          </div>

          <!-- Model Selection - Only for superadmin -->
          <div v-if="userRole === 'superadmin'">
            <label class="block text-sm font-semibold text-slate-700 mb-2">
              选择模型
            </label>
            <div class="relative model-select-wrapper">
              <select 
                v-model="selectedModel"
                @focus="fetchAvailableModels"
                class="model-select w-full px-4 py-2.5 pr-10 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 text-sm appearance-none cursor-pointer transition-all"
                :disabled="llmConfigLoading"
                size="1"
              >
                <option value="" disabled>{{ llmConfigLoading ? '加载中...' : '选择一个模型' }}</option>
                <option 
                  v-for="model in availableModels" 
                  :key="model.id" 
                  :value="model.id"
                >
                  {{ model.name }} ({{ model.provider }})
                </option>
              </select>
              <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </div>
            </div>
            <p class="mt-2 text-xs text-slate-500">
              当前模型: <span class="font-medium text-slate-700">{{ llmConfig.model || 'N/A' }}</span>
              <span class="ml-2 text-indigo-600">（共 {{ availableModels.length }} 个可用模型）</span>
            </p>
            
            <!-- Custom Model Input -->
            <div class="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <label class="block text-xs font-medium text-amber-900 mb-2">
                或手动输入模型名称
              </label>
              <input 
                v-model="customModelName"
                type="text"
                placeholder="例如: gpt-4o, cbit-elite-4.2"
                class="w-full px-3 py-2 text-sm bg-white border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500 transition-all"
                @input="selectedModel = customModelName"
              />
              <p class="mt-1 text-xs text-amber-700">
                💡 如果列表中没有您需要的模型，可以手动输入模型名称
              </p>
            </div>
          </div>

          <!-- User info message - for regular users -->
          <div v-if="userRole !== 'superadmin'" class="p-4 bg-blue-50 border border-blue-200 rounded-xl">
            <div class="flex items-start gap-3">
              <svg class="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              <div>
                <div class="font-medium text-blue-900 text-sm mb-1">
                  AI 模型信息
                </div>
                <div class="text-sm text-blue-700 leading-relaxed">
                  您正在使用 CBIT 提供的高性能AI 服务。该模型由CBIT基于Qwen3 和VoxChina提供的语料微调训练，确保精准性能和稳定性。
                </div>
              </div>
            </div>
          </div>

          <!-- Status - Only for superadmin -->
          <div v-if="userRole === 'superadmin' && llmConfig.api_key_set" class="flex items-center gap-2 text-sm">
            <div class="w-2 h-2 bg-green-500 rounded-full"></div>
            <span class="text-green-700 font-medium">API 密钥已配置</span>
          </div>

          <!-- Error Message -->
          <div v-if="llmConfigError" class="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
            {{ llmConfigError }}
          </div>
        </div>
        
        <div class="p-6 border-t border-slate-200 flex justify-end space-x-3 bg-slate-50">
          <button 
            @click="llmSettingsOpen = false"
            class="px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors text-sm font-medium"
          >
            关闭
          </button>
          <button 
            v-if="userRole === 'superadmin'"
            @click="saveLLMConfig"
            :disabled="llmConfigLoading || !selectedModel || (selectedProvider === 'openai' && !selectedApiKey && !llmConfig.api_key_set)"
            class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors text-sm font-medium shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ llmConfigLoading ? '保存中...' : '保存配置' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Integrated Voiceover History Modal -->
    <div 
      v-if="showIntegratedHistory" 
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showIntegratedHistory = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        <div class="p-6 border-b border-slate-200 flex items-center justify-between">
          <h3 class="text-lg font-semibold text-slate-800 flex items-center">
            <Clock class="w-5 h-5 mr-2 text-blue-600" />
            {{ t('historyTitle') }}
          </h3>
          <button 
            @click="showIntegratedHistory = false"
            class="text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X class="w-6 h-6" />
          </button>
        </div>
        
        <div class="p-6 overflow-y-auto flex-1">
          <div v-if="loadingHistory" class="text-center py-12">
            <Loader2 class="w-8 h-8 animate-spin mx-auto text-blue-600" />
            <p class="mt-4 text-slate-500">加载中...</p>
          </div>
          
          <div v-else-if="integratedHistoryList.length === 0" class="text-center py-12">
            <AlertCircle class="w-12 h-12 mx-auto text-slate-300" />
            <p class="mt-4 text-slate-500">暂无历史记录</p>
          </div>
          
          <div v-else class="space-y-3">
            <div 
              v-for="task in integratedHistoryList" 
              :key="task.task_id"
              class="bg-white border border-slate-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <h4 class="font-medium text-slate-800 mb-1">{{ task.topic_hint }}</h4>
                  <div class="flex items-center gap-4 text-sm text-slate-500">
                    <span>{{ task.files_count }} {{ t('documents') }}</span>
                    <span>{{ new Date(task.created_at).toLocaleString() }}</span>
                    <span 
                      :class="{
                        'text-green-600': task.status === 'completed',
                        'text-blue-600': task.status === 'processing',
                        'text-red-600': task.status === 'failed'
                      }"
                      class="font-medium"
                    >
                      {{ task.status === 'completed' ? '已完成' : task.status === 'processing' ? '处理中' : '失败' }}
                    </span>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <button
                    v-if="task.status === 'completed'"
                    @click="loadIntegratedTask(task.task_id)"
                    class="px-3 py-1.5 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors text-sm"
                  >
                    查看
                  </button>
                  <button
                    @click="deleteIntegratedTask(task.task_id)"
                    class="px-3 py-1.5 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors text-sm"
                  >
                    {{ t('deleteTask') }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Save to Knowledge Base Dialog -->
    <div v-if="showSaveToKBDialog" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm" style="animation: fadeIn 0.2s ease-out;">
      <div class="bg-white rounded-2xl shadow-2xl max-w-lg w-full mx-4 p-6 flex flex-col max-h-[90vh]" style="animation: scaleIn 0.3s ease-out;">
        <div class="flex items-start mb-4">
          <div class="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center mr-4 flex-shrink-0">
            <svg class="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2" />
            </svg>
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-slate-800 mb-1">{{ t('saveToKnowledgeBase') }}</h3>
            <p class="text-sm text-slate-500">{{ t('saveToKnowledgeBaseDesc') }}</p>
          </div>
        </div>
        
        <!-- Tag Selection Section -->
        <div class="flex-1 overflow-y-auto mb-6 pr-2">
          <div class="mb-4">
            <label class="block text-sm font-medium text-slate-700 mb-2 flex items-center">
              <Tag class="w-4 h-4 mr-1.5 text-indigo-500" />
              {{ currentLanguage === 'zh' ? '标签 (Tags)' : 'Tags' }}
            </label>
            
            <!-- Recommended Tags -->
            <div v-if="recommendedTags.length > 0" class="mb-3">
              <div class="text-xs font-semibold text-slate-500 mb-2 uppercase tracking-wider flex items-center">
                <span class="w-1.5 h-1.5 rounded-full bg-green-500 mr-1.5"></span>
                {{ currentLanguage === 'zh' ? '智能推荐' : 'Recommended' }}
              </div>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="tag in recommendedTags"
                  :key="tag"
                  @click="toggleTag(tag)"
                  :class="[
                    'px-3 py-1.5 rounded-full text-xs font-medium transition-all border',
                    selectedTags.has(tag)
                      ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm'
                      : 'bg-indigo-50 text-indigo-700 border-indigo-100 hover:bg-indigo-100'
                  ]"
                >
                  {{ tag }}
                  <span v-if="selectedTags.has(tag)" class="ml-1">✓</span>
                </button>
              </div>
            </div>
            
            <!-- Custom Tag Input -->
            <div class="flex gap-2 mb-4">
              <input 
                v-model="customTagInput"
                @keyup.enter="addCustomTag"
                type="text" 
                :placeholder="currentLanguage === 'zh' ? '添加自定义标签...' : 'Add custom tag...'"
                class="flex-1 px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
              />
              <button 
                @click="addCustomTag"
                :disabled="!customTagInput.trim()"
                class="px-3 py-2 bg-slate-100 text-slate-600 rounded-lg hover:bg-slate-200 disabled:opacity-50 text-sm font-medium"
              >
                +
              </button>
            </div>
            
            <!-- All Available Tags -->
            <div>
              <div class="text-xs font-semibold text-slate-500 mb-2 uppercase tracking-wider">
                {{ currentLanguage === 'zh' ? '所有标签' : 'All Tags' }}
              </div>
              <div class="flex flex-wrap gap-2 max-h-32 overflow-y-auto p-1">
                <button
                  v-for="tag in availableTags.filter(t => !recommendedTags.includes(t))"
                  :key="tag"
                  @click="toggleTag(tag)"
                  :class="[
                    'px-2.5 py-1 rounded-full text-xs transition-colors border',
                    selectedTags.has(tag)
                      ? 'bg-slate-800 text-white border-slate-800'
                      : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
                  ]"
                >
                  {{ tag }}
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="flex gap-3 mt-auto pt-4 border-t border-slate-100">
          <button 
            @click="skipKBSave"
            :disabled="isSavingToKB"
            class="flex-1 px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ t('cancel') }}
          </button>
          <button 
            @click="saveToKnowledgeBase"
            :disabled="isSavingToKB"
            class="flex-1 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Loader2 v-if="isSavingToKB" class="w-4 h-4 mr-2 animate-spin" />
            <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            {{ isSavingToKB ? (currentLanguage === 'zh' ? '保存中...' : 'Saving...') : t('save') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Upload Article Dialog -->
    <div v-if="showUploadArticleDialog" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm" style="animation: fadeIn 0.2s ease-out;">
      <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full mx-4 p-6 flex flex-col max-h-[90vh]" style="animation: scaleIn 0.3s ease-out;">
        <div class="flex items-start mb-4">
          <div class="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center mr-4 flex-shrink-0">
            <Upload class="w-6 h-6 text-indigo-600" />
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-slate-800 mb-1">
              {{ currentLanguage === 'zh' ? '上传文章到知识库' : 'Upload Article to Knowledge Base' }}
            </h3>
            <p class="text-sm text-slate-500">
              {{ currentLanguage === 'zh' ? '上传文档并选择相关标签' : 'Upload document and select relevant tags' }}
            </p>
          </div>
        </div>
        
        <div class="flex-1 overflow-y-auto mb-6 pr-2">
          <!-- File Upload Area -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-slate-700 mb-2">
              {{ currentLanguage === 'zh' ? '文档文件' : 'Document File' }}
            </label>
            <div 
              @drop.prevent="handleUploadFileDrop"
              @dragover.prevent="isUploadDragging = true"
              @dragleave.prevent="isUploadDragging = false"
              :class="[
                'border-2 border-dashed rounded-xl p-8 text-center transition-colors',
                isUploadDragging ? 'border-indigo-500 bg-indigo-50' : 'border-slate-200 hover:border-slate-300'
              ]"
            >
              <input 
                ref="uploadFileInput"
                type="file" 
                @change="handleUploadFileSelect"
                accept=".pdf,.doc,.docx,.txt"
                class="hidden"
              />
              <div v-if="!uploadArticleFile">
                <Upload class="w-10 h-10 mx-auto mb-3 text-slate-400" />
                <p class="text-sm text-slate-600 mb-1">
                  {{ currentLanguage === 'zh' ? '拖放文件到此处或' : 'Drop file here or' }}
                  <button 
                    @click="$refs.uploadFileInput.click()"
                    class="text-indigo-600 hover:text-indigo-700 font-medium"
                  >
                    {{ currentLanguage === 'zh' ? '浏览' : 'browse' }}
                  </button>
                </p>
                <p class="text-xs text-slate-400">PDF, DOC, DOCX, TXT</p>
              </div>
              <div v-else class="flex items-center justify-between bg-slate-50 rounded-lg p-3">
                <div class="flex items-center">
                  <FileText class="w-5 h-5 text-indigo-600 mr-2" />
                  <span class="text-sm text-slate-700">{{ uploadArticleFile.name }}</span>
                </div>
                <button 
                  @click="uploadArticleFile = null"
                  class="text-slate-400 hover:text-red-500 transition-colors"
                >
                  <X class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          <!-- Tag Selection -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-slate-700 mb-2 flex items-center">
              <Tag class="w-4 h-4 mr-1.5 text-indigo-500" />
              {{ currentLanguage === 'zh' ? '选择标签' : 'Select Tags' }}
            </label>
            
            <!-- AI Recommended Tags -->
            <div v-if="recommendedTags.length > 0" class="mb-4 p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
              <div class="flex items-center mb-2">
                <Zap class="w-4 h-4 text-green-600 mr-1.5" />
                <span class="text-xs font-semibold text-green-700 uppercase tracking-wider">
                  {{ currentLanguage === 'zh' ? 'AI 智能推荐' : 'AI Recommended' }}
                </span>
              </div>
              <p class="text-xs text-slate-600 mb-2">
                {{ currentLanguage === 'zh' ? '点击下方标签即可选择，您可以自由选择或忽略这些建议' : 'Click tags below to select. You can choose or ignore these suggestions freely' }}
              </p>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="tag in recommendedTags"
                  :key="tag"
                  @click="toggleTag(tag)"
                  :class="[
                    'px-3 py-1.5 rounded-full text-xs font-medium transition-all border-2',
                    selectedTags.has(tag)
                      ? 'bg-green-600 text-white border-green-600 shadow-md scale-105'
                      : 'bg-white text-green-700 border-green-300 hover:bg-green-50 hover:border-green-400'
                  ]"
                >
                  {{ tag }}
                  <span v-if="selectedTags.has(tag)" class="ml-1">✓</span>
                </button>
              </div>
            </div>
            
            <!-- Loading Indicator -->
            <div v-if="tagsLoading" class="mb-4 flex items-center justify-center p-4 bg-slate-50 rounded-lg border border-slate-200">
              <Loader2 class="w-5 h-5 text-indigo-500 animate-spin mr-2" />
              <span class="text-sm text-slate-600">
                {{ currentLanguage === 'zh' ? '正在分析文档并推荐标签...' : 'Analyzing document and recommending tags...' }}
              </span>
            </div>
            
            <!-- Custom Tag Input -->
            <div class="flex gap-2 mb-3">
              <input 
                v-model="customTagInput"
                @keyup.enter="addCustomTag"
                type="text" 
                :placeholder="currentLanguage === 'zh' ? '添加自定义标签...' : 'Add custom tag...'"
                class="flex-1 px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
              />
              <button 
                @click="addCustomTag"
                :disabled="!customTagInput.trim()"
                class="px-3 py-2 bg-slate-100 text-slate-600 rounded-lg hover:bg-slate-200 disabled:opacity-50 text-sm font-medium"
              >
                +
              </button>
            </div>
            
            <!-- All Available Tags -->
            <div>
              <div class="text-xs font-medium text-slate-500 mb-2">
                {{ currentLanguage === 'zh' ? '所有标签' : 'All Tags' }}
              </div>
              <div class="flex flex-wrap gap-2 max-h-48 overflow-y-auto p-2 border border-slate-200 rounded-lg bg-slate-50">
                <button
                  v-for="tag in availableTags.filter(t => !recommendedTags.includes(t))"
                  :key="tag"
                  @click="toggleTag(tag)"
                  :class="[
                    'px-3 py-1.5 rounded-full text-xs transition-colors border',
                    selectedTags.has(tag)
                      ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm'
                      : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300 hover:bg-white'
                  ]"
                >
                  {{ tag }}
                  <span v-if="selectedTags.has(tag)" class="ml-1">✓</span>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="flex gap-3 mt-auto pt-4 border-t border-slate-100">
          <button 
            @click="cancelUploadArticle"
            :disabled="isUploadingArticle"
            class="flex-1 px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
          >
            {{ t('cancel') }}
          </button>
          <button 
            @click="uploadArticleToKB"
            :disabled="!uploadArticleFile || isUploadingArticle"
            class="flex-1 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center justify-center disabled:opacity-50"
          >
            <Loader2 v-if="isUploadingArticle" class="w-4 h-4 mr-2 animate-spin" />
            <Upload v-else class="w-4 h-4 mr-2" />
            {{ isUploadingArticle ? (currentLanguage === 'zh' ? '上传中...' : 'Uploading...') : (currentLanguage === 'zh' ? '上传' : 'Upload') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Tag Management Dialog -->
    <div v-if="showTagManagementDialog" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm" style="animation: fadeIn 0.2s ease-out;">
      <div class="bg-white rounded-2xl shadow-2xl max-w-lg w-full mx-4 p-6 flex flex-col max-h-[90vh]" style="animation: scaleIn 0.3s ease-out;">
        <div class="flex items-start mb-4">
          <div class="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center mr-4 flex-shrink-0">
            <Tag class="w-6 h-6 text-indigo-600" />
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-slate-800 mb-1">
              {{ currentLanguage === 'zh' ? '标签管理' : 'Tag Management' }}
            </h3>
            <p class="text-sm text-slate-500">
              {{ currentLanguage === 'zh' ? '管理知识库的所有标签' : 'Manage all knowledge base tags' }}
            </p>
          </div>
        </div>
        
        <div class="flex-1 overflow-y-auto mb-6 pr-2">
          <!-- Add New Tag -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-slate-700 mb-2">
              {{ currentLanguage === 'zh' ? '添加新标签' : 'Add New Tag' }}
            </label>
            <div class="flex gap-2">
              <input 
                v-model="newTagInput"
                @keyup.enter="addNewTag"
                type="text" 
                :placeholder="currentLanguage === 'zh' ? '输入标签名称...' : 'Enter tag name...'"
                class="flex-1 px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
              />
              <button 
                @click="addNewTag"
                :disabled="!newTagInput.trim() || tagsLoading"
                class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 text-sm font-medium"
              >
                {{ currentLanguage === 'zh' ? '添加' : 'Add' }}
              </button>
            </div>
          </div>

          <!-- Tags List -->
          <div>
            <div class="text-sm font-medium text-slate-700 mb-3">
              {{ currentLanguage === 'zh' ? '所有标签' : 'All Tags' }} ({{ availableTags.length }})
            </div>
            <div v-if="tagsLoading" class="flex items-center justify-center py-8">
              <Loader2 class="w-6 h-6 text-indigo-500 animate-spin" />
            </div>
            <div v-else class="space-y-2 max-h-64 overflow-y-auto">
              <div 
                v-for="tag in availableTags" 
                :key="tag"
                class="flex items-center justify-between p-2 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors group"
              >
                <span class="text-sm text-slate-700">{{ tag }}</span>
                <button 
                  @click="deleteTag(tag)"
                  class="text-slate-400 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100"
                  :title="currentLanguage === 'zh' ? '删除标签' : 'Delete tag'"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="flex gap-3 mt-auto pt-4 border-t border-slate-100">
          <button 
            @click="showTagManagementDialog = false"
            class="flex-1 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition-colors"
          >
            {{ currentLanguage === 'zh' ? '完成' : 'Done' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Email Template Modal -->
    <div v-if="showEmailTemplateModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm" style="animation: fadeIn 0.2s ease-out;">
      <div class="bg-white rounded-2xl shadow-2xl max-w-5xl w-full mx-4 p-6 flex flex-col max-h-[90vh]" style="animation: scaleIn 0.3s ease-out;">
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-slate-800 mb-1">{{ editingEmailTemplate ? (currentLanguage === 'zh' ? '编辑模板' : 'Edit Template') : (currentLanguage === 'zh' ? '新建模板' : 'New Template') }}</h3>
          </div>
          <button 
            @click="closeEmailTemplateModal"
            class="text-slate-400 hover:text-slate-600"
          >
            <X class="w-5 h-5" />
          </button>
        </div>
        
        <div class="flex-1 overflow-y-auto mb-6">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">{{ currentLanguage === 'zh' ? '模板名称' : 'Template Name' }}</label>
              <input type="text" v-model="emailTemplateForm.name" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500">
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">{{ currentLanguage === 'zh' ? '邮件主题' : 'Email Subject' }}</label>
              <input type="text" v-model="emailTemplateForm.subject" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500">
            </div>
            <div>
              <div class="flex items-center justify-between mb-2">
                <label class="block text-sm font-medium text-slate-700">{{ currentLanguage === 'zh' ? '邮件内容' : 'Email Content' }}</label>
                <div class="flex gap-2">
                  <button 
                    @click="switchEmailTemplateViewMode('visual')"
                    :class="[
                      'px-3 py-1 text-xs font-medium rounded-md transition-colors',
                      emailTemplateViewMode === 'visual' 
                        ? 'bg-indigo-600 text-white' 
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    ]"
                  >
                    <svg class="w-3 h-3 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    {{ currentLanguage === 'zh' ? '可视化' : 'Visual' }}
                  </button>
                  <button 
                    @click="switchEmailTemplateViewMode('code')"
                    :class="[
                      'px-3 py-1 text-xs font-medium rounded-md transition-colors',
                      emailTemplateViewMode === 'code' 
                        ? 'bg-indigo-600 text-white' 
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    ]"
                  >
                    <FileText class="w-3 h-3 inline-block mr-1" />
                    {{ currentLanguage === 'zh' ? '代码' : 'Code' }}
                  </button>
                  <button 
                    @click="switchEmailTemplateViewMode('preview')"
                    :class="[
                      'px-3 py-1 text-xs font-medium rounded-md transition-colors',
                      emailTemplateViewMode === 'preview' 
                        ? 'bg-indigo-600 text-white' 
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    ]"
                  >
                    <svg class="w-3 h-3 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    {{ currentLanguage === 'zh' ? '预览' : 'Preview' }}
                  </button>
                </div>
              </div>
              
              <!-- Visual Editor -->
              <div v-show="emailTemplateViewMode === 'visual'">
                <div id="quill-editor" class="border border-slate-300 rounded-lg" style="min-height: 400px;"></div>
                <div class="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p class="text-xs text-blue-800 font-medium mb-1">
                    💡 {{ currentLanguage === 'zh' ? '可视化编辑模式' : 'Visual Editing Mode' }}
                  </p>
                  <ul class="text-xs text-blue-700 space-y-1 ml-4">
                    <li>{{ currentLanguage === 'zh' ? '✓ 使用工具栏格式化文本、添加颜色、插入链接和图片' : '✓ Use toolbar to format text, add colors, insert links and images' }}</li>
                    <li>{{ currentLanguage === 'zh' ? '✓ 直接粘贴带格式的内容（从 Word、网页等）' : '✓ Paste formatted content directly (from Word, web pages, etc.)' }}</li>
                    <li>{{ currentLanguage === 'zh' ? '✓ 所见即所得，编辑后立即看到效果' : '✓ WYSIWYG - see the result immediately as you edit' }}</li>
                  </ul>
                </div>
              </div>
              
              <!-- Code Editor -->
              <div v-show="emailTemplateViewMode === 'code'">
                <textarea 
                  v-model="emailTemplateForm.content" 
                  rows="15" 
                  class="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-mono"
                  placeholder="<html><body>...</body></html>"
                ></textarea>
                <div class="mt-3 p-3 bg-slate-50 border border-slate-200 rounded-lg">
                  <p class="text-xs text-slate-700 font-medium mb-1">
                    💡 {{ currentLanguage === 'zh' ? '代码编辑模式（高级）' : 'Code Editing Mode (Advanced)' }}
                  </p>
                  <ul class="text-xs text-slate-600 space-y-1 ml-4">
                    <li>{{ currentLanguage === 'zh' ? '✓ 直接编辑 HTML 源代码' : '✓ Edit HTML source code directly' }}</li>
                    <li v-if="currentLanguage === 'zh'">✓ 使用 &#123;&#123;变量名&#125;&#125; 定义可替换的内容</li>
                    <li v-else>✓ Use &#123;&#123;variable_name&#125;&#125; for replaceable content</li>
                    <li>{{ currentLanguage === 'zh' ? '✓ 适合有 HTML/CSS 经验的高级用户' : '✓ For advanced users with HTML/CSS experience' }}</li>
                  </ul>
                </div>
              </div>
              
              <!-- Preview -->
              <div v-show="emailTemplateViewMode === 'preview'" class="border border-slate-300 rounded-lg overflow-hidden bg-slate-50">
                <div class="bg-gradient-to-r from-slate-700 to-slate-600 text-white px-4 py-3 text-xs font-medium flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <span>{{ currentLanguage === 'zh' ? '邮件预览' : 'Email Preview' }}</span>
                  </div>
                  <span class="text-slate-300">{{ emailTemplateForm.subject || (currentLanguage === 'zh' ? '（未设置主题）' : '(No subject)') }}</span>
                </div>
                <div class="p-4 bg-white">
                  <iframe 
                    ref="previewIframe"
                    class="w-full border-0"
                    style="min-height: 500px; max-height: 500px;"
                    sandbox="allow-same-origin"
                  ></iframe>
                </div>
                <div class="mt-2 px-4 pb-3">
                  <div class="p-3 bg-amber-50 border border-amber-200 rounded-lg">
                    <p class="text-xs text-amber-800 font-medium mb-1">
                      💡 {{ currentLanguage === 'zh' ? '预览模式（只读）' : 'Preview Mode (Read-only)' }}
                    </p>
                    <ul class="text-xs text-amber-700 space-y-1 ml-4">
                      <li>{{ currentLanguage === 'zh' ? '✓ 查看邮件在客户端中的最终效果' : '✓ See how the email will look in email clients' }}</li>
                      <li v-if="currentLanguage === 'zh'">✓ 变量（如 &#123;&#123;name&#125;&#125;）会原样显示</li>
                      <li v-else>✓ Variables like &#123;&#123;name&#125;&#125; will be shown as-is</li>
                      <li>{{ currentLanguage === 'zh' ? '✓ 需要编辑请切换到"可视化"或"代码"模式' : '✓ Switch to Visual or Code mode to edit' }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="flex gap-3 mt-auto pt-4 border-t border-slate-100">
          <button 
            @click="closeEmailTemplateModal"
            class="flex-1 px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-sm font-medium transition-colors"
          >
            {{ currentLanguage === 'zh' ? '取消' : 'Cancel' }}
          </button>
          <button 
            @click="saveEmailTemplate"
            class="flex-1 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition-colors"
          >
            {{ currentLanguage === 'zh' ? '保存' : 'Save' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { 
  FileText, 
  Mic, 
  Search, 
  Flame, 
  Bell,
  LayoutGrid,
  Play,
  Trash2,
  Upload,
  Loader2,
  Settings,
  Volume2,
  BookOpen,
  Database,
  Languages,
  RefreshCw,
  FileVideo,
  Image,
  Clock,
  X,
  AlertCircle,
  Copy,
  ExternalLink,
  TrendingUp,
  Newspaper,
  Zap,
  Save,
  Tag,
  Mail
} from 'lucide-vue-next';

// Configuration
// 根据访问域名动态选择API地址（支持前后端分离部署）
const API_BASE_URL = (() => {
  const hostname = window.location.hostname;
  console.log('[API Config] Hostname:', hostname, 'Port:', window.location.port);
  // 如果是通过 llmhi.com 或 localhost 访问（前后端同服务器），使用内部代理
  if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === 'llmhi.com') {
    console.log('[API Config] Using Vite proxy (empty string)');
    return ''; // 使用Vite proxy，避免NAT问题
  }
  // 如果是从其他域名访问（前端部署在其他服务器），使用外部IP
  console.log('[API Config] Using direct connection to backend');
  return 'http://113.106.62.42:8300';
})();
const router = useRouter();

// Interfaces
interface Voice {
  id: string;
  name: string;
  audio_url: string;
}

// State
const activeTab = ref('academic');
const voices = ref<Voice[]>([]);
const uploadVoiceName = ref('');
const uploadVoiceFile = ref<File | null>(null);
const voiceUploading = ref(false);
const uploadError = ref('');
const previewLoading = ref<string | null>(null);
const previewAudioUrl = ref<Record<string, string>>({});
const userDisplayName = ref('Workspace');
const userInitials = ref('AI');
// 文本转语音状态
const ttsInputText = ref('');
const ttsSelectedVoiceId = ref('');
const generatingTTSAudio = ref(false);
const ttsGeneratedAudioUrl = ref('');
const userRole = ref(localStorage.getItem('vox_role') || 'user');

// Language State (Default: English)
const currentLanguage = ref<'en' | 'zh'>(localStorage.getItem('vox_language') as 'en' | 'zh' || 'en');

// Knowledge Base State
const knowledgeDocs = ref<any[]>([]);
const knowledgeSearchQuery = ref('');
const knowledgeLoading = ref(false);
const knowledgePage = ref(1);
const knowledgePageSize = ref(12);
const knowledgeTotal = ref(0);

// Academic Extract State
const academicFile = ref<File | null>(null);
const academicExtracting = ref(false);
const academicProgress = ref(0);
const academicError = ref('');
const currentStep = ref('');
const academicResult = ref<any>(null);
const academicResultTab = ref('summary');
const isDraggingAcademic = ref(false);
const isSavingAcademicToKB = ref(false);
// Academic Extract 推荐标签
const academicRecommendedTags = ref<string[]>([]);
const academicSelectedTags = ref<string[]>([]);
const academicCustomTag = ref('');
const loadingAcademicTags = ref(false);
const academicHistory = ref<any[]>([]);
const academicHistorySearch = ref('');
const academicHistoryPage = ref(1);
const academicHistoryPageSize = ref(10);
const academicHistoryTotal = ref(0);
// Academic Extract 编辑模式状态
const isEditingAcademicSummary = ref(false);
const editedAcademicSummaryZh = ref('');
const editedAcademicSummaryEn = ref('');

// TTS State for Academic Extract
const selectedVoiceId = ref('');
const selectedSummaryLang = ref('zh');
const audioUrl = ref('');
const isGeneratingAudio = ref(false);

// TTS State for Integrated Voiceover
const selectedIntegratedVoiceId = ref('');
const integratedAudioUrl = ref('');
const isGeneratingIntegratedAudio = ref(false);

// Knowledge Base Save State
const showSaveToKBDialog = ref(false);
const pendingKBSave = ref<any>(null);
const isSavingToKB = ref(false);

// Tag Management State
const availableTags = ref<string[]>([]);
const selectedTags = ref<Set<string>>(new Set());
const recommendedTags = ref<string[]>([]);
const customTagInput = ref('');
const tagsLoading = ref(false);
const selectedTagFilter = ref('');
const newTagInput = ref('');

// Upload Article State
const showUploadArticleDialog = ref(false);
const uploadArticleFile = ref<File | null>(null);
const isUploadDragging = ref(false);
const isUploadingArticle = ref(false);

// Tag Management Dialog State
const showTagManagementDialog = ref(false);

// Integrated Voiceover State
const integratedForm = ref({
  topic_hint: '',
  speaker_affiliation: '',
  speaker_name: '',
  include_vox_intro: true,
  style_preference: '',
  language: 'zh',
  word_limit: null as number | null  // 字数限制: 2000/3000/4000 或 null(不限制)
});
const integratedFiles = ref<File[]>([]);
const isDraggingIntegrated = ref(false);
const integratedSubmitting = ref(false);
const integratedTaskId = ref<string | null>(null);
const integratedStatus = ref<any>(null);
const integratedResult = ref<any>(null);
const integratedError = ref('');
const integratedResultTab = ref('style');
const integratedParsedDocs = ref<any[]>([]);
const isSavingIntegratedToKB = ref(false);
// Integrated Voiceover 标签管理
const showIntegratedTagModal = ref(false);
const integratedRecommendedTags = ref<string[]>([]);
const integratedSelectedTags = ref<string[]>([]);
const integratedCustomTag = ref('');
const loadingIntegratedTags = ref(false);
let integratedPollingInterval: number | null = null;
// 编辑模式状态
const isEditingIntegratedFinal = ref(false);
const editedIntegratedFinal = ref('');

// Document Detail State
const documentDetailOpen = ref(false);
const selectedDocument = ref<any>(null);

// Asset Detail State
const assetDetailOpen = ref(false);
const selectedAsset = ref<any>(null);

// Email Marketing State
const currentEmailTab = ref('subscribers');
const emailTabs = [
  { id: 'subscribers', name: currentLanguage.value === 'zh' ? '订阅用户' : 'Subscribers' },
  { id: 'templates', name: currentLanguage.value === 'zh' ? '邮件模板' : 'Templates' },
  { id: 'send', name: currentLanguage.value === 'zh' ? '发送邮件' : 'Send Email' },
  { id: 'settings', name: currentLanguage.value === 'zh' ? '配置设置' : 'Settings' }
];
const emailSubscribers = ref<any[]>([]);
const emailTemplates = ref<any[]>([]);
const emailLoading = ref(false);
const emailSending = ref(false);
const emailSendForm = ref({
  template_id: '',
  type: 'all',
  test_email: ''
});
const emailConfigForm = ref({
  smtp_server: '',
  smtp_port: 587,
  smtp_username: '',
  smtp_password: '',
  sender_email: '',
  sender_name: '',
  use_tls: true
});
const showEmailTemplateModal = ref(false);
const editingEmailTemplate = ref<any>(null);
const emailTemplateForm = ref({
  name: '',
  subject: '',
  content: ''
});
const emailTemplateViewMode = ref<'visual' | 'code' | 'preview'>('visual');
let quillEditor: any = null;
const previewIframe = ref<HTMLIFrameElement | null>(null);

// LLM Settings State
const llmSettingsOpen = ref(false);
const llmConfig = ref({
  provider: 'openai',
  model: 'gpt-4o',
  display_name: 'CBIT CBIT-Elite 4.2',
  api_key_set: false
});
const availableModels = ref<Array<{id: string, name: string, provider: string}>>([]);
const selectedProvider = ref('openai');
const selectedModel = ref('');

// Integrated Voiceover History State
const integratedHistoryList = ref<any[]>([]);
const showIntegratedHistory = ref(false);
const loadingHistory = ref(false);

// Image Management State
const imageList = ref<any[]>([]);
const loadingImages = ref(false);
const selectedImages = ref<Set<string>>(new Set());
const selectedApiKey = ref('');
const customModelName = ref('');
const llmConfigLoading = ref(false);
const llmConfigError = ref('');

// AI Search State
const searchQuery = ref('');
const searchType = ref('knowledge');
const searchLanguage = ref('zh');
const searchLimit = ref(10);
const isSearching = ref(false);
const searchResults = ref<any>(null);
const searchResultsList = ref<any[]>([]);
const aiAnswer = ref('');
const searchDuration = ref(0);
const searchHistory = ref<string[]>([]);

// Hot News State
const hotNewsTopic = ref('');
const hotNewsStyle = ref('professional');
const hotNewsLength = ref('medium');
const hotNewsGenerateScript = ref(false);
const hotNewsGenerating = ref(false);
const hotNewsResult = ref<any>(null);
const trendingTopics = ref<any[]>([]);
const latestNews = ref<any[]>([]);
const loadingTrending = ref(false);
const loadingNews = ref(false);
const selectedNewsDetail = ref<any>(null);
const showNewsDetail = ref(false);
const savingNewsToKB = ref(false);
const loadingNewsContent = ref(false);
// 新闻源选择
const availableNewsSources = ref<any[]>([]);
const selectedNewsSources = ref<string[]>([]);
const loadingNewsSources = ref(false);
const showNewsSourceSelector = ref(false);

// i18n Translations
const translations = {
  en: {
    // Navigation
    academicExtract: 'Academic Extract',
    knowledgeDatabase: 'Knowledge Database',
    voiceLibrary: 'Voice Library',
    aiSearch: 'AI Search',
    hotTopics: 'Hot Topics',
    integratedVoiceover: 'Integrated Voiceover',
    imageManagement: 'Image Management',
    emailMarketing: 'Email Marketing',
    
    // Common
    settings: 'LLM Settings',
    export: 'Export',
    logOut: 'Log Out',
    historyTitle: 'History',
    viewHistory: 'View History',
    deleteTask: 'Delete',
    confirmDelete: 'Are you sure you want to delete this task?',
    imageCount: 'images',
    deleteImage: 'Delete',
    deleteSelected: 'Delete Selected',
    selectAll: 'Select All',
    clearAll: 'Clear All',
    cleanupOld: 'Cleanup Old Images',
    daysOld: 'days old',
    back: 'Back to Main',
    
        
    // Academic Extract
    uploadDocument: 'Upload Document',
    extractionCompleted: 'Extraction Completed',
    extractionHistory: 'Extraction History',
    noHistory: 'No history available',
    refresh: 'Refresh',
    summaryView: 'Summary View',
    factTableView: 'Fact Table View',
    chineseSummary: 'Chinese Summary',
    englishSummary: 'English Summary',
    basicInformation: 'Basic Information',
    authorsAffiliation: 'Authors & Affiliation',
    researchQuestion: 'Research Question',
    researchObject: 'Research Object / Scope',
    dataSample: 'Data & Sample',
    researchMethod: 'Research Method',
    keyFindings: 'Key Findings',
    mechanisms: 'Mechanisms',
    policyImplications: 'Policy Implications',
    oralBroadcast: 'Oral Broadcast',
    loadingVoices: 'Loading voices...',
    selectContent: 'Select Content',
    selectVoice: 'Select Voice',
    generateAndPlay: 'Generate & Play',
    downloadAudio: 'Download Audio',
    noSummaryText: 'No summary text available',
    audioGenerationFailed: 'Failed to generate audio. Please try again.',
    saveToKnowledgeBase: 'Save to Knowledge Base?',
    saveToKnowledgeBaseDesc: 'Save this extraction result to the knowledge base for future queries and use.',
    skipSave: 'Skip',
    save: 'Save',
    savedToKBSuccess: '✅ Successfully saved to knowledge base!',
    savedToKBFailed: '❌ Failed to save to knowledge base, please try again',
    
    // Knowledge Database
    searchKnowledge: 'Search knowledge...',
    databaseEmpty: 'Database is empty',
    viewDetails: 'View Details',
    
    // Voice Library
    cloneNewVoice: 'Clone New Voice',
    voiceName: 'Voice Name',
    referenceAudio: 'Reference Audio',
    startCloning: 'Start Cloning',
    cloning: 'Cloning...',
    myVoices: 'My Voices',
    noVoices: 'No voices yet',
    generatePreview: 'Generate Preview',
    generating: 'Generating...',
    
    // Messages
    copied: '✅ Copied to clipboard',
    copyFailed: '❌ Copy failed',
    extractionSuccess: '✅ Extraction successful!',
    extractionFailed: '❌ Extraction failed',
    deleteConfirm: 'Are you sure you want to delete this?',
    uploadSuccess: '✅ Upload successful!',
    uploadFailed: '❌ Upload failed',
    
    // Integrated Voiceover
    integratedVoiceoverDesc: 'Generate evidence-based voiceover scripts from multiple documents',
    topicHint: 'Topic / Question',
    topicPlaceholder: 'e.g., Current Status and Challenges of China Digital Economy',
    speakerAffiliation: 'Speaker Affiliation',
    speakerName: 'Speaker Name',
    includeVoxIntro: 'Include VOXCHINA Intro',
    structurePreference: 'Structure Preference',
    autoSelect: 'Auto Select',
    uploadDocuments: 'Upload Documents',
    supportedFormats: 'Supported: .docx, .doc, .pdf',
    clickOrDrag: 'Click or drag files here',
    multipleFiles: 'Multiple files supported',
    startGeneration: 'Start Generation',
    processing: 'Processing...',
    reset: 'Reset',
    styleProfile: 'Style Profile',
    evidenceLedger: 'Evidence Ledger',
    visualAssets: 'Visual Assets',
    structure: 'Structure',
    reviewVersion: 'Review Version',
    finalVersion: 'Final Version',
    copy: 'Copy',
    download: 'Download',
    generatingVoiceover: 'Generating voiceover script...',
    currentStep: 'Current Step',
    generationFailed: 'Generation failed',
    noResult: 'No result yet',
    voxIntro: 'VOX Intro',
    enabled: 'Enabled',
    disabled: 'Disabled',
    mainStructure: 'Main Structure',
    figureStyle: 'Figure Style',
    styleRules: 'Style Rules',
    scriptStructure: 'Script Structure',
    totalSections: 'Total Sections',
    structureType: 'Structure Type',
    paragraphs: 'Paragraphs',
    assets: 'Assets',
    contentPreview: 'Content Preview',
    moreParagraphs: 'more paragraphs',
    assetsUsed: 'Assets Used',
    noVisualAssets: 'No visual assets found in documents',
    caption: 'Caption / Title',
    noCaption: 'No caption',
    keyNumbers: 'Key Numbers',
    takeaway: 'Takeaway',
    editingInstruction: 'Editing Instruction',
    linkedFindings: 'Linked Findings',
    reviewVersionDesc: 'With evidence annotations for internal review',
    finalVersionDesc: 'Ready for recording without evidence markers',
    docs: 'Docs',
    relatedDocs: 'Related Documents',
    relatedAssets: 'Related Assets',
    sectionGoal: 'Section Goal',
    untitled: 'Untitled Section',
    troubleshootingTips: 'Troubleshooting Tips',
    tip1: 'The LLM service may be overloaded. Please wait a moment and try again.',
    tip2: 'Reduce the number of uploaded documents (try 2-3 documents).',
    tip3: 'Simplify your topic description.',
    retryGeneration: 'Retry Generation',
    backToForm: 'Back to Form'
  },
  zh: {
    // Navigation
    academicExtract: 'Academic Extract',
    knowledgeDatabase: '知识库',
    voiceLibrary: '声音库',
    aiSearch: 'AI 搜索',
    hotTopics: '热点话题',
    integratedVoiceover: '整合口播',
    imageManagement: '图片管理',
    emailMarketing: '邮件营销',
    
    // Common
    settings: 'LLM 设置',
    export: '导出',
    logOut: '退出登录',
    historyTitle: '历史记录',
    viewHistory: '查看历史',
    deleteTask: '删除',
    confirmDelete: '确定要删除这条任务吗？',
    imageCount: '张图片',
    deleteImage: '删除',
    deleteSelected: '删除选中',
    selectAll: '全选',
    clearAll: '清空',
    cleanupOld: '清理旧图片',
    daysOld: '天前',
    back: '返回主页',
    
        
    // Academic Extract
    uploadDocument: '上传文档',
    extractionCompleted: '提取完成',
    extractionHistory: '提取历史',
    noHistory: '暂无历史记录',
    refresh: '刷新',
    summaryView: '摘要视图',
    factTableView: '事实表视图',
    chineseSummary: '中文摘要',
    englishSummary: '英文摘要',
    basicInformation: '基本信息',
    authorsAffiliation: '作者与机构',
    researchQuestion: '研究问题',
    researchObject: '研究对象/范围',
    dataSample: '数据与样本',
    researchMethod: '研究方法',
    keyFindings: '核心发现',
    mechanisms: '作用机制',
    policyImplications: '政策启示',
    oralBroadcast: '口播播放',
    loadingVoices: '正在加载声音库...',
    selectContent: '选择内容',
    selectVoice: '选择声音',
    generateAndPlay: '生成并播放',
    downloadAudio: '下载音频',
    noSummaryText: '没有可用的摘要文本',
    audioGenerationFailed: '音频生成失败，请重试',
    saveToKnowledgeBase: '保存到知识库？',
    saveToKnowledgeBaseDesc: '将此提取结果保存到知识库，以便后续查询和使用。',
    skipSave: '暂不保存',
    save: '保存',
    savedToKBSuccess: '✅ 成功保存到知识库！',
    savedToKBFailed: '❌ 保存到知识库失败，请稍后重试',
    
    // Knowledge Database
    searchKnowledge: '搜索知识...',
    databaseEmpty: '数据库为空',
    viewDetails: '查看详情',
    
    // Voice Library
    cloneNewVoice: '克隆新声音',
    voiceName: '声音名称',
    referenceAudio: '参考音频',
    startCloning: '开始克隆',
    cloning: '克隆中...',
    myVoices: '我的声音',
    noVoices: '暂无声音',
    generatePreview: '生成试听',
    generating: '生成中...',
    
    // Messages
    copied: '✅ 已复制到剪贴板',
    copyFailed: '❌ 复制失败',
    extractionSuccess: '✅ 提取成功！',
    extractionFailed: '❌ 提取失败',
    deleteConfirm: '确定要删除吗？',
    uploadSuccess: '✅ 上传成功！',
    uploadFailed: '❌ 上传失败',
    
    // Integrated Voiceover
    integratedVoiceoverDesc: '基于多文献生成符合证据的口播稿',
    topicHint: '主题/问题',
    topicPlaceholder: '例如：中国数字经济发展现状与挑战',
    speakerAffiliation: '主播机构',
    speakerName: '主播姓名',
    includeVoxIntro: '包含VOXCHINA片头',
    structurePreference: '结构偏好',
    autoSelect: '自动选择',
    uploadDocuments: '上传文档',
    supportedFormats: '支持格式：.docx, .doc, .pdf',
    clickOrDrag: '点击或拖拽文件到此处',
    multipleFiles: '支持多文件上传',
    startGeneration: '开始生成',
    processing: '处理中...',
    reset: '重置',
    styleProfile: '风格配置',
    evidenceLedger: '证据台账',
    visualAssets: '图表台账',
    structure: '结构设计',
    reviewVersion: '审阅版',
    finalVersion: '上屏版',
    copy: '复制',
    download: '下载',
    generatingVoiceover: '正在生成口播稿...',
    currentStep: '当前步骤',
    generationFailed: '生成失败',
    noResult: '暂无结果',
    voxIntro: 'VOX片头',
    enabled: '已启用',
    disabled: '未启用',
    mainStructure: '主结构',
    figureStyle: '图表风格',
    styleRules: '风格规则',
    scriptStructure: '稿件结构',
    totalSections: '总章节数',
    structureType: '结构类型',
    paragraphs: '段落',
    assets: '资产',
    contentPreview: '内容预览',
    moreParagraphs: '个段落',
    assetsUsed: '使用的资产',
    noVisualAssets: '文档中未发现图表资产',
    caption: '标题',
    noCaption: '无标题',
    keyNumbers: '关键数字',
    takeaway: '要点',
    editingInstruction: '剪辑指示',
    linkedFindings: '关联证据',
    reviewVersionDesc: '带证据标注，用于内部审核',
    finalVersionDesc: '可直接用于录制的最终稿件',
    docs: '文档',
    relatedDocs: '相关文档',
    relatedAssets: '相关资产',
    sectionGoal: '章节目标',
    untitled: '无标题章节',
    troubleshootingTips: '解决建议',
    tip1: 'LLM服务可能负载较高，请稍等片刻后重试',
    tip2: '减少上传文档数量（建议2-3篇文档）',
    tip3: '简化主题描述，使用更简洁的表达',
    retryGeneration: '重新生成',
    backToForm: '返回表单'
  }
};

const t = (key: string): string => {
  return translations[currentLanguage.value][key] || key;
};

const toggleLanguage = () => {
  currentLanguage.value = currentLanguage.value === 'en' ? 'zh' : 'en';
  localStorage.setItem('vox_language', currentLanguage.value);
};

// Helper function for structure names
const getStructureName = (structureCode: string): string => {
  const structureNames = {
    en: {
      'S1': 'Three-Dimension Analysis',
      'S2': 'Timeline Progression',
      'S3': 'Status-Mechanism-Policy',
      'S4': 'Mechanism Chain'
    },
    zh: {
      'S1': '三维度分析',
      'S2': '时间线推进',
      'S3': '现状-机制-对策',
      'S4': '机制链条'
    }
  };
  return structureNames[currentLanguage.value][structureCode] || structureCode;
};

// Helper function to get full image URL
const getImageUrl = (imageUrl: string): string => {
  console.log('[getImageUrl] Input:', imageUrl);
  if (!imageUrl) {
    console.warn('[getImageUrl] Empty imageUrl');
    return '';
  }
  // If URL already starts with http, return as is
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    console.log('[getImageUrl] Absolute URL:', imageUrl);
    return imageUrl;
  }
  // If API_BASE_URL is empty (using proxy), return relative URL
  if (!API_BASE_URL) {
    console.log('[getImageUrl] Using relative URL:', imageUrl);
    return imageUrl;
  }
  // Otherwise, prepend API_BASE_URL
  const fullUrl = `${API_BASE_URL}${imageUrl}`;
  console.log('[getImageUrl] Full URL:', fullUrl);
  return fullUrl;
};

// Helper function to handle image load errors
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  console.warn('[Image] Failed to load:', img.src);
  img.style.display = 'none';
};

// Helper function to format script text (convert Markdown-like format to HTML)
const formatScriptText = (text: string): string => {
  if (!text) return '';
  
  let formatted = text;
  
  // Convert ## headings to styled spans with proper line breaks
  // Match ## heading at the start of a line
  formatted = formatted.replace(/^## (.+)$/gm, '<div class="script-heading-main">$1</div>');
  
  // Convert ### sub-headings
  formatted = formatted.replace(/^### (.+)$/gm, '<div class="script-heading-sub">$1</div>');
  
  // Convert evidence markers to clickable badges（支持全角【】、半角[]、圆括号（）等多种变体）
  const evidenceBadgeReplacer = (_match: string, content: string) => {
    return `<span class="evidence-badge clickable-evidence" data-evidence-id="${content.trim()}" title="点击查看证据详情">📚 证据: ${content.trim()}</span>`;
  };
  // 全角方括号：【证据：...】 或 【证据:...】
  formatted = formatted.replace(/【证据[：:]([^】]+)】/g, evidenceBadgeReplacer);
  // 半角方括号：[证据：...] 或 [证据:...]
  formatted = formatted.replace(/\[证据[：:]([^\]]+)\]/g, evidenceBadgeReplacer);
  // 圆括号变体：（证据：...）
  formatted = formatted.replace(/（证据[：:]([^）]+)）/g, evidenceBadgeReplacer);
  
  // Helper: 从图表标记内容中提取 asset_id
  const extractAssetId = (content: string): string => {
    const assetIdMatch = content.match(/(D\d+-(?:FIG|TAB)-\d+)/);
    return assetIdMatch ? assetIdMatch[1] : content.trim();
  };

  // For Final Version: Replace figure markers with actual images
  if (integratedResultTab.value === 'final' && integratedResult.value?.visual_asset_ledger?.assets) {
    const assets = integratedResult.value.visual_asset_ledger.assets;
    console.log('[formatScriptText] Final mode, assets count:', assets.length, 'FIG assets:', assets.filter((a: any) => a.asset_type === 'FIG' && a.image_url).length);
    
    // Helper: 尝试将图表标记替换为实际图片
    const figureImageReplacer = (match: string, content: string) => {
      const assetId = extractAssetId(content);
      const asset = assets.find((a: any) => a.asset_id === assetId);
      console.log(`[figureImageReplacer] marker="${match}", assetId="${assetId}", found=${!!asset}, image_url=${asset?.image_url || 'N/A'}, type=${asset?.asset_type || 'N/A'}`);
      if (asset && asset.image_url && asset.asset_type === 'FIG') {
        const imgUrl = getImageUrl(asset.image_url);
        const caption = asset.caption_or_title || assetId;
        return `<div class="figure-container"><img src="${imgUrl}" alt="${caption}" class="figure-image" onerror="this.alt='图片加载失败: ${assetId}';this.style.border='2px dashed #e53e3e';this.style.padding='20px';this.style.background='#fff5f5';this.src=''" /><p class="figure-caption">${caption}</p></div>`;
      }
      return `<span class="figure-badge clickable-asset" data-asset-id="${assetId}" title="点击查看图表详情">📊 图表: ${assetId}</span>`;
    };

    // Replace various figure marker formats with actual images
    formatted = formatted.replace(/📊\s*图表[:：]\s*([^\n\r]+)/g, (match, assetId) => {
      const asset = assets.find((a: any) => a.asset_id === assetId.trim());
      if (asset && asset.image_url && asset.asset_type === 'FIG') {
        const imgUrl = getImageUrl(asset.image_url);
        const caption = asset.caption_or_title || assetId;
        return `<div class="figure-container"><img src="${imgUrl}" alt="${caption}" class="figure-image" onerror="this.alt='图片加载失败';this.style.border='2px dashed #e53e3e';this.style.padding='20px';this.style.background='#fff5f5';this.src=''" /><p class="figure-caption">${caption}</p></div>`;
      }
      return match;
    });
    
    formatted = formatted.replace(/🖼️\s*图[:：]\s*([^\n\r]+)/g, (match, assetId) => {
      const asset = assets.find((a: any) => a.asset_id === assetId.trim());
      if (asset && asset.image_url && asset.asset_type === 'FIG') {
        const imgUrl = getImageUrl(asset.image_url);
        const caption = asset.caption_or_title || assetId;
        return `<div class="figure-container"><img src="${imgUrl}" alt="${caption}" class="figure-image" onerror="this.alt='图片加载失败';this.style.border='2px dashed #e53e3e';this.style.padding='20px';this.style.background='#fff5f5';this.src=''" /><p class="figure-caption">${caption}</p></div>`;
      }
      return match;
    });
    
    // 全角方括号：【图表：...】
    formatted = formatted.replace(/【图表[：:]([^】]+)】/g, figureImageReplacer);
    // 半角方括号：[图表：...] 或 [图表:...]
    formatted = formatted.replace(/\[图表[：:]([^\]]+)\]/g, figureImageReplacer);
    // 兜底：〔画面：D1-FIG-1（标题）— 要点〕 格式（figure_style B 可能产生）
    formatted = formatted.replace(/〔画面[：:]([^〕]+)〕/g, figureImageReplacer);
    // 兜底：[图：...] 或 【图：...】 简写格式
    formatted = formatted.replace(/【图[：:]([^】]+)】/g, figureImageReplacer);
    formatted = formatted.replace(/\[图[：:]([^\]]+)\]/g, figureImageReplacer);
  } else {
    console.log('[formatScriptText] Badge mode (not final), tab:', integratedResultTab.value, 'has_assets:', !!integratedResult.value?.visual_asset_ledger?.assets);
    // For Review Version: Keep as clickable badges
    const figureBadgeReplacer = (_match: string, content: string) => {
      const assetId = extractAssetId(content);
      return `<span class="figure-badge clickable-asset" data-asset-id="${assetId}" title="点击查看图表详情">📊 图表: ${assetId}</span>`;
    };
    // 全角方括号
    formatted = formatted.replace(/【图表[：:]([^】]+)】/g, figureBadgeReplacer);
    // 半角方括号
    formatted = formatted.replace(/\[图表[：:]([^\]]+)\]/g, figureBadgeReplacer);
    // 兜底：〔画面：...〕 格式
    formatted = formatted.replace(/〔画面[：:]([^〕]+)〕/g, figureBadgeReplacer);
    // 兜底：[图：...] 或 【图：...】 简写格式
    formatted = formatted.replace(/【图[：:]([^】]+)】/g, figureBadgeReplacer);
    formatted = formatted.replace(/\[图[：:]([^\]]+)\]/g, figureBadgeReplacer);
  }
  
  // Also handle D1-FIG-1, D2-TAB-1 style references in text (including after colons)
  // 注意：不要匹配已经在 HTML 标签内的内容（如 alt="D1-FIG-1" 或 data-asset-id="D1-FIG-1"）
  // 只匹配纯文本中的引用
  formatted = formatted.replace(/(?<![="'])(D\d+-(?:FIG|TAB)-\d+)(?![^<]*>)/g, (match, assetId) => {
    return `<span class="asset-ref clickable-asset" data-asset-id="${assetId}" title="点击查看资产详情">${assetId}</span>`;
  });
  
  // Convert paragraphs (double line breaks)
  formatted = formatted.replace(/\n\n/g, '</p><p class="script-paragraph">');
  
  // Wrap in paragraph tags
  formatted = '<p class="script-paragraph">' + formatted + '</p>';
  
  // Clean up empty paragraphs
  formatted = formatted.replace(/<p class="script-paragraph">\s*<\/p>/g, '');
  
  return formatted;
};

// Navigation
const navItems = computed(() => [
  { id: 'academic', name: t('academicExtract'), icon: BookOpen },
  { id: 'integrated', name: t('integratedVoiceover'), icon: FileVideo },
  { id: 'knowledge', name: t('knowledgeDatabase'), icon: Database },
  { id: 'voices', name: t('voiceLibrary'), icon: Mic },
  { id: 'images', name: t('imageManagement'), icon: Image },
  { id: 'search', name: t('aiSearch'), icon: Search },
  { id: 'trending', name: t('hotTopics'), icon: Flame },
  { id: 'email', name: t('emailMarketing'), icon: Mail },
]);

const activeItem = computed(() => navItems.value.find(i => i.id === activeTab.value));

const setActiveTab = (id: string) => {
  activeTab.value = id;
  if (id === 'voices') {
    fetchVoices();
  } else if (id === 'knowledge') {
    fetchKnowledgeDocs();
    fetchTags(); // Load available tags when switching to knowledge tab
  } else if (id === 'academic') {
    fetchAcademicHistory();
  } else if (id === 'integrated') {
    // Reset integrated voiceover state
    resetIntegratedForm();
  } else if (id === 'images') {
    fetchImages();
  } else if (id === 'trending') {
    fetchTrendingTopics();
    fetchLatestNews();
  } else if (id === 'email') {
    fetchEmailSubscribers();
    fetchEmailTemplates();
    fetchEmailConfig();
  }
};

const handleLogout = () => {
  if (confirm('Are you sure you want to log out?')) {
    localStorage.removeItem('vox_token');
    localStorage.removeItem('vox_role');
    localStorage.removeItem('vox_username');
    localStorage.removeItem('vox_display_name');
    router.push('/login');
  }
};

// Integrated Voiceover Functions
const resetIntegratedForm = () => {
  integratedForm.value = {
    topic_hint: '',
    speaker_affiliation: '',
    speaker_name: '',
    include_vox_intro: true,
    style_preference: '',
    language: currentLanguage.value,
    word_limit: null  // 重置字数限制为默认
  };
  integratedFiles.value = [];
  integratedTaskId.value = null;
  integratedStatus.value = null;
  integratedResult.value = null;
  integratedError.value = '';
  stopIntegratedPolling();
};

const retryIntegratedGeneration = () => {
  // 清除错误状态但保留表单数据和文件
  integratedError.value = '';
  integratedTaskId.value = null;
  integratedStatus.value = null;
  integratedResult.value = null;
  stopIntegratedPolling();
  
  // 重新提交
  submitIntegratedTask();
};

const handleIntegratedFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files) {
    // 追加新文件到现有列表（去重）
    const newFiles = Array.from(target.files);
    const existingNames = new Set(integratedFiles.value.map(f => f.name));
    const uniqueNewFiles = newFiles.filter(f => !existingNames.has(f.name));
    integratedFiles.value = [...integratedFiles.value, ...uniqueNewFiles];
    // 清空 input 以便可以重复选择同一文件
    target.value = '';
  }
};

const handleIntegratedFileDrop = (event: DragEvent) => {
  isDraggingIntegrated.value = false;
  if (event.dataTransfer?.files) {
    // 追加拖拽的文件到现有列表（去重）
    const newFiles = Array.from(event.dataTransfer.files);
    const existingNames = new Set(integratedFiles.value.map(f => f.name));
    const uniqueNewFiles = newFiles.filter(f => !existingNames.has(f.name));
    integratedFiles.value = [...integratedFiles.value, ...uniqueNewFiles];
  }
};

const removeIntegratedFile = (index: number) => {
  integratedFiles.value.splice(index, 1);
};

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
};

// 过滤无效的 key_numbers（如 "1. The" 这样的无意义数据）
const filterValidKeyNumbers = (keyNumbers: string[] | undefined): string[] => {
  if (!keyNumbers || !Array.isArray(keyNumbers)) return [];
  return keyNumbers.filter(num => {
    if (!num || typeof num !== 'string') return false;
    // 过滤掉以 "1. " 开头但后面不是数字的项
    if (/^\d+\.\s*[A-Za-z]/.test(num)) return false;
    // 过滤掉太短的项（少于2个字符）
    if (num.trim().length < 2) return false;
    // 过滤掉重复的 "1. The" 类型
    if (num.trim().toLowerCase().startsWith('1. the')) return false;
    return true;
  });
};

// Open document detail modal
const openDocumentDetail = (docId: string) => {
  console.log('[Document Detail] Opening document:', docId);
  
  // Find the document from integratedStatus.parsed_docs
  if (integratedStatus.value?.parsed_docs) {
    const doc = integratedStatus.value.parsed_docs.find((d: any) => d.doc_id === docId);
    if (doc) {
      selectedDocument.value = doc;
      documentDetailOpen.value = true;
      console.log('[Document Detail] Document found:', doc);
    } else {
      console.warn('[Document Detail] Document not found:', docId);
      alert(currentLanguage.value === 'zh' ? '文档未找到' : 'Document not found');
    }
  } else {
    console.warn('[Document Detail] No parsed documents available');
    alert(currentLanguage.value === 'zh' ? '文档数据未加载' : 'Document data not loaded');
  }
};

// Open asset detail modal
const openAssetDetail = (assetId: string) => {
  console.log('[Asset Detail] Opening asset:', assetId);
  
  // Find the asset from visual_asset_ledger
  if (integratedResult.value?.visual_asset_ledger?.assets) {
    const asset = integratedResult.value.visual_asset_ledger.assets.find((a: any) => a.asset_id === assetId);
    if (asset) {
      selectedAsset.value = asset;
      assetDetailOpen.value = true;
      console.log('[Asset Detail] Asset found:', asset);
    } else {
      // 资产不存在时，创建一个占位资产对象显示基本信息
      console.warn('[Asset Detail] Asset not found in ledger:', assetId);
      selectedAsset.value = {
        asset_id: assetId,
        asset_type: assetId.includes('FIG') ? 'FIG' : 'TAB',
        caption_or_title: `${assetId} (${currentLanguage.value === 'zh' ? '资产未在台账中' : 'Not in ledger'})`,
        location_anchor: currentLanguage.value === 'zh' 
          ? '该资产在结构设计中被引用，但未在图表台账中找到对应数据。这可能是因为原文档中未包含此图表，或提取过程中未能识别。'
          : 'This asset is referenced in the structure but not found in the visual asset ledger. This may be because the original document does not contain this figure/table, or it was not recognized during extraction.'
      };
      assetDetailOpen.value = true;
    }
  } else {
    console.warn('[Asset Detail] No visual assets available');
    // 同样创建占位对象
    selectedAsset.value = {
      asset_id: assetId,
      asset_type: assetId.includes('FIG') ? 'FIG' : 'TAB',
      caption_or_title: assetId,
      location_anchor: currentLanguage.value === 'zh' 
        ? '图表台账数据未加载' 
        : 'Visual asset ledger not loaded'
    };
    assetDetailOpen.value = true;
  }
};

// Handle clicks on evidence and asset badges in script content
const handleScriptContentClick = (event: MouseEvent) => {
  const target = event.target as HTMLElement;
  
  // Handle clickable evidence
  if (target.classList.contains('clickable-evidence')) {
    const evidenceId = target.getAttribute('data-evidence-id');
    if (evidenceId) {
      console.log('[Script Click] Evidence clicked:', evidenceId);
      showEvidenceDetail(evidenceId);
    }
    return;
  }
  
  // Handle clickable asset (figure/table badges and D1-FIG-1 style references)
  if (target.classList.contains('clickable-asset')) {
    const assetId = target.getAttribute('data-asset-id');
    if (assetId) {
      console.log('[Script Click] Asset clicked:', assetId);
      openAssetDetail(assetId);
    }
    return;
  }
};

// Show evidence detail
const showEvidenceDetail = (evidenceId: string) => {
  console.log('[Evidence Detail] Showing evidence:', evidenceId);
  
  // 证据标记可能包含多个引用，如 "D1-F1, D2-F1" 或 "D1-1, D2-1"
  const evidenceRefs = evidenceId.split(',').map(s => s.trim());
  const foundEvidences: any[] = [];
  
  // evidence_ledger 结构: [{doc_id: "D1", findings: [{finding_index: 1, claim: "..."}]}]
  if (integratedResult.value?.evidence_ledger && Array.isArray(integratedResult.value.evidence_ledger)) {
    for (const ref of evidenceRefs) {
      // 解析引用格式，兼容多种变体:
      // D1-F1 -> doc_id: D1, finding_index: 1
      // D1-1  -> doc_id: D1, finding_index: 1
      // D1-f1 -> doc_id: D1, finding_index: 1
      const match = ref.match(/^(D\d+)-[Ff]?(\d+)$/);
      if (match) {
        const docId = match[1];
        const findingIndex = parseInt(match[2]);
        
        // 在 evidence_ledger 中查找对应文档
        const docLedger = integratedResult.value.evidence_ledger.find(
          (ledger: any) => ledger.doc_id === docId
        );
        
        if (docLedger && docLedger.findings) {
          // 查找对应的 finding
          const finding = docLedger.findings.find(
            (f: any) => f.finding_index === findingIndex
          );
          
          if (finding) {
            foundEvidences.push({
              ref: ref,
              docTitle: docLedger.title,
              claim: finding.claim,
              type: finding.type,
              numbers: finding.numbers || []
            });
          }
        }
      }
    }
  }
  
  if (foundEvidences.length > 0) {
    // 构建显示内容
    let message = currentLanguage.value === 'zh' ? '📚 证据详情\n\n' : '📚 Evidence Details\n\n';
    
    for (const ev of foundEvidences) {
      message += `【${ev.ref}】\n`;
      message += `${currentLanguage.value === 'zh' ? '来源' : 'Source'}: ${ev.docTitle}\n`;
      message += `${currentLanguage.value === 'zh' ? '类型' : 'Type'}: ${ev.type}\n`;
      message += `${currentLanguage.value === 'zh' ? '内容' : 'Content'}: ${ev.claim}\n`;
      if (ev.numbers.length > 0) {
        message += `${currentLanguage.value === 'zh' ? '关键数字' : 'Key Numbers'}: ${ev.numbers.join(', ')}\n`;
      }
      message += '\n';
    }
    
    alert(message);
    return;
  }
  
  // If not found in evidence_ledger, try to find in visual_asset_ledger (for figures)
  if (evidenceId.includes('FIG') || evidenceId.includes('TAB')) {
    openAssetDetail(evidenceId);
    return;
  }
  
  // 如果还是找不到，显示引用信息而不是错误
  console.warn('[Evidence Detail] Evidence not found:', evidenceId);
  
  // 构建一个友好的提示信息
  let message = currentLanguage.value === 'zh' 
    ? `📚 证据引用: ${evidenceId}\n\n该证据引用在证据台账中未找到对应记录。\n\n可能的原因：\n• 证据编号格式与台账不匹配\n• 该证据来自未被完整解析的文档部分`
    : `📚 Evidence Reference: ${evidenceId}\n\nThis evidence reference was not found in the evidence ledger.\n\nPossible reasons:\n• Evidence ID format mismatch\n• Evidence from incompletely parsed document section`;
  
  // 尝试提供更多上下文
  if (integratedResult.value?.evidence_ledger && Array.isArray(integratedResult.value.evidence_ledger)) {
    const availableDocs = integratedResult.value.evidence_ledger.map((l: any) => l.doc_id).join(', ');
    message += currentLanguage.value === 'zh' 
      ? `\n\n可用的文档: ${availableDocs}`
      : `\n\nAvailable documents: ${availableDocs}`;
  }
  
  alert(message);
};

const submitIntegratedTask = async () => {
  if (!integratedForm.value.topic_hint.trim() || integratedFiles.value.length === 0) {
    return;
  }

  integratedSubmitting.value = true;
  integratedError.value = '';

  try {
    const token = localStorage.getItem('vox_token');
    const formData = new FormData();
    
    formData.append('topic_hint', integratedForm.value.topic_hint);
    if (integratedForm.value.speaker_affiliation) {
      formData.append('speaker_affiliation', integratedForm.value.speaker_affiliation);
    }
    if (integratedForm.value.speaker_name) {
      formData.append('speaker_name', integratedForm.value.speaker_name);
    }
    formData.append('include_vox_intro', String(integratedForm.value.include_vox_intro));
    if (integratedForm.value.style_preference) {
      formData.append('style_preference', integratedForm.value.style_preference);
    }
    formData.append('language', integratedForm.value.language);
    // 添加字数限制参数（如果用户选择了）
    if (integratedForm.value.word_limit !== null) {
      formData.append('word_limit', String(integratedForm.value.word_limit));
    }
    
    integratedFiles.value.forEach(file => {
      formData.append('files', file);
    });

    console.log('[Integrated] Submitting task to:', `${API_BASE_URL}/api/v1/integrated-voiceover/create`);
    
    const response = await fetch(`${API_BASE_URL}/api/v1/integrated-voiceover/create`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });

    console.log('[Integrated] Response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('[Integrated] Error response:', errorText);
      try {
        const error = JSON.parse(errorText);
        throw new Error(error.detail || 'Failed to create task');
      } catch (e) {
        throw new Error(`Server error: ${response.status} - ${errorText.substring(0, 200)}`);
      }
    }

    const result = await response.json();
    console.log('[Integrated] Task created:', result);
    integratedTaskId.value = result.task_id;
    
    // Initialize status
    integratedStatus.value = {
      task_id: result.task_id,
      status: 'processing',
      progress: 0,
      current_step: 'Initializing'
    };
    
    // Start polling
    startIntegratedPolling();

  } catch (error: any) {
    console.error('[Integrated] Submit error:', error);
    integratedError.value = error.message;
    integratedTaskId.value = null;
    alert('Error: ' + error.message);
  } finally {
    integratedSubmitting.value = false;
  }
};

const startIntegratedPolling = () => {
  if (integratedPollingInterval) {
    clearInterval(integratedPollingInterval);
  }
  
  pollIntegratedStatus();
  integratedPollingInterval = window.setInterval(pollIntegratedStatus, 3000);
};

const stopIntegratedPolling = () => {
  if (integratedPollingInterval) {
    clearInterval(integratedPollingInterval);
    integratedPollingInterval = null;
  }
};

const pollIntegratedStatus = async () => {
  if (!integratedTaskId.value) {
    console.warn('[Integrated] Poll called but no task ID');
    return;
  }

  try {
    const token = localStorage.getItem('vox_token');
    const url = `${API_BASE_URL}/api/v1/integrated-voiceover/status/${integratedTaskId.value}`;
    console.log('[Integrated] Polling status from:', url);
    
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    console.log('[Integrated] Poll response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('[Integrated] Poll error response:', errorText);
      throw new Error(`Failed to get task status: ${response.status}`);
    }

    const status = await response.json();
    console.log('[Integrated] Status update:', JSON.stringify(status, null, 2));
    integratedStatus.value = status;

    if (status.status === 'completed') {
      console.log('[Integrated] Task completed!');
      integratedResult.value = status.result;
      integratedParsedDocs.value = status.parsed_docs || [];
      stopIntegratedPolling();
    } else if (status.status === 'failed') {
      console.error('[Integrated] Task failed!');
      console.error('[Integrated] Error details:', status);
      const errorMsg = status.error || status.result?.error || 'Task processing failed (no error details)';
      console.error('[Integrated] Error message:', errorMsg);
      integratedError.value = errorMsg;
      stopIntegratedPolling();
    }

  } catch (error: any) {
    console.error('[Integrated] Poll error:', error);
    // Don't stop polling on error, might be temporary network issue
    // But show error in UI
    if (!integratedError.value) {
      integratedError.value = `Polling error: ${error.message}`;
    }
  }
};

const getStepName = (step: string): string => {
  const stepNames: Record<string, string> = {
    'Parsing': currentLanguage.value === 'en' ? 'Parsing documents' : '解析文档',
    'Step0': currentLanguage.value === 'en' ? 'Generating style profile' : '生成风格配置',
    'StepA': currentLanguage.value === 'en' ? 'Building evidence ledger' : '构建证据台账',
    'StepA2': currentLanguage.value === 'en' ? 'Building visual assets' : '构建图表台账',
    'StepB': currentLanguage.value === 'en' ? 'Selecting structure' : '选择结构',
    'StepC': currentLanguage.value === 'en' ? 'Generating review version' : '生成审阅版',
    'StepD': currentLanguage.value === 'en' ? 'Generating final version' : '生成上屏版'
  };
  return stepNames[step] || step;
};

const copyIntegratedContent = async (text: string) => {
  try {
    // 尝试使用 Clipboard API
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
    } else {
      // 回退方案：使用 execCommand
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.left = '-9999px';
      textarea.style.top = '0';
      document.body.appendChild(textarea);
      textarea.focus();
      textarea.select();
      const successful = document.execCommand('copy');
      document.body.removeChild(textarea);
      if (!successful) {
        throw new Error('execCommand copy failed');
      }
    }
    alert(t('copied'));
  } catch (error) {
    console.error('Copy failed:', error);
    alert(t('copyFailed'));
  }
};

// Integrated Voiceover 编辑功能
const startEditIntegratedFinal = () => {
  if (integratedResult.value?.script_final) {
    editedIntegratedFinal.value = integratedResult.value.script_final;
    isEditingIntegratedFinal.value = true;
  }
};

const saveEditIntegratedFinal = () => {
  if (integratedResult.value && editedIntegratedFinal.value.trim()) {
    integratedResult.value.script_final = editedIntegratedFinal.value;
    isEditingIntegratedFinal.value = false;
    alert(currentLanguage.value === 'zh' ? '✅ 内容已保存' : '✅ Content saved');
  }
};

const cancelEditIntegratedFinal = () => {
  isEditingIntegratedFinal.value = false;
  editedIntegratedFinal.value = '';
};

const downloadIntegratedFinal = async () => {
  if (!integratedResult.value || !integratedResult.value.script_final) {
    alert('没有可下载的内容');
    return;
  }
  
  try {
    // 动态导入 html2pdf
    const html2pdf = (await import('html2pdf.js')).default;
    
    // 获取格式化后的 HTML 内容（包含图片）
    const htmlContent = formatScriptText(integratedResult.value.script_final);
    
    // 创建临时容器
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = htmlContent;
    tempDiv.style.padding = '20px';
    tempDiv.style.fontFamily = 'Arial, sans-serif';
    tempDiv.style.lineHeight = '1.6';
    tempDiv.style.color = '#333';
    
    // 添加标题
    const topic = integratedResult.value.request?.topic_hint || '口播稿';
    const titleDiv = document.createElement('div');
    titleDiv.style.fontSize = '24px';
    titleDiv.style.fontWeight = 'bold';
    titleDiv.style.marginBottom = '20px';
    titleDiv.style.textAlign = 'center';
    titleDiv.textContent = topic;
    tempDiv.insertBefore(titleDiv, tempDiv.firstChild);
    
    // 添加样式
    const styleDiv = document.createElement('style');
    styleDiv.textContent = `
      .script-heading-main {
        font-size: 20px;
        font-weight: bold;
        margin: 20px 0 10px 0;
        color: #1a1a1a;
      }
      .script-heading-sub {
        font-size: 16px;
        font-weight: 600;
        margin: 15px 0 8px 0;
        color: #333;
      }
      .script-paragraph {
        margin: 10px 0;
        line-height: 1.8;
      }
      .figure-container {
        margin: 20px 0;
        text-align: center;
        page-break-inside: avoid;
      }
      .figure-image {
        max-width: 100%;
        height: auto;
        border: 1px solid #ddd;
        border-radius: 4px;
        margin-bottom: 10px;
      }
      .figure-caption {
        font-size: 14px;
        color: #666;
        font-style: italic;
        margin: 5px 0;
      }
    `;
    tempDiv.appendChild(styleDiv);
    
    // 创建文件名
    const timestamp = new Date().toISOString().slice(0, 10);
    const filename = `VoxChina_${topic.substring(0, 20)}_${timestamp}.pdf`;
    
    // 配置 PDF 选项
    const opt = {
      margin: [10, 10, 10, 10],
      filename: filename,
      image: { type: 'jpeg', quality: 0.95 },
      html2canvas: { 
        scale: 2,
        useCORS: true,
        logging: false,
        letterRendering: true
      },
      jsPDF: { 
        unit: 'mm', 
        format: 'a4', 
        orientation: 'portrait' 
      }
    };
    
    // 生成 PDF
    console.log('[Integrated] Generating PDF...');
    await html2pdf().set(opt).from(tempDiv).save();
    console.log('[Integrated] PDF downloaded successfully');
    
  } catch (error) {
    console.error('[Integrated] Download error:', error);
    alert('下载失败，请重试。如果问题持续，请联系管理员。');
  }
};

// 下载 Word 格式的口播稿
const downloadIntegratedWord = async () => {
  if (!integratedResult.value || !integratedResult.value.script_final) {
    alert(currentLanguage.value === 'zh' ? '没有可下载的内容' : 'No content to download');
    return;
  }
  
  try {
    const token = localStorage.getItem('vox_token');
    const topic = integratedResult.value.request?.topic_hint || '口播稿';
    
    console.log('[Integrated] Starting Word download for:', topic);
    
    // 收集图片资产信息
    const assets = integratedResult.value.visual_asset_ledger?.assets || [];
    const imageAssets = assets
      .filter((a: any) => a.asset_type === 'FIG' && a.image_path)
      .map((a: any) => ({
        asset_id: a.asset_id,
        caption: a.caption_or_title || a.asset_id,
        image_path: a.image_path
      }));
    
    console.log('[Integrated] Image assets for Word:', imageAssets.length);
    
    const response = await fetch(`${API_BASE_URL}/api/v1/integrated-voiceover/download-word`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        content: integratedResult.value.script_final,
        title: topic,
        image_assets: imageAssets
      })
    });
    
    if (!response.ok) {
      // 尝试获取错误详情
      let errorDetail = '';
      try {
        const errorData = await response.json();
        errorDetail = errorData.detail || '';
      } catch {
        errorDetail = response.statusText;
      }
      console.error('[Integrated] Download failed:', response.status, errorDetail);
      throw new Error(`Download failed: ${response.status} ${errorDetail}`);
    }
    
    // 获取文件并下载
    const blob = await response.blob();
    
    if (blob.size === 0) {
      throw new Error('Empty file received');
    }
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const timestamp = new Date().toISOString().slice(0, 10);
    // 清理文件名中的非法字符
    const safeTopic = topic.replace(/[\/\\:*?"<>|]/g, '_').substring(0, 20);
    a.download = `VoxChina_${safeTopic}_${timestamp}.docx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    console.log('[Integrated] Word document downloaded successfully');
  } catch (error: any) {
    console.error('[Integrated] Word download error:', error);
    const errorMsg = error.message || 'Unknown error';
    alert(currentLanguage.value === 'zh' ? `下载失败: ${errorMsg}` : `Download failed: ${errorMsg}`);
  }
};

// 打开 Integrated Voiceover 标签选择模态框
const openIntegratedTagModal = async () => {
  if (!integratedResult.value || !integratedResult.value.script_final) {
    alert(currentLanguage.value === 'zh' ? '没有可保存的内容' : 'No content to save');
    return;
  }
  
  // 重置状态
  integratedSelectedTags.value = [];
  integratedRecommendedTags.value = [];
  integratedCustomTag.value = '';
  showIntegratedTagModal.value = true;
  
  // 自动获取推荐标签
  await fetchIntegratedRecommendedTags();
};

// 获取 Integrated Voiceover 推荐标签
const fetchIntegratedRecommendedTags = async () => {
  if (!integratedResult.value?.script_final) return;
  
  loadingIntegratedTags.value = true;
  
  try {
    const text = integratedResult.value.script_final.substring(0, 2000);
    
    const response = await fetch(`${API_BASE_URL}/api/v1/integrated-voiceover/recommend-tags`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('vox_token')}`
      },
      body: JSON.stringify({ text, limit: 8 })
    });
    
    if (!response.ok) {
      throw new Error('Failed to get tags');
    }
    
    const data = await response.json();
    integratedRecommendedTags.value = data.tags || [];
    
    console.log('[Integrated] Recommended tags:', integratedRecommendedTags.value);
    
  } catch (error) {
    console.error('[Integrated] Failed to get recommended tags:', error);
  } finally {
    loadingIntegratedTags.value = false;
  }
};

// 切换 Integrated Voiceover 标签选择
const toggleIntegratedTag = (tag: string) => {
  const index = integratedSelectedTags.value.indexOf(tag);
  if (index === -1) {
    integratedSelectedTags.value.push(tag);
  } else {
    integratedSelectedTags.value.splice(index, 1);
  }
};

// 添加自定义标签
const addIntegratedCustomTag = () => {
  const tag = integratedCustomTag.value.trim();
  if (tag && !integratedSelectedTags.value.includes(tag)) {
    integratedSelectedTags.value.push(tag);
    integratedCustomTag.value = '';
  }
};

// 确认保存到知识库
const confirmSaveIntegratedToKB = async () => {
  if (!integratedResult.value || !integratedResult.value.script_final) {
    return;
  }
  
  if (isSavingIntegratedToKB.value) return;
  
  try {
    isSavingIntegratedToKB.value = true;
    
    const tagsToSave = integratedSelectedTags.value.length > 0 
      ? integratedSelectedTags.value 
      : integratedRecommendedTags.value;
    
    const response = await fetch(
      `${API_BASE_URL}/api/v1/integrated-voiceover/save-to-kb`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('vox_token')}`
        },
        body: JSON.stringify({
          script_final: integratedResult.value.script_final,
          topic_hint: integratedResult.value.request?.topic_hint || '',
          speaker_name: integratedResult.value.request?.speaker_name || '',
          speaker_affiliation: integratedResult.value.request?.speaker_affiliation || '',
          task_id: integratedTaskId.value || '',
          tags: tagsToSave
        })
      }
    );
    
    const data = await response.json();
    
    if (response.ok && data.status === 'success') {
      showIntegratedTagModal.value = false;
      alert(currentLanguage.value === 'zh' ? '✅ 已成功保存到知识库' : '✅ Successfully saved to knowledge base');
    } else {
      throw new Error(data.detail || 'Save failed');
    }
  } catch (error: any) {
    console.error('Failed to save to knowledge base:', error);
    const errorMsg = error.message || 'Unknown error';
    alert(currentLanguage.value === 'zh' ? `❌ 保存失败: ${errorMsg}` : `❌ Save failed: ${errorMsg}`);
  } finally {
    isSavingIntegratedToKB.value = false;
  }
};

// Save Integrated Voiceover to Knowledge Base (legacy, kept for compatibility)
const saveIntegratedToKB = async () => {
  if (!integratedResult.value || !integratedResult.value.script_final) {
    alert(currentLanguage.value === 'zh' ? '没有可保存的内容' : 'No content to save');
    return;
  }
  
  if (isSavingIntegratedToKB.value) return;
  
  try {
    isSavingIntegratedToKB.value = true;
    
    const response = await fetch(
      `${API_BASE_URL}/api/v1/integrated-voiceover/save-to-kb`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('vox_token')}`
        },
        body: JSON.stringify({
          script_final: integratedResult.value.script_final,
          topic_hint: integratedResult.value.request?.topic_hint || '',
          speaker_name: integratedResult.value.request?.speaker_name || '',
          speaker_affiliation: integratedResult.value.request?.speaker_affiliation || '',
          task_id: integratedTaskId.value || ''
        })
      }
    );
    
    const data = await response.json();
    
    if (response.ok && data.status === 'success') {
      alert(currentLanguage.value === 'zh' ? '✅ 已成功保存到知识库' : '✅ Successfully saved to knowledge base');
    } else {
      throw new Error(data.detail || 'Save failed');
    }
  } catch (error: any) {
    console.error('Failed to save to knowledge base:', error);
    const errorMsg = error.message || 'Unknown error';
    alert(currentLanguage.value === 'zh' ? `❌ 保存失败: ${errorMsg}` : `❌ Save failed: ${errorMsg}`);
  } finally {
    isSavingIntegratedToKB.value = false;
  }
};

// Drag & Drop State
const isDraggingVoice = ref(false);

const onVoiceDrop = (e: DragEvent) => {
  isDraggingVoice.value = false;
  if (e.dataTransfer?.files && e.dataTransfer.files[0]) {
    uploadVoiceFile.value = e.dataTransfer.files[0];
  }
};


// Helper: Fetch with Auth (Read from localStorage as LegacyApp does)
const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('vox_token');
  const headers = new Headers(options.headers);
  
  if (token) {
    headers.append('Authorization', `Bearer ${token}`);
  }
  
  const response = await fetch(url, { ...options, headers });
  
  if (response.status === 401) {
    console.error("Unauthorized - please login");
    handleLogout(); // Force logout on 401
  }
  
  return response;
};

// Voice Actions
const fetchVoices = async () => {
  try {
    console.log('[VoiceClone] Fetching voices from:', `${API_BASE_URL}/api/v1/voices/`);
    const response = await fetch(`${API_BASE_URL}/api/v1/voices/`);
    console.log('[VoiceClone] Response status:', response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log('[VoiceClone] Received voices:', data);
      voices.value = [...data]; // 强制触发响应式更新
      console.log('[VoiceClone] Voices count:', voices.value.length);
    } else {
      console.error('[VoiceClone] Response not OK:', response.status, response.statusText);
    }
  } catch (e) {
    console.error("[VoiceClone] Failed to fetch voices", e);
  }
};

const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    uploadVoiceFile.value = target.files[0];
  }
};

const uploadVoice = async () => {
  if (!uploadVoiceName.value || !uploadVoiceFile.value) return;
  
  console.log('[VoiceClone] Starting upload:', uploadVoiceName.value, uploadVoiceFile.value.name);
  voiceUploading.value = true;
  uploadError.value = '';
  
  const formData = new FormData();
  formData.append('name', uploadVoiceName.value);
  formData.append('file', uploadVoiceFile.value);
  
  try {
    console.log('[VoiceClone] Uploading to:', `${API_BASE_URL}/api/v1/voices/upload`);
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/voices/upload`, {
      method: 'POST',
      body: formData
    });
    
    console.log('[VoiceClone] Upload response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');
      console.error('[VoiceClone] Upload failed:', errorText);
      throw new Error(`Upload failed: ${response.status}`);
    }
    
    const result = await response.json();
    console.log('[VoiceClone] Upload successful:', result);
    
    // Reset form
    uploadVoiceName.value = '';
    uploadVoiceFile.value = null;
    const fileInput = document.getElementById('voice-upload') as HTMLInputElement;
    if (fileInput) fileInput.value = '';
    
    // 延迟刷新，确保后端已保存
    console.log('[VoiceClone] Refreshing voice list...');
    setTimeout(() => {
      fetchVoices();
    }, 500);
    
    alert('✅ Voice cloned successfully!');
    
  } catch (e: any) {
    console.error('[VoiceClone] Upload error:', e);
    uploadError.value = e.message;
    alert(`❌ Upload failed: ${e.message}`);
  } finally {
    voiceUploading.value = false;
  }
};

const deleteVoice = async (id: string) => {
  if (!confirm('Are you sure you want to delete this voice?')) return;
  try {
    await fetchWithAuth(`${API_BASE_URL}/api/v1/voices/${id}`, { method: 'DELETE' });
    fetchVoices();
  } catch (e) {
    console.error(e);
  }
};

// 文本转语音功能
const generateTTSAudio = async () => {
  if (!ttsInputText.value.trim() || !ttsSelectedVoiceId.value) return;
  
  generatingTTSAudio.value = true;
  ttsGeneratedAudioUrl.value = '';
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/voices/preview`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('vox_token')}`
      },
      body: JSON.stringify({
        voice_id: ttsSelectedVoiceId.value,
        text: ttsInputText.value,
        language: currentLanguage.value
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || '生成失败');
    }
    
    const data = await response.json();
    // 添加时间戳防止浏览器缓存
    const timestamp = new Date().getTime();
    ttsGeneratedAudioUrl.value = `${API_BASE_URL}${data.audio_url}?t=${timestamp}`;
    
    console.log('[TTS] Generated audio:', ttsGeneratedAudioUrl.value);
    
  } catch (error: any) {
    console.error('[TTS] Error:', error);
    alert(currentLanguage.value === 'zh' ? `生成失败: ${error.message}` : `Generation failed: ${error.message}`);
  } finally {
    generatingTTSAudio.value = false;
  }
};

const downloadTTSAudio = () => {
  if (!ttsGeneratedAudioUrl.value) return;
  
  const a = document.createElement('a');
  a.href = ttsGeneratedAudioUrl.value;
  const timestamp = new Date().toISOString().slice(0, 10);
  a.download = `tts_audio_${timestamp}.wav`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
};

const previewVoice = async (id: string) => {
  previewLoading.value = id;
  
  // 完全使用 LegacyApp 的方式：传递 null 让后端生成默认文本
  const text = null;
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/voices/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        voice_id: id,
        text: text,
        language: currentLanguage.value
      })
    });
    
    if (!response.ok) throw new Error("Preview failed");
    
    const data = await response.json();
    // 添加时间戳防止浏览器缓存
    const timestamp = new Date().getTime();
    previewAudioUrl.value = { ...previewAudioUrl.value, [id]: `${API_BASE_URL}${data.audio_url}?t=${timestamp}` };
    
  } catch (e) {
    console.error(e);
    alert("Preview failed");
  } finally {
    previewLoading.value = null;
  }
};




const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text);
    alert('✅ Copied to clipboard');
  } catch (e) {
    console.error('Failed to copy:', e);
    alert('❌ Copy failed');
  }
};

const formatDate = (dateString: string) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Pagination helper
const paginationPages = (total: number, pageSize: number, currentPage: number) => {
  const totalPages = Math.ceil(total / pageSize);
  const pages: number[] = [];
  
  if (totalPages <= 7) {
    // Show all pages if total is 7 or less
    for (let i = 1; i <= totalPages; i++) {
      pages.push(i);
    }
  } else {
    // Always show first page
    pages.push(1);
    
    // Calculate range around current page
    let start = Math.max(2, currentPage - 1);
    let end = Math.min(totalPages - 1, currentPage + 1);
    
    // Add ellipsis after first page if needed
    if (start > 2) {
      pages.push(-1); // -1 represents ellipsis
    }
    
    // Add pages around current page
    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    
    // Add ellipsis before last page if needed
    if (end < totalPages - 1) {
      pages.push(-1); // -1 represents ellipsis
    }
    
    // Always show last page
    pages.push(totalPages);
  }
  
  return pages.filter(p => p !== -1); // Remove ellipsis for now, can add later
};

// Academic Extract Actions
const handleAcademicUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    academicFile.value = target.files[0];
    academicError.value = '';
  }
};

const onAcademicDrop = (e: DragEvent) => {
  isDraggingAcademic.value = false;
  if (e.dataTransfer?.files && e.dataTransfer.files[0]) {
    academicFile.value = e.dataTransfer.files[0];
    academicError.value = '';
  }
};

const ACADEMIC_PROGRESS_STEPS = [
  { step: 'Document Acquisition & Preprocessing', progress: 10 },
  { step: 'Structural Parsing & Noise Filtering', progress: 20 },
  { step: 'Intelligent Chunking & Coverage Assurance', progress: 30 },
  { step: 'CBIT-LLM Semantic Analysis', progress: 45 },
  { step: 'Deep Understanding & Fact Extraction', progress: 60 },
  { step: 'Evidence Consistency Verification', progress: 75 },
  { step: 'Hallucination Filtering & Credibility Assessment', progress: 85 },
  { step: 'Summary Generation & Style Alignment', progress: 95 },
  { step: 'Preparing Final Results', progress: 100 }
];

const startAcademicExtraction = async () => {
  if (!academicFile.value) return;
  
  academicExtracting.value = true;
  academicError.value = '';
  academicResult.value = null;
  academicProgress.value = 0;
  
  // Simulate progress
  const progressInterval = setInterval(() => {
    const nextIndex = ACADEMIC_PROGRESS_STEPS.findIndex(s => s.progress > academicProgress.value);
    if (nextIndex !== -1 && nextIndex < ACADEMIC_PROGRESS_STEPS.length) {
      currentStep.value = ACADEMIC_PROGRESS_STEPS[nextIndex].step;
      academicProgress.value = ACADEMIC_PROGRESS_STEPS[nextIndex].progress;
    }
  }, 2000);
  
  try {
    const formData = new FormData();
    formData.append('file', academicFile.value);
    
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/academic-extract/extract`, {
      method: 'POST',
      body: formData
    });
    
    clearInterval(progressInterval);
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');
      throw new Error(`Extraction failed: ${response.status}`);
    }
    
    const result = await response.json();
    console.log('[Academic Extract] Result:', result);
    
    academicProgress.value = 100;
    currentStep.value = '';
    academicResult.value = result;
    
    // Delay to let user see 100%
    setTimeout(async () => {
      academicExtracting.value = false;
      
      // Automatically save to knowledge base (silent save)
      console.log('[Academic Extract] Auto-saving to knowledge base...');
      try {
        await autoSaveToKB(result);
      } catch (e) {
        console.error('[Academic Extract] Auto-save failed, but continuing:', e);
      }
    }, 500);
    
  } catch (e: any) {
    clearInterval(progressInterval);
    console.error('[Academic Extract] Error:', e);
    academicError.value = e.message || 'Extraction failed';
    alert(`❌ Extraction failed: ${e.message}`);
    academicExtracting.value = false;
    currentStep.value = '';
  }
};

// 获取 Academic Extract 推荐标签
const fetchAcademicRecommendedTags = async () => {
  if (!academicResult.value) return;
  
  loadingAcademicTags.value = true;
  
  try {
    const text = `${academicResult.value.summary_zh || ''}\n${academicResult.value.summary_en || ''}`;
    
    const response = await fetch(`${API_BASE_URL}/api/v1/academic-extract/recommend-tags`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('vox_token')}`
      },
      body: JSON.stringify({ text, limit: 8 })
    });
    
    if (!response.ok) {
      throw new Error('Failed to get tags');
    }
    
    const data = await response.json();
    academicRecommendedTags.value = data.tags || data || [];
    
    console.log('[Academic] Recommended tags:', academicRecommendedTags.value);
    
  } catch (error) {
    console.error('[Academic] Failed to get recommended tags:', error);
    alert(currentLanguage.value === 'zh' ? '获取推荐标签失败' : 'Failed to get recommended tags');
  } finally {
    loadingAcademicTags.value = false;
  }
};

// 切换 Academic Extract 标签选择
const toggleAcademicTag = (tag: string) => {
  const index = academicSelectedTags.value.indexOf(tag);
  if (index === -1) {
    academicSelectedTags.value.push(tag);
  } else {
    academicSelectedTags.value.splice(index, 1);
  }
};

// 添加自定义标签
const addAcademicCustomTag = () => {
  const tag = academicCustomTag.value.trim();
  if (tag && !academicSelectedTags.value.includes(tag) && !academicRecommendedTags.value.includes(tag)) {
    academicSelectedTags.value.push(tag);
    academicCustomTag.value = '';
  } else if (tag && !academicSelectedTags.value.includes(tag)) {
    // 如果标签在推荐列表中但未选中，则选中它
    academicSelectedTags.value.push(tag);
    academicCustomTag.value = '';
  }
};

const copyAcademicResult = async () => {
  if (!academicResult.value) return;
  const text = `【Chinese Summary】\n${academicResult.value.summary_zh}\n\n【English Summary】\n${academicResult.value.summary_en}`;
  try {
    // 尝试使用 Clipboard API
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
    } else {
      // 回退方案：使用 execCommand
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.left = '-9999px';
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
    }
    alert(currentLanguage.value === 'zh' ? '✅ 已复制到剪贴板' : '✅ Copied to clipboard');
  } catch (e) {
    console.error('Failed to copy:', e);
    alert(currentLanguage.value === 'zh' ? '❌ 复制失败' : '❌ Copy failed');
  }
};

// Academic Extract 编辑功能
const startEditAcademicSummary = () => {
  if (academicResult.value) {
    editedAcademicSummaryZh.value = academicResult.value.summary_zh || '';
    editedAcademicSummaryEn.value = academicResult.value.summary_en || '';
    isEditingAcademicSummary.value = true;
  }
};

const saveEditAcademicSummary = () => {
  if (academicResult.value) {
    academicResult.value.summary_zh = editedAcademicSummaryZh.value;
    academicResult.value.summary_en = editedAcademicSummaryEn.value;
    isEditingAcademicSummary.value = false;
    alert(currentLanguage.value === 'zh' ? '✅ 摘要已保存' : '✅ Summary saved');
  }
};

const cancelEditAcademicSummary = () => {
  isEditingAcademicSummary.value = false;
  editedAcademicSummaryZh.value = '';
  editedAcademicSummaryEn.value = '';
};

const downloadAcademicResult = () => {
  if (!academicResult.value) return;
  let content = `Academic Extract Results\n${'='.repeat(50)}\n\n`;
  content += `【Chinese Summary】\n${academicResult.value.summary_zh}\n\n`;
  content += `【English Summary】\n${academicResult.value.summary_en}\n\n`;
  content += `${'='.repeat(50)}\n\n【Structured Fact Table】\n`;
  content += JSON.stringify(academicResult.value.fact_table, null, 2);

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `academic_extract_${Date.now()}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

// 下载 Word 格式的学术摘要
const downloadAcademicWord = async () => {
  if (!academicResult.value) {
    alert(currentLanguage.value === 'zh' ? '没有可下载的内容' : 'No content to download');
    return;
  }
  
  try {
    const token = localStorage.getItem('vox_token');
    
    console.log('[Academic] Starting Word download...');
    
    const response = await fetch(`${API_BASE_URL}/api/v1/academic-extract/download-word`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        summary_zh: academicResult.value.summary_zh,
        summary_en: academicResult.value.summary_en,
        fact_table: academicResult.value.fact_table
      })
    });
    
    if (!response.ok) {
      // 尝试获取错误详情
      let errorDetail = '';
      try {
        const errorData = await response.json();
        errorDetail = errorData.detail || '';
      } catch {
        errorDetail = response.statusText;
      }
      console.error('[Academic] Download failed:', response.status, errorDetail);
      throw new Error(`Download failed: ${response.status} ${errorDetail}`);
    }
    
    // 获取文件并下载
    const blob = await response.blob();
    
    if (blob.size === 0) {
      throw new Error('Empty file received');
    }
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const timestamp = new Date().toISOString().slice(0, 10);
    a.download = `academic_extract_${timestamp}.docx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    console.log('[Academic] Word document downloaded successfully');
  } catch (error: any) {
    console.error('[Academic] Word download error:', error);
    const errorMsg = error.message || 'Unknown error';
    alert(currentLanguage.value === 'zh' ? `下载失败: ${errorMsg}` : `Download failed: ${errorMsg}`);
  }
};

// Save Academic Extract to Knowledge Base
const saveAcademicToKB = async () => {
  if (!academicResult.value) {
    alert(currentLanguage.value === 'zh' ? '没有可保存的内容' : 'No content to save');
    return;
  }
  
  if (isSavingAcademicToKB.value) return;
  
  try {
    isSavingAcademicToKB.value = true;
    
    const response = await fetch(
      `${API_BASE_URL}/api/v1/academic-extract/save-to-kb`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('vox_token')}`
        },
        body: JSON.stringify({
          summary_zh: academicResult.value.summary_zh,
          summary_en: academicResult.value.summary_en,
          fact_table: academicResult.value.fact_table,
          tags: academicSelectedTags.value.length > 0 ? academicSelectedTags.value : academicRecommendedTags.value,  // 优先使用用户选择的标签
          task_id: academicResult.value.extract_id || ''  // 添加 task_id 用于关联跳转
        })
      }
    );
    
    const data = await response.json();
    
    if (response.ok && data.status === 'success') {
      alert(currentLanguage.value === 'zh' ? '✅ 已成功保存到知识库' : '✅ Successfully saved to knowledge base');
    } else {
      throw new Error(data.detail || 'Save failed');
    }
  } catch (error: any) {
    console.error('Failed to save to knowledge base:', error);
    const errorMsg = error.message || 'Unknown error';
    alert(currentLanguage.value === 'zh' ? `❌ 保存失败: ${errorMsg}` : `❌ Save failed: ${errorMsg}`);
  } finally {
    isSavingAcademicToKB.value = false;
  }
};

const fetchAcademicHistory = async () => {
  try {
    console.log('[Academic Extract] Fetching history...');
    const offset = (academicHistoryPage.value - 1) * academicHistoryPageSize.value;
    const params = new URLSearchParams({
      limit: academicHistoryPageSize.value.toString(),
      offset: offset.toString()
    });
    
    if (academicHistorySearch.value) {
      params.append('search', academicHistorySearch.value);
    }
    
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/academic-extract/extracts?${params}`);
    
    if (response.ok) {
      const data = await response.json();
      if (data.items) {
        academicHistory.value = data.items;
        academicHistoryTotal.value = data.total || data.items.length;
      } else {
        // Fallback for old API format
        academicHistory.value = data;
        academicHistoryTotal.value = data.length;
      }
      console.log('[Academic Extract] History loaded:', academicHistory.value.length, 'items, total:', academicHistoryTotal.value);
    }
  } catch (e) {
    console.error('[Academic Extract] Failed to fetch history:', e);
  }
};

const searchAcademicHistory = () => {
  academicHistoryPage.value = 1; // Reset to first page when searching
  fetchAcademicHistory();
};

const viewAcademicHistory = async (extractId: string) => {
  try {
    console.log('[Academic Extract] Viewing history item:', extractId);
    
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/academic-extract/extracts/${extractId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch extract detail');
    }
    
    const detail = await response.json();
    
    academicResult.value = {
      extract_id: detail.id,
      summary_zh: detail.summary_zh,
      summary_en: detail.summary_en,
      fact_table: detail.fact_table,
      metadata: detail.metadata
    };
    
    // Scroll to result
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
  } catch (e) {
    console.error('[Academic Extract] Failed to view history item:', e);
    alert('❌ Failed to load history details');
  }
};

const confirmDeleteAcademicHistory = async (extractId: string, title: string) => {
  if (!confirm(`Are you sure you want to delete "${title}"? This cannot be undone.`)) {
    return;
  }
  
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/academic-extract/extracts/${extractId}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      throw new Error('Delete failed');
    }
    
    alert('✅ Delete successful!');
    
    // Clear current result if it's the deleted one
    if (academicResult.value?.extract_id === extractId) {
      academicResult.value = null;
    }
    
    // Refresh history
    await fetchAcademicHistory();
    
  } catch (e: any) {
    console.error('[Academic Extract] Failed to delete extract:', e);
    alert(`❌ Delete failed: ${e.message}`);
  }
};


// TTS Functions for Academic Extract
const generateAcademicAudio = async () => {
  if (!academicResult.value) return;
  
  // Auto-select first voice if none selected
  if (!selectedVoiceId.value && voices.value.length > 0) {
    selectedVoiceId.value = voices.value[0].id;
  }
  
  if (!selectedVoiceId.value) {
    alert(t('noSummaryText'));
    return;
  }
  
  const text = selectedSummaryLang.value === 'zh' 
    ? academicResult.value.summary_zh 
    : academicResult.value.summary_en;
    
  if (!text) {
    alert(t('noSummaryText'));
    return;
  }
  
  // Warn user about expected wait time
  if (!confirm(currentLanguage.value === 'zh' 
    ? '音频生成需要约2-5分钟（取决于文本长度），请耐心等待。确定继续吗？' 
    : 'Audio generation takes about 2-5 minutes (depending on text length). Please wait patiently. Continue?')) {
    return;
  }
  
  isGeneratingAudio.value = true;
  audioUrl.value = '';
  
  try {
    // Increase timeout for TTS generation (5 minutes for long texts)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 300000);
    
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/voices/preview`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        voice_id: selectedVoiceId.value,
        text: text,
        language: selectedSummaryLang.value
      }),
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');
      throw new Error(`Generation failed: ${response.status} - ${errorText}`);
    }
    
    const data = await response.json();
    console.log('[TTS] Raw response:', data);
    
    // Ensure URL is correct relative to API base if needed
    if (API_BASE_URL && !data.audio_url.startsWith('http')) {
      audioUrl.value = `${API_BASE_URL}${data.audio_url}`;
      console.log('[TTS] Using full URL:', audioUrl.value);
    } else {
      audioUrl.value = data.audio_url;
      console.log('[TTS] Using relative URL:', audioUrl.value);
    }
    
    alert(currentLanguage.value === 'zh' ? '✅ 音频生成成功！' : '✅ Audio generated successfully!');
    
  } catch (e: any) {
    console.error('TTS Generation failed:', e);
    if (e.name === 'AbortError') {
      alert(currentLanguage.value === 'zh' 
        ? '⏱️ 请求超时，音频生成时间过长。请稍后重试或联系管理员。' 
        : '⏱️ Request timeout. Please try again later or contact administrator.');
    } else {
      alert(t('audioGenerationFailed') + '\n' + (e.message || ''));
    }
  } finally {
    isGeneratingAudio.value = false;
  }
};

// TTS Functions for Integrated Voiceover
const generateIntegratedAudio = async () => {
  if (!integratedResult.value || !integratedResult.value.script_final) return;
  
  // Auto-select first voice if none selected
  if (!selectedIntegratedVoiceId.value && voices.value.length > 0) {
    selectedIntegratedVoiceId.value = voices.value[0].id;
  }
  
  if (!selectedIntegratedVoiceId.value) {
    alert(currentLanguage.value === 'zh' ? '请先选择一个声音' : 'Please select a voice first');
    return;
  }
  
  const text = integratedResult.value.script_final;
    
  if (!text) {
    alert(currentLanguage.value === 'zh' ? '没有可用的脚本文本' : 'No script text available');
    return;
  }
  
  // Warn user about expected wait time
  if (!confirm(currentLanguage.value === 'zh' 
    ? '音频生成需要约2-5分钟（取决于文本长度），请耐心等待。确定继续吗？' 
    : 'Audio generation takes about 2-5 minutes (depending on text length). Please wait patiently. Continue?')) {
    return;
  }
  
  isGeneratingIntegratedAudio.value = true;
  integratedAudioUrl.value = '';
  
  try {
    // Increase timeout for TTS generation (5 minutes for long texts)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 300000);
    
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/voices/preview`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        voice_id: selectedIntegratedVoiceId.value,
        text: text,
        language: 'zh' // Integrated Voiceover is typically in Chinese
      }),
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');
      throw new Error(`Generation failed: ${response.status} - ${errorText}`);
    }
    
    const data = await response.json();
    console.log('[TTS Integrated] Raw response:', data);
    
    // Ensure URL is correct relative to API base if needed
    if (API_BASE_URL && !data.audio_url.startsWith('http')) {
      integratedAudioUrl.value = `${API_BASE_URL}${data.audio_url}`;
      console.log('[TTS Integrated] Using full URL:', integratedAudioUrl.value);
    } else {
      integratedAudioUrl.value = data.audio_url;
      console.log('[TTS Integrated] Using relative URL:', integratedAudioUrl.value);
    }
    
    alert(currentLanguage.value === 'zh' ? '✅ 音频生成成功！' : '✅ Audio generated successfully!');
    
  } catch (e: any) {
    console.error('TTS Integrated Generation failed:', e);
    if (e.name === 'AbortError') {
      alert(currentLanguage.value === 'zh' 
        ? '⏱️ 请求超时，音频生成时间过长。请稍后重试或联系管理员。' 
        : '⏱️ Request timeout. Please try again later or contact administrator.');
    } else {
      alert((currentLanguage.value === 'zh' ? '音频生成失败' : 'Audio generation failed') + '\n' + (e.message || ''));
    }
  } finally {
    isGeneratingIntegratedAudio.value = false;
  }
};

// Tag Management Actions
const fetchTags = async () => {
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/knowledge/tags`);
    if (response.ok) {
      availableTags.value = await response.json();
    }
  } catch (e) {
    console.error("Failed to fetch tags", e);
  }
};

const getRecommendedTags = async (text: string) => {
  tagsLoading.value = true;
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/knowledge/recommend-tags`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, limit: 5 })
    });
    
    if (response.ok) {
      recommendedTags.value = await response.json();
      // 只显示推荐标签，不自动选中，让用户自己决定是否采用
      console.log('[Tag Recommendation] 推荐标签:', recommendedTags.value);
    }
  } catch (e) {
    console.error("Failed to get recommended tags", e);
  } finally {
    tagsLoading.value = false;
  }
};

const toggleTag = (tag: string) => {
  if (selectedTags.value.has(tag)) {
    selectedTags.value.delete(tag);
  } else {
    selectedTags.value.add(tag);
  }
};

const addCustomTag = () => {
  const tag = customTagInput.value.trim();
  if (tag && !selectedTags.value.has(tag)) {
    selectedTags.value.add(tag);
    // Optionally add to available tags locally for this session
    if (!availableTags.value.includes(tag)) {
      availableTags.value.push(tag);
    }
    customTagInput.value = '';
  }
};

// Tag Filter Function
const filterByTag = async () => {
  // Reset page to 1 when filtering
  knowledgePage.value = 1;
  await fetchKnowledgeDocs();
};

// Add New Tag to Database
const addNewTag = async () => {
  const tag = newTagInput.value.trim();
  if (!tag) return;

  try {
    tagsLoading.value = true;
    const response = await fetch(`${API_BASE_URL}/api/v1/knowledge/tags`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ name: tag })
    });

    if (response.ok) {
      alert(currentLanguage.value === 'zh' ? '标签添加成功！' : 'Tag added successfully!');
      newTagInput.value = '';
      await fetchTags();
    } else {
      throw new Error('Failed to add tag');
    }
  } catch (error) {
    console.error('Error adding tag:', error);
    alert(currentLanguage.value === 'zh' ? '添加标签失败' : 'Failed to add tag');
  } finally {
    tagsLoading.value = false;
  }
};

// Delete Tag (Note: This only removes from local list, backend doesn't have delete endpoint)
const deleteTag = async (tag: string) => {
  if (confirm(currentLanguage.value === 'zh' 
    ? `确定要删除标签 "${tag}" 吗？` 
    : `Are you sure you want to delete tag "${tag}"?`)) {
    // Remove from local list
    availableTags.value = availableTags.value.filter(t => t !== tag);
    alert(currentLanguage.value === 'zh' 
      ? '标签已从列表中移除（注意：已使用此标签的文档不受影响）' 
      : 'Tag removed from list (Note: Documents using this tag are not affected)');
  }
};

// Upload Article Functions
const openUploadArticleDialog = () => {
  // 重置所有状态
  uploadArticleFile.value = null;
  uploadedFileContent.value = null;
  selectedTags.value.clear();
  recommendedTags.value = [];
  customTagInput.value = '';
  
  // 加载可用标签
  fetchTags();
  
  // 打开对话框
  showUploadArticleDialog.value = true;
};

const handleUploadFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    uploadArticleFile.value = target.files[0];
    // 自动解析文件并推荐标签
    await processUploadedFile(target.files[0]);
  }
};

const handleUploadFileDrop = async (event: DragEvent) => {
  isUploadDragging.value = false;
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    uploadArticleFile.value = event.dataTransfer.files[0];
    // 自动解析文件并推荐标签
    await processUploadedFile(event.dataTransfer.files[0]);
  }
};

const cancelUploadArticle = () => {
  showUploadArticleDialog.value = false;
  uploadArticleFile.value = null;
  uploadedFileContent.value = null;
  selectedTags.value.clear();
  recommendedTags.value = [];
  customTagInput.value = '';
};

// 处理文件上传并解析内容
const uploadedFileContent = ref<any>(null);

const processUploadedFile = async (file: File) => {
  try {
    tagsLoading.value = true;
    
    // 上传并解析文件
    const formData = new FormData();
    formData.append('file', file);

    const uploadResponse = await fetch(`${API_BASE_URL}/api/v1/knowledge/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: formData
    });

    if (!uploadResponse.ok) {
      throw new Error('File parsing failed');
    }

    uploadedFileContent.value = await uploadResponse.json();

    // 自动推荐标签（不自动选中）
    await getRecommendedTags(uploadedFileContent.value.title || uploadedFileContent.value.content?.substring(0, 200) || '');
  } catch (error) {
    console.error('Error processing file:', error);
    alert(currentLanguage.value === 'zh' 
      ? '文件解析失败，但您仍可手动选择标签并上传' 
      : 'File parsing failed, but you can still select tags manually and upload');
  } finally {
    tagsLoading.value = false;
  }
};

const uploadArticleToKB = async () => {
  if (!uploadArticleFile.value || !uploadedFileContent.value) return;

  try {
    isUploadingArticle.value = true;

    // 保存到知识库
    const saveResponse = await fetch(`${API_BASE_URL}/api/v1/knowledge/documents`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        content: uploadedFileContent.value.content,
        metadata: {
          title: uploadedFileContent.value.title || uploadArticleFile.value.name,
          type: 'UPLOADED',
          filename: uploadArticleFile.value.name,
          tags: Array.from(selectedTags.value),
          created_at: new Date().toISOString()
        }
      })
    });

    if (!saveResponse.ok) {
      throw new Error('Failed to save to knowledge base');
    }

    alert(currentLanguage.value === 'zh' 
      ? '文章上传成功！' 
      : 'Article uploaded successfully!');
    
    cancelUploadArticle();
    await fetchKnowledgeDocs();
  } catch (error) {
    console.error('Error uploading article:', error);
    alert(currentLanguage.value === 'zh' 
      ? '上传失败，请重试' 
      : 'Upload failed, please try again');
  } finally {
    isUploadingArticle.value = false;
  }
};

// Knowledge Base Save Functions
const saveToKnowledgeBase = async () => {
  if (!pendingKBSave.value) return;
  
  isSavingToKB.value = true;
  
  try {
    console.log('[KB Save] Saving to knowledge base...', {
      summary_zh_length: pendingKBSave.value.summary_zh?.length,
      summary_en_length: pendingKBSave.value.summary_en?.length,
      has_fact_table: !!pendingKBSave.value.fact_table,
      tags: Array.from(selectedTags.value)
    });
    
    // Show progress: Generating embeddings
    if (currentLanguage.value === 'zh') {
      alert('正在生成向量嵌入...\n这可能需要1-2分钟，请耐心等待。');
    } else {
      alert('Generating vector embeddings...\nThis may take 1-2 minutes, please wait patiently.');
    }
    
    // Increase timeout to 120 seconds for embedding generation (doubled for large texts)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000);
    
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/academic-extract/save-to-kb`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        summary_zh: pendingKBSave.value.summary_zh || '',
        summary_en: pendingKBSave.value.summary_en || '',
        fact_table: pendingKBSave.value.fact_table || {},
        tags: Array.from(selectedTags.value)
      }),
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (response.ok) {
      const result = await response.json();
      console.log('[KB Save] Success:', result);
      
      // Show success message with progress update
      alert(currentLanguage.value === 'zh' 
        ? '✅ 保存成功！\n文档已添加到知识库。\n切换到"知识库"标签页即可查看。' 
        : '✅ Save successful!\nDocument added to knowledge base.\nSwitch to "Knowledge Database" tab to view.');
      
      // Always refresh knowledge database list (even if not on that tab)
      await fetchKnowledgeDocs();
      
      console.log('[KB Save] Knowledge database list refreshed');
    } else {
      const errorText = await response.text().catch(() => 'Unknown error');
      console.error('[KB Save] Failed:', response.status, errorText);
      throw new Error(`Save failed: ${response.status} - ${errorText}`);
    }
  } catch (e: any) {
    console.error('[KB Save] Error:', e);
    const errorMsg = e.message || 'Unknown error';
    if (e.name === 'AbortError') {
      alert(currentLanguage.value === 'zh' 
        ? '⏱️ 保存超时（120秒）。这可能是因为嵌入模型响应较慢，请稍后重试或联系管理员。\n建议：检查Ollama服务是否正常运行。' 
        : '⏱️ Save timeout (120s). This may be due to slow embedding model response. Please try again later or contact administrator.\nTip: Check if Ollama service is running properly.');
    } else if (errorMsg.includes('Ollama') || errorMsg.includes('embedding')) {
      alert(currentLanguage.value === 'zh' 
        ? '❌ 保存失败：嵌入服务不可用。请确保 Ollama 服务正在运行并已加载 qwen3-embedding 模型。' 
        : '❌ Save failed: Embedding service unavailable. Please ensure Ollama is running with qwen3-embedding model.');
    } else {
      alert(t('savedToKBFailed') + '\n详细信息: ' + errorMsg);
    }
  } finally {
    isSavingToKB.value = false;
    showSaveToKBDialog.value = false;
    pendingKBSave.value = null;
  }
};

const skipKBSave = () => {
  showSaveToKBDialog.value = false;
  pendingKBSave.value = null;
};

// Auto-save to KB (silent, no dialog)
const autoSaveToKB = async (result: any) => {
  try {
    console.log('[Auto KB Save] Starting automatic save to knowledge base...');
    
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/academic-extract/save-to-kb`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        summary_zh: result.summary_zh || '',
        summary_en: result.summary_en || '',
        fact_table: result.fact_table || {}
      })
    });
    
    if (response.ok) {
      const saveResult = await response.json();
      console.log('[Auto KB Save] ✅ Success:', saveResult);
      
      // Silently refresh history list
      await fetchAcademicHistory();
      console.log('[Auto KB Save] History refreshed');
      
    } else {
      const errorText = await response.text().catch(() => 'Unknown error');
      console.error('[Auto KB Save] ❌ Failed:', response.status, errorText);
      // Don't throw error, just log it (silent failure)
    }
  } catch (e: any) {
    console.error('[Auto KB Save] ❌ Error:', e);
    // Silent failure - don't interrupt user experience
  }
};

// Knowledge Actions
const fetchKnowledgeDocs = async () => {
  knowledgeLoading.value = true;
  try {
    const offset = (knowledgePage.value - 1) * knowledgePageSize.value;
    
    if (knowledgeSearchQuery.value) {
      // Search mode
      const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/knowledge/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: knowledgeSearchQuery.value, 
          limit: knowledgePageSize.value,
          offset: offset
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        let docs = data.items || data;
        
        // Apply tag filter if selected
        if (selectedTagFilter.value) {
          docs = docs.filter((doc: any) => 
            doc.payload.tags && doc.payload.tags.includes(selectedTagFilter.value)
          );
        }
        
        knowledgeDocs.value = docs;
        knowledgeTotal.value = docs.length;
      }
    } else {
      // List mode
      const params = new URLSearchParams({
        limit: knowledgePageSize.value.toString(),
        offset: offset.toString()
      });
      
      const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/knowledge/list?${params}`);
      
      if (response.ok) {
        const data = await response.json();
        let docs = data.items || data;
        
        // Apply tag filter if selected
        if (selectedTagFilter.value) {
          docs = docs.filter((doc: any) => 
            doc.payload.tags && doc.payload.tags.includes(selectedTagFilter.value)
          );
        }
        
        knowledgeDocs.value = docs;
        knowledgeTotal.value = docs.length;
      }
    }
  } catch (e) {
    console.error("Failed to fetch knowledge docs", e);
  } finally {
    knowledgeLoading.value = false;
  }
};

const searchKnowledge = () => {
  knowledgePage.value = 1; // Reset to first page when searching
  fetchKnowledgeDocs();
};

const deleteKnowledgeDoc = async (id: string) => {
  if (!confirm('Are you sure you want to delete this document from the Knowledge Base?')) return;
  try {
    await fetchWithAuth(`${API_BASE_URL}/api/v1/knowledge/${id}`, { method: 'DELETE' });
    fetchKnowledgeDocs();
  } catch (e) {
    console.error(e);
  }
};

const viewKnowledgeDetail = (doc: any) => {
  // Format detailed information
  const payload = doc.payload || {};
  const title = payload.title || 'Untitled';
  const type = payload.type || 'unknown';
  const createdAt = formatDate(payload.created_at);
  const summaryZh = payload.summary_zh || '';
  const summaryEn = payload.summary_en || '';
  const content = payload.content || '';
  
  // Build detail message
  let detailMsg = `📄 ${title}\n`;
  detailMsg += `\n📌 Type: ${type}`;
  detailMsg += `\n🕒 Created: ${createdAt}`;
  detailMsg += `\n📊 Score: ${doc.score ? doc.score.toFixed(4) : 'N/A'}`;
  
  if (summaryZh) {
    detailMsg += `\n\n【中文摘要】\n${summaryZh}`;
  }
  
  if (summaryEn) {
    detailMsg += `\n\n【English Summary】\n${summaryEn}`;
  }
  
  if (content && !summaryZh && !summaryEn) {
    // Show content if no summaries available
    const truncatedContent = content.length > 500 ? content.substring(0, 500) + '...' : content;
    detailMsg += `\n\n【Content】\n${truncatedContent}`;
  }
  
  // Show fact table if available
  if (payload.fact_table) {
    detailMsg += `\n\n【Additional Info】`;
    if (payload.fact_table.basic_info?.research_question) {
      detailMsg += `\n🔬 Research: ${payload.fact_table.basic_info.research_question.question || 'N/A'}`;
    }
    if (payload.fact_table.key_findings && Array.isArray(payload.fact_table.key_findings)) {
      detailMsg += `\n📊 Findings: ${payload.fact_table.key_findings.length} items`;
    }
  }
  
  alert(detailMsg);
};

// 导航到源任务（从知识库跳转到历史处理的文章）
const navigateToSourceTask = (payload: any) => {
  const sourceType = payload.source_type;
  const sourceTaskId = payload.source_task_id;
  
  if (!sourceTaskId) {
    alert(currentLanguage.value === 'zh' ? '无法找到源任务信息' : 'Source task information not found');
    return;
  }
  
  if (sourceType === 'integrated_voiceover') {
    // 切换到 Integrated Voiceover 标签页并加载历史任务
    activeTab.value = 'integrated';
    // 尝试从历史记录中加载该任务
    loadIntegratedHistoryTask(sourceTaskId);
  } else if (sourceType === 'academic_extract') {
    // 切换到 Academic Extract 标签页并加载历史任务
    activeTab.value = 'academic';
    // 尝试从历史记录中加载该任务
    loadAcademicHistoryTask(sourceTaskId);
  } else {
    alert(currentLanguage.value === 'zh' 
      ? `源任务类型: ${sourceType || '未知'}\n任务ID: ${sourceTaskId}` 
      : `Source type: ${sourceType || 'Unknown'}\nTask ID: ${sourceTaskId}`);
  }
};

// 加载 Integrated Voiceover 历史任务
const loadIntegratedHistoryTask = async (taskId: string) => {
  try {
    console.log('[Integrated] Loading history task:', taskId);
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/integrated-voiceover/status/${taskId}`);
    
    if (response.ok) {
      const data = await response.json();
      console.log('[Integrated] API response:', data);
      
      if (data.status === 'completed' && data.result) {
        integratedResult.value = data.result;
        integratedStatus.value = data;
        integratedTaskId.value = taskId;
        
        // 确保 parsed_docs 被正确设置
        console.log('[Integrated] parsed_docs:', data.parsed_docs?.length || 0, 'documents');
        
        alert(currentLanguage.value === 'zh' ? '✅ 已加载历史任务' : '✅ Historical task loaded');
      } else {
        console.warn('[Integrated] Task not completed:', data.status);
        alert(currentLanguage.value === 'zh' ? '该任务尚未完成或结果不可用' : 'Task not completed or result unavailable');
      }
    } else if (response.status === 404) {
      console.warn('[Integrated] Task not found in backend:', taskId);
      alert(currentLanguage.value === 'zh' 
        ? '历史任务未找到，可能已被清理或服务已重启' 
        : 'Historical task not found, it may have been cleaned up or service restarted');
    } else {
      console.error('[Integrated] API error:', response.status);
      alert(currentLanguage.value === 'zh' ? '无法加载历史任务' : 'Failed to load historical task');
    }
  } catch (error) {
    console.error('Failed to load integrated history task:', error);
    alert(currentLanguage.value === 'zh' ? '加载失败' : 'Load failed');
  }
};

// 加载 Academic Extract 历史任务
const loadAcademicHistoryTask = async (taskId: string) => {
  try {
    console.log('[Academic] Loading history task:', taskId);
    
    // 直接从 API 获取详情
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/academic-extract/extracts/${taskId}`);
    
    if (response.ok) {
      const detail = await response.json();
      console.log('[Academic] Loaded detail:', detail);
      
      academicResult.value = {
        extract_id: detail.id,
        summary_zh: detail.summary_zh,
        summary_en: detail.summary_en,
        fact_table: detail.fact_table,
        metadata: detail.metadata
      };
      
      // 清除之前的标签选择
      academicSelectedTags.value = [];
      academicRecommendedTags.value = [];
      
      alert(currentLanguage.value === 'zh' ? '✅ 已加载历史任务' : '✅ Historical task loaded');
    } else {
      // 如果 API 获取失败，尝试从本地历史记录中查找
      console.log('[Academic] API failed, trying local history...');
      await fetchAcademicHistory();
      const historyItem = academicHistory.value.find((item: any) => item.id === taskId);
      
      if (historyItem) {
        academicResult.value = {
          extract_id: historyItem.id,
          summary_zh: historyItem.summary_zh,
          summary_en: historyItem.summary_en,
          fact_table: historyItem.fact_table
        };
        alert(currentLanguage.value === 'zh' ? '✅ 已加载历史任务' : '✅ Historical task loaded');
      } else {
        alert(currentLanguage.value === 'zh' ? '无法找到该历史任务' : 'Historical task not found');
      }
    }
  } catch (error) {
    console.error('Failed to load academic history task:', error);
    alert(currentLanguage.value === 'zh' ? '加载失败' : 'Load failed');
  }
};

// LLM Config Actions
const fetchLLMConfig = async () => {
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/llm/config`)
    if (response.ok) {
      const data = await response.json()
      llmConfig.value = data
      selectedProvider.value = data.provider || 'openai'
      selectedModel.value = data.model || ''
      // 不显示实际的 API Key，只显示是否已配置
      selectedApiKey.value = ''
      console.log('✅ LLM配置已加载:', data)
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
  // 验证必填字段
  if (!selectedModel.value) {
    llmConfigError.value = '请先选择一个模型'
    return
  }
  
  if (selectedProvider.value === 'openai' && !selectedApiKey.value && !llmConfig.value.api_key_set) {
    llmConfigError.value = '请输入 API Key'
    return
  }
  
  llmConfigLoading.value = true
  llmConfigError.value = ''
  console.log('🔄 保存配置 - Provider:', selectedProvider.value, 'Model:', selectedModel.value)
  
  try {
    const payload: any = {
      provider: selectedProvider.value,
      model: selectedModel.value
    }
    
    // 只在有新 API Key 时才发送
    if (selectedApiKey.value) {
      payload.api_key = selectedApiKey.value
    }
    
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/llm/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`保存失败 (${response.status}): ${errorText}`)
    }
    
    const result = await response.json()
    console.log('✅ LLM配置已保存:', result)
    
    // 更新本地状态
    llmConfig.value.model = selectedModel.value
    llmConfigError.value = ''
    
    // 显示成功消息
    alert('✅ LLM 配置已保存并生效！')
    llmSettingsOpen.value = false
    
  } catch (e: any) {
    console.error('❌ 保存LLM配置失败:', e)
    llmConfigError.value = e.message || '保存失败'
  } finally {
    llmConfigLoading.value = false
  }
}

// ==================== Integrated Voiceover History Management ====================
const fetchIntegratedHistory = async () => {
  loadingHistory.value = true;
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/integrated-voiceover/list`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('vox_token')}`
      }
    });
    if (response.ok) {
      const data = await response.json();
      integratedHistoryList.value = data;
    } else {
      console.error('[Integrated History] Failed to fetch:', response.status);
    }
  } catch (e) {
    console.error('[Integrated History] Error:', e);
  } finally {
    loadingHistory.value = false;
  }
};

const deleteIntegratedTask = async (taskId: string) => {
  if (!confirm(t('confirmDelete'))) return;
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/integrated-voiceover/delete/${taskId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('vox_token')}`
      }
    });
    if (response.ok) {
      // Remove from list
      integratedHistoryList.value = integratedHistoryList.value.filter(t => t.task_id !== taskId);
    } else {
      alert('删除失败');
    }
  } catch (e) {
    console.error('[Integrated History] Delete error:', e);
    alert('删除失败');
  }
};

const loadIntegratedTask = async (taskId: string) => {
  try {
    console.log('[Integrated History] Loading task:', taskId);
    const response = await fetch(`${API_BASE_URL}/api/v1/integrated-voiceover/status/${taskId}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('vox_token')}`
      }
    });
    
    console.log('[Integrated History] Response status:', response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log('[Integrated History] Loaded task data:', data);
      console.log('[Integrated History] Result present:', !!data.result);
      console.log('[Integrated History] Parsed docs count:', data.parsed_docs?.length || 0);
      
      // Load the task result
      integratedTaskId.value = taskId;
      integratedStatus.value = {
        status: data.status,
        progress: data.progress || 100,
        current_step: data.current_step || 'StepD',
        error: data.error
      };
      integratedResult.value = data.result;
      integratedParsedDocs.value = data.parsed_docs || [];
      
      // Set result tab to style profile by default
      integratedResultTab.value = 'style';
      
      showIntegratedHistory.value = false;
      
      console.log('[Integrated History] ✅ Task loaded successfully');
    } else {
      const errorText = await response.text();
      console.error('[Integrated History] Failed to load task. Status:', response.status);
      console.error('[Integrated History] Error response:', errorText);
      alert(`加载任务失败 (${response.status}): ${errorText.substring(0, 100)}`);
    }
  } catch (e) {
    console.error('[Integrated History] Load error:', e);
    console.error('[Integrated History] Error details:', e.message, e.stack);
    alert(`加载任务失败: ${e.message}`);
  }
};

// ==================== Image Management ====================
const fetchImages = async () => {
  loadingImages.value = true;
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/images/list`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('vox_token')}`
      }
    });
    if (response.ok) {
      const data = await response.json();
      imageList.value = data.images || [];
    } else {
      console.error('[Image Management] Failed to fetch:', response.status);
    }
  } catch (e) {
    console.error('[Image Management] Error:', e);
  } finally {
    loadingImages.value = false;
  }
};

const deleteImage = async (filename: string, skipConfirm: boolean = false) => {
  if (!skipConfirm && !confirm(`${t('confirmDelete')}`)) return;
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/images/${filename}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('vox_token')}`
      }
    });
    if (response.ok) {
      imageList.value = imageList.value.filter(img => img.filename !== filename);
      selectedImages.value.delete(filename);
      return true;
    } else {
      return false;
    }
  } catch (e) {
    console.error('[Image Management] Delete error:', e);
    return false;
  }
};

const deleteSelectedImages = async () => {
  if (selectedImages.value.size === 0) {
    alert('请先选择要删除的图片');
    return;
  }
  
  if (!confirm(`确定要删除选中的 ${selectedImages.value.size} 张图片吗？`)) return;
  
  // 批量删除，跳过单个确认
  const promises = Array.from(selectedImages.value).map(filename => deleteImage(filename, true));
  const results = await Promise.all(promises);
  
  // 统计成功和失败的数量
  const successCount = results.filter(r => r).length;
  const failCount = results.length - successCount;
  
  if (failCount > 0) {
    alert(`删除完成：成功 ${successCount} 张，失败 ${failCount} 张`);
  }
  
  selectedImages.value.clear();
};

const toggleImageSelection = (filename: string) => {
  if (selectedImages.value.has(filename)) {
    selectedImages.value.delete(filename);
  } else {
    selectedImages.value.add(filename);
  }
};

const toggleSelectAll = () => {
  if (selectedImages.value.size === imageList.value.length) {
    selectedImages.value.clear();
  } else {
    imageList.value.forEach(img => selectedImages.value.add(img.filename));
  }
};

const cleanupOldImages = async (days: number = 30) => {
  if (!confirm(`确定要清理 ${days} 天前的旧图片吗？`)) return;
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/images/cleanup?days=${days}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('vox_token')}`
      }
    });
    if (response.ok) {
      const data = await response.json();
      alert(data.message);
      fetchImages();
    } else {
      alert('清理失败');
    }
  } catch (e) {
    console.error('[Image Management] Cleanup error:', e);
    alert('清理失败');
  }
};

// AI Search Functions
const performSearch = async () => {
  if (!searchQuery.value.trim()) {
    alert(currentLanguage.value === 'zh' ? '请输入搜索内容' : 'Please enter search query');
    return;
  }

  isSearching.value = true;
  searchResults.value = null;
  searchResultsList.value = [];
  aiAnswer.value = '';
  searchDuration.value = 0;

  const startTime = Date.now();

  try {
    // Add to search history
    if (!searchHistory.value.includes(searchQuery.value.trim())) {
      searchHistory.value.unshift(searchQuery.value.trim());
      if (searchHistory.value.length > 10) {
        searchHistory.value = searchHistory.value.slice(0, 10);
      }
      // Save to localStorage
      localStorage.setItem('vox_search_history', JSON.stringify(searchHistory.value));
    }

    if (searchType.value === 'ai_qa') {
      // AI Q&A mode - use /api/v1/search/query
      const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/search/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: searchQuery.value.trim(),
          language: searchLanguage.value,
          limit: searchLimit.value
        })
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.status}`);
      }

      const data = await response.json();
      searchResults.value = data;
      aiAnswer.value = data.answer || '';
      searchResultsList.value = data.sources || [];

    } else {
      // Knowledge Base mode - use /api/v1/knowledge/search
      const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/knowledge/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: searchQuery.value.trim(),
          limit: searchLimit.value
        })
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.status}`);
      }

      const data = await response.json();
      searchResults.value = data;
      searchResultsList.value = (data.items || []).map((item: any) => ({
        id: item.id,
        title: item.payload?.title || 'Untitled',
        summary: item.payload?.summary || item.payload?.content || '',
        content: item.payload?.content || '',
        score: item.score || 0
      }));
    }

    searchDuration.value = Date.now() - startTime;

  } catch (e: any) {
    console.error('Search failed:', e);
    alert((currentLanguage.value === 'zh' ? '搜索失败：' : 'Search failed: ') + (e.message || ''));
  } finally {
    isSearching.value = false;
  }
};

const clearSearchHistory = () => {
  if (confirm(currentLanguage.value === 'zh' ? '确定清空搜索历史？' : 'Clear search history?')) {
    searchHistory.value = [];
    localStorage.removeItem('vox_search_history');
  }
};

const viewSearchResult = (result: any) => {
  // Show result details in a modal or expand inline
  console.log('View result:', result);
  alert(currentLanguage.value === 'zh' 
    ? `标题: ${result.title}\n\n内容: ${result.summary || result.content}` 
    : `Title: ${result.title}\n\nContent: ${result.summary || result.content}`
  );
};

// Hot News Functions
const generateHotPost = async () => {
  if (!hotNewsTopic.value.trim()) return;
  
  hotNewsGenerating.value = true;
  hotNewsResult.value = null;
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/hot-news/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('vox_token')}`
      },
      body: JSON.stringify({
        topic: hotNewsTopic.value,
        style: hotNewsStyle.value,
        length: hotNewsLength.value,
        language: currentLanguage.value,
        generate_script: hotNewsGenerateScript.value
      })
    });
    
    if (!response.ok) {
      throw new Error('生成失败');
    }
    
    const data = await response.json();
    hotNewsResult.value = data;
    
  } catch (error) {
    console.error('[Hot News] Generate error:', error);
    alert(currentLanguage.value === 'en' ? 'Failed to generate post' : '生成推文失败');
  } finally {
    hotNewsGenerating.value = false;
  }
};

const fetchTrendingTopics = async () => {
  loadingTrending.value = true;
  
  try {
    // 添加时间戳防止缓存
    const timestamp = new Date().getTime();
    const response = await fetch(`${API_BASE_URL}/api/v1/hot-news/trending?limit=10&_t=${timestamp}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('vox_token')}`,
        'Cache-Control': 'no-cache',
        'Accept': 'application/json; charset=utf-8'
      }
    });
    
    if (!response.ok) {
      throw new Error('获取失败');
    }
    
    const data = await response.json();
    trendingTopics.value = data.topics || [];
    
    console.log('[Hot News] Loaded trending topics:', trendingTopics.value.length);
    
  } catch (error) {
    console.error('[Hot News] Fetch trending error:', error);
  } finally {
    loadingTrending.value = false;
  }
};

const fetchLatestNews = async () => {
  loadingNews.value = true;
  
  try {
    // 构建请求体，包含新闻源筛选
    const requestBody: any = {
      max_items: 30
    };
    
    // 如果选择了特定新闻源，添加筛选条件
    if (selectedNewsSources.value.length > 0 && selectedNewsSources.value.length < availableNewsSources.value.length) {
      requestBody.source_filter = selectedNewsSources.value;
    }
    
    const response = await fetch(`${API_BASE_URL}/api/v1/hot-news/fetch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('vox_token')}`,
        'Cache-Control': 'no-cache'
      },
      body: JSON.stringify(requestBody)
    });
    
    if (!response.ok) {
      throw new Error('获取失败');
    }
    
    const data = await response.json();
    latestNews.value = data.news_list || [];
    
    console.log('[Hot News] Loaded latest news:', latestNews.value.length, 'with filter:', selectedNewsSources.value.length > 0 ? selectedNewsSources.value : 'all');
    
  } catch (error) {
    console.error('[Hot News] Fetch news error:', error);
  } finally {
    loadingNews.value = false;
  }
};

// 获取可用的新闻源列表
const fetchNewsSources = async () => {
  loadingNewsSources.value = true;
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/hot-news/sources`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('vox_token')}`
      }
    });
    
    if (!response.ok) {
      throw new Error('获取新闻源失败');
    }
    
    const data = await response.json();
    availableNewsSources.value = data.sources || [];
    
    // 默认选择所有新闻源
    if (selectedNewsSources.value.length === 0) {
      selectedNewsSources.value = availableNewsSources.value.map((s: any) => s.name);
    }
    
    console.log('[Hot News] Loaded news sources:', availableNewsSources.value.length);
    
  } catch (error) {
    console.error('[Hot News] Fetch sources error:', error);
  } finally {
    loadingNewsSources.value = false;
  }
};

// 切换新闻源选择器显示
const toggleNewsSourceSelector = async () => {
  showNewsSourceSelector.value = !showNewsSourceSelector.value;
  
  // 如果打开选择器且还没有加载新闻源，则加载
  if (showNewsSourceSelector.value && availableNewsSources.value.length === 0) {
    await fetchNewsSources();
  }
};

// 全选/取消全选新闻源
const selectAllNewsSources = () => {
  if (selectedNewsSources.value.length === availableNewsSources.value.length) {
    selectedNewsSources.value = [];
  } else {
    selectedNewsSources.value = availableNewsSources.value.map((s: any) => s.name);
  }
};

// 应用新闻源筛选
const applyNewsSourceFilter = () => {
  showNewsSourceSelector.value = false;
  fetchLatestNews();
};

const viewNewsDetail = (news: any) => {
  selectedNewsDetail.value = { ...news, fullContent: null };
  showNewsDetail.value = true;
};

const closeNewsDetail = () => {
  showNewsDetail.value = false;
  selectedNewsDetail.value = null;
  loadingNewsContent.value = false;
};

// 获取新闻全文内容
const fetchNewsFullContent = async () => {
  if (!selectedNewsDetail.value) return;
  
  const url = selectedNewsDetail.value.link || selectedNewsDetail.value.url;
  if (!url) {
    alert(currentLanguage.value === 'zh' ? '没有可用的链接' : 'No link available');
    return;
  }
  
  loadingNewsContent.value = true;
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/hot-news/fetch-content`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('vox_token')}`
      },
      body: JSON.stringify({ url })
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch content');
    }
    
    const data = await response.json();
    
    if (data.content) {
      selectedNewsDetail.value = {
        ...selectedNewsDetail.value,
        fullContent: data.content,
        description: data.content  // 也更新 description 以便保存到知识库
      };
    } else {
      alert(currentLanguage.value === 'zh' ? '无法获取内容，请尝试访问原文链接' : 'Could not fetch content. Please try visiting the original link.');
    }
    
  } catch (error) {
    console.error('[News] Failed to fetch full content:', error);
    alert(currentLanguage.value === 'zh' ? '获取全文失败，请尝试访问原文链接' : 'Failed to fetch content. Please try visiting the original link.');
  } finally {
    loadingNewsContent.value = false;
  }
};

const viewTrendingDetail = (topic: any) => {
  // 在模态框中显示详情
  selectedNewsDetail.value = topic;
  showNewsDetail.value = true;
};

const generatePostFromTrending = (topic: any) => {
  // 使用标题和描述（全文）生成推文
  const fullContent = `${topic.title}\n\n${topic.description || ''}`;
  hotNewsTopic.value = fullContent.trim();
  generateHotPost();
};

const generatePostFromNews = (news: any) => {
  // 使用标题和描述（全文）生成推文
  const fullContent = `${news.title}\n\n${news.description || ''}`;
  hotNewsTopic.value = fullContent.trim();
  generateHotPost();
};

const generatePostFromDetail = () => {
  // 从详情模态框生成推文
  if (selectedNewsDetail.value) {
    const fullContent = `${selectedNewsDetail.value.title}\n\n${selectedNewsDetail.value.description || ''}`;
    hotNewsTopic.value = fullContent.trim();
    generateHotPost();
  }
};

const saveNewsDetailToKB = async () => {
  if (!selectedNewsDetail.value || savingNewsToKB.value) return;
  
  const detail = selectedNewsDetail.value;
  savingNewsToKB.value = true;
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/hot-news/save-to-kb`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('vox_token')}`
      },
      body: JSON.stringify({
        title: detail.title,
        content: detail.description || detail.title,
        url: detail.url || detail.link || '',
        source: detail.source || '热点新闻',
        published_date: detail.published_date || ''
      })
    });
    
    if (!response.ok) {
      throw new Error('保存失败');
    }
    
    const data = await response.json();
    alert(currentLanguage.value === 'en' ? 'Saved to knowledge base successfully!' : '已成功保存到知识库！');
    console.log('[News Detail] Saved to KB:', data);
    
  } catch (error) {
    console.error('[News Detail] Save to KB error:', error);
    alert(currentLanguage.value === 'en' ? 'Failed to save' : '保存失败');
  } finally {
    savingNewsToKB.value = false;
  }
};

const saveTrendingToKB = async (topic: any) => {
  if (savingNewsToKB.value) return;
  
  savingNewsToKB.value = true;
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/hot-news/save-to-kb`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('vox_token')}`
      },
      body: JSON.stringify({
        title: topic.title,
        content: topic.description || topic.title,
        url: topic.url || '',
        source: '热点新闻',
        published_date: topic.published_date || ''
      })
    });
    
    if (!response.ok) {
      throw new Error('保存失败');
    }
    
    const data = await response.json();
    alert(currentLanguage.value === 'en' ? 'Saved to knowledge base successfully!' : '已成功保存到知识库！');
    console.log('[Trending] Saved to KB:', data);
    
  } catch (error) {
    console.error('[Trending] Save to KB error:', error);
    alert(currentLanguage.value === 'en' ? 'Failed to save' : '保存失败');
  } finally {
    savingNewsToKB.value = false;
  }
};

const saveNewsToKB = async (news: any) => {
  if (savingNewsToKB.value) return;
  
  savingNewsToKB.value = true;
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/hot-news/save-to-kb`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('vox_token')}`
      },
      body: JSON.stringify({
        title: news.title,
        content: news.description || news.title,
        url: news.link || '',
        source: news.source || '最新新闻',
        published_date: news.published_date || ''
      })
    });
    
    if (!response.ok) {
      throw new Error('保存失败');
    }
    
    alert(currentLanguage.value === 'en' ? '✅ Saved to knowledge base!' : '✅ 已保存到知识库！');
    
  } catch (error) {
    console.error('[Hot News] Save to KB error:', error);
    alert(currentLanguage.value === 'en' ? '❌ Failed to save' : '❌ 保存失败');
  } finally {
    savingNewsToKB.value = false;
  }
};

// Email Marketing Functions
const fetchEmailSubscribers = async () => {
  emailLoading.value = true;
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/email/subscribers`);
    if (res.ok) emailSubscribers.value = await res.json();
  } catch (e) {
    console.error(e);
  } finally {
    emailLoading.value = false;
  }
};

const fetchEmailTemplates = async () => {
  try {
    console.log('📡 正在获取邮件模板...');
    const res = await fetch(`${API_BASE_URL}/api/v1/email/templates`);
    if (res.ok) {
      const templates = await res.json();
      emailTemplates.value = templates;
      console.log('✅ 成功加载', templates.length, '个模板');
      console.log('📋 模板列表:', templates.map((t: any) => ({
        id: t.id,
        name: t.name,
        contentLength: t.content?.length || 0
      })));
    } else {
      console.error('❌ 获取模板失败:', res.status, res.statusText);
    }
  } catch (e) {
    console.error('❌ 获取模板出错:', e);
  }
};

const fetchEmailConfig = async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/email/config`);
    if (res.ok) {
      const data = await res.json();
      Object.assign(emailConfigForm.value, data);
    }
  } catch (e) {
    console.error(e);
  }
};

const handleEmailFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (!target.files?.length) return;
  
  const formData = new FormData();
  formData.append('file', target.files[0]);
  
  emailLoading.value = true;
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/email/subscribers/upload`, {
      method: 'POST',
      body: formData
    });
    if (res.ok) {
      alert(currentLanguage.value === 'zh' ? '导入成功' : 'Import successful');
      fetchEmailSubscribers();
    } else {
      const err = await res.json();
      alert(`${currentLanguage.value === 'zh' ? '导入失败' : 'Import failed'}: ${err.detail}`);
    }
  } catch (e) {
    alert(currentLanguage.value === 'zh' ? '导入出错' : 'Import error');
  } finally {
    emailLoading.value = false;
    target.value = '';
  }
};

const deleteEmailSubscriber = async (id: number) => {
  if (!confirm(currentLanguage.value === 'zh' ? '确定删除该用户吗？' : 'Delete this subscriber?')) return;
  try {
    await fetch(`${API_BASE_URL}/api/v1/email/subscribers/${id}`, { method: 'DELETE' });
    fetchEmailSubscribers();
  } catch (e) {
    alert(currentLanguage.value === 'zh' ? '删除失败' : 'Delete failed');
  }
};

const openEmailTemplateModal = (tpl: any = null) => {
  console.log('🚀 打开模板编辑器...');
  console.log('📦 传入的模板数据:', tpl);
  
  editingEmailTemplate.value = tpl;
  emailTemplateViewMode.value = 'visual'; // 默认打开可视化模式
  
  if (tpl) {
    emailTemplateForm.value.name = tpl.name;
    emailTemplateForm.value.subject = tpl.subject;
    emailTemplateForm.value.content = tpl.content || '';
    
    console.log('✅ 模板已加载:', tpl.name);
    console.log('✅ 模板 ID:', tpl.id);
    console.log('✅ 主题:', tpl.subject);
    console.log('✅ 内容长度:', tpl.content?.length || 0, '字符');
    
    if (tpl.content && tpl.content.length > 0) {
      console.log('✅ 内容预览 (前 200 字符):', tpl.content.substring(0, 200) + '...');
      console.log('📝 emailTemplateForm.value.content 已设置:', emailTemplateForm.value.content.length, '字符');
    } else {
      console.warn('⚠️ 模板内容为空！');
    }
  } else {
    emailTemplateForm.value.name = '';
    emailTemplateForm.value.subject = '';
    emailTemplateForm.value.content = '';
    console.log('📝 创建新模板');
  }
  
  showEmailTemplateModal.value = true;
  console.log('✅ 模态框已打开');
  
  // 延迟初始化 Quill，确保 DOM 已渲染
  nextTick(() => {
    console.log('⏳ nextTick: DOM 应该已更新');
    setTimeout(() => {
      console.log('⏰ 延迟 100ms 后开始初始化 Quill...');
      initQuillEditor();
    }, 100);
  });
};

const initQuillEditor = () => {
  console.log('🔧 initQuillEditor 被调用');
  console.log('📝 当前 emailTemplateForm.value.content 长度:', emailTemplateForm.value.content?.length || 0);
  
  // Destroy existing editor if any
  if (quillEditor) {
    console.log('🗑️ 清理旧的 Quill 编辑器');
    try {
      // 移除事件监听器
      quillEditor.off('text-change');
      // 不要清空整个父节点，只重置编辑器本身
      quillEditor = null;
    } catch (e) {
      console.warn('⚠️ Error destroying previous Quill editor:', e);
      quillEditor = null;
    }
  }
  
  const editorElement = document.getElementById('quill-editor');
  if (!editorElement) {
    console.error('❌ Quill editor element (#quill-editor) not found!');
    console.log('🔍 当前 emailTemplateViewMode:', emailTemplateViewMode.value);
    console.log('🔍 检查是否在 DOM 中:', document.body.contains(document.getElementById('quill-editor')));
    
    // 如果找不到元素，等待一下再试
    setTimeout(() => {
      const retryElement = document.getElementById('quill-editor');
      if (retryElement) {
        console.log('✅ 重试后找到元素，继续初始化...');
        initQuillEditor();
      } else {
        console.error('❌ 重试后仍未找到元素');
      }
    }, 200);
    return;
  }
  
  // 检查元素是否可见
  const isVisible = editorElement.offsetParent !== null;
  console.log('✅ 找到编辑器元素:', editorElement);
  console.log('👁️ 元素是否可见:', isVisible);
  console.log('📏 元素尺寸:', editorElement.offsetWidth, 'x', editorElement.offsetHeight);
  
  if (!isVisible) {
    console.warn('⚠️ 元素不可见，等待 100ms 后重试...');
    setTimeout(() => initQuillEditor(), 100);
    return;
  }
  
  console.log('🔧 正在初始化 Quill 编辑器...');
  
  // Clear the element
  editorElement.innerHTML = '';
  
  // Import Quill dynamically
  import('quill').then((Quill) => {
    const QuillConstructor = Quill.default || Quill;
    console.log('📦 Quill 库已加载');
    
    quillEditor = new QuillConstructor('#quill-editor', {
      theme: 'snow',
      modules: {
        toolbar: [
          [{ 'header': [1, 2, 3, false] }],
          ['bold', 'italic', 'underline', 'strike'],
          [{ 'color': [] }, { 'background': [] }],
          [{ 'list': 'ordered'}, { 'list': 'bullet' }],
          [{ 'align': [] }],
          ['link', 'image'],
          ['clean']
        ],
        clipboard: {
          matchVisual: true // 保持粘贴内容的格式
        }
      },
      placeholder: currentLanguage.value === 'zh' ? '在此编辑邮件内容...' : 'Edit email content here...'
    });
    
    console.log('✅ Quill 编辑器实例创建成功');
    console.log('📋 Quill 编辑器对象:', quillEditor);
    
    // 强制更新 Quill 布局（解决从 preview 切换回来时的显示问题）
    try {
      if (typeof quillEditor.update === 'function') {
        quillEditor.update();
        console.log('🔄 已强制更新 Quill 布局');
      }
    } catch (e) {
      console.warn('⚠️ 更新布局失败:', e);
    }
    
    // Wait for Quill to be fully initialized before setting content
    setTimeout(() => {
      console.log('⏰ 准备加载内容到 Quill...');
      console.log('📝 emailTemplateForm.value.content:', emailTemplateForm.value.content ? `${emailTemplateForm.value.content.length} 字符` : '空');
      console.log('📋 quillEditor 对象:', quillEditor ? '存在' : '不存在');
      
      if (emailTemplateForm.value.content && quillEditor) {
        console.log('🚀 开始加载内容...');
        
        // 提取 body 内容（Quill 只接受 HTML 片段，不接受完整的 HTML 文档）
        let contentToLoad = emailTemplateForm.value.content;
        const bodyMatch = emailTemplateForm.value.content.match(/<body[^>]*>([\s\S]*)<\/body>/i);
        if (bodyMatch && bodyMatch[1]) {
          contentToLoad = bodyMatch[1];
          console.log('📄 提取了 <body> 标签内的内容');
          console.log('📝 提取后的内容长度:', contentToLoad.length);
        } else {
          console.log('ℹ️ 未找到 <body> 标签，使用原始内容');
        }
        
        try {
          // 暂时移除 text-change 监听器，避免在加载时被触发
          const loadingFlag = { isLoading: true };
          (quillEditor as any)._loadingFlag = loadingFlag;
          
          // 使用 pasteHTML 方法（最适合加载完整 HTML）
          quillEditor.clipboard.dangerouslyPasteHTML(contentToLoad);
          console.log('✅ 内容已加载到 Quill (使用 pasteHTML)');
          console.log('📝 原始内容长度:', emailTemplateForm.value.content.length);
          console.log('📋 Quill root 内容长度:', quillEditor.root.innerHTML.length);
          console.log('👁️ Quill 内容预览 (前 300 字符):', quillEditor.root.innerHTML.substring(0, 300) + '...');
          
          // 标记加载完成并强制刷新布局
          setTimeout(() => {
            loadingFlag.isLoading = false;
            console.log('✅ 内容加载完成，可以开始编辑');
            
            // 最后一次强制更新布局，确保内容正确显示
            try {
              if (quillEditor && typeof quillEditor.update === 'function') {
                quillEditor.update();
                console.log('🔄 内容加载后已刷新 Quill 布局');
              }
              // 滚动到顶部，确保用户看到内容
              if (quillEditor && quillEditor.root) {
                quillEditor.root.scrollTop = 0;
                console.log('📜 已滚动到编辑器顶部');
              }
            } catch (e) {
              console.warn('⚠️ 刷新布局时出错:', e);
            }
          }, 300);
        } catch (err) {
          console.error('❌ 加载内容失败:', err);
        }
      } else if (!emailTemplateForm.value.content) {
        console.log('ℹ️ 内容为空，这是一个新模板');
      } else if (!quillEditor) {
        console.error('❌ quillEditor 对象不存在！');
      }
    }, 200);
    
    // Listen for content changes (忽略初始加载期间的变化)
    quillEditor.on('text-change', () => {
      if (quillEditor && quillEditor.root) {
        // 检查是否正在加载
        const loadingFlag = (quillEditor as any)._loadingFlag;
        if (loadingFlag && loadingFlag.isLoading) {
          console.log('⏳ 正在加载内容，忽略此次变化');
          return;
        }
        
        // 获取 body 内容
        const bodyContent = quillEditor.root.innerHTML;
        
        // 如果原始内容有完整的 HTML 结构，保持它
        if (emailTemplateForm.value.content.includes('<html>')) {
          // 替换 body 内容，保持 head 不变
          emailTemplateForm.value.content = emailTemplateForm.value.content.replace(
            /<body[^>]*>[\s\S]*<\/body>/i,
            `<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f4f4;">\n${bodyContent}\n</body>`
          );
          console.log('📝 内容已更新（保持 HTML 结构），body 长度:', bodyContent.length);
        } else {
          // 如果是片段，直接保存
          emailTemplateForm.value.content = bodyContent;
          console.log('📝 内容已更新，长度:', bodyContent.length);
        }
      }
    });
  }).catch(err => {
    console.error('❌ Failed to load Quill editor:', err);
    alert(currentLanguage.value === 'zh' 
      ? '富文本编辑器加载失败，请刷新页面重试' 
      : 'Failed to load rich text editor, please refresh the page');
  });
};

const switchEmailTemplateViewMode = (mode: 'visual' | 'code' | 'preview') => {
  console.log(`🔄 切换到 ${mode} 模式，当前模式: ${emailTemplateViewMode.value}`);
  
  // Save content from current editor before switching
  if (emailTemplateViewMode.value === 'visual' && quillEditor) {
    try {
      // 获取 body 内容
      const bodyContent = quillEditor.root.innerHTML;
      
      // 如果原始内容有完整的 HTML 结构，保持它
      if (emailTemplateForm.value.content.includes('<html>')) {
        // 替换 body 内容，保持 head 不变
        emailTemplateForm.value.content = emailTemplateForm.value.content.replace(
          /<body[^>]*>[\s\S]*<\/body>/i,
          `<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f4f4;">\n${bodyContent}\n</body>`
        );
        console.log('💾 已保存 Visual 模式的内容（保持 HTML 结构）, body 长度:', bodyContent.length);
      } else {
        // 如果是片段，直接保存
        emailTemplateForm.value.content = bodyContent;
        console.log('💾 已保存 Visual 模式的内容，长度:', bodyContent.length);
      }
    } catch (e) {
      console.warn('⚠️ 保存 Visual 模式内容时出错:', e);
    }
  }
  
  // 切换模式前先保存当前状态
  const previousMode = emailTemplateViewMode.value;
  emailTemplateViewMode.value = mode;
  
  // Initialize Quill when switching to visual mode
  if (mode === 'visual') {
    console.log('🔧 准备初始化 Visual 模式...');
    console.log('📝 当前 emailTemplateForm.value.content 长度:', emailTemplateForm.value.content?.length || 0);
    console.log('📝 从哪个模式切换过来:', previousMode);
    
    // 如果从 preview 切换过来，需要更长的延迟确保 DOM 完全准备好
    const delay = previousMode === 'preview' ? 300 : 150;
    console.log(`⏱️ 将在 ${delay}ms 后初始化 Quill...`);
    
    nextTick(() => {
      setTimeout(() => {
        console.log('⏰ 开始初始化 Quill 编辑器...');
        initQuillEditor();
      }, delay);
    });
  }
  
  // Update preview iframe when switching to preview mode
  if (mode === 'preview') {
    nextTick(() => {
      setTimeout(() => {
        if (previewIframe.value && emailTemplateForm.value.content) {
          const iframe = previewIframe.value;
          // 如果 content 包含 <html>，直接使用；否则包装一下
          const previewContent = emailTemplateForm.value.content.includes('<html>') 
            ? emailTemplateForm.value.content 
            : `<html><head><meta charset="UTF-8"></head><body>${emailTemplateForm.value.content}</body></html>`;
          iframe.srcdoc = previewContent;
          console.log('✅ 预览内容已加载，长度:', emailTemplateForm.value.content.length, '字符');
        } else if (previewIframe.value) {
          const emptyContent = `
            <div style="text-align: center; padding: 60px 20px; color: #999; font-family: Arial, sans-serif;">
              <svg style="width: 64px; height: 64px; margin-bottom: 16px; opacity: 0.3;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p style="font-size: 16px; margin: 0;">${currentLanguage.value === 'zh' ? '暂无内容' : 'No content'}</p>
              <p style="font-size: 14px; margin: 8px 0 0 0; opacity: 0.7;">${currentLanguage.value === 'zh' ? '请在可视化或代码模式下编辑内容' : 'Please edit content in Visual or Code mode'}</p>
            </div>
          `;
          previewIframe.value.srcdoc = emptyContent;
          console.log('⚠️ 预览内容为空');
        } else {
          console.error('❌ 预览 iframe 未找到');
        }
      }, 100);
    });
  }
};

const closeEmailTemplateModal = () => {
  // Save content before closing if in visual mode
  if (emailTemplateViewMode.value === 'visual' && quillEditor) {
    try {
      emailTemplateForm.value.content = quillEditor.root.innerHTML;
      console.log('💾 关闭前已保存内容');
    } catch (e) {
      console.warn('⚠️ 关闭前保存内容时出错:', e);
    }
  }
  
  // Clean up Quill editor
  if (quillEditor) {
    try {
      quillEditor = null;
    } catch (e) {
      console.warn('⚠️ 清理编辑器时出错:', e);
    }
  }
  
  showEmailTemplateModal.value = false;
  emailTemplateViewMode.value = 'visual';
};

const saveEmailTemplate = async () => {
  // Save content from Quill editor if in visual mode
  if (emailTemplateViewMode.value === 'visual' && quillEditor) {
    emailTemplateForm.value.content = quillEditor.root.innerHTML;
  }
  
  const url = editingEmailTemplate.value 
    ? `${API_BASE_URL}/api/v1/email/templates/${editingEmailTemplate.value.id}`
    : `${API_BASE_URL}/api/v1/email/templates`;
  const method = editingEmailTemplate.value ? 'PUT' : 'POST';
  
  try {
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(emailTemplateForm.value)
    });
    if (res.ok) {
      closeEmailTemplateModal();
      fetchEmailTemplates();
    } else {
      alert(currentLanguage.value === 'zh' ? '保存失败' : 'Save failed');
    }
  } catch (e) {
    alert(currentLanguage.value === 'zh' ? '保存出错' : 'Save error');
  }
};

const deleteEmailTemplate = async (id: number) => {
  if (!confirm(currentLanguage.value === 'zh' ? '确定删除该模板吗？' : 'Delete this template?')) return;
  try {
    await fetch(`${API_BASE_URL}/api/v1/email/templates/${id}`, { method: 'DELETE' });
    fetchEmailTemplates();
  } catch (e) {
    alert(currentLanguage.value === 'zh' ? '删除失败' : 'Delete failed');
  }
};

const applySmtpPreset = (event: Event) => {
  const target = event.target as HTMLSelectElement;
  const preset = target.value;
  
  console.log('📧 应用 SMTP 预设:', preset);
  
  if (!preset) return;
  
  const smtpPresets: Record<string, any> = {
    gmail: {
      smtp_server: 'smtp.gmail.com',
      smtp_port: 587,
      use_tls: true,
      hint: currentLanguage.value === 'zh' 
        ? '提示：Gmail 需要使用应用专用密码，不能使用账户密码。请访问 Google 账户安全设置生成应用专用密码。' 
        : 'Note: Gmail requires an app-specific password. Visit Google Account Security settings to generate one.'
    },
    outlook: {
      smtp_server: 'smtp-mail.outlook.com',
      smtp_port: 587,
      use_tls: true,
      hint: currentLanguage.value === 'zh' 
        ? '提示：适用于 Outlook.com 和 Hotmail.com 邮箱。\n\n⚠️ Outlook 可能需要：\n• 启用"允许不够安全的应用"或使用应用密码\n• 检查账户设置中的 SMTP 权限\n• 测试邮件可能会进入垃圾邮件文件夹' 
        : 'Note: For Outlook.com and Hotmail.com email addresses.\n\n⚠️ Outlook may require:\n• Enable "Allow less secure apps" or use app password\n• Check SMTP permissions in account settings\n• Test email may go to spam folder'
    },
    office365: {
      smtp_server: 'smtp.office365.com',
      smtp_port: 587,
      use_tls: true,
      hint: currentLanguage.value === 'zh' 
        ? '提示：适用于 Office 365 企业邮箱。' 
        : 'Note: For Office 365 business email accounts.'
    },
    '163': {
      smtp_server: 'smtp.163.com',
      smtp_port: 465,
      use_tls: false,
      hint: currentLanguage.value === 'zh' 
        ? '提示：163 邮箱需要在邮箱设置中开启 SMTP 服务并使用授权码作为密码。' 
        : 'Note: Enable SMTP service in 163 mailbox settings and use authorization code as password.'
    },
    qq: {
      smtp_server: 'smtp.qq.com',
      smtp_port: 587,
      use_tls: true,
      hint: currentLanguage.value === 'zh' 
        ? '提示：QQ 邮箱需要在设置中开启 SMTP 服务并使用授权码作为密码。' 
        : 'Note: Enable SMTP service in QQ Mail settings and use authorization code as password.'
    },
    yahoo: {
      smtp_server: 'smtp.mail.yahoo.com',
      smtp_port: 587,
      use_tls: true,
      hint: currentLanguage.value === 'zh' 
        ? '提示：Yahoo 可能需要使用应用专用密码。' 
        : 'Note: Yahoo may require an app-specific password.'
    },
    icloud: {
      smtp_server: 'smtp.mail.me.com',
      smtp_port: 587,
      use_tls: true,
      hint: currentLanguage.value === 'zh' 
        ? '提示：iCloud 需要使用应用专用密码。请访问 appleid.apple.com 生成。' 
        : 'Note: iCloud requires an app-specific password. Generate one at appleid.apple.com.'
    }
  };
  
  const config = smtpPresets[preset];
  if (config) {
    emailConfigForm.value.smtp_server = config.smtp_server;
    emailConfigForm.value.smtp_port = config.smtp_port;
    emailConfigForm.value.use_tls = config.use_tls;
    
    // ⚠️ 自动同步：如果已填写用户名，发件人邮箱应该和用户名一致
    if (emailConfigForm.value.smtp_username) {
      emailConfigForm.value.sender_email = emailConfigForm.value.smtp_username;
      console.log('✅ 自动同步发件人邮箱为:', emailConfigForm.value.sender_email);
    }
    
    console.log('✅ 已应用预设配置:', config);
    
    // 显示提示信息
    if (config.hint) {
      alert(config.hint + 
        (currentLanguage.value === 'zh' 
          ? '\n\n⚠️ 重要提示：\n• 发件人邮箱必须和用户名（邮箱地址）一致！\n• 否则邮件会发送失败！'
          : '\n\n⚠️ Important:\n• Sender email MUST match username (email address)!\n• Otherwise emails will fail!'));
    }
    
    // 重置选择器
    target.value = '';
  }
};

const testSmtpConnection = async () => {
  console.log('🧪 测试 SMTP 连接...');
  
  // 验证必填字段
  if (!emailConfigForm.value.smtp_server || !emailConfigForm.value.smtp_username || 
      !emailConfigForm.value.smtp_password || !emailConfigForm.value.sender_email) {
    return {
      success: false,
      message: '请填写所有必填字段：服务器、用户名、密码、发件人邮箱',
      message_en: 'Please fill in all required fields: server, username, password, sender email'
    };
  }
  
  try {
    // 方案：先保存配置（临时），然后使用现有的发送测试邮件功能
    // 1. 保存配置
    const saveRes = await fetch(`${API_BASE_URL}/api/v1/email/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(emailConfigForm.value)
    });
    
    if (!saveRes.ok) {
      return {
        success: false,
        message: '保存配置失败',
        message_en: 'Failed to save configuration'
      };
    }
    
    // 2. 获取第一个模板（用于测试）
    const templatesRes = await fetch(`${API_BASE_URL}/api/v1/email/templates`);
    const templates = await templatesRes.json();
    
    if (templates.length === 0) {
      return {
        success: false,
        message: '没有可用的邮件模板，无法测试',
        message_en: 'No email templates available for testing'
      };
    }
    
    // 3. 发送测试邮件到发件人自己的邮箱
    const sendRes = await fetch(`${API_BASE_URL}/api/v1/email/send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        template_id: templates[0].id,
        type: 'test',
        test_email: emailConfigForm.value.sender_email
      })
    });
    
    const sendResult = await sendRes.json();
    console.log('🧪 发送结果:', sendResult);
    
    if (sendRes.ok && sendResult.success !== undefined) {
      if (sendResult.success > 0 || sendResult.total > 0) {
        return {
          success: true,
          message: `SMTP 连接测试成功！测试邮件已发送到 ${emailConfigForm.value.sender_email}`,
          message_en: `SMTP connection test successful! Test email sent to ${emailConfigForm.value.sender_email}`
        };
      }
    }
    
    // 如果响应格式不同，检查是否有错误
    if (sendResult.detail) {
      return {
        success: false,
        message: `测试失败：${sendResult.detail}`,
        message_en: `Test failed: ${sendResult.detail}`,
        error_detail: sendResult.detail
      };
    }
    
    // 默认成功（发送API没有返回错误）
    return {
      success: true,
      message: `测试邮件已发送到 ${emailConfigForm.value.sender_email}`,
      message_en: `Test email sent to ${emailConfigForm.value.sender_email}`
    };
    
  } catch (e) {
    console.error('❌ 测试连接出错:', e);
    return {
      success: false,
      message: currentLanguage.value === 'zh' ? `测试连接时发生错误：${e}` : `Error during connection test: ${e}`,
      message_en: `Error during connection test: ${e}`,
      error_detail: String(e)
    };
  }
};

const handleTestConnection = async () => {
  if (!emailConfigForm.value.smtp_server || !emailConfigForm.value.smtp_username || 
      !emailConfigForm.value.smtp_password || !emailConfigForm.value.sender_email) {
    alert(currentLanguage.value === 'zh' 
      ? '❌ 请填写所有必填字段：服务器、用户名、密码、发件人邮箱' 
      : '❌ Please fill in all required fields: server, username, password, sender email');
    return;
  }
  
  // ⚠️ 关键验证：发件人邮箱必须和用户名一致（特别是 Gmail 和 Outlook）
  if (emailConfigForm.value.sender_email !== emailConfigForm.value.smtp_username) {
    const fixMsg = currentLanguage.value === 'zh'
      ? `⚠️ 配置错误！\n\n发件人邮箱和用户名不一致：\n• 用户名: ${emailConfigForm.value.smtp_username}\n• 发件人: ${emailConfigForm.value.sender_email}\n\n大多数邮件服务器（Gmail、Outlook 等）要求发件人邮箱和登录用户名一致，否则邮件会发送失败！\n\n是否自动修正为：${emailConfigForm.value.smtp_username}？`
      : `⚠️ Configuration Error!\n\nSender email does not match username:\n• Username: ${emailConfigForm.value.smtp_username}\n• Sender: ${emailConfigForm.value.sender_email}\n\nMost email servers (Gmail, Outlook, etc.) require sender email to match username, or emails will fail!\n\nAuto-correct to: ${emailConfigForm.value.smtp_username}?`;
    
    if (confirm(fixMsg)) {
      emailConfigForm.value.sender_email = emailConfigForm.value.smtp_username;
      alert(currentLanguage.value === 'zh' 
        ? `✅ 已自动修正！\n\n发件人邮箱已更改为：${emailConfigForm.value.sender_email}\n\n请再次点击"测试连接"。` 
        : `✅ Auto-corrected!\n\nSender email changed to: ${emailConfigForm.value.sender_email}\n\nPlease click "Test Connection" again.`);
      return;
    } else {
      alert(currentLanguage.value === 'zh'
        ? '⚠️ 建议修正配置后再测试，否则很可能无法发送邮件！'
        : '⚠️ Please correct the configuration before testing, or emails may fail!');
      return;
    }
  }
  
  const confirmMsg = currentLanguage.value === 'zh'
    ? `🧪 测试 SMTP 连接\n\n将会：\n1. 保存您的配置\n2. 发送一封测试邮件到：${emailConfigForm.value.sender_email}\n3. 验证连接是否成功\n\n确定继续吗？`
    : `🧪 Test SMTP Connection\n\nWill:\n1. Save your configuration\n2. Send a test email to: ${emailConfigForm.value.sender_email}\n3. Verify the connection\n\nContinue?`;
  
  if (!confirm(confirmMsg)) {
    return;
  }
  
  emailSending.value = true;
  
  const result = await testSmtpConnection();
  
  emailSending.value = false;
  
  if (result.success) {
    alert(`✅ ${currentLanguage.value === 'zh' ? result.message : result.message_en}\n\n` +
          `${currentLanguage.value === 'zh' ? '📬 请检查邮箱（可能需要 1-2 分钟）：' : '📬 Please check your inbox (may take 1-2 minutes):'} ${emailConfigForm.value.sender_email}\n\n` +
          `${currentLanguage.value === 'zh' ? '⚠️ 如果没收到邮件：' : '⚠️ If you did not receive the email:'}\n` +
          `${currentLanguage.value === 'zh' ? '• 检查垃圾邮件/垃圾箱文件夹' : '• Check spam/junk folder'}\n` +
          `${currentLanguage.value === 'zh' ? '• 等待几分钟（某些服务器较慢）' : '• Wait a few minutes (some servers are slow)'}\n` +
          `${currentLanguage.value === 'zh' ? '• 检查发件人邮箱地址是否正确' : '• Verify sender email address is correct'}\n\n` +
          `${currentLanguage.value === 'zh' ? '🔧 Outlook 用户特别注意：' : '🔧 Outlook users note:'}\n` +
          `${currentLanguage.value === 'zh' ? '• 可能需要应用密码而不是账户密码' : '• May need app password instead of account password'}\n` +
          `${currentLanguage.value === 'zh' ? '• 访问：account.microsoft.com/security' : '• Visit: account.microsoft.com/security'}`);
  } else {
    const errorMsg = currentLanguage.value === 'zh' ? result.message : result.message_en;
    alert(`❌ ${errorMsg}\n\n${currentLanguage.value === 'zh' ? '请检查您的配置：' : 'Please check your configuration:'}\n` +
          `\n${currentLanguage.value === 'zh' ? '✓ 服务器地址和端口是否正确' : '✓ Server address and port are correct'}` +
          `\n${currentLanguage.value === 'zh' ? '✓ 用户名（完整邮箱地址）是否正确' : '✓ Username (full email address) is correct'}` +
          `\n${currentLanguage.value === 'zh' ? '✓ 密码或授权码是否正确' : '✓ Password or authorization code is correct'}` +
          `\n${currentLanguage.value === 'zh' ? '✓ TLS 设置是否正确' : '✓ TLS setting is correct'}` +
          `\n\n${currentLanguage.value === 'zh' ? '📧 Outlook 用户：' : '📧 Outlook users:'}` +
          `\n${currentLanguage.value === 'zh' ? '• 需要应用密码，不能用账户密码' : '• Need app password, not account password'}` +
          `\n${currentLanguage.value === 'zh' ? '• 生成地址：account.microsoft.com/security' : '• Generate at: account.microsoft.com/security'}` +
          (result.error_detail ? `\n\n${currentLanguage.value === 'zh' ? '详细错误：' : 'Details:'}\n${result.error_detail}` : ''));
  }
};

const saveEmailConfig = async () => {
  // 直接保存配置（测试功能已经通过发送测试邮件实现）
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/email/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(emailConfigForm.value)
    });
    if (res.ok) {
      alert(currentLanguage.value === 'zh' ? '配置保存成功' : 'Configuration saved');
    } else {
      alert(currentLanguage.value === 'zh' ? '保存失败' : 'Save failed');
    }
  } catch (e) {
    alert(currentLanguage.value === 'zh' ? '保存出错' : 'Save error');
  }
};

const sendEmail = async () => {
  if (!emailSendForm.value.template_id) return;
  
  emailSending.value = true;
  try {
    const payload: any = {
      template_id: emailSendForm.value.template_id
    };
    
    if (emailSendForm.value.type === 'test') {
      if (!emailSendForm.value.test_email) {
        alert(currentLanguage.value === 'zh' ? '请输入测试邮箱' : 'Please enter test email');
        emailSending.value = false;
        return;
      }
      payload.test_email = emailSendForm.value.test_email;
    }
    
    const res = await fetch(`${API_BASE_URL}/api/v1/email/send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    if (res.ok) {
      alert(emailSendForm.value.type === 'test' 
        ? (currentLanguage.value === 'zh' ? '测试邮件已发送' : 'Test email sent')
        : (currentLanguage.value === 'zh' ? '批量发送任务已提交后台' : 'Batch send task submitted'));
    } else {
      const err = await res.json();
      alert(`${currentLanguage.value === 'zh' ? '发送失败' : 'Send failed'}: ${err.detail}`);
    }
  } catch (e) {
    alert(currentLanguage.value === 'zh' ? '发送出错' : 'Send error');
  } finally {
    emailSending.value = false;
  }
};

onMounted(() => {
    // Fetch LLM config from backend
    fetchLLMConfig();
    
    // Fetch voices for TTS features (used in multiple tabs)
    fetchVoices();
    
    // Fetch academic history for the History section
    fetchAcademicHistory();
    
    // Load search history from localStorage
    const savedSearchHistory = localStorage.getItem('vox_search_history');
    if (savedSearchHistory) {
      try {
        searchHistory.value = JSON.parse(savedSearchHistory);
      } catch (e) {
        console.error('Failed to load search history:', e);
      }
    }
    
    // Initial fetch based on active tab    
    // Set User Info
    const storedName = localStorage.getItem('vox_display_name') || localStorage.getItem('vox_username');
    if (storedName) {
        userDisplayName.value = storedName;
        userInitials.value = storedName.charAt(0).toUpperCase();
    }
});
</script>

<style>
/* Quill Editor Styles */
@import 'quill/dist/quill.snow.css';
</style>

<style scoped>
/* Custom Scrollbar for Webkit */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Animations */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes scaleIn {
  from {
    transform: scale(0.9);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
.animate-spin {
  animation: spin 1s linear infinite;
}

/* Markdown Prose Styles */
.prose {
  max-width: none;
}

.prose :deep(h2) {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

.prose :deep(h3) {
  font-size: 1.125rem;
  font-weight: 600;
  color: #334155;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

.prose :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.875rem;
}

.prose :deep(th) {
  padding: 0.75rem 1rem;
  background-color: #f1f5f9;
  text-align: left;
  font-weight: 600;
  color: #334155;
  border: 1px solid #cbd5e1;
}

.prose :deep(td) {
  padding: 0.75rem 1rem;
  color: #475569;
  border: 1px solid #e2e8f0;
}

.prose :deep(tr:hover) {
  background-color: #f8fafc;
}

.prose :deep(code) {
  padding: 0.125rem 0.375rem;
  background-color: #eef2ff;
  color: #4f46e5;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-family: monospace;
}

.prose :deep(p) {
  margin-bottom: 0.75rem;
  line-height: 1.6;
  color: #334155;
}

.prose :deep(strong) {
  font-weight: 600;
  color: #1e293b;
}

/* Script Content Styles */
.script-content {
  font-size: 0.95rem;
  line-height: 1.8;
  color: #334155;
}

.script-content :deep(.script-heading-main) {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-top: 2rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 3px solid #4f46e5;
}

.script-content :deep(.script-heading-main:first-child) {
  margin-top: 0;
}

.script-content :deep(.script-heading-sub) {
  font-size: 1.15rem;
  font-weight: 600;
  color: #475569;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  padding-left: 0.75rem;
  border-left: 4px solid #818cf8;
}

.script-content :deep(.script-paragraph) {
  margin-bottom: 1rem;
  line-height: 1.9;
  text-align: justify;
}

.script-content :deep(.evidence-badge) {
  display: inline-block;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
  padding: 0.15rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  margin-left: 0.25rem;
  margin-right: 0.25rem;
  border: 1px solid #fbbf24;
}

.script-content :deep(.figure-badge) {
  display: inline-block;
  background: linear-gradient(135deg, #ddd6fe 0%, #c4b5fd 100%);
  color: #5b21b6;
  padding: 0.15rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  margin-left: 0.25rem;
  margin-right: 0.25rem;
  border: 1px solid #a78bfa;
}

/* Clickable evidence and asset badges */
.script-content :deep(.clickable-evidence),
.script-content :deep(.clickable-asset) {
  cursor: pointer;
  transition: all 0.2s ease;
}

.script-content :deep(.clickable-evidence:hover) {
  background: linear-gradient(135deg, #fde68a 0%, #fbbf24 100%);
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(251, 191, 36, 0.4);
}

.script-content :deep(.clickable-asset:hover) {
  background: linear-gradient(135deg, #c4b5fd 0%, #a78bfa 100%);
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(167, 139, 250, 0.4);
}

/* Asset reference style (D1-FIG-1, D2-TAB-1) */
.script-content :deep(.asset-ref) {
  display: inline-block;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #4338ca;
  padding: 0.1rem 0.4rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  font-family: monospace;
  border: 1px solid #818cf8;
}

.script-content :deep(.asset-ref:hover) {
  background: linear-gradient(135deg, #c7d2fe 0%, #a5b4fc 100%);
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(129, 140, 248, 0.4);
}

/* Model Select Dropdown - 确保下拉菜单完整显示 */
.model-select-wrapper {
  /* 确保下拉菜单不被父容器截断 */
  position: relative;
  z-index: 1000;
}

.model-select {
  /* 强制浏览器显示原生下拉菜单，最大高度设置为可滚动 */
  -webkit-appearance: menulist;
  -moz-appearance: menulist;
  appearance: menulist;
  max-height: 300px;
}

/* 在打开时增加 z-index，确保在所有元素之上 */
.model-select:focus {
  z-index: 9999;
  position: relative;
}

/* 优化选项样式 */
.model-select option {
  padding: 10px 12px;
  background: white;
  color: #334155;
  line-height: 1.5;
}

.model-select option:hover {
  background: #f1f5f9;
}

.model-select option:checked {
  background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%);
  color: #4f46e5;
  font-weight: 600;
}

.model-select option:disabled {
  color: #94a3b8;
  background: #f8fafc;
}

/* Figure/Image container styles for Final Version */
.script-content :deep(.figure-container) {
  margin: 24px 0;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  text-align: center;
}

.script-content :deep(.figure-image) {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin: 0 auto;
  display: block;
}

.script-content :deep(.figure-caption) {
  margin-top: 12px;
  font-size: 14px;
  color: #64748b;
  font-style: italic;
  text-align: center;
}
</style>
