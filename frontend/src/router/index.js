import { createRouter, createWebHistory } from 'vue-router'

// 路由组件懒加载
const Home = () => import('../views/Home.vue')
const PostList = () => import('../views/blog/PostList.vue')
const PostDetail = () => import('../views/blog/PostDetail.vue')
const CreatePost = () => import('../views/blog/CreatePost.vue')
const ThoughtList = () => import('../views/thoughts/ThoughtList.vue')
const MoodIndex = () => import('../views/mood/MoodIndex.vue')
const MoodCalendar = () => import('../views/mood/MoodCalendar.vue')
const MoodHistory = () => import('../views/mood/MoodHistory.vue')
const Login = () => import('../views/auth/Login.vue')
const Register = () => import('../views/auth/Register.vue')
const Profile = () => import('../views/auth/Profile.vue')
const NotFound = () => import('../views/NotFound.vue')

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: '首页' }
  },
  {
    path: '/blog',
    name: 'PostList',
    component: PostList,
    meta: { title: '博客' }
  },
  {
    path: '/blog/:id',
    name: 'PostDetail',
    component: PostDetail,
    meta: { title: '文章详情' }
  },
  {
    path: '/blog/create',
    name: 'CreatePost',
    component: CreatePost,
    meta: { title: '写文章', requiresAuth: true }
  },
  {
    path: '/blog/:id/edit',
    name: 'EditPost',
    component: CreatePost,
    meta: { title: '编辑文章', requiresAuth: true }
  },
  {
    path: '/thoughts',
    name: 'ThoughtList',
    component: ThoughtList,
    meta: { title: '想法记录' }
  },
  {
    path: '/mood',
    name: 'MoodIndex',
    component: MoodIndex,
    meta: { title: '心情记录' }
  },
  {
    path: '/mood/calendar',
    name: 'MoodCalendar',
    component: MoodCalendar,
    meta: { title: '心情日历' }
  },
  {
    path: '/mood/history',
    name: 'MoodHistory',
    component: MoodHistory,
    meta: { title: '心情历史' }
  },
  {
    path: '/mood/date/:date',
    name: 'MoodDetail',
    component: MoodHistory,
    meta: { title: '心情详情' }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { title: '注册' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { title: '个人资料', requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { title: '页面未找到' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - Sad Blog` : 'Sad Blog'

  // 检查认证状态
  const { useAuthStore } = await import('../stores/auth')
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router