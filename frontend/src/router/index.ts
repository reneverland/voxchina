import { createRouter, createWebHistory } from 'vue-router'
import LegacyApp from '../views/LegacyApp.vue'
import MainPage from '../views/MainPage.vue'
import LoginPage from '../views/LoginPage.vue'
import AcademicExtractPage from '../views/AcademicExtractPage.vue'

const routes = [
  {
    path: '/',
    name: 'Root',
    redirect: (to) => {
      return localStorage.getItem('vox_token') ? '/mainpage' : '/login'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/legacy',
    name: 'LegacyApp',
    component: LegacyApp
  },
  {
    path: '/mainpage',
    name: 'MainPage',
    component: MainPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/academic-extract',
    name: 'AcademicExtract',
    component: AcademicExtractPage,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('vox_token');
  if (to.meta.requiresAuth && !token) {
    next('/login');
  } else {
    next();
  }
});

export default router
