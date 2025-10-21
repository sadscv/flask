# Flask Blog Application

一个功能丰富的Flask博客应用，集成了想法记录、心情追踪等现代化功能。

## UI/UX Improvement Notes
- Establish a clearer design system in `frontend/tailwind.config.js` by extending neutral palettes, adding a secondary accent, and defining font stacks so navigation (`frontend/src/App.vue:4`) and cards (`frontend/src/views/Home.vue:20`) share consistent tokens.
- Refresh the global layout by replacing repetitive `bg-white` card blocks in the home feed (`frontend/src/views/Home.vue:42`, `frontend/src/views/Home.vue:257`) with glassmorphism or soft gradient surfaces, and introduce a 24/16/12 spacing rhythm for better hierarchy.
- Tune typography and micro-interactions in `frontend/src/assets/css/main.css:14` so headings, body text, and hover/active states feel more premium across desktop and mobile experiences.
- Rework the header in `frontend/src/App.vue:4` to include a logo lockup, a primary call-to-action, and a compact user capsule while preserving the scroll-safe background and blur elevation.
- Add bespoke empty/error states (e.g., illustrations or friendly copy) in the thoughts and mood modules under `frontend/src/views` to give feedback moments more character.

## Known Issues & TODOs
- `frontend/src/main.js:23` imports `useUIStore` after runtime statements, breaking Vite/ESM parsing. Move the import to the top of the file.
- `frontend/src/api/index.js:89` calls `useAuthStore()` but never imports it, so every 401 response raises a `ReferenceError`.
- Frontend Auth API calls (`frontend/src/api/auth.js:15`, `frontend/src/api/auth.js:29`) expect `/api/auth/logout`, `/api/auth/change-password`, etc., yet only `/api/auth/login`, `/api/auth/register`, and `/api/auth/me` exist in `app/main/views.py:1310-1477`.
- Several blog endpoints declared in `frontend/src/api/blog.js:30-87` (`/posts/search`, `/posts/user/<username>`, `/posts/categories`, etc.) have no matching Flask route, so those features currently fail.
- `frontend/src/api/thoughts.js:15` assumes a `limit` query parameter, but `app/api_1_0/thoughts.py:14-68` ignores it and always paginates by `per_page`, causing the “recent thoughts” widget to fetch more data than intended.
- `app/main/views.py:1310-1477` accepts any token shaped like `real_token_<user_id>_*`, allowing easy forgery because the random suffix is never validated or stored.
- `app/main/views.py:1330-1352` silently rewrites the password hash for `finaltest@example.com`, leaving a hard-coded backdoor.

## 🚀 功能特性

### 📝 博客功能
- **文章管理**: 创建、编辑、删除博客文章
- **评论系统**: 支持文章评论和互动
- **用户认证**: 完整的用户注册、登录、权限管理
- **富文本编辑**: 支持Markdown格式和代码高亮

### 💭 想法记录 (Thino-like)
- **快速记录**: 类似Twitter的短内容记录
- **多种类型**: 笔记、引用、想法、任务分类
- **标签系统**: 灵活的标签分类和筛选
- **隐私控制**: 公开/私密想法设置
- **搜索功能**: 全文搜索和标签筛选

### 😊 心情追踪
- **每日心情**: 记录每日情绪状态
- **强度设置**: 1-10级情绪强度记录
- **日历视图**: 月度心情日历展示
- **统计分析**: 情绪趋势和数据统计
- **日记功能**: 结合心情的文字记录

### 🎨 用户体验
- **响应式设计**: 完美适配桌面和移动设备
- **模态对话框**: 现代化的确认和操作界面
- **AJAX交互**: 无刷新的用户体验
- **动画效果**: 流畅的页面过渡和交互动画
- **深色模式**: 自动适应系统主题

## 🏗️ 技术架构

### 后端技术
- **Flask 3.1.2**: 核心Web框架
- **SQLAlchemy 2.0.43**: ORM数据库操作
- **Flask-Login**: 用户会话管理
- **Flask-Migrate**: 数据库迁移工具
- **Flask-WTF**: 表单处理和CSRF保护

### 前端技术
- **Tailwind CSS**: 原子化CSS框架
- **Font Awesome**: 图标库
- **JavaScript ES6+**: 现代化前端交互
- **AJAX**: 异步数据交互

### 数据库
- **MySQL**: 主要数据存储
- **PyMySQL**: Python MySQL驱动

## 📁 项目结构

