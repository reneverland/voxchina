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
          href="#"
          @click.prevent="goBack"
          class="flex items-center px-4 py-3 rounded-xl transition-all duration-200 group text-slate-500 hover:bg-slate-50 hover:text-slate-700 hover:shadow-sm"
        >
          <svg class="w-5 h-5 transition-transform duration-300 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          <span class="ml-3 font-medium hidden lg:block">Back to Main</span>
        </a>
      </nav>

      <!-- User Profile -->
      <div class="p-4 border-t border-slate-50">
        <div 
          class="flex items-center justify-center lg:justify-start px-2 py-2 rounded-xl hover:bg-slate-50 cursor-pointer transition-colors"
          @click="handleLogout"
          title="Log Out"
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
          <h1 class="text-2xl font-light text-slate-800 tracking-tight">Academic Extract</h1>
          <p class="text-xs text-slate-400 mt-1">AI Workbench / Academic Extract · Model: {{ llmModel || 'Loading...' }}</p>
        </div>
      </header>

      <!-- Content Area -->
      <div class="flex-1 overflow-y-auto p-8">
        <div class="max-w-6xl mx-auto w-full">
          
          <!-- Dynamic Content -->
          <div class="bg-white rounded-2xl shadow-xl shadow-slate-200/40 border border-slate-100 min-h-[600px] p-8 transition-all duration-300">
            
            <!-- Academic Extract Content -->
            <div class="h-full flex flex-col">
              <div class="mb-8 border-b border-slate-50 pb-6 flex justify-between items-end">
                <div>
                  <h2 class="text-xl font-medium text-slate-700 mb-2">Academic Article Extraction</h2>
                  <p class="text-slate-500 font-light">
                    Upload academic papers (DOCX/PDF) to generate zero-hallucination, evidence-traceable bilingual summaries and structured fact tables.
                  </p>
                </div>
              </div>

              <!-- Main Layout -->
              <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
                <!-- Left: Upload Section -->
                <div class="lg:col-span-1 space-y-6">
                  <div class="bg-slate-50/50 rounded-xl border border-slate-100 p-6">
                    <h3 class="text-md font-semibold text-slate-800 mb-4 flex items-center">
                      <div class="p-1.5 bg-indigo-100 text-indigo-600 rounded-lg mr-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      Upload Academic Article
                    </h3>

                    
                    <div class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-slate-600 mb-1.5">Select File</label>
                        <div class="relative group">
                          <input 
                            type="file" 
                            id="academic-file-upload"
                            ref="fileInput"
                            @change="handleFileSelect"
                            accept=".docx,.doc,.pdf"
                            class="hidden"
                          />
                          <label 
                            for="academic-file-upload"
                            @dragover.prevent="isDragging = true"
                            @dragleave.prevent="isDragging = false"
                            @drop.prevent="handleFileDrop"
                            :class="[
                              'flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer transition-all',
                              isDragging ? 'border-indigo-500 bg-indigo-50' : 'border-slate-300 bg-white hover:bg-slate-50 hover:border-indigo-400'
                            ]"
                          >
                            <div v-if="!selectedFile" class="flex flex-col items-center justify-center pt-5 pb-6">
                              <svg class="w-8 h-8 text-slate-300 mb-2 group-hover:text-indigo-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                              </svg>
                              <p class="text-xs text-slate-500">Click to upload academic paper</p>
                              <p class="text-[10px] text-slate-400 mt-1">DOCX, DOC, PDF (Recommended < 10MB)</p>
                            </div>
                            <div v-else class="flex flex-col items-center justify-center pt-5 pb-6 px-4 text-center">
                              <div class="w-8 h-8 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-2">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                                </svg>
                              </div>
                              <p class="text-sm text-slate-700 font-medium truncate w-full max-w-[180px]">{{ selectedFile.name }}</p>
                              <p class="text-xs text-green-600 mt-1">Ready to Extract</p>
                            </div>
                          </label>
                        </div>
                      </div>

                      <button 
                        type="button"
                        @click="startExtraction"
                        :disabled="!selectedFile || isExtracting"
                        class="w-full py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-medium shadow-lg shadow-indigo-200 hover:bg-indigo-700 hover:shadow-indigo-300 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center"
                      >
                        <svg v-if="isExtracting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        {{ isExtracting ? 'Extracting...' : 'Start Extraction' }}
                      </button>
                      
                      <p v-if="errorMessage" class="text-xs text-red-500 text-center">{{ errorMessage }}</p>
                    </div>
                  </div>

                  <!-- Progress Display -->
                  <div v-if="isExtracting" class="bg-slate-50/50 rounded-xl border border-slate-100 p-6">
                    <h3 class="text-md font-semibold text-slate-800 mb-4">Extraction Progress</h3>
                    <div class="space-y-2.5">
                      <div 
                        v-for="(stage, index) in progressStages" 
                        :key="index"
                        class="flex items-center"
                      >
                        <div :class="[
                          'w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold mr-2.5 transition-all',
                          currentProgress >= stage.progress ? 'bg-indigo-600 text-white' : 'bg-slate-200 text-slate-400'
                        ]">
                          <svg v-if="currentProgress >= stage.progress" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                          </svg>
                          <span v-else class="text-[10px]">{{ index + 1 }}</span>
                        </div>
                        <div class="flex-1">
                          <p :class="[
                            'text-xs transition-all',
                            currentProgress >= stage.progress ? 'text-slate-800 font-medium' : 'text-slate-400'
                          ]">
                            {{ stage.name }}
                          </p>
                        </div>
                      </div>
                    </div>
                    <div class="mt-3 w-full bg-slate-200 rounded-full h-1.5">
                      <div 
                        class="bg-indigo-600 h-1.5 rounded-full transition-all duration-500"
                        :style="{ width: `${currentProgress}%` }"
                      ></div>
                    </div>
                    <p class="text-xs text-center text-slate-600 mt-2">{{ currentProgress }}%</p>
                  </div>
                </div>

                <!-- Right: Result Display Area -->
                <div class="lg:col-span-2">
                  <h3 class="text-md font-semibold text-slate-800 mb-4 flex items-center justify-between">
                    <span class="flex items-center">
                      <div class="p-1.5 bg-purple-100 text-purple-600 rounded-lg mr-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      Extraction Results
                    </span>
                  </h3>

                  <div v-if="extractResult" class="bg-white border border-slate-100 rounded-xl overflow-hidden">
                    <div class="p-6">
                      <div class="flex items-center justify-between mb-6">
                        <div class="flex items-center">
                          <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-green-50 to-emerald-50 flex items-center justify-center text-green-600 mr-3 border border-green-100/50">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          </div>
                          <div>
                            <h4 class="font-semibold text-slate-800 text-sm">Extraction Completed</h4>
                            <p class="text-[10px] text-slate-400">View Results</p>
                          </div>
                        </div>
                        <div class="flex space-x-2">
                          <button 
                            @click="copyToClipboard"
                            class="px-3 py-1.5 bg-slate-50 hover:bg-slate-100 text-slate-600 text-xs font-medium rounded-lg border border-slate-200 transition-colors"
                          >
                            Copy
                          </button>
                          <button 
                            @click="downloadResult"
                            class="px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-600 text-xs font-medium rounded-lg border border-indigo-200 transition-colors"
                          >
                            Download
                          </button>
                        </div>
                      </div>

                      <!-- Tab Switcher -->
                      <div class="flex space-x-1 mb-4 bg-slate-50 p-1 rounded-lg">
                        <button 
                          @click="activeTab = 'summary'"
                          :class="[
                            'flex-1 px-4 py-2 text-sm font-medium rounded-md transition-all',
                            activeTab === 'summary' 
                              ? 'bg-white text-indigo-600 shadow-sm' 
                              : 'text-slate-500 hover:text-slate-700'
                          ]"
                        >
                          Summary View
                        </button>
                        <button 
                          @click="activeTab = 'facttable'"
                          :class="[
                            'flex-1 px-4 py-2 text-sm font-medium rounded-md transition-all',
                            activeTab === 'facttable' 
                              ? 'bg-white text-indigo-600 shadow-sm' 
                              : 'text-slate-500 hover:text-slate-700'
                          ]"
                        >
                          Fact Table View
                        </button>
                      </div>

                      <!-- Summary View -->
                      <div v-if="activeTab === 'summary'" class="space-y-4">
                        <!-- Chinese Summary -->
                        <div class="border border-slate-100 rounded-lg overflow-hidden">
                          <div class="bg-slate-50 px-4 py-2 border-b border-slate-100">
                            <h4 class="text-sm font-semibold text-slate-700">Chinese Summary</h4>
                          </div>
                          <div class="p-4 bg-white">
                            <p class="text-slate-700 leading-relaxed text-sm">{{ extractResult.summary_zh }}</p>
                          </div>
                        </div>

                        <!-- English Summary -->
                        <div class="border border-slate-100 rounded-lg overflow-hidden">
                          <div class="bg-slate-50 px-4 py-2 border-b border-slate-100">
                            <h4 class="text-sm font-semibold text-slate-700">English Summary</h4>
                          </div>
                          <div class="p-4 bg-white">
                            <p class="text-slate-700 leading-relaxed text-sm">{{ extractResult.summary_en }}</p>
                          </div>
                        </div>
                      </div>

                      <!-- Fact Table View -->
                      <div v-if="activeTab === 'facttable'" class="space-y-6">
                        <!-- Basic Info -->
                        <div>
                          <h3 class="text-md font-semibold text-slate-800 mb-3">Basic Information</h3>
                          <div class="space-y-3">
                            <!-- Authors -->
                            <div v-if="extractResult.fact_table.basic_info.authors">
                              <p class="text-xs text-slate-500 mb-1">Authors & Affiliation</p>
                              <div class="space-y-1">
                                <div 
                                  v-for="(author, idx) in extractResult.fact_table.basic_info.authors" 
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
                            <div v-if="extractResult.fact_table.basic_info.research_question">
                              <p class="text-xs text-slate-500 mb-1">Research Question</p>
                              <p class="text-sm text-slate-700">
                                {{ extractResult.fact_table.basic_info.research_question.question }}
                                <span v-if="extractResult.fact_table.basic_info.research_question.evidence" class="text-xs text-indigo-600 ml-2">
                                  [{{ extractResult.fact_table.basic_info.research_question.evidence }}]
                                </span>
                              </p>
                            </div>

                            <!-- Research Object -->
                            <div v-if="extractResult.fact_table.basic_info.research_object">
                              <p class="text-xs text-slate-500 mb-1">Research Object / Scope</p>
                              <p class="text-sm text-slate-700">
                                {{ extractResult.fact_table.basic_info.research_object.description }}
                                <span v-if="extractResult.fact_table.basic_info.research_object.evidence" class="text-xs text-indigo-600 ml-2">
                                  [{{ extractResult.fact_table.basic_info.research_object.evidence }}]
                                </span>
                              </p>
                            </div>

                            <!-- Data Sample -->
                            <div v-if="extractResult.fact_table.basic_info.data_sample">
                              <p class="text-xs text-slate-500 mb-1">Data & Sample</p>
                              <div class="text-sm text-slate-700 space-y-1">
                                <p v-if="extractResult.fact_table.basic_info.data_sample.source">
                                  <span class="font-medium">Source:</span> {{ extractResult.fact_table.basic_info.data_sample.source }}
                                </p>
                                <p v-if="extractResult.fact_table.basic_info.data_sample.sample_size">
                                  <span class="font-medium">Sample Size:</span> {{ extractResult.fact_table.basic_info.data_sample.sample_size }}
                                </p>
                                <p v-if="extractResult.fact_table.basic_info.data_sample.time_span">
                                  <span class="font-medium">Time Span:</span> {{ extractResult.fact_table.basic_info.data_sample.time_span }}
                                </p>
                                <p v-if="extractResult.fact_table.basic_info.data_sample.region">
                                  <span class="font-medium">Region:</span> {{ extractResult.fact_table.basic_info.data_sample.region }}
                                </p>
                                <span v-if="extractResult.fact_table.basic_info.data_sample.evidence" class="text-xs text-indigo-600">
                                  [{{ extractResult.fact_table.basic_info.data_sample.evidence }}]
                                </span>
                              </div>
                            </div>

                            <!-- Method -->
                            <div v-if="extractResult.fact_table.basic_info.method">
                              <p class="text-xs text-slate-500 mb-1">Research Method</p>
                              <p class="text-sm text-slate-700">
                                {{ extractResult.fact_table.basic_info.method.description }}
                                <span v-if="extractResult.fact_table.basic_info.method.evidence" class="text-xs text-indigo-600 ml-2">
                                  [{{ extractResult.fact_table.basic_info.method.evidence }}]
                                </span>
                              </p>
                            </div>
                          </div>
                        </div>

                        <!-- Key Findings -->
                        <div v-if="extractResult.fact_table.key_findings?.length > 0">
                          <h3 class="text-md font-semibold text-slate-800 mb-3">Key Findings</h3>
                          <div class="space-y-3">
                            <div 
                              v-for="(finding, idx) in extractResult.fact_table.key_findings" 
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
                        <div v-if="extractResult.fact_table.mechanisms?.length > 0">
                          <h3 class="text-md font-semibold text-slate-800 mb-3">Mechanisms</h3>
                          <div class="space-y-3">
                            <div 
                              v-for="(mechanism, idx) in extractResult.fact_table.mechanisms" 
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
                        <div v-if="extractResult.fact_table.policy_implications?.length > 0">
                          <h3 class="text-md font-semibold text-slate-800 mb-3">Policy Implications</h3>
                          <div class="space-y-3">
                            <div 
                              v-for="(policy, idx) in extractResult.fact_table.policy_implications" 
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
                          口播播放 (Oral Broadcast)
                        </h4>
                        
                        <div class="bg-slate-50 rounded-xl p-4 border border-slate-100">
                          <div v-if="availableVoices.length === 0" class="text-center py-4">
                            <p class="text-sm text-slate-500">正在加载声音库...</p>
                          </div>
                          <div v-else class="flex flex-col md:flex-row gap-4 items-end">
                            <div class="flex-1 w-full">
                              <label class="block text-xs font-medium text-slate-500 mb-1">选择内容 (Content)</label>
                              <select v-model="selectedSummaryLang" class="w-full text-sm rounded-lg border-slate-200 focus:border-indigo-500 focus:ring-indigo-500">
                                <option value="zh">中文摘要 (Chinese Summary)</option>
                                <option value="en">英文摘要 (English Summary)</option>
                              </select>
                            </div>
                            
                            <div class="flex-1 w-full">
                              <label class="block text-xs font-medium text-slate-500 mb-1">选择声音 (Voice)</label>
                              <select v-model="selectedVoiceId" class="w-full text-sm rounded-lg border-slate-200 focus:border-indigo-500 focus:ring-indigo-500">
                                <option v-for="voice in availableVoices" :key="voice.id" :value="voice.id">
                                  {{ voice.name }}
                                </option>
                              </select>
                            </div>
                            
                            <button 
                              @click="generateAudio"
                              :disabled="isGeneratingAudio || !selectedVoiceId"
                              class="w-full md:w-auto px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center whitespace-nowrap"
                            >
                              <svg v-if="isGeneratingAudio" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                              <span v-else class="flex items-center">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                生成并播放
                              </span>
                            </button>
                          </div>
                          
                          <!-- Player Section -->
                          <div v-if="audioUrl" class="mt-4 pt-4 border-t border-slate-200">
                            <div class="flex items-center gap-4">
                              <audio controls :src="audioUrl" class="flex-1 h-10 w-full" ref="audioPlayer" autoplay></audio>
                              <a 
                                :href="audioUrl" 
                                download="summary_broadcast.wav"
                                class="flex-shrink-0 p-2 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                                title="下载音频 (Download Audio)"
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

                  <!-- Empty State with History -->
                  <div v-else>
                    <div class="text-center py-12 bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
                      <div class="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-3">
                        <svg class="w-6 h-6 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <p class="text-slate-500 font-medium">No Results Yet</p>
                      <p class="text-xs text-slate-400 mt-1">Upload an academic article and click "Start Extraction"</p>
                    </div>
                    
                    <!-- History List -->
                    <div v-if="extractHistory.length > 0" class="mt-6">
                      <h4 class="text-sm font-semibold text-slate-700 mb-3 flex items-center">
                        <svg class="w-4 h-4 mr-2 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        提取历史 (Recent Extracts)
                      </h4>
                      <div class="space-y-2">
                        <div 
                          v-for="item in extractHistory" 
                          :key="item.id"
                          class="flex items-center justify-between p-3 bg-white border border-slate-200 rounded-lg hover:border-indigo-300 hover:shadow-sm transition-all cursor-pointer group"
                          @click="loadHistoryItem(item)"
                        >
                          <div class="flex-1 min-w-0">
                            <p class="text-sm font-medium text-slate-700 truncate group-hover:text-indigo-600">
                              {{ item.filename }}
                            </p>
                            <p class="text-xs text-slate-400 mt-0.5">
                              {{ new Date(item.timestamp).toLocaleString('zh-CN') }}
                            </p>
                          </div>
                          <div class="flex items-center gap-2 ml-3">
                            <button 
                              @click.stop="loadHistoryItem(item)"
                              class="p-1.5 text-indigo-600 hover:bg-indigo-50 rounded-md transition-colors"
                              title="查看"
                            >
                              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                              </svg>
                            </button>
                            <button 
                              @click.stop="deleteHistoryItem(item.id)"
                              class="p-1.5 text-red-400 hover:bg-red-50 rounded-md transition-colors"
                              title="删除"
                            >
                              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
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
        </div>
      </div>
    </main>
    
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
            <h3 class="text-lg font-semibold text-slate-800 mb-1">保存到知识库？</h3>
            <p class="text-sm text-slate-500">将此提取结果保存到知识库，以便后续查询和使用。</p>
          </div>
        </div>
        
        <div class="flex gap-3 mt-6">
          <button 
            @click="skipKBSave"
            class="flex-1 px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-sm font-medium transition-colors"
          >
            暂不保存
          </button>
          <button 
            @click="saveToKnowledgeBase"
            class="flex-1 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center justify-center"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// ==================== State Management ====================
