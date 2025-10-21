import { request } from './index'

export const userApi = {
  // 获取当前用户信息
  getCurrentUser: () => {
    return request.get('/api/user/me')
  },

  // 更新用户资料
  updateProfile: (profileData) => {
    return request.put('/api/user/profile', profileData)
  },

  // 更新用户名
  updateUsername: (username) => {
    return request.put('/api/user/username', { username })
  },

  // 更新邮箱
  updateEmail: (email) => {
    return request.put('/api/user/email', { email })
  },

  // 更改密码
  changePassword: (passwordData) => {
    return request.put('/api/user/password', passwordData)
  },

  // 上传头像
  uploadAvatar: (formData) => {
    return request.post('/api/user/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取用户统计信息
  getUserStats: (userId) => {
    return request.get(`/api/user/${userId}/stats`)
  },

  // 获取用户活动记录
  getUserActivities: (userId, page = 1, limit = 20) => {
    return request.get(`/api/user/${userId}/activities?page=${page}&limit=${limit}`)
  },

  // 获取用户的文章
  getUserPosts: (userId, page = 1, limit = 10) => {
    return request.get(`/api/user/${userId}/posts?page=${page}&limit=${limit}`)
  },

  // 获取用户的想法
  getUserThoughts: (userId, page = 1, limit = 10) => {
    return request.get(`/api/user/${userId}/thoughts?page=${page}&limit=${limit}`)
  },

  // 获取用户的心情记录
  getUserMoods: (userId, page = 1, limit = 10) => {
    return request.get(`/api/user/${userId}/moods?page=${page}&limit=${limit}`)
  },

  // 删除账户
  deleteAccount: (password) => {
    return request.delete('/api/user/account', { data: { password } })
  },

  // 导出用户数据
  exportUserData: () => {
    return request.get('/api/user/export', { responseType: 'blob' })
  },

  // 设置隐私偏好
  updatePrivacySettings: (settings) => {
    return request.put('/api/user/privacy', settings)
  },

  // 获取隐私设置
  getPrivacySettings: () => {
    return request.get('/api/user/privacy')
  },

  // 验证邮箱
  verifyEmail: (token) => {
    return request.post('/api/user/verify-email', { token })
  },

  // 重新发送验证邮件
  resendVerificationEmail: () => {
    return request.post('/api/user/resend-verification')
  },

  // 获取用户关注列表
  getFollowing: (userId, page = 1, limit = 20) => {
    return request.get(`/api/user/${userId}/following?page=${page}&limit=${limit}`)
  },

  // 获取用户粉丝列表
  getFollowers: (userId, page = 1, limit = 20) => {
    return request.get(`/api/user/${userId}/followers?page=${page}&limit=${limit}`)
  },

  // 关注用户
  followUser: (userId) => {
    return request.post(`/api/user/${userId}/follow`)
  },

  // 取消关注
  unfollowUser: (userId) => {
    return request.delete(`/api/user/${userId}/follow`)
  },

  // 检查是否关注了某用户
  checkFollowing: (userId) => {
    return request.get(`/api/user/${userId}/follow-status`)
  }
}