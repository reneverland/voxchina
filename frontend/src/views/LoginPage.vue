<template>
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden bg-slate-50 font-sans">
    <!-- Background Elements -->
    <div class="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
      <div class="absolute -top-[10%] -right-[5%] w-[50%] h-[50%] bg-blue-50/50 rounded-full blur-3xl opacity-60"></div>
      <div class="absolute top-[20%] left-[10%] w-[40%] h-[40%] bg-purple-50/30 rounded-full blur-3xl opacity-60"></div>
    </div>

    <!-- Login Card -->
    <div class="relative w-full max-w-md p-8 bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-white/50 animate-in fade-in zoom-in duration-500">
      <div class="text-center mb-10">
        <div class="w-20 h-20 mx-auto mb-6 flex items-center justify-center bg-white rounded-2xl shadow-sm border border-slate-100">
          <img src="/voxchinalogo2.jpg" alt="VoxChina Logo" class="w-16 h-16 object-cover rounded-xl" />
        </div>
        <h2 class="text-2xl font-bold text-slate-800 mb-2">Welcome Back</h2>
        <p class="text-slate-500 text-sm">Sign in to access your AI Workbench</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="space-y-6">
        <div class="group">
          <label class="block text-sm font-medium text-slate-700 mb-1.5">Username</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <User class="h-5 w-5 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
            </div>
            <input 
              v-model="username" 
              type="text" 
              class="w-full bg-slate-50 border border-slate-200 rounded-xl py-3 pl-10 pr-4 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
              placeholder="Enter your username"
              required
            />
          </div>
        </div>
        
        <div class="group">
          <label class="block text-sm font-medium text-slate-700 mb-1.5">Password</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Lock class="h-5 w-5 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
            </div>
            <input 
              v-model="password" 
              type="password" 
              class="w-full bg-slate-50 border border-slate-200 rounded-xl py-3 pl-10 pr-4 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
              placeholder="Enter your password"
              required
            />
          </div>
        </div>
        
        <div v-if="error" class="p-3 rounded-lg bg-red-50 border border-red-100 text-red-600 text-sm text-center font-medium animate-pulse">
          {{ error }}
        </div>
        
        <button 
          type="submit" 
          :disabled="loading" 
          class="w-full py-3.5 bg-slate-900 text-white rounded-xl font-semibold text-sm hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-900 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-slate-200 flex items-center justify-center"
        >
          <Loader2 v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4" />
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>
      
      <div class="mt-8 text-center">
        <p class="text-xs text-slate-400">
          Powered by VoxChina AI & CBIT
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { User, Lock, Loader2 } from 'lucide-vue-next';

const router = useRouter();
const username = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');

// 根据访问域名动态选择API地址（支持前后端分离部署）
const API_BASE_URL = (() => {
  const hostname = window.location.hostname;
  // 如果是通过 llmhi.com 或 localhost 访问（前后端同服务器），使用内部代理
  if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === 'llmhi.com') {
    return ''; // 使用Vite proxy，避免NAT问题
  }
  // 如果是从其他域名访问（前端部署在其他服务器），使用外部IP
  return 'http://113.106.62.42:8300';
})();

onMounted(() => {
  if (localStorage.getItem('vox_token')) {
    router.push('/mainpage');
  }
});

const handleLogin = async () => {
  if (!username.value || !password.value) return;
  
  loading.value = true;
  error.value = '';
  
  try {
    const formData = new FormData();
    formData.append('username', username.value);
    formData.append('password', password.value);
    
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error("Invalid credentials");
    }
    
    const data = await response.json();
    
    // Save auth data
    localStorage.setItem('vox_token', data.access_token);
    localStorage.setItem('vox_role', data.role || 'user');
    localStorage.setItem('vox_username', data.username || username.value);
    localStorage.setItem('vox_display_name', data.display_name || username.value);
    
    // Redirect to main page
    router.push('/mainpage');
    
  } catch (e: any) {
    console.error(e);
    error.value = "Incorrect username or password. Please try again.";
  } finally {
    loading.value = false;
  }
};
</script>
