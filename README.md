# AI Skills Manager

一个基于网页的 AI 编码助手技能/规则管理器，配备实时 Markdown 预览编辑器。

## 效果图
<img src="https://github.com/GaiJilong/skillManage/blob/main/public/1.png" width="100%" />

## 功能

- 浏览/搜索 Skills
- 左右分栏编辑器 + 实时预览
- 中英文切换
- 明暗主题切换
- 新建/编辑/删除/复制

## 快速启动

```bash
# 后端
cd server && pip install -r requirements.txt && python app.py

# 前端（新终端）
npm install && npm run dev
```

- 后端: http://localhost:8000
- 前端: http://localhost:3000

## Skills 结构

```
skills/
└── skill-name/
    └── SKILL.md
```

## 技术栈

- 前端: Vue 3 + Vite
- 后端: Python FastAPI

## 许可证

Apache-2.0