const selectedFile = ref<File | null>(null)
const isDragging = ref(false)
const isExtracting = ref(false)
const currentProgress = ref(0)
const errorMessage = ref('')
const extractResult = ref<any>(null)
const activeTab = ref('summary')
const llmModel = ref('')

// TTS State
const availableVoices = ref<any[]>([])
const selectedVoiceId = ref('')
const selectedSummaryLang = ref('zh')
const audioUrl = ref('')
const isGeneratingAudio = ref(false)
const audioPlayer = ref<HTMLAudioElement | null>(null)

// History State
const extractHistory = ref<any[]>([])
const showSaveToKBDialog = ref(false)
const pendingKBSave = ref<any>(null)

const fileInput = ref<HTMLInputElement | null>(null)

// User Info
const userDisplayName = computed(() => localStorage.getItem('vox_display_name') || 'User')
const userInitials = computed(() => {
  const name = userDisplayName.value
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

const progressStages = ref([
  { name: "Document Acquisition & Preprocessing", progress: 10 },
  { name: "Structural Parsing & Noise Filtering", progress: 20 },
  { name: "Intelligent Chunking & Coverage Assurance", progress: 30 },
  { name: "CBIT-LLM Semantic Analysis", progress: 45 },
  { name: "Deep Understanding & Fact Extraction", progress: 60 },
  { name: "Evidence Consistency Verification", progress: 75 },
  { name: "Hallucination Filtering & Credibility Assessment", progress: 85 },
  { name: "Summary Generation & Style Alignment", progress: 95 },
  { name: "Preparing Final Results", progress: 100 }
])

// ==================== API Configuration ====================
const API_BASE_URL = (() => {
  const hostname = window.location.hostname;
  if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === 'llmhi.com') {
    return ''; // Use Vite proxy
  }
  return 'http://113.106.62.42:8300';
})();

const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('vox_token');
  const headers = new Headers(options.headers);
  
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  
  return fetch(url, {
    ...options,
    headers
  });
}

