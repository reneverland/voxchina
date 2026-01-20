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
                          @click="copyAcademicResult"
                          class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-600 text-xs font-medium rounded-lg transition-colors"
                        >
                          {{ t('copyAll') }}
                        </button>
                        <button 
                          @click="downloadAcademicResult"
                          class="px-3 py-1.5 bg-indigo-100 hover:bg-indigo-200 text-indigo-600 text-xs font-medium rounded-lg transition-colors"
                        >
                          {{ t('download') }}
                        </button>
                      </div>
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
                      <div class="border border-slate-100 rounded-lg overflow-hidden">
                        <div class="bg-slate-50 px-4 py-2 border-b border-slate-100">
                          <h4 class="text-sm font-semibold text-slate-700">{{ t('chineseSummary') }}</h4>
                        </div>
                        <div class="p-4 bg-white">
                          <p class="text-slate-700 leading-relaxed text-sm">{{ academicResult.summary_zh }}</p>
                        </div>
                      </div>

                      <div class="border border-slate-100 rounded-lg overflow-hidden">
                        <div class="bg-slate-50 px-4 py-2 border-b border-slate-100">
                          <h4 class="text-sm font-semibold text-slate-700">{{ t('englishSummary') }}</h4>
                        </div>
                        <div class="p-4 bg-white">
                          <p class="text-slate-700 leading-relaxed text-sm">{{ academicResult.summary_en }}</p>
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
                  class="group bg-white border border-slate-100 rounded-xl p-5 hover:border-indigo-200 hover:shadow-md transition-all relative flex flex-col h-[280px]"
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
                  
                  <div class="flex-1 overflow-hidden relative mb-3">
                    <p class="text-xs text-slate-500 leading-relaxed line-clamp-6">
                      {{ doc.payload.summary_zh || doc.payload.content || 'No summary available.' }}
                    </p>
                    <div class="absolute bottom-0 left-0 w-full h-8 bg-gradient-to-t from-white to-transparent"></div>
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

            <!-- Integrated Voiceover Content -->
            <div v-else-if="activeTab === 'integrated'" class="h-full flex flex-col">
              <div class="mb-8 border-b border-slate-50 pb-6 flex justify-between items-end">
                <div>
                  <h2 class="text-xl font-medium text-slate-700 mb-2">{{ t('integratedVoiceover') }}</h2>
                  <p class="text-slate-500 font-light">
                    {{ t('integratedVoiceoverDesc') }}
                  </p>
                </div>
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
                    <div class="grid grid-cols-2 gap-4">
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
                            <!-- Image Preview (if available) -->
                            <div v-if="asset.image_url && asset.asset_type === 'FIG'" class="mb-3">
                              <img 
                                :src="getImageUrl(asset.image_url)" 
                                :alt="asset.caption_or_title || 'Image'" 
                                class="w-full h-auto rounded-lg border border-slate-200 object-contain max-h-48"
                                @error="handleImageError"
                                loading="lazy"
                              />
                            </div>
                            <div v-else-if="asset.asset_type === 'FIG'" class="mb-3 bg-slate-100 rounded-lg p-8 text-center">
                              <svg xmlns="http://www.w3.org/2000/svg" class="w-16 h-16 mx-auto text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                              </svg>
                              <p class="text-xs text-slate-400 mt-2">{{ currentLanguage === 'zh' ? '图片未能提取' : 'Image not extracted' }}</p>
                            </div>
                            
                            <!-- Caption/Title -->
                            <div>
                              <div class="text-xs font-medium text-slate-500 uppercase mb-1">{{ t('caption') }}</div>
                              <p class="text-sm text-slate-700 font-medium">{{ asset.caption_or_title || t('noCaption') }}</p>
                            </div>
                            
                            <!-- Key Numbers -->
                            <div v-if="asset.key_numbers && asset.key_numbers.length > 0">
                              <div class="text-xs font-medium text-slate-500 uppercase mb-2">{{ t('keyNumbers') }}</div>
                              <div class="flex flex-wrap gap-2">
                                <span
                                  v-for="(num, idx) in asset.key_numbers"
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
                                <span
                                  v-for="assetId in section.related_assets"
                                  :key="assetId"
                                  class="inline-flex items-center px-2 py-1 bg-purple-50 text-purple-700 rounded text-xs font-medium"
                                >
                                  📊 {{ assetId }}
                                </span>
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
                        <div class="script-content" v-html="formatScriptText(integratedResult.script_review)"></div>
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
                          <button
                            @click="copyIntegratedContent(integratedResult.script_final)"
                            class="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors font-medium shadow-sm"
                          >
                            📋 {{ t('copy') }}
                          </button>
                        </div>
                      </div>
                      <div class="bg-white rounded-lg border border-slate-200 p-8 shadow-sm">
                        <div class="script-content" v-html="formatScriptText(integratedResult.script_final)"></div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Error Message -->
                <div v-if="integratedError" class="bg-red-50 border border-red-200 rounded-xl p-6">
                  <div class="flex items-start space-x-3">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-red-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div>
                      <h3 class="text-lg font-semibold text-red-800 mb-2">{{ t('generationFailed') }}</h3>
                      <p class="text-sm text-red-700">{{ integratedError }}</p>
                    </div>
                  </div>
                </div>

                <!-- Back Button -->
                <div class="flex justify-center">
                  <button
                    @click="resetIntegratedForm"
                    class="px-6 py-2.5 bg-white border border-slate-200 text-slate-600 font-medium rounded-lg hover:border-slate-300 transition-all text-sm"
                  >
                    {{ t('back') }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Default Placeholder for other tabs -->
            <div v-else class="h-full flex flex-col">
              <div class="mb-8 border-b border-slate-50 pb-6">
                <h2 class="text-xl font-medium text-slate-700 mb-2">Workspace</h2>
                <p class="text-slate-500 font-light">
                  Use the tools on the sidebar to start generating content. This is your high-fidelity canvas.
                </p>
              </div>

              <!-- Empty State / Dashboard -->
              <div class="flex-1 flex flex-col items-center justify-center text-center p-12 border-2 border-dashed border-slate-100 rounded-xl bg-slate-50/50">
                <div class="w-16 h-16 bg-white rounded-full shadow-md flex items-center justify-center mb-6">
                   <component :is="activeItem?.icon" class="w-8 h-8 text-slate-300" />
                </div>
                <h3 class="text-lg font-medium text-slate-600 mb-2">Ready to create?</h3>
                <p class="text-slate-400 max-w-md mb-8">
                  Select a tool from the sidebar to begin academic extraction, voice synthesis, search, or trend analysis.
                </p>
                <button class="px-6 py-2.5 bg-white border border-slate-200 text-slate-600 font-medium rounded-lg shadow-sm hover:border-slate-300 hover:shadow transition-all">
                  Load Recent Project
                </button>
              </div>
            </div>

          </div>

        </div>
      </div>
    </main>
    
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
    
    <!-- LLM Settings Modal -->
    <div 
      v-if="llmSettingsOpen" 
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="llmSettingsOpen = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden">
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
        
        <div class="p-6 space-y-6">
          <!-- Provider Display -->
          <div>
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

          <!-- Model Selection - Only for superadmin -->
          <div v-if="userRole === 'superadmin'">
            <label class="block text-sm font-semibold text-slate-700 mb-2">
              选择模型
            </label>
            <div class="relative">
              <select 
                v-model="selectedModel"
                @focus="fetchAvailableModels"
                class="w-full px-4 py-2.5 pr-10 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 text-sm appearance-none cursor-pointer transition-all"
                :disabled="llmConfigLoading"
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
            </p>
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
            :disabled="llmConfigLoading || !selectedModel"
            class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors text-sm font-medium shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ llmConfigLoading ? '保存中...' : '保存配置' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Save to Knowledge Base Dialog -->
    <div v-if="showSaveToKBDialog" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm" style="animation: fadeIn 0.2s ease-out;">
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 p-6" style="animation: scaleIn 0.3s ease-out;">
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
        
        <div class="flex gap-3 mt-6">
          <button 
            @click="skipKBSave"
            :disabled="isSavingToKB"
            class="flex-1 px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ t('skipSave') }}
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
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
  FileVideo
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
const academicHistory = ref<any[]>([]);
const academicHistorySearch = ref('');
const academicHistoryPage = ref(1);
const academicHistoryPageSize = ref(10);
const academicHistoryTotal = ref(0);

// TTS State for Academic Extract
const selectedVoiceId = ref('');
const selectedSummaryLang = ref('zh');
const audioUrl = ref('');
const isGeneratingAudio = ref(false);

// Knowledge Base Save State
const showSaveToKBDialog = ref(false);
const pendingKBSave = ref<any>(null);
const isSavingToKB = ref(false);

// Integrated Voiceover State
const integratedForm = ref({
  topic_hint: '',
  speaker_affiliation: '',
  speaker_name: '',
  include_vox_intro: true,
  style_preference: '',
  language: 'zh'
});
const integratedFiles = ref<File[]>([]);
const isDraggingIntegrated = ref(false);
const integratedSubmitting = ref(false);
const integratedTaskId = ref<string | null>(null);
const integratedStatus = ref<any>(null);
const integratedResult = ref<any>(null);
const integratedError = ref('');
const integratedResultTab = ref('style');
let integratedPollingInterval: number | null = null;

// Document Detail State
const documentDetailOpen = ref(false);
const selectedDocument = ref<any>(null);

// LLM Settings State
const llmSettingsOpen = ref(false);
const llmConfig = ref({
  provider: 'openai',
  model: 'gpt-4o',
  display_name: 'CBIT CBIT-Elite 4.2',
  api_key_set: false
});
const availableModels = ref<Array<{id: string, name: string, provider: string}>>([]);
const selectedModel = ref('');
const llmConfigLoading = ref(false);
const llmConfigError = ref('');

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
    
    // Common
    settings: 'LLM Settings',
    export: 'Export',
    logOut: 'Log Out',
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
    generating: 'Generating voiceover script...',
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
    untitled: 'Untitled Section'
  },
  zh: {
    // Navigation
    academicExtract: 'Academic Extract',
    knowledgeDatabase: '知识库',
    voiceLibrary: '声音库',
    aiSearch: 'AI 搜索',
    hotTopics: '热点话题',
    integratedVoiceover: '整合口播',
    
    // Common
    settings: 'LLM 设置',
    export: '导出',
    logOut: '退出登录',
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
    generating: '正在生成口播稿...',
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
    untitled: '无标题章节'
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
  if (!imageUrl) return '';
  // If URL already starts with http, return as is
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl;
  }
  // If API_BASE_URL is empty (using proxy), return relative URL
  if (!API_BASE_URL) {
    return imageUrl;
  }
  // Otherwise, prepend API_BASE_URL
  return `${API_BASE_URL}${imageUrl}`;
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
  
  // Convert evidence markers like 【证据：...】 to styled badges
  formatted = formatted.replace(/【证据：([^】]+)】/g, '<span class="evidence-badge">📚 证据: $1</span>');
  
  // Convert figure markers like 【图表：...】 to styled badges
  formatted = formatted.replace(/【图表：([^】]+)】/g, '<span class="figure-badge">📊 图表: $1</span>');
  
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
  { id: 'search', name: t('aiSearch'), icon: Search },
  { id: 'trending', name: t('hotTopics'), icon: Flame },
]);

