import { request } from './index'

export const thoughtsApi = {
  // 获取想法列表
  getThoughts: (page = 1, perPage = 20) => {
    return request.get(`/thoughts?page=${page}&per_page=${perPage}`)
  },

  // 获取最近想法
  getRecentThoughts: (limit = 5) => {
    return request.get(`/thoughts/recent?limit=${limit}`)
  },

  // 获取单条想法
  getThought: (id) => {
    return request.get(`/thoughts/${id}`)
  },

  // 创建想法
  createThought: (thoughtData) => {
    return request.post('/thoughts', thoughtData)
  },

  // 更新想法
  updateThought: (id, thoughtData) => {
    return request.put(`/thoughts/${id}`, thoughtData)
  },

  // 删除想法
  deleteThought: (id) => {
    return request.delete(`/thoughts/${id}`)
  },

  // 搜索想法
  searchThoughts: (query, page = 1) => {
    return request.get(`/thoughts/search?q=${encodeURIComponent(query)}&page=${page}`)
  },

  // 根据标签获取想法
  getThoughtsByTag: (tag, page = 1) => {
    return request.get(`/thoughts/tag/${encodeURIComponent(tag)}?page=${page}`)
  },

  // 获取用户想法
  getUserThoughts: (username, page = 1) => {
    return request.get(`/thoughts/user/${username}?page=${page}`)
  },

  // 获取想法类型列表
  getThoughtTypes: () => {
    return request.get('/thoughts/types')
  },

  // 根据类型获取想法
  getThoughtsByType: (type, page = 1) => {
    return request.get(`/thoughts/type/${type}?page=${page}`)
  },

  // 获取公开想法
  getPublicThoughts: (page = 1) => {
    return request.get(`/thoughts/public?page=${page}`)
  },

  // 获取私有想法
  getPrivateThoughts: (page = 1) => {
    return request.get(`/thoughts/private?page=${page}`)
  },

  // 切换想法公开状态
  togglePublic: (id) => {
    return request.post(`/thoughts/${id}/toggle-public`)
  },

  // 获取热门标签
  getPopularTags: (limit = 20) => {
    return request.get(`/thoughts/tags/popular?limit=${limit}`)
  },

  // 获取相关想法
  getRelatedThoughts: (id, limit = 5) => {
    return request.get(`/thoughts/${id}/related?limit=${limit}`)
  },

  // 获取想法统计
  getThoughtStats: (period = 'week') => {
    return request.get(`/thoughts/stats?period=${period}`)
  },

  // 批量删除想法
  batchDeleteThoughts: (ids) => {
    return request.post('/thoughts/batch-delete', { ids })
  },

  // 导出想法
  exportThoughts: (format = 'json') => {
    return request.get(`/thoughts/export?format=${format}`, { responseType: 'blob' })
  },

  // 导入想法
  importThoughts: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/thoughts/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}