// ==================== Navigation ====================
const goBack = () => {
  router.push('/mainpage')
}

const handleLogout = () => {
  localStorage.removeItem('vox_token');
  localStorage.removeItem('vox_role');
  localStorage.removeItem('vox_username');
  localStorage.removeItem('vox_display_name');
  router.push('/login');
}

// ==================== File Handling ====================
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]
    errorMessage.value = ''
  }
}

const handleFileDrop = (event: DragEvent) => {
  isDragging.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    selectedFile.value = event.dataTransfer.files[0]
    errorMessage.value = ''
  }
}

const clearFile = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// ==================== Extraction Process ====================
const startExtraction = async () => {
  if (!selectedFile.value) {
    errorMessage.value = 'Please select a file first'
    return
  }

  isExtracting.value = true
  errorMessage.value = ''
  extractResult.value = null
  currentProgress.value = 0

  // Simulate progress updates
  const progressInterval = setInterval(() => {
    if (currentProgress.value < 95) {
      currentProgress.value += 5
    }
  }, 1000)

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/academic-extract/extract`, {
      method: 'POST',
      body: formData
    })

    clearInterval(progressInterval)

    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error')
      throw new Error(`Extraction failed: ${response.status} - ${errorText}`)
    }

    const result = await response.json()
    console.log('[Academic Extract] Success:', result)

    currentProgress.value = 100
    extractResult.value = result
    
    // Save to history
    saveToHistory(result, selectedFile.value?.name || 'unknown')

    // Delay to let user see 100%
    setTimeout(() => {
      isExtracting.value = false
      // Ask user if they want to save to KB
      pendingKBSave.value = result
      showSaveToKBDialog.value = true
    }, 500)

  } catch (error: any) {
    clearInterval(progressInterval)
    console.error('[Academic Extract] Error:', error)
    errorMessage.value = error.message || 'Extraction failed, please try again'
    isExtracting.value = false
    currentProgress.value = 0
  }
}

// ==================== Result Operations ====================
const copyToClipboard = () => {
  if (!extractResult.value) return

  const text = `【Chinese Summary】\n${extractResult.value.summary_zh}\n\n【English Summary】\n${extractResult.value.summary_en}`
  
  navigator.clipboard.writeText(text).then(() => {
    alert('Copied to clipboard')
  }).catch(err => {
    console.error('Copy failed:', err)
  })
}

const downloadResult = () => {
  if (!extractResult.value) return

  let content = `Academic Extract Results\n`
  content += `=`.repeat(50) + '\n\n'
  content += `【Chinese Summary】\n${extractResult.value.summary_zh}\n\n`
  content += `【English Summary】\n${extractResult.value.summary_en}\n\n`
  content += `=`.repeat(50) + '\n\n'
  content += `【Structured Fact Table】\n`
  content += JSON.stringify(extractResult.value.fact_table, null, 2)

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `academic_extract_${Date.now()}.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// ==================== History Management ====================
const loadHistory = () => {
  try {
    const historyData = localStorage.getItem('academic_extract_history')
    if (historyData) {
      extractHistory.value = JSON.parse(historyData)
    }
  } catch (e) {
    console.error('Failed to load history:', e)
    extractHistory.value = []
  }
}

const saveToHistory = (result: any, filename: string) => {
  const historyItem = {
    id: Date.now().toString(),
    filename: filename,
    timestamp: new Date().toISOString(),
    result: result
  }
  
  extractHistory.value.unshift(historyItem)
  
  // Keep only last 10 items
  if (extractHistory.value.length > 10) {
    extractHistory.value = extractHistory.value.slice(0, 10)
  }
  
  localStorage.setItem('academic_extract_history', JSON.stringify(extractHistory.value))
}

const loadHistoryItem = (item: any) => {
  extractResult.value = item.result
  activeTab.value = 'summary'
  audioUrl.value = ''
}

const deleteHistoryItem = (itemId: string) => {
  extractHistory.value = extractHistory.value.filter(item => item.id !== itemId)
  localStorage.setItem('academic_extract_history', JSON.stringify(extractHistory.value))
}

// ==================== TTS Operations ====================
const fetchVoices = async () => {
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/voices/`)
    if (response.ok) {
      const voices = await response.json()
      availableVoices.value = voices
      if (voices.length > 0) {
        selectedVoiceId.value = voices[0].id
      }
    }
  } catch (e) {
    console.error('Failed to fetch voices:', e)
  }
}

const generateAudio = async () => {
  if (!extractResult.value || !selectedVoiceId.value) return
  
  const text = selectedSummaryLang.value === 'zh' 
    ? extractResult.value.summary_zh 
    : extractResult.value.summary_en
    
  if (!text) {
    alert('No summary text available')
    return
  }
  
  isGeneratingAudio.value = true
  audioUrl.value = ''
  
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/voices/preview`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        voice_id: selectedVoiceId.value,
        text: text,
        language: selectedSummaryLang.value
      })
    })
    
    if (!response.ok) throw new Error('Generation failed')
    
    const data = await response.json()
    // Ensure URL is correct relative to API base if needed
    // The backend returns e.g. /static/audio/...
    // If API_BASE_URL is set, we might need to prepend it if not proxying
    if (API_BASE_URL && !data.audio_url.startsWith('http')) {
        audioUrl.value = `${API_BASE_URL}${data.audio_url}`
    } else {
        audioUrl.value = data.audio_url
    }
    
  } catch (e) {
    console.error('TTS Generation failed:', e)
    alert('Failed to generate audio. Please try again.')
  } finally {
    isGeneratingAudio.value = false
  }
}

