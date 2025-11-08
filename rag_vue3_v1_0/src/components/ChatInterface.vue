<template>
    <div class="chat-container">
        <div class="main-content">
            <!-- 聊天区域 -->
            <div class="chat-area">
                <div class="chat-header">
                    <h2>🔋 电池策略大模型LLM</h2>
                </div>

                <div class="messages-container" ref="messagesContainer">
                    <div v-for="(message, index) in messages" :key="index"
                         :class="['message', message.type, message.type === 'user' ? 'user-message' : 'bot-message']">
                        <div class="message-content" v-html="message.content"></div>
                        <div class="message-time">{{ message.time }}</div>
                    </div>

                    <div v-if="loading" class="message bot loading">
                        <div class="message-content">
                            <div class="typing-indicator">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="input-area">
                    <el-input
                        v-model="currentQuestion"
                        type="textarea"
                        :autosize="{ minRows: 4, maxRows: 8 }"
                        placeholder="请输入您的问题..."
                        @keydown.enter.prevent="handleEnter"
                        :disabled="loading"
                        resize="none"
                        class="question-input"
                    />
                    <div class="input-actions">
                        <el-button
                            type="primary"
                            @click="sendQuestion"
                            :loading="loading"
                            :disabled="!currentQuestion.trim()"
                            class="send-button"
                        >
                            <el-icon class="el-icon--left"><Promotion /></el-icon>
                            发送
                        </el-button>
                    </div>
                </div>

                <!-- 底部联系信息 -->
                <div class="footer">
                    <p>相关问题或建议，请联系：lushangjun1@byd.com</p>
                </div>
            </div>
        </div>

        <!-- 反馈侧边栏 -->
        <div class="feedback-sidebar">
            <div class="feedback-header">
                <h2>📝 反馈</h2>
            </div>

            <div class="feedback-content">
                <el-form :model="feedbackForm" label-width="90px">
                    <el-form-item label="输入的问题">
                        <el-input
                            v-model="feedbackForm.question"
                            type="textarea"
                            :rows="7"
                            placeholder="请输入您的提问(选填)"
                            resize="none"
                        />
                    </el-form-item>

                    <el-form-item label="LLM回答">
                        <el-input
                            v-model="feedbackForm.answer"
                            type="textarea"
                            :rows="7"
                            placeholder="请输入LLM的回答(选填)"
                            resize="none"
                        />
                    </el-form-item>

                    <el-form-item label="反馈意见" required>
                        <el-input
                            v-model="feedbackForm.feedback"
                            type="textarea"
                            :rows="7"
                            placeholder="请输入您的反馈意见(必填)"
                            resize="none"
                        />
                    </el-form-item>

                    <el-form-item label="联系方式" required>
                        <el-input
                            v-model="feedbackForm.email"
                            type="textarea"
                            :rows="1"
                            placeholder="请输入邮箱等联系方式(必填)"
                            resize="none"
                        />
                    </el-form-item>

                    <el-button
                        type="primary"
                        @click="submitFeedback"
                        :loading="submittingFeedback"
                        style="width: 100%;"
                    >
                        提交反馈
                    </el-button>
                </el-form>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Promotion } from '@element-plus/icons-vue'
import { ragApi } from '@/services/api'

const messages = ref([])
const currentQuestion = ref('')
const loading = ref(false)
const submittingFeedback = ref(false)
const messagesContainer = ref(null)

const feedbackForm = ref({
    question: '',
    answer: '',
    feedback: '',
    email: ''
})

// 自动滚动到底部
const scrollToBottom = () => {
    nextTick(() => {
        if (messagesContainer.value) {
            messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
    })
}

// 处理回车键
const handleEnter = (event) => {
    if (event.shiftKey) {
        // Shift + Enter 换行
        return
    } else {
        // Enter 发送
        event.preventDefault()
        sendQuestion()
    }
}

// 发送问题
const sendQuestion = async () => {
    if (!currentQuestion.value.trim() || loading.value) return

    const question = currentQuestion.value.trim()
    messages.value.push({
        type: 'user',
        content: question,
        time: new Date().toLocaleTimeString()
    })

    currentQuestion.value = ''
    loading.value = true
    scrollToBottom()

    try {
        const response = await ragApi.askQuestion(question)

        messages.value.push({
            type: 'bot',
            content: response.data.answer,
            time: new Date().toLocaleTimeString()
        })

        // 设置反馈表单中的问题和答案
        // feedbackForm.value.question = question
        // feedbackForm.value.answer = response.data.answer

    } catch (error) {
        console.error('Error:', error)
        ElMessage.error('请求失败，请稍后重试')
    } finally {
        loading.value = false
        scrollToBottom()
    }
}

// 提交反馈
const submitFeedback = async () => {
    if (!feedbackForm.value.feedback.trim()) {
        ElMessage.warning('请填写反馈意见')
        return
    }
    if (!feedbackForm.value.email.trim()) {
        ElMessage.warning('请填写联系方式')
        return
    }

    submittingFeedback.value = true

    try {
        await ragApi.submitFeedback(feedbackForm.value)
        ElMessage.success('反馈提交成功！')

        // 重置反馈表单
        feedbackForm.value.feedback = ''
        feedbackForm.value.question = ''
        feedbackForm.value.answer = ''
        feedbackForm.value.email = ''


    } catch (error) {
        console.error('Feedback error:', error)
        ElMessage.error('反馈提交失败')
    } finally {
        submittingFeedback.value = false
    }
}

// 初始化时检查服务状态
onMounted(async () => {
    try {
        await ragApi.healthCheck()
    } catch (error) {
        ElMessage.error('服务连接失败，请检查网络连接')
    }
})
</script>

<style scoped>
.chat-container {
    display: flex;
    height: 100vh;
    background: #f5f7fa;
}

.main-content {
    flex: 3;
    display: flex;
    flex-direction: column;
    height: 100vh; /* 固定高度 */
    overflow: hidden; /* 防止内部溢出影响整体页面 */
}

.chat-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: white;
    margin: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    overflow: hidden; /* 防止内部元素溢出 */
    /* position: relative; */
}

