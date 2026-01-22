<script setup>
/**
 * App.vue - AI Skills 管理器
 * 通过后端API管理skills目录中的文件
 */
import { ref, computed, onMounted } from 'vue'

// API基础URL（通过vite代理）
const API_BASE = '/api'

// ==================== 状态 ====================
const skills = ref([])
const selectedSkillName = ref('')
const selectedSkillContent = ref('')
const searchQuery = ref('')
const isEditing = ref(false)
const editContent = ref('')
const copied = ref(false)
const loading = ref(false)
const error = ref('')

// 主题状态
const isDark = ref(true)

/**
 * 切换主题
 */
function toggleTheme() {
  isDark.value = !isDark.value
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

/**
 * 初始化主题
 */
function initTheme() {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    isDark.value = savedTheme === 'dark'
  } else {
    // 检测系统主题偏好
    isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
}

// ==================== 国际化 ====================

// 语言包
const messages = {
  en: {
    search: 'Search...',
    loading: 'Loading...',
    noSkills: 'No Skills',
    copy: 'Copy',
    copied: 'Copied!',
    edit: 'Edit',
    delete: 'Delete',
    cancel: 'Cancel',
    save: 'Save',
    newSkill: 'New',
    lightMode: 'Light mode',
    darkMode: 'Dark mode',
    selectOrCreate: 'Select a skill or create new one',
    enterSkillName: 'Enter Skill name (e.g. my-skill-name):',
    confirmDelete: 'Are you sure to delete "{name}"?',
    createFailed: 'Create failed',
    saveFailed: 'Save failed',
    deleteFailed: 'Delete failed',
    fetchListFailed: 'Failed to fetch list',
    fetchContentFailed: 'Failed to fetch content',
    defaultDescription: 'Enter description here',
    defaultContent: 'Enter skill content here...',
    editor: 'Editor',
    preview: 'Preview'
  },
  zh: {
    search: '搜索...',
    loading: '加载中...',
    noSkills: '暂无Skills',
    copy: '复制',
    copied: '已复制!',
    edit: '编辑',
    delete: '删除',
    cancel: '取消',
    save: '保存',
    newSkill: '新建',
    lightMode: '亮色模式',
    darkMode: '暗色模式',
    selectOrCreate: '选择一个 Skill 或创建新的',
    enterSkillName: '输入Skill名称 (例如: my-skill-name):',
    confirmDelete: '确定删除 "{name}" 吗？',
    createFailed: '创建失败',
    saveFailed: '保存失败',
    deleteFailed: '删除失败',
    fetchListFailed: '获取列表失败',
    fetchContentFailed: '获取内容失败',
    defaultDescription: '在此输入描述',
    defaultContent: '在此输入Skill内容...',
    editor: '编辑',
    preview: '预览'
  }
}

// 当前语言
const locale = ref('en')

/**
 * 翻译函数
 * @param {string} key - 翻译键
 * @param {object} params - 替换参数
 */
function t(key, params = {}) {
  let text = messages[locale.value]?.[key] || messages['en'][key] || key
  // 替换参数 {name} => value
  Object.keys(params).forEach(k => {
    text = text.replace(`{${k}}`, params[k])
  })
  return text
}

/**
 * 切换语言
 */
function toggleLocale() {
  locale.value = locale.value === 'en' ? 'zh' : 'en'
  localStorage.setItem('locale', locale.value)
}

/**
 * 初始化语言
 */
function initLocale() {
  const savedLocale = localStorage.getItem('locale')
  if (savedLocale) {
    locale.value = savedLocale
  } else {
    // 检测浏览器语言
    const browserLang = navigator.language || navigator.userLanguage
    locale.value = browserLang.startsWith('zh') ? 'zh' : 'en'
  }
}

// 过滤后的列表
const filteredSkills = computed(() => {
  if (!searchQuery.value) return skills.value
  const query = searchQuery.value.toLowerCase()
  return skills.value.filter(s => s.name.toLowerCase().includes(query))
})

// ==================== API调用 ====================

/**
 * 获取skills列表
 */
async function fetchSkills() {
  try {
    loading.value = true
    error.value = ''
    const res = await fetch(`${API_BASE}/skills`)
    if (!res.ok) throw new Error(t('fetchListFailed'))
    skills.value = await res.json()
    
    // 默认选中第一个
    if (skills.value.length > 0 && !selectedSkillName.value) {
      selectSkill(skills.value[0].name)
    }
  } catch (err) {
    error.value = err.message
    console.error('获取skills失败:', err)
  } finally {
    loading.value = false
  }
}

/**
 * 获取单个skill内容
 */
async function selectSkill(name) {
  try {
    loading.value = true
    isEditing.value = false
    selectedSkillName.value = name
    
    const res = await fetch(`${API_BASE}/skills/${name}`)
    if (!res.ok) throw new Error(t('fetchContentFailed'))
    const data = await res.json()
    selectedSkillContent.value = data.content
  } catch (err) {
    error.value = err.message
    console.error('获取skill内容失败:', err)
  } finally {
    loading.value = false
  }
}

/**
 * 创建新skill
 */
async function createSkill() {
  const name = prompt(t('enterSkillName'))
  if (!name || !name.trim()) return
  
  const defaultContent = `---
name: ${name.trim().toLowerCase().replace(/\s+/g, '-')}
description: ${t('defaultDescription')}
---

# ${name.trim()}

${t('defaultContent')}
`
  
  try {
    loading.value = true
    const res = await fetch(`${API_BASE}/skills`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: name.trim(),
        content: defaultContent
      })
    })
    
    if (!res.ok) {
      const data = await res.json()
      throw new Error(data.detail || t('createFailed'))
    }
    
    const data = await res.json()
    await fetchSkills()
    selectSkill(data.name)
    
    // 进入编辑模式
    isEditing.value = true
    editContent.value = defaultContent
  } catch (err) {
    alert(t('createFailed') + ': ' + err.message)
    console.error('创建skill失败:', err)
  } finally {
    loading.value = false
  }
}

