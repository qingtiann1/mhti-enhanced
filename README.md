# MHTI Enhanced - 里番刮削增强版

基于 [xiyan520/MHTI](https://github.com/xiyan520/MHTI) 的增强版，新增多数据源元数据聚合、中文翻译和 Bangumi R18 支持。

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
- 支持日文原名 (kana) → 中文名 → 拉丁名多级回退搜索

## 部署方式

### Docker Compose

```yaml
mhti:
  image: xiyan520/mhti:latest
  environment:
    - BANGUMI_ACCESS_TOKEN=<your-token>
    - HANIME_API_URL=http://host.docker.internal:8000
```

### 获取 Bangumi 访问令牌

1. 登录 https://bgm.tv
2. 访问 https://next.bgm.tv/demo/access-token
3. 点击「创建个人令牌」，选择 365 天有效期
4. 将令牌设置为环境变量 `BANGUMI_ACCESS_TOKEN`

## 项目结构

```
server/
├── services/
│   ├── bangumi_service.py    # Bangumi (bgm.tv) API 服务
│   ├── hanime_service.py     # Hanime1.me API 服务
│   ├── translation_service.py # Google 翻译服务
│   ├── scraper_service.py    # 刮削主流程
│   └── ...
├── models/
│   └── bangumi.py            # Bangumi 数据模型
└── core/
    └── container.py          # 依赖注入容器
```

## 鸣谢

- [xiyan520/MHTI](https://github.com/xiyan520/MHTI) — 原始 MHTI 项目
- [Bangumi](https://bgm.tv) — 番组计划 API
- [TMDB](https://www.themoviedb.org) — 影视数据库
