# MHTI Enhanced - 多源视频刮削增强版

基于 [xiyan520/MHTI](https://github.com/xiyan520/MHTI) 的增强版，新增多数据源元数据聚合、中文翻译、Bangumi R18 支持和 Emby 通知。

## 增强功能

### 三级数据源串联
刮削按优先级依次尝试三个数据源：

| 优先级 | 数据源 | 特点 |
|--------|--------|------|
| 1 | **TMDB** | 通用影视数据库，覆盖最广 |
| 2 | **Hanime** | Hanime1.me API，精确 video_id 匹配 |
| 3 | **Bangumi** | bgm.tv 番组计划，日文名模糊搜索 + 中文名回退 |

### 中文翻译
- 通过 Google Translate 免费 API 自动将日/英文描述翻译为中文
- 智能检测文本语言，跳过已有中文内容
- 生成的 NFO 文件均为中文

### Bangumi R18 支持
- 使用个人访问令牌 (Personal Access Token) 访问 Bangumi API
- 可获取 R18 (NSFW) 内容的完整摘要、标签、评分
- 支持日文原名 → 中文名 → 拉丁名多级回退搜索

### Emby 入库通知
- 刮削完成后自动通知 Emby 刷新媒体库
- 可在 Emby 设置页面配置冲突检查

## 一键部署

### Docker Compose（推荐）

```bash
# 1. 创建 .env 文件
cat > .env << 'EOF'
MEDIA_DIR=/path/to/your/media
OUTPUT_DIR=/path/to/your/output
BANGUMI_ACCESS_TOKEN=your_token_here
EOF

# 2. 启动
docker compose up -d
```

### Docker Run

```bash
docker run -d \
  --name mhti \
  --restart unless-stopped \
  -p 8000:8000 \
  -v /your/data:/app/data \
  -v /your/media:/media:ro \
  -v /your/output:/output \
  -e BANGUMI_ACCESS_TOKEN=your_token \
  ghcr.io/qingtiann1/mhti-enhanced:latest
```

### 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| `MEDIA_DIR` | 是 | 媒体源目录 |
| `OUTPUT_DIR` | 是 | 刮削输出目录 |
| `BANGUMI_ACCESS_TOKEN` | 否 | Bangumi 个人令牌 (用于 R18 内容) |
| `HANIME_API_URL` | 否 | Hanime-server API 地址 |
| `HTTP_PROXY` | 否 | HTTP 代理地址 |

### 获取 Bangumi 访问令牌

1. 登录 https://bgm.tv
2. 访问 https://next.bgm.tv/demo/access-token
3. 点击「创建个人令牌」，选择 365 天有效期
4. 将令牌设置为环境变量 `BANGUMI_ACCESS_TOKEN`

## 从源码构建

```bash
git clone https://github.com/qingtiann1/mhti-enhanced.git
cd mhti-enhanced
docker build -t mhti-enhanced:latest .
```

## 项目结构

```
server/
├── api/           # FastAPI 路由
├── core/          # 依赖注入容器
├── models/        # Pydantic 数据模型
├── services/      # 业务逻辑
│   ├── bangumi_service.py      # Bangumi API
│   ├── hanime_service.py       # Hanime1.me API
│   ├── emby_service.py         # Emby 集成 & 通知
│   ├── translation_service.py  # Google 翻译
│   ├── scraper_service.py      # 刮削主流程
│   └── ...
└── main.py        # 应用入口
```

## 鸣谢

- [xiyan520/MHTI](https://github.com/xiyan520/MHTI) — 原始 MHTI 项目
- [Bangumi](https://bgm.tv) — 番组计划 API
- [TMDB](https://www.themoviedb.org) — 影视数据库