const activeItem = computed(() => navItems.value.find(i => i.id === activeTab.value));

const setActiveTab = (id: string) => {
  activeTab.value = id;
  if (id === 'voices') {
    fetchVoices();
  } else if (id === 'knowledge') {
    fetchKnowledgeDocs();
  } else if (id === 'academic') {
    fetchAcademicHistory();
  } else if (id === 'integrated') {
    // Reset integrated voiceover state
    resetIntegratedForm();
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
    language: currentLanguage.value
  };
  integratedFiles.value = [];
  integratedTaskId.value = null;
  integratedStatus.value = null;
  integratedResult.value = null;
  integratedError.value = '';
  stopIntegratedPolling();
};

const handleIntegratedFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files) {
    integratedFiles.value = Array.from(target.files);
  }
};

const handleIntegratedFileDrop = (event: DragEvent) => {
  isDraggingIntegrated.value = false;
  if (event.dataTransfer?.files) {
    integratedFiles.value = Array.from(event.dataTransfer.files);
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
    await navigator.clipboard.writeText(text);
    alert(t('copied'));
  } catch (error) {
    alert(t('copyFailed'));
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
        language: currentLocale.value
      })
    });
    
    if (!response.ok) throw new Error("Preview failed");
    
    const data = await response.json();
    previewAudioUrl.value = { ...previewAudioUrl.value, [id]: `${API_BASE_URL}${data.audio_url}` };
    
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

