# 每日热点&GitHub项目微信推送

纯云端免费部署，通过 GitHub Actions 定时抓取全网热点和 GitHub Trending 项目，推送至企业微信。

## 功能
- 🔥 每日科技热点（36kr）
- ⭐ GitHub Trending 热门项目
- 📱 企业微信推送（个人微信同步接收）
- 🏷️ 自定义关键词过滤

## 使用方式
1. 在 GitHub 仓库 Settings → Secrets → Actions 中添加 `WEWORK_WEBHOOK_URL`
2. 启用 Actions 工作流
3. 每日北京时间 7:30 自动推送

## 手动触发
进入 Actions → 选择工作流 → Run workflow
