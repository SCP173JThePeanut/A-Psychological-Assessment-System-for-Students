import { createRouter, createWebHistory } from 'vue-router'

// 导入页面组件
import Splash from '@/views/Splash.vue'
import RelaxGuide from '@/views/RelaxGuide.vue'  // 新增
import Test from '@/views/Test.vue'
import Report from '@/views/Report.vue'

const routes = [
  {
    path: '/',
    redirect: '/splash'
  },
  {
    path: '/splash',
    name: 'Splash',
    component: Splash
  },
  {
    path: '/relax-guide',  // 新增路由
    name: 'RelaxGuide',
    component: RelaxGuide
  },
  {
    path: '/test',
    name: 'Test',
    component: Test
  },
  {
    path: '/report/:id?',
    name: 'Report',
    component: Report,
    props: true
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/splash'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router