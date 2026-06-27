---
name: open-praxis-youtube-clipper
description: >
  YouTube 视频智能剪辑工具。下载视频和字幕，AI 分析生成精细章节（2-5分钟级别），
  用户选择片段后自动剪辑、翻译字幕为中英双语、烧录字幕到视频，并生成总结文案。
  触发词：视频剪辑、YouTube剪辑、字幕翻译、双语字幕、clip video、"帮我剪这个视频"
---

# YouTube 视频智能剪辑工具

从长视频中智能提取高质量短视频片段，支持双语字幕和总结文案生成。

## 前置依赖

| 工具 | 安装方式 | 用途 |
|------|----------|------|
| `yt-dlp` | `brew install yt-dlp` | 下载视频和字幕 |
| `ffmpeg` (含 libass) | `brew install ffmpeg-full` | 视频剪辑和字幕烧录 |
| `python3` + `pysrt` | `pip install pysrt` | 字幕处理 |

## 工作流程

### 阶段 1: 环境检测

确保所有必需工具已安装：

```bash
yt-dlp --version
ffmpeg -version
ffmpeg -filters 2>&1 | grep subtitles
```

**注意**: 标准 Homebrew FFmpeg 不含 libass，无法烧录字幕。需要 `ffmpeg-full`。
- ffmpeg-full 路径: `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg` (Apple Silicon)

### 阶段 2: 下载视频

1. 获取用户提供的 YouTube URL
2. 下载视频（最高 1080p，mp4 格式）和英文字幕（VTT 格式）

```bash
# 下载视频 + 字幕
yt-dlp -f 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]' \
  --write-sub --write-auto-sub --sub-lang en --sub-format vtt \
  -o '%(id)s.%(ext)s' '<youtube-url>'
```

3. 向用户展示：视频标题、时长、文件大小、下载路径

### 阶段 3: AI 章节分析（核心功能）

这是最关键的步骤——用 AI 分析字幕内容，生成精细章节。

1. 读取完整 VTT 字幕文件
2. 理解内容语义，识别自然的话题切换点
3. 生成 2-5 分钟粒度的章节

每个章节包含：
- **标题**: 精炼的主题概括（10-20 字）
- **时间范围**: 起始和结束时间（MM:SS 或 HH:MM:SS）
- **核心摘要**: 1-2 句话说明内容（50-100 字）
- **关键词**: 3-5 个核心概念词

**章节生成原则**：
- 粒度：每个章节 2-5 分钟
- 完整性：所有视频内容都被覆盖，无遗漏
- 有意义：每个章节是相对独立的话题
- 自然切分：在主题转换点切分，不要机械按时间切

展示格式：
```
📊 分析完成，生成 X 个章节：

1. [00:00 - 03:15] AGI 不是时间点，是指数曲线
   核心: AI 模型能力每 4-12 月翻倍，工程师已用 Claude 写代码
   关键词: AGI、指数增长、Claude Code

2. [03:15 - 06:30] 中国在 AI 上的差距
   ...
```

### 阶段 4: 用户选择

让用户选择：
- 要剪辑的章节（支持多选）
- 是否生成双语字幕（英文 + 中文）
- 是否烧录字幕到视频（硬字幕）
- 是否生成总结文案

### 阶段 5: 剪辑处理

对每个选中的章节执行：

#### 5.1 剪辑视频片段
```bash
ffmpeg -i input.mp4 -ss <start> -to <end> -c copy output_clip.mp4
```

#### 5.2 提取字幕片段
从完整字幕中过滤该时间段，调整时间戳从 00:00:00 开始，转换为 SRT 格式。

#### 5.3 翻译字幕（如果选择）
批量翻译（每批 20 条），翻译策略：
- 保持技术术语准确
- 口语化表达（适合短视频）
- 简洁流畅

#### 5.4 生成双语字幕（如果选择）
合并英文和中文字幕为 SRT 双语格式，英文在上、中文在下。

#### 5.5 烧录字幕到视频（如果选择）
```bash
ffmpeg -i clip.mp4 -vf "subtitles=bilingual.srt:force_style='FontSize=24,MarginV=30'" \
  -c:a copy output_with_subs.mp4
```

**重要**: 使用临时目录解决路径空格问题。

#### 5.6 生成总结文案（如果选择）
基于章节内容生成适合社交媒体的文案（小红书、抖音等）。

### 阶段 6: 输出结果

文件结构：
```
youtube-clips/<日期时间>/
└── <章节标题>/
    ├── <章节标题>_clip.mp4              # 原始剪辑
    ├── <章节标题>_with_subtitles.mp4    # 烧录字幕版本
    ├── <章节标题>_bilingual.srt         # 双语字幕
    └── <章节标题>_summary.md            # 总结文案
```

## 关键技术点

1. **FFmpeg 路径空格**: subtitles 滤镜无法解析含空格路径，使用临时目录解决
2. **批量翻译**: 每批 20 条字幕一起翻译，节省 95% API 调用
3. **章节精细度**: 2-5 分钟粒度，基于语义而非机械时间切分
4. **ffmpeg-full vs ffmpeg**: 标准 ffmpeg 无 libass，无法烧录字幕

## 文件命名规范

- 移除特殊字符（`/ \ : * ? " < > |`）
- 空格替换为下划线
- 限制长度（最多 100 字符）

## Credits

Based on [op7418/Youtube-clipper-skill](https://github.com/op7418/Youtube-clipper-skill).
