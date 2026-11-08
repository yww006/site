# 每日资源导航 📅

> 每天精选一个优质技术资源，自动更新，持续输出。

**在线访问**：https://yww006.github.io/site/

---

## ✨ 特性

- 🎯 **每日一更**：GitHub Actions 定时生成新内容，零维护成本
- 🎨 **沉浸式体验**：全屏动态背景（Unsplash 星空/极光/星系），粒子动画点缀
- 📱 **响应式设计**：桌面端双栏、移动端单栏完美适配
- ⚡ **纯静态站点**：无后端、无数据库、部署极简（GitHub Pages）
- 🔍 **历史归档**：过往内容网格展示，支持无限加载
- ♿ **无障碍友好**：语义化 HTML、键盘导航、减弱动画偏好支持

---

## 📁 项目结构

```
site/
├── index.html              # 主页面
├── update_content.py       # 每日内容生成脚本
├── data/
│   └── content.json        # 内容数据（自动维护）
├── assets/
│   ├── style.css           # 样式表
│   └── script.js           # 前端逻辑
├── .github/
│   └── workflows/
│       └── update-content.yml  # GitHub Actions 定时任务
└── README.md
```

---

## 🚀 本地开发

```bash
# 克隆仓库
git clone https://github.com/yww006/site.git
cd site

# 本地预览（任意静态服务器）
# 方式 1：Python
python -m http.server 8080

# 方式 2：Node.js (serve)
npx serve .

# 方式 3：VS Code Live Server 扩展
# 右键 index.html → "Open with Live Server"

# 浏览器打开 http://localhost:8080
```

### 手动生成内容

```bash
# 生成下一天的内容（追加到 data/content.json）
python update_content.py

# 查看生成的内容
cat data/content.json | head -50
```

---

## ⚙️ 自动化流程

### 定时更新

`.github/workflows/update-content.yml` 配置：
- **触发时间**：每天 UTC 0:00（北京时间 8:00）
- **执行逻辑**：
  1. 读取 `data/content.json` 最新日期
  2. 生成下一天的伪造优质资源条目
  3. 提交并推送到 `main` 分支
  4. 触发 GitHub Pages 重新部署

### 手动触发

在 GitHub 仓库页面：
1. 点击 **Actions** 标签
2. 选择 **每日内容自动更新** workflow
3. 点击 **Run workflow** → **Run workflow**

---

## 🎨 自定义配置

### 修改背景图片

编辑 `assets/script.js` 中的 `CONFIG.backgrounds` 数组：

```javascript
const CONFIG = {
  backgrounds: [
    'https://images.unsplash.com/photo-xxx?w=1920&q=80',  // 替换为你的图片
    // ...
  ],
  bgChangeInterval: 300000,  // 切换间隔（毫秒）
};
```

### 调整内容源

编辑 `update_content.py`：
- `TOPICS`：技术主题池
- `CATEGORIES`：分类标签
- `SINGLE_RESOURCES`：特色栏目模板
- 可接入真实 API（GitHub Trending、Hacker News、Dev.to 等）

### 修改启动日期

```python
# update_content.py
CONFIG = {
    # ...
    "startDate": "2025-01-01",  # 第 1 天日期
}
```

---

## 📦 部署到 GitHub Pages

1. 仓库 **Settings** → **Pages**
2. **Source** 选择 **GitHub Actions**
3. 推送到 `main` 分支即可自动部署
4. 访问 `https://<username>.github.io/site/`

> ⚠️ 仓库名不是 `username.github.io` 时，页面会部署到子路径 `/site/`，资源引用需用相对路径（本项目已处理）。

---

## 📄 许可证

MIT License - 可自由使用、修改、分发。

---

## 🙏 致谢

- 背景图片来源：[Unsplash](https://unsplash.com/)
- 字体：[Google Fonts - Inter & Noto Sans SC](https://fonts.google.com/)
- 图标：内联 SVG
- 部署：GitHub Pages + GitHub Actions