.chat-header {
    padding: 20px;
    border-bottom: 1px solid #e6e6e6;
    text-align: center;
}

.chat-header h2 {
    margin: 0;
    color: #303133;
}

.messages-container {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    /* max-height: calc(100vh - 200px); */
}

/* 消息气泡样式 */
.message {
    margin-bottom: 16px;
    padding: 12px 16px;
    border-radius: 18px;
    max-width: 60%;
    position: relative;
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* 用户消息样式 */
.message.user {
    margin-left: auto;
    background: #f0f2f5;;
    color: #333;
    border-bottom-right-radius: 6px;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

/* 机器人消息样式 */
.message.bot {
    margin-right: auto;
    background: white;
    color: #333;
    border: 1px solid #e8e8e8;
    border-bottom-left-radius: 6px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}


.message-content {
    word-wrap: break-word;
    line-height: 1.8;
    font-size: 15px;
}

.message-content :deep(*) {
    margin: 0;
    line-height: 1.6;
}

.message-content :deep(ul),
.message-content :deep(ol) {
    padding-left: 20px;
    margin: 8px 0;
}

.message-content :deep(li) {
    margin: 4px 0;
}

.message-content :deep(p) {
    margin: 8px 0;
}

.message-content :deep(p:first-child) {
    margin-top: 0;
}

.message-content :deep(p:last-child) {
    margin-bottom: 0;
}

.message-time {
    font-size: 10px;
    color: #999;
    margin-top: 4px;
    text-align: right;
}

.message.bot .message-time {
    color: #999;
}

/* 输入区域样式 */
.input-area {
    padding: 20px;
    border-top: 1px solid #f0f0f0;
    background: white;
    border-radius: 0 0 12px 12px;
}

.question-input {
    margin-bottom: 12px;
}

.question-input :deep(.el-textarea__inner) {
    border-radius: 12px;
    border: 1px solid #e0e0e0;
    padding: 12px 16px;
    font-size: 14px;
    line-height: 1.5;
    resize: none;
    transition: all 0.3s ease;
}

.question-input :deep(.el-textarea__inner:focus) {
    border-color: #e0e0e0;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.input-actions {
    display: flex;
    justify-content: flex-end;
}

.send-button {
    border-radius: 20px;
    padding: 10px 24px;
    font-weight: 500;
}

/* 加载动画 */
.typing-indicator {
    display: flex;
    align-items: center;
    gap: 4px;
}

.typing-indicator span {
    height: 8px;
    width: 8px;
    border-radius: 50%;
    background: #999;
    animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
    0%, 80%, 100% {
        transform: scale(0.8);
        opacity: 0.5;
    }
    40% {
        transform: scale(1);
        opacity: 1;
    }
}

/* 底部联系信息 */
.footer {
    /* position: absolute; */
    bottom: 0;
    left: 0;
    right: 0;
    text-align: center;
    padding: 6px;
    background: white;
    border-top: 1px solid #f0f0f0;
    border-radius: 0 0 12px 12px;
    margin-top: auto; /* 将 footer 推到底部 */
}

.footer p {
    margin: 0;
    font-size: 12px;
    color: #000000;
    font-weight: bold;
}

/* 反馈侧边栏 */
.feedback-sidebar {
    flex: 1;
    background: white;
    margin: 20px;
    margin-left: 0;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    min-width: 300px;
    /* max-width: 350px; */
}

.feedback-header {
    padding: 20px;
    border-bottom: 1px solid #e6e6e6;
    text-align: center;
}

/* .feedback-header h3 {
    margin: 0;
    color: rgb(0, 0, 0);
    font-weight: 600;
} */

.feedback-content {
    padding: 15px;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .chat-container {
        flex-direction: column;
    }

    .feedback-sidebar {
        margin-left: 20px;
        margin-top: 0;
        max-width: none;
    }

    .message {
        max-width: 60%;
    }

    .chat-area {
        margin: 10px;
    }

    .feedback-sidebar {
        margin: 10px;
    }
}
</style>