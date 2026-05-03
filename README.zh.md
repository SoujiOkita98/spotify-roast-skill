# Spotify Playlist Roast

> 把任意**公开** Spotify 歌单提取成干净的 JSON，再让 AI 用涂鸦风格的页面锐评你的音乐品味——可截图、可分享、一键导出 PNG。中英双语。

🌐 **在线 Demo →** [Life Sucks — 一份 AI 裁决](https://soujiokita98.github.io/spotify-playlist-roast/examples/life-sucks/judgment.html)

English version: [README.md](./README.md)。

---

## 这玩意儿为什么存在

Spotify 什么 API 都有，但都要 OAuth。如果只是「我就想拿歌单里的歌名」这种轻量需求，OAuth 是大炮打蚊子。这个 skill 的做法是：抓 Spotify 公开 embed 页面里的匿名 token，再用它分页调官方 API。**不用登录，不用注册 app，不用 client secret。** 任何公开歌单都能用。

拿到 JSON 之后，事情就有意思了。

## 你能用它做什么

1. **🔥 锐评一份歌单。** 生成涂鸦风格的「裁决页面」（整体氛围、歌曲分类学、最大众/最装/最混乱选择、锐评、情绪曲线），可截图、可一键导出 PNG，中英文一键切换。看 [Live Demo](https://soujiokita98.github.io/spotify-playlist-roast/examples/life-sucks/judgment.html)。
2. **🤖 把你的音乐品味喂给 AI。** 把 JSON 直接丢给 Claude / ChatGPT / 你自己的助手。它就真的知道你听什么了——而不是靠你模糊描述去猜。
3. **🎬 帮你给 vlog 选歌。** 描述场景（"夕阳开车、忧郁但有点希望"），让 AI 从你**真实歌单**里挑曲，而不是凭空想象。
4. **🔍 审计一份歌单。** 找重复、统计语言、看年代分布、对比两份歌单、找异常专辑——所有这些 AI 拿到 JSON 后都能做。

## 快速开始

```bash
git clone https://github.com/SoujiOkita98/spotify-playlist-roast.git
cd spotify-playlist-roast
pip install requests

python3 scripts/extract_spotify_playlist.py \
  'https://open.spotify.com/playlist/0r6ZDp6DoLzGcsEyO5Xfy4' \
  --format json > my-playlist.json
```

输出格式：

```bash
# 纯文本——歌单标题 + 编号 "歌名 — 歌手"
python3 scripts/extract_spotify_playlist.py '<url>' --format text

# JSON——完整曲目元数据，最适合喂给 AI
python3 scripts/extract_spotify_playlist.py '<url>' --format json > playlist.json

# CSV——给表格用
python3 scripts/extract_spotify_playlist.py '<url>' --format csv > playlist.csv
```

## 生成锐评页面

锐评页面是 **AI 生成的**，不是模板。规则写在 [`recipes/judgment-page.md`](./recipes/judgment-page.md)——这是一份给 LLM 看的「设计 + 内容简报」，任何 LLM 都能按它产出和 demo 同款风格的页面。

最简单的用法：

```
> 这是我的 playlist JSON：[粘贴]
> 读一下 recipes/judgment-page.md，给我做一个像 demo 那样的裁决页面
```

或者把这个 skill 装进 [OpenClaw](https://github.com/openclaw) 兼容的 agent 里，`SKILL.md` 已经把 extract + recipe 串好了。

## 把歌单喂给 AI

JSON 就是你交付给 AI 的"成品"。拿到 `playlist.json` 后，你可以问：

- *"这份歌单给你什么感觉？说真话。"*
- *"找出重复的曲目，再告诉我哪些我可以删掉。"*
- *"挑 5 首适合『夕阳开车、忧郁但有希望』的歌。"*
- *"做这种歌单的，会是个什么样的人？"*
- *"对比这份和 [另一份歌单].json，重叠的是哪些？各自独有的是哪些？"*
- *"按情绪给这些歌分组。"*

核心思路就一句：**JSON 是可移植的音乐品味上下文**。把它丢进任何对话，你的 AI 在音乐相关的话题上立刻变成有意义的合作者。

## 抓取原理

1. 从 URL 解析出 playlist ID。
2. 请求 `https://open.spotify.com/embed/playlist/<id>`（轻量 embed 页面，不是 JS 巨多的主页）。
3. 解析 Next.js 的 `__NEXT_DATA__` JSON blob。
4. 读取 `props.pageProps.state.settings.session.accessToken`——一个**短期匿名 embed bearer token**。
5. 用这个 token 调用 `GET https://api.spotify.com/v1/playlists/<id>/tracks`，按 `offset += 100` 分页。
6. 遇到 `429 Retry-After` 老老实实等待。

让这个方法成立的关键是匿名 embed token——它是临时的、不需要登录，Spotify 对所有允许 embed 的公开歌单都开放。

## 限制

- **只支持公开歌单。** 私密歌单、Liked Songs、账户级别的导出都需要真正的 Spotify OAuth。
- **拿不到音频特征。** Tempo / energy / valence / danceability 这些都要 OAuth。我们只能拿到曲目元数据：歌名、歌手、专辑、时长、链接。
- **Embed token 会变。** Spotify 可能改 embed 页面结构或封掉匿名访问，到时候脚本需要维护。
- **情绪匹配是基于歌名的。** 让 AI 按 vibe 选歌时，它是用歌名 + 歌手匹配（对知名艺人意外地好用），不是用真实音频特征。

## 项目结构

```
spotify-playlist-roast/
├── README.md              # 英文说明
├── README.zh.md           # 这份
├── LICENSE                # MIT
├── SKILL.md               # OpenClaw 风格 skill 描述
├── scripts/
│   └── extract_spotify_playlist.py
├── recipes/
│   └── judgment-page.md   # 给 AI 看的「设计 + 内容简报」
└── examples/
    └── life-sucks/
        ├── playlist.json
        └── judgment.html  # 在线 demo（双语 + 一键 PNG 导出）
```

## License

MIT——随便用，别告我就行。

## 致谢

由 [@SoujiOkita98](https://github.com/SoujiOkita98) 与 AI 共同创作。灵感来自一个瞬间：你意识到自己把一份歌单命名为「Life Sucks」，然后里面塞满了 *Three Little Birds*。
