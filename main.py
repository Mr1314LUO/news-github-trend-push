import requests
import os
from datetime import datetime


def get_keywords():
    """读取自定义关键词"""
    try:
        with open("config/keywords.txt", "r", encoding="utf-8") as f:
            keys = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("#")]
        return keys
    except Exception:
        return ["GitHub", "开源", "AI", "程序员", "嵌入式", "Linux"]


def filter_content(text):
    """过滤无关内容"""
    filter_words = ["娱乐", "明星", "八卦", "广告", "综艺"]
    for word in filter_words:
        if word in text:
            return True
    return False


def get_github_trend():
    """获取GitHub今日热门项目"""
    url = "https://github-trending-api.now.sh/repositories?language=&since=daily"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()[:8]
        repo_list = []
        for item in data:
            name = item.get("name", "")
            author = item.get("author", "")
            desc = item.get("description", "暂无简介")
            stars = item.get("stars", 0)
            repo_url = item.get("url", "")
            repo_list.append(f"【{author}/{name}】\n简介：{desc}\nStar数：{stars}\n地址：{repo_url}")
        return "\n\n".join(repo_list)
    except Exception as e:
        return f"GitHub热门项目获取失败: {e}"


def get_tech_news():
    """获取科技热点新闻"""
    news_list = []
    try:
        url = "https://36kr.com/backend/api/news/latest"
        res = requests.get(url, timeout=10)
        data = res.json().get("data", [])[:10]
        for item in data:
            title = item.get("title", "")
            if title and not filter_content(title):
                news_list.append(title)
        return "\n".join([f"{i+1}. {item}" for i, item in enumerate(news_list)])
    except Exception as e:
        return f"科技热点获取失败: {e}"


def send_wechat_msg():
    """企业微信推送消息"""
    webhook = os.getenv("WEWORK_WEBHOOK_URL")
    if not webhook:
        print("错误: 未设置 WEWORK_WEBHOOK_URL 环境变量")
        return False

    today = datetime.now().strftime('%Y-%m-%d')
    content = (
        f"### 🌅 每日技术日报（{today}）\n\n"
        f"#### 🔥 今日科技热点\n{get_tech_news()}\n\n"
        f"#### ⭐ GitHub今日热门项目\n{get_github_trend()}"
    )

    body = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }
    res = requests.post(webhook, json=body)
    success = res.json().get("errcode") == 0
    if success:
        print("推送成功！")
    else:
        print(f"推送失败: {res.text}")
    return success


if __name__ == "__main__":
    send_wechat_msg()
