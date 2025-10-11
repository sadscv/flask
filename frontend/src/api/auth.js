import { request } from './index'

export const authApi = {
  // 登录
  login: (credentials) => {
    return request.post('/auth/login', credentials)
  },

  // 注册
  register: (userData) => {
    return request.post('/auth/register', userData)
  },

  // 登出
  logout: () => {
    return request.post('/auth/logout')
  },

  // 获取当前用户信息
  getCurrentUser: () => {
    return request.get('/auth/me')
  },

  // 更新用户资料
  updateProfile: (userData) => {
    return request.put('/auth/profile', userData)
  },

  // 修改密码
  changePassword: (passwordData) => {
    return request.post('/auth/change-password', passwordData)
  },

  // 忘记密码
  forgotPassword: (email) => {
    return request.post('/auth/forgot-password', { email })
  },

  // 重置密码
  resetPassword: (token, passwordData) => {
    return request.post(`/auth/reset-password/${token}`, passwordData)
  },

  // 验证邮箱
  verifyEmail: (token) => {
    return request.get(`/auth/verify-email/${token}`)
  },

  // 重新发送验证邮件
  resendVerification: () => {
    return request.post('/auth/resend-verification')
  },

  // 刷新token
  refreshToken: () => {
    return request.post('/auth/refresh-token')
  },

  // 检查用户名是否可用
  checkUsername: (username) => {
    return request.get(`/auth/check-username/${username}`)
  },

  // 检查邮箱是否可用
  checkEmail: (email) => {
    return request.get(`/auth/check-email/${email}`)
  }
}