// ==================== Knowledge Base Save ====================
const saveToKnowledgeBase = async () => {
  if (!pendingKBSave.value) return
  
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/academic-extract/save-to-kb`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        summary_zh: pendingKBSave.value.summary_zh,
        summary_en: pendingKBSave.value.summary_en,
        fact_table: pendingKBSave.value.fact_table
      })
    })
    
    if (response.ok) {
      alert('✅ 成功保存到知识库！')
    } else {
      throw new Error('保存失败')
    }
  } catch (e) {
    console.error('Failed to save to KB:', e)
    alert('❌ 保存到知识库失败，请稍后重试')
  } finally {
    showSaveToKBDialog.value = false
    pendingKBSave.value = null
  }
}

const skipKBSave = () => {
  showSaveToKBDialog.value = false
  pendingKBSave.value = null
}

// ==================== Lifecycle ====================
onMounted(async () => {
  // Check login status
  const token = localStorage.getItem('vox_token');
  if (!token) {
    router.push('/login');
    return;
  }
  
  loadHistory()
  fetchVoices()

  // Get current LLM configuration
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/api/v1/academic-extract/health`)
    if (response.ok) {
      const data = await response.json()
      llmModel.value = 'CBIT CBIT-Elite 4.2'
    } else {
      llmModel.value = 'CBIT CBIT-Elite 4.2'
    }
  } catch (error) {
    console.error('Failed to fetch LLM config:', error)
    llmModel.value = 'CBIT CBIT-Elite 4.2'
  }
})
</script>

<style scoped>
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
</style>