/**
 * 保存编辑
 */
async function saveEdit() {
  try {
    loading.value = true
    const res = await fetch(`${API_BASE}/skills/${selectedSkillName.value}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: editContent.value })
    })
    
    if (!res.ok) throw new Error(t('saveFailed'))
    
    selectedSkillContent.value = editContent.value
    isEditing.value = false
  } catch (err) {
    alert(t('saveFailed') + ': ' + err.message)
    console.error('保存skill失败:', err)
  } finally {
    loading.value = false
  }
}

/**
 * 删除skill
 */
async function deleteSkill() {
  if (!confirm(t('confirmDelete', { name: selectedSkillName.value }))) return
  
  try {
    loading.value = true
    const res = await fetch(`${API_BASE}/skills/${selectedSkillName.value}`, {
      method: 'DELETE'
    })
    
    if (!res.ok) throw new Error(t('deleteFailed'))
    
    selectedSkillName.value = ''
    selectedSkillContent.value = ''
    await fetchSkills()
  } catch (err) {
    alert(t('deleteFailed') + ': ' + err.message)
    console.error('删除skill失败:', err)
  } finally {
    loading.value = false
  }
}

/**
 * 开始编辑
 */
function startEdit() {
  editContent.value = selectedSkillContent.value
  isEditing.value = true
}

/**
 * 取消编辑
 */
function cancelEdit() {
  isEditing.value = false
}

/**
 * 复制内容
 */
async function copyContent() {
  try {
    await navigator.clipboard.writeText(selectedSkillContent.value)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch (err) {
    console.error('复制失败:', err)
  }
}

// 初始化
onMounted(() => {
  initTheme()
  initLocale()
  fetchSkills()
})
</script>

<template>
  <div class="app">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <h1 class="logo">AI Skills</h1>
        <div class="header-btns">
          <button class="lang-btn" @click="toggleLocale" :title="locale === 'en' ? 'Chinese' : 'English'">
            {{ locale === 'en' ? 'CN' : 'US' }}
          </button>
          <button class="theme-btn" @click="toggleTheme" :title="isDark ? t('lightMode') : t('darkMode')">
            <!-- 太阳图标（暗色时显示） -->
            <svg v-if="isDark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="5"/>
              <line x1="12" y1="1" x2="12" y2="3"/>
              <line x1="12" y1="21" x2="12" y2="23"/>
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
              <line x1="1" y1="12" x2="3" y2="12"/>
              <line x1="21" y1="12" x2="23" y2="12"/>
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
            </svg>
            <!-- 月亮图标（亮色时显示） -->
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
            </svg>
          </button>
          <button class="add-btn" @click="createSkill" :title="t('newSkill')">+</button>
        </div>
      </div>
      
      <!-- 搜索 -->
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="t('search')"
          class="search-input"
        />
      </div>
      
      <!-- 列表 -->
      <ul class="skill-list">
        <li
          v-for="skill in filteredSkills"
          :key="skill.name"
          class="skill-item"
          :class="{ active: selectedSkillName === skill.name }"
          @click="selectSkill(skill.name)"
        >
          {{ skill.name }}
        </li>
        
        <li v-if="filteredSkills.length === 0" class="empty-item">
          {{ loading ? t('loading') : t('noSkills') }}
        </li>
      </ul>
    </aside>

    <!-- 主内容 -->
    <main class="main">
      <template v-if="selectedSkillName">
        <!-- 工具栏 -->
        <div class="toolbar">
          <h2 class="skill-name">{{ selectedSkillName }}</h2>
          <div class="toolbar-actions">
            <button v-if="!isEditing" class="btn" @click="copyContent" :disabled="loading">
              {{ copied ? t('copied') : t('copy') }}
            </button>
            <button v-if="!isEditing" class="btn" @click="startEdit" :disabled="loading">{{ t('edit') }}</button>
            <button v-if="!isEditing" class="btn btn-danger" @click="deleteSkill" :disabled="loading">{{ t('delete') }}</button>
            <button v-if="isEditing" class="btn" @click="cancelEdit">{{ t('cancel') }}</button>
            <button v-if="isEditing" class="btn btn-primary" @click="saveEdit" :disabled="loading">{{ t('save') }}</button>
          </div>
        </div>

        <!-- 内容区 -->
        <div class="content-area" :class="{ 'edit-mode': isEditing }">
          <!-- 编辑模式：左右分栏 -->
          <template v-if="isEditing">
            <div class="edit-pane">
              <div class="pane-header">
                <span class="pane-title">{{ t('editor') }}</span>
              </div>
              <textarea
                v-model="editContent"
                class="editor"
                spellcheck="false"
              ></textarea>
            </div>
            <div class="preview-pane">
              <div class="pane-header">
                <span class="pane-title">{{ t('preview') }}</span>
              </div>
              <div class="markdown-content" v-html="renderMarkdown(editContent)"></div>
            </div>
          </template>
          
          <!-- 查看模式：Markdown格式显示 -->
          <div v-else class="markdown-content" v-html="renderMarkdown(selectedSkillContent)"></div>
        </div>
      </template>

      <!-- 空状态 -->
      <div v-else class="empty">
        <p v-if="error">{{ error }}</p>
        <p v-else-if="loading">{{ t('loading') }}</p>
        <p v-else>{{ t('selectOrCreate') }}</p>
      </div>
    </main>
  </div>
</template>

<script>
/**
 * 简单的Markdown渲染函数
 * 将Markdown转换为HTML显示
 */
function renderMarkdown(text) {
  if (!text) return ''
  
  let html = text
  
  // 转义HTML特殊字符（但保留我们后面要处理的）
  html = html
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  // 代码块 (```code```)
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
    return `<pre class="code-block"><code class="language-${lang}">${code.trim()}</code></pre>`
  })
  
  // 行内代码 (`code`)
  html = html.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
  
  // YAML frontmatter (---)
  html = html.replace(/^---\n([\s\S]*?)\n---/m, (match, yaml) => {
    return `<div class="frontmatter"><pre>${yaml}</pre></div>`
  })
  
  // 标题
  html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>')
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>')
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>')
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>')
  
  // 粗体
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  
  // 斜体
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  
  // 无序列表
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>')
  
  // 将连续的li包装成ul
  html = html.replace(/(<li>.*<\/li>\n?)+/g, (match) => {
    return '<ul>' + match + '</ul>'
  })
  
  // 表格（简单处理）
  html = html.replace(/^\|(.+)\|$/gm, (match, content) => {
    const cells = content.split('|').map(c => c.trim())
    if (cells.every(c => /^-+$/.test(c))) {
      return '' // 跳过分隔行
    }
    return '<tr>' + cells.map(c => `<td>${c}</td>`).join('') + '</tr>'
  })
  html = html.replace(/(<tr>.*<\/tr>\n?)+/g, (match) => {
    return '<table>' + match + '</table>'
  })
  
  // 段落（双换行）
  html = html.replace(/\n\n/g, '</p><p>')
  
  // 单换行转<br>（在非标签内）
  // html = html.replace(/\n/g, '<br>')
  
  return '<div class="md-body"><p>' + html + '</p></div>'
}

// 导出给setup使用
export default {
  methods: {
    renderMarkdown
  }
}
</script>

<style scoped>
.app {
  display: flex;
  height: 100vh;
  background: var(--bg-primary);
}

/* 侧边栏 */
.sidebar {
  width: 260px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.logo {
  font-family: var(--font-display);
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.header-btns {
  display: flex;
  gap: 8px;
}

.lang-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-glass);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-muted);
  font-size: 0.7rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.lang-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  background: rgba(6, 182, 212, 0.1);
}

.theme-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-glass);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.theme-btn svg {
  width: 16px;
  height: 16px;
}

.theme-btn:hover {
  border-color: var(--color-warning);
  color: var(--color-warning);
  background: rgba(245, 158, 11, 0.1);
}

.add-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1.2rem;
  cursor: pointer;
  transition: background 0.2s;
}

.add-btn:hover {
  background: var(--color-primary-light);
}

/* 搜索 */
.search-box {
  padding: 12px 16px;
}

.search-input {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.search-input::placeholder {
  color: var(--text-muted);
}

/* 列表 */
.skill-list {
  flex: 1;
  overflow-y: auto;
  list-style: none;
  padding: 0;
  margin: 0;
}

.skill-item {
  padding: 12px 16px;
  color: var(--text-secondary);
  cursor: pointer;
  border-left: 3px solid transparent;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  transition: all 0.15s;
}

.skill-item:hover {
  background: var(--bg-glass);
  color: var(--text-primary);
}

.skill-item.active {
  background: linear-gradient(90deg, rgba(99, 102, 241, 0.1), transparent);
  border-left-color: var(--color-primary);
  color: var(--text-primary);
}

.empty-item {
  padding: 20px 16px;
  color: var(--text-muted);
  text-align: center;
  font-size: 0.85rem;
}

/* 主内容 */
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* 工具栏 */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.skill-name {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-primary-light);
}

.toolbar-actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 6px 14px;
  background: var(--bg-glass);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.15s;
}

.btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--text-primary);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-light);
}

.btn-danger:hover:not(:disabled) {
  border-color: var(--color-danger);
  color: var(--color-danger);
}

/* 内容区 */
.content-area {
  flex: 1;
  overflow: auto;
  padding: 24px;
}

/* 编辑模式：左右分栏 */
.content-area.edit-mode {
  display: flex;
  gap: 1px;
  padding: 0;
  background: var(--border-color);
  overflow: hidden;
}

.edit-pane,
.preview-pane {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: var(--bg-primary);
}

.pane-header {
  padding: 10px 16px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.pane-title {
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
}

.edit-pane .editor {
  flex: 1;
  width: 100%;
  padding: 16px;
  background: var(--bg-primary);
  border: none;
  outline: none;
  resize: none;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.875rem;
  line-height: 1.6;
  color: var(--text-primary);
}

.preview-pane {
  overflow: hidden;
}

.preview-pane .markdown-content {
  flex: 1;
  overflow: auto;
  padding: 16px;
}

/* Markdown样式 */
.markdown-content {
  font-size: 0.95rem;
  line-height: 1.7;
  color: var(--text-secondary);
}

.markdown-content :deep(.md-body) {
  max-width: 800px;
}

.markdown-content :deep(.frontmatter) {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(6, 182, 212, 0.05));
  border: 1px solid var(--border-glow);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
  overflow: hidden;
}

.markdown-content :deep(.frontmatter pre) {
  margin: 0;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  color: var(--color-accent);
  white-space: pre-wrap;
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
}

.markdown-content :deep(h1) {
  font-family: var(--font-display);
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 32px 0 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--border-color);
}

.markdown-content :deep(h2) {
  font-family: var(--font-display);
  font-size: 1.4rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 28px 0 12px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border-color);
}

.markdown-content :deep(h3) {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 24px 0 10px;
}

.markdown-content :deep(h4) {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 20px 0 8px;
}

.markdown-content :deep(p) {
  margin: 12px 0;
}

.markdown-content :deep(strong) {
  color: var(--text-primary);
  font-weight: 600;
}

.markdown-content :deep(em) {
  font-style: italic;
}

.markdown-content :deep(ul) {
  margin: 12px 0;
  padding-left: 24px;
}

.markdown-content :deep(li) {
  margin: 8px 0;
  position: relative;
}

.markdown-content :deep(li::marker) {
  color: var(--color-primary);
}

.markdown-content :deep(.code-block) {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
  overflow-x: auto;
}

.markdown-content :deep(.code-block code) {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  color: var(--color-accent);
  line-height: 1.5;
}

.markdown-content :deep(.inline-code) {
  background: var(--bg-glass);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85em;
  color: var(--color-primary-light);
}

.markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
}

.markdown-content :deep(td) {
  padding: 10px 14px;
  border: 1px solid var(--border-color);
  font-size: 0.9rem;
}

.markdown-content :deep(tr:first-child td) {
  background: var(--bg-glass);
  font-weight: 600;
  color: var(--text-primary);
}

/* 编辑器 */
.editor {
  width: 100%;
  height: 100%;
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  line-height: 1.6;
  color: var(--text-primary);
  resize: none;
}

.editor:focus {
  outline: none;
  border-color: var(--color-primary);
}

/* 空状态 */
.empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}
</style>
