import { request } from './index'

export const thoughtsApi = {
  // 获取想法列表
  getThoughts: (page = 1, perPage = 20, filters = {}) => {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString(),
      ...filters
    })
    return request.get(`/api/v1.0/thoughts?${params}`)
  },

  // 获取最近想法
  getRecentThoughts: (limit = 5) => {
    return request.get(`/api/v1.0/thoughts?limit=${limit}`)
  },

  // 获取单条想法
  getThought: (id) => {
    return request.get(`/api/v1.0/thoughts/${id}`)
  },

  // 创建想法
  createThought: (thoughtData) => {
    return request.post('/api/v1.0/thoughts', thoughtData)
  },

  // 更新想法
  updateThought: (id, thoughtData) => {
    return request.put(`/api/v1.0/thoughts/${id}`, thoughtData)
  },

  // 删除想法
  deleteThought: (id) => {
    return request.delete(`/api/v1.0/thoughts/${id}`)
  },

  // 搜索想法
  searchThoughts: (query, page = 1, filters = {}) => {
    const params = new URLSearchParams({
      q: query,
      page: page.toString(),
      ...filters
    })
    return request.get(`/api/v1.0/thoughts/search?${params}`)
  },

  // 根据标签获取想法
  getThoughtsByTag: (tag, page = 1) => {
    return request.get(`/api/v1.0/thoughts/tag/${encodeURIComponent(tag)}?page=${page}`)
  },

  // 获取用户想法
  getUserThoughts: (username, page = 1) => {
    return request.get(`/api/v1.0/thoughts/user/${username}?page=${page}`)
  },

  // 获取想法类型列表
  getThoughtTypes: () => {
    return request.get('/api/v1.0/thoughts/types')
  },

  // 根据类型获取想法
  getThoughtsByType: (type, page = 1) => {
    return request.get(`/api/v1.0/thoughts/type/${type}?page=${page}`)
  },

  // 获取公开想法
  getPublicThoughts: (page = 1) => {
    return request.get(`/api/v1.0/thoughts/public?page=${page}`)
  },

  // 获取私有想法
  getPrivateThoughts: (page = 1) => {
    return request.get(`/api/v1.0/thoughts/private?page=${page}`)
  },

  // 切换想法公开状态
  togglePublic: (id) => {
    return request.post(`/api/v1.0/thoughts/${id}/toggle-public`)
  },

  // 获取热门标签
  getPopularTags: (limit = 20) => {
    return request.get(`/api/v1.0/thoughts/tags/popular?limit=${limit}`)
  },

  // 获取相关想法
  getRelatedThoughts: (id, limit = 5) => {
    return request.get(`/api/v1.0/thoughts/${id}/related?limit=${limit}`)
  },

  // 获取想法统计
  getThoughtStats: (period = 'week') => {
    return request.get(`/api/v1.0/thoughts/stats?period=${period}`)
  },

  // 批量删除想法
  batchDeleteThoughts: (ids) => {
    return request.post('/api/v1.0/thoughts/batch-delete', { ids })
  },

  // 导出想法
  exportThoughts: (format = 'json') => {
    return request.get(`/api/v1.0/thoughts/export?format=${format}`, { responseType: 'blob' })
  },

  // 导入想法
  importThoughts: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/api/v1.0/thoughts/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}