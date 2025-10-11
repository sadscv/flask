import { request } from './index'

export const moodApi = {
  // 获取今日心情
  getTodayMood: () => {
    return request.get('/mood/today')
  },

  // 创建心情记录
  createMood: (moodData) => {
    return request.post('/mood', moodData)
  },

  // 更新心情记录
  updateMood: (id, moodData) => {
    return request.put(`/mood/${id}`, moodData)
  },

  // 删除心情记录
  deleteMood: (id) => {
    return request.delete(`/mood/${id}`)
  },

  // 获取心情历史
  getMoodHistory: (page = 1, limit = 30) => {
    return request.get(`/mood/history?page=${page}&limit=${limit}`)
  },

  // 获取心情统计
  getMoodStats: (period = 'week') => {
    return request.get(`/mood/stats?period=${period}`)
  },

  // 获取心情日历数据
  getMoodCalendar: (year, month) => {
    return request.get(`/mood/calendar/${year}/${month}`)
  },

  // 获取特定日期的心情
  getMoodByDate: (date) => {
    return request.get(`/mood/date/${date}`)
  },

  // 获取心情分布
  getMoodDistribution: (startDate, endDate) => {
    return request.get(`/mood/distribution?start=${startDate}&end=${endDate}`)
  },

  // 获取心情趋势
  getMoodTrend: (period = 'month') => {
    return request.get(`/mood/trend?period=${period}`)
  },

  // 获取心情分析
  getMoodAnalysis: (period = 'month') => {
    return request.get(`/mood/analysis?period=${period}`)
  },

  // 获取最常见的心情类型
  getTopMoods: (limit = 10, period = 'month') => {
    return request.get(`/mood/top?limit=${limit}&period=${period}`)
  },

  // 获取心情强度分布
  getIntensityDistribution: (period = 'month') => {
    return request.get(`/mood/intensity?period=${period}`)
  },

  // 获取心情平均值
  getMoodAverage: (period = 'month') => {
    return request.get(`/mood/average?period=${period}`)
  },

  // 获取心情建议
  getMoodSuggestions: () => {
    return request.get('/mood/suggestions')
  },

  // 获取心情报告
  getMoodReport: (period = 'month') => {
    return request.get(`/mood/report?period=${period}`)
  },

  // 导出心情数据
  exportMoodData: (format = 'json', period = 'month') => {
    return request.get(`/mood/export?format=${format}&period=${period}`, { responseType: 'blob' })
  },

  // 获取心情提醒设置
  getMoodReminders: () => {
    return request.get('/mood/reminders')
  },

  // 设置心情提醒
  setMoodReminder: (reminderData) => {
    return request.post('/mood/reminders', reminderData)
  },

  // 更新心情提醒
  updateMoodReminder: (id, reminderData) => {
    return request.put(`/mood/reminders/${id}`, reminderData)
  },

  // 删除心情提醒
  deleteMoodReminder: (id) => {
    return request.delete(`/mood/reminders/${id}`)
  },

  // 获取心情目标
  getMoodGoals: () => {
    return request.get('/mood/goals')
  },

  // 设置心情目标
  setMoodGoal: (goalData) => {
    return request.post('/mood/goals', goalData)
  },

  // 更新心情目标
  updateMoodGoal: (id, goalData) => {
    return request.put(`/mood/goals/${id}`, goalData)
  },

  // 删除心情目标
  deleteMoodGoal: (id) => {
    return request.delete(`/mood/goals/${id}`)
  },

  // 获取心情日记
  getMoodDiary: (date) => {
    return request.get(`/mood/diary/${date}`)
  },

  // 保存心情日记
  saveMoodDiary: (date, diaryContent) => {
    return request.post(`/mood/diary/${date}`, { content: diaryContent })
  },

  // 获取心情模板
  getMoodTemplates: () => {
    return request.get('/mood/templates')
  },

  // 创建心情模板
  createMoodTemplate: (templateData) => {
    return request.post('/mood/templates', templateData)
  },

  // 获取心情活动日志
  getMoodActivity: (page = 1, limit = 20) => {
    return request.get(`/mood/activity?page=${page}&limit=${limit}`)
  }
}