```
flask/
├── app/
│   ├── __init__.py              # 应用工厂
│   ├── models.py                # 数据模型
│   ├── decorator.py             # 装饰器
│   ├── exceptions.py            # 异常处理
│   └── main/
│       ├── __init__.py          # 蓝图初始化
│       ├── views.py             # 主视图函数
│       ├── thought_views.py     # 想法相关视图
│       ├── post_views.py        # 文章相关视图
│       ├── mood_views.py        # 心情相关视图
│       └── forms.py             # 表单定义
│   ├── services/                # 服务层
│   │   ├── __init__.py
│   │   ├── auth_service.py      # 认证服务
│   │   ├── permission_service.py # 权限服务
│   │   └── ajax_service.py      # AJAX服务
│   ├── templates/               # 模板文件
│   │   ├── base.html
│   │   ├── thoughts.html
│   │   ├── mood/
│   │   └── ...
│   └── static/
│       ├── css/                 # 样式文件
│       │   ├── main.css         # 主样式文件
│       │   ├── base.css         # 基础样式
│       │   ├── components/      # 组件样式
│       │   └── pages/           # 页面样式
│       ├── js/                  # JavaScript文件
│       │   └── common.js        # 公共JavaScript库
│       └── images/              # 图片资源
├── migrations/                  # 数据库迁移
├── tests/                       # 测试文件
├── config.py                    # 配置文件
├── manage.py                    # 命令行工具
└── requirements.txt             # 依赖包列表
```

## 🛠️ 安装和运行

### 环境要求
- Python 3.8+
- MySQL 5.7+
- Node.js 14+ (可选，用于前端开发)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/sadscv/flask.git
   cd flask
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置数据库**
   - 创建MySQL数据库
   - 修改配置文件中的数据库连接信息
   - 运行数据库迁移

5. **初始化数据库**
   ```bash
   python manage.py db upgrade
   ```

6. **运行应用**
   ```bash
   python manage.py runserver
   ```

7. **访问应用**
   打开浏览器访问 `http://127.0.0.1:5000`

## 📚 API文档

### 认证接口
- `POST /api/auth/login` - 用户登录（返回 `real_token_*` 样式的临时 token）
- `POST /api/auth/register` - 用户注册
- `GET /api/auth/me` - 根据 Authorization 头返回当前用户信息

> ⚠️ 前端已实现但后端缺失的接口：`/api/auth/logout`, `/api/auth/change-password`, `/api/auth/forgot-password`, `/api/auth/reset-password`, `/api/auth/resend-verification`。

### 文章接口
- `GET /api/posts` - 获取文章列表
- `GET /api/posts/<id>` - 获取单篇文章
- `POST /api/posts` - 创建文章
- `PUT /api/posts/<id>` - 更新文章
- `DELETE /api/posts/<id>` - 删除文章

> ⚠️ `/posts/search`, `/posts/user/<username>`, `/posts/categories`, `/posts/tags`, `/posts/recommended` 等前端调用目前无后端实现。

### 想法接口
- `GET /api/v1.0/thoughts` - 获取想法列表
- `POST /api/v1.0/thoughts` - 创建想法
- `PUT /api/v1.0/thoughts/<id>` - 更新想法
- `DELETE /api/v1.0/thoughts/<id>` - 删除想法

> ⚠️ `/api/v1.0/thoughts/batch-delete`, `/api/v1.0/thoughts/import`, `/api/v1.0/thoughts/export`, `/api/v1.0/thoughts/<id>/related` 等接口尚未在后端实现。

### 心情接口
- `GET /api/moods` - 获取心情列表（支持分页、日期筛选）
- `GET /api/moods/today` - 获取当日心情
- `POST /api/moods` - 记录心情
- `PUT /api/moods/<id>` - 更新心情记录
- `DELETE /api/moods/<id>` - 删除心情记录

> ⚠️ `/mood/distribution`, `/mood/trend`, `/mood/templates` 等分析/模板相关接口尚未提供。

## 🔧 开发指南

### 添加新功能

1. **数据模型**: 在 `app/models.py` 中定义新的数据模型
2. **表单**: 在 `app/main/forms.py` 中添加表单类
3. **视图**: 在 `app/main/` 中添加新的视图函数
4. **模板**: 在 `app/templates/` 中添加模板文件
5. **样式**: 在 `app/static/css/` 中添加样式

### 代码规范

- **Python**: 遵循PEP 8编码规范
- **JavaScript**: 使用ES6+语法和模块化编程
- **CSS**: 使用BEM命名规范和模块化结构
- **Git**: 使用有意义的提交信息

### 测试

```bash
# 运行所有测试
python manage.py test

# 运行特定测试
python manage.py test tests.test_models
```

## 🚀 部署

### 生产环境部署

1. **环境配置**
   ```bash
   export FLASK_ENV=production
   export FLASK_CONFIG=ProductionConfig
   ```

2. **数据库配置**
   - 使用生产环境数据库
   - 配置数据库连接池
   - 设置数据库备份策略

3. **Web服务器**
   - 使用Nginx + Gunicorn
   - 配置HTTPS证书
   - 设置静态文件服务

4. **监控**
   - 配置日志记录
   - 设置性能监控
   - 配置错误报告

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [Flask](https://flask.palletsprojects.com/) - 优秀的Web框架
- [Tailwind CSS](https://tailwindcss.com/) - 原子化CSS框架
- [Font Awesome](https://fontawesome.com/) - 图标库
- 所有贡献者和用户的支持

## 📞 联系方式

- 作者: sadscv
- 项目地址: [https://github.com/sadscv/flask](https://github.com/sadscv/flask)
- 问题反馈: [Issues](https://github.com/sadscv/flask/issues)

---

⭐ 如果这个项目对你有帮助，请给它一个星标！