const copyAcademicResult = async () => {
  if (!academicResult.value) return;
  const text = `【Chinese Summary】\n${academicResult.value.summary_zh}\n\n【English Summary】\n${academicResult.value.summary_en}`;
  try {
    await navigator.clipboard.writeText(text);
    alert('✅ Copied to clipboard');
  } catch (e) {
    console.error('Failed to copy:', e);
    alert('❌ Copy failed');
  }
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
    ? '音频生成需要约60-90秒，请耐心等待。确定继续吗？' 
    : 'Audio generation takes about 60-90 seconds. Please wait patiently. Continue?')) {
    return;
  }
  
  isGeneratingAudio.value = true;
  audioUrl.value = '';
  
  try {
    // Increase timeout for TTS generation (2 minutes)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000);
    
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

// Knowledge Base Save Functions
const saveToKnowledgeBase = async () => {
  if (!pendingKBSave.value) return;
  
  isSavingToKB.value = true;
  
  try {
    console.log('[KB Save] Saving to knowledge base...', {
      summary_zh_length: pendingKBSave.value.summary_zh?.length,
      summary_en_length: pendingKBSave.value.summary_en?.length,
      has_fact_table: !!pendingKBSave.value.fact_table
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
        fact_table: pendingKBSave.value.fact_table || {}
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
        if (data.items) {
          knowledgeDocs.value = data.items;
          knowledgeTotal.value = data.total || data.items.length;
        } else {
          knowledgeDocs.value = data;
          knowledgeTotal.value = data.length;
        }
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
        if (data.items) {
          knowledgeDocs.value = data.items;
          knowledgeTotal.value = data.total || data.items.length;
        } else {
          knowledgeDocs.value = data;
          knowledgeTotal.value = data.length;
        }
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

onMounted(() => {
    // Fetch LLM config from backend
    fetchLLMConfig();
    
    // Fetch voices for TTS features (used in multiple tabs)
    fetchVoices();
    
    // Fetch academic history for the History section
    fetchAcademicHistory();
    
    // Initial fetch based on active tab    
    // Set User Info
    const storedName = localStorage.getItem('vox_display_name') || localStorage.getItem('vox_username');
    if (storedName) {
        userDisplayName.value = storedName;
        userInitials.value = storedName.charAt(0).toUpperCase();
    }
});
</script>

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
</style>
