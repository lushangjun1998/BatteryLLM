import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000' // 'http://10.0.62.60:26945' 服务器端

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json'
    }
})

export const ragApi = {
    // 提问
    askQuestion: (question) => {
        return api.post('/ask', { question })
    },

    // 提交反馈
    submitFeedback: (feedbackData) => {
        return api.post('/feedback', feedbackData)
    },

    // 健康检查
    healthCheck: () => {
        return api.get('/health')
    }
}

export default api