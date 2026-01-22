/**
 * 应用入口文件
 * 创建Vue应用实例并挂载到DOM
 */
import { createApp } from 'vue'
import App from './App.vue'
import './styles/main.css'

const app = createApp(App)
app.mount('#app')
