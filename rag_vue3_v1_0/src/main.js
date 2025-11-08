import { createApp } from 'vue'
import App from './App.vue'

import ElementPlus from 'element-plus'  // 导入ElementPlus组件库的所有模块和功能
import 'element-plus/dist/index.css'    // 导入ElementPlus组件库所需的全局css样式
import * as ElementPlusIconsVue from '@element-plus/icons-vue' // 导入所有图标

const app = createApp(App)  // 将Elements插件注册到Vue应用中

// 将 ElementPlus 插件注册到Vue应用中
app.use(ElementPlus)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}

app.mount('#app')