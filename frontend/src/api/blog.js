import { request } from './index'

export const blogApi = {
  // 获取文章列表
  getPosts: (page = 1, perPage = 10) => {
    return request.get(`/posts?page=${page}&per_page=${perPage}`)
  },

  // 获取单篇文章
  getPost: (id) => {
    return request.get(`/posts/${id}`)
  },

  // 创建文章
  createPost: (postData) => {
    return request.post('/posts', postData)
  },

  // 更新文章
  updatePost: (id, postData) => {
    return request.put(`/posts/${id}`, postData)
  },

  // 删除文章
  deletePost: (id) => {
    return request.delete(`/posts/${id}`)
  },

  // 搜索文章
  searchPosts: (query, page = 1) => {
    return request.get(`/posts/search?q=${encodeURIComponent(query)}&page=${page}`)
  },

  // 获取用户文章
  getUserPosts: (username, page = 1) => {
    return request.get(`/posts/user/${username}?page=${page}`)
  },

  // 获取文章分类
  getCategories: () => {
    return request.get('/posts/categories')
  },

  // 获取分类文章
  getPostsByCategory: (category, page = 1) => {
    return request.get(`/posts/category/${category}?page=${page}`)
  },

  // 获取文章标签
  getTags: () => {
    return request.get('/posts/tags')
  },

  // 获取标签文章
  getPostsByTag: (tag, page = 1) => {
    return request.get(`/posts/tag/${tag}?page=${page}`)
  },

  // 点赞文章
  likePost: (id) => {
    return request.post(`/posts/${id}/like`)
  },

  // 取消点赞
  unlikePost: (id) => {
    return request.delete(`/posts/${id}/like`)
  },

  // 获取文章评论
  getComments: (postId, page = 1) => {
    return request.get(`/posts/${postId}/comments?page=${page}`)
  },

  // 添加评论
  addComment: (postId, commentData) => {
    return request.post(`/posts/${postId}/comments`, commentData)
  },

  // 删除评论
  deleteComment: (postId, commentId) => {
    return request.delete(`/posts/${postId}/comments/${commentId}`)
  },

  // 获取热门文章
  getPopularPosts: (limit = 10) => {
    return request.get(`/posts/popular?limit=${limit}`)
  },

  // 获取最新文章
  getLatestPosts: (limit = 10) => {
    return request.get(`/posts/latest?limit=${limit}`)
  },

  // 获取推荐文章
  getRecommendedPosts: (limit = 10) => {
    return request.get(`/posts/recommended?limit=${limit}`)
  }
}