# 🍳 早餐决策系统 | Breakfast Decision System

一个帮助你决定明天早餐吃什么的智能系统！

## ✨ 功能特点

- 🎲 **随机抽取** - 根据评分权重随机推荐早餐
- 📅 **提前规划** - 提前一天选好明天的早餐
- 🛒 **食材提醒** - 显示所需食材清单
- ⭐ **评分系统** - 给喜欢的菜品打高分，下次更容易抽中
- 🤖 **AI助手** - 遇到烹饪问题随时问AI
- 📧 **通知提醒** - 每天定时发送邮件/WhatsApp提醒

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
python init_db.py
```

### 3. 配置环境变量

复制 `.env.example` 到 `.env` 并填写你的配置：

```bash
cp .env.example .env
```

### 4. 启动应用

```bash
python app.py
```

访问 http://localhost:5000 开始使用！

## 📧 配置通知

### Email 通知

1. 使用 Gmail 需要开启"应用专用密码"
2. 在 `.env` 中配置 SMTP 相关设置

### WhatsApp 通知

1. 注册 [Twilio](https://www.twilio.com/) 账号
2. 获取 WhatsApp Sandbox 或正式号码
3. 在 `.env` 中配置 Twilio 相关设置

## 🤖 配置 AI 助手

1. 获取 [OpenAI API Key](https://platform.openai.com/api-keys)
2. 在 `.env` 中设置 `OPENAI_API_KEY`

## ☁️ 部署到云端

### Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template)

1. Fork 本项目
2. 在 Railway 创建新项目
3. 连接 GitHub 仓库
4. 设置环境变量
5. 部署！

### Render

1. 创建 Render 账号
2. 新建 Web Service
3. 连接 GitHub 仓库
4. 设置环境变量
5. 部署！

## 📁 项目结构

```
Food_platform/
├── app.py              # Flask 主应用
├── init_db.py          # 数据库初始化
├── server.py           # 生产服务器（含定时任务）
├── notifications.py    # 通知服务
├── ai_assistant.py     # AI 烹饪助手
├── templates/
│   └── index.html      # 前端页面
├── breakfast.db        # SQLite 数据库
├── requirements.txt    # Python 依赖
├── Procfile           # 云平台部署配置
└── .env.example       # 环境变量模板
```

## 🍽️ 包含的食谱

系统预置了 12 道健康早餐：

1. 清蒸鸡蛋 (Steamed Egg)
2. 水煮鸡蛋 (Boiled Egg)
3. 烤红薯 (Baked Sweet Potato)
4. 清蒸玉米 (Steamed Corn)
5. 虾仁沙拉 (Shrimp Salad)
6. 香煎鸡胸肉 (Pan-fried Chicken Breast)
7. 牛油果吐司 (Avocado Toast)
8. 燕麦粥 (Oatmeal Porridge)
9. 酸奶水果杯 (Yogurt Fruit Cup)
10. 蔬菜煎蛋 (Vegetable Omelette)
11. 豆浆 (Soy Milk)
12. 小米粥 (Millet Porridge)

## ☁️ 部署与更新 (Deployment)

本项目已针对 **Render** 进行优化。

### 部署到 Render
1. 在 [Render](https://render.com) 上创建新的 Web Service
2. 连接 GitHub 仓库
3. **Run Command**: `python server.py` (系统会自动处理数据库初始化)
4. 环境变量自动检测，无需额外配置

### 🔄 如何更新菜单 (How to Add Recipes)

由于 Render Free Plan 的文件系统是临时的（重启后数据库会重置），**推荐直接修改代码**来永久添加菜谱。

#### 方法：修改 `init_db.py`

1. 打开项目的 `init_db.py` 文件。
2. 找到 `recipes` 列表（通常在文件顶部）。
3. 按照现有格式添加新的菜谱数据：

```python
    {
        'recipe_name': '新菜谱名',
        'recipe_name_en': 'New Recipe Name',
        'category': '类别',
        'difficulty': 1,  # 1-5
        'cooking_time': 15, # 分钟
        'source_article': '', 'source_author': '', 'source_link': '',
        'publish_date': '2024-01-01', 'likes_count': 0,
        'ingredients': [
            {'name': '鸡蛋', 'quantity': 2, 'unit': '个'},
            {'name': '盐', 'quantity': 1, 'unit': 'g'},
        ],
        'instructions': [
            {'step': 1, 'description': '把水烧开...'},
            {'step': 2, 'description': '放入食材...'},
        ],
        'nutrition': {
            'calories': 150, 'protein': 12, 'carbohydrate': 5, 'fat': 10, 'fiber': 0
        }
    },
```

4. **推送到 GitHub**：
   Render 会检测到代码变更，自动重新部署并重建包含新菜谱的数据库。

   ```bash
   git add init_db.py
   git commit -m "feat: add new recipe"
   git push
   ```

## 📝 License

MIT License

---

Made with ❤️ for healthy breakfast lovers
