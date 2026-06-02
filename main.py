import requests
import os
import json
from datetime import datetime, timedelta


def get_keywords():
    """读取自定义关键词"""
    try:
        with open("config/keywords.txt", "r", encoding="utf-8") as f:
            keys = [line.strip() for line in f.readlines()
                    if line.strip() and not line.startswith("#")]
        return keys
    except Exception:
        return ["GitHub", "开源", "AI", "程序员", "嵌入式", "Linux"]


def get_github_trend():
    """获取GitHub热门项目 - 使用官方Search API按stars排序"""
    try:
        # 搜索最近7天创建的高星项目
        since = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        url = f"https://api.github.com/search/repositories"
        params = {
            "q": f"created:>{since}",
            "sort": "stars",
            "order": "desc",
            "per_page": 8
        }
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "news-bot"
        }
        res = requests.get(url, params=params, headers=headers, timeout=15)
        data = res.json()

        if "items" not in data:
            return f"GitHub API 限流，请稍后重试"

        repo_list = []
        for item in data["items"][:8]:
            full_name = item.get("full_name", "")
            desc = item.get("description", "暂无简介") or "暂无简介"
            stars = item.get("stargazers_count", 0)
            html_url = item.get("html_url", "")
            language = item.get("language", "")
            lang_str = f" 语言:{language}" if language else ""
            repo_list.append(
                f"**【{full_name}】**{lang_str}\n"
                f"> {desc[:80]}\n"
                f"⭐ {stars} | [查看]({html_url})"
            )

        return "\n\n".join(repo_list) if repo_list else "暂无热门项目数据"

    except Exception as e:
        return f"GitHub热门项目获取失败: {e}"


def get_hacker_news():
    """获取Hacker News Top 10 科技新闻"""
    try:
        # 获取Top故事ID列表
        top_ids = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=10
        ).json()[:10]

        # 获取每个故事的详情
        stories = []
        for sid in top_ids:
            try:
                item = requests.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                    timeout=5
                ).json()
                title = item.get("title", "")
                url = item.get("url", f"https://news.ycombinator.com/item?id={sid}")
                score = item.get("score", 0)
                if title:
                    stories.append(f"[{title}]({url}) （👍{score}）")
            except Exception:
                continue

        return "\n".join([f"{i+1}. {s}" for i, s in enumerate(stories)])
    except Exception as e:
        return f"Hacker News获取失败: {e}"


def get_bilibili_hot():
    """获取B站热门视频（中文热点风向标）"""
    try:
        url = "https://api.bilibili.com/x/web-interface/popular?ps=8"
        headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.bilibili.com"}
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()

        if data.get("code") != 0:
            return f"B站API异常: {data.get('message')}"

        videos = data.get("data", {}).get("list", [])[:8]
        lines = []
        for i, v in enumerate(videos):
            title = v.get("title", "")
            owner = v.get("owner", {}).get("name", "")
            url = f"https://www.bilibili.com/video/av{v.get('aid')}"
            lines.append(f"{i+1}. [{title}]({url}) - {owner}")

        return "\n".join(lines) if lines else "暂无B站数据"
    except Exception as e:
        return f"B站热点获取失败: {e}"


def get_weibo_hot():
    """获取微博热搜（多个备用接口）"""
    apis = [
        "https://tenapi.cn/v2/weibohot",
        "https://api.vvhan.com/api/hotlist?type=wbHot",
    ]
    for api_url in apis:
        try:
            res = requests.get(api_url, timeout=10,
                               headers={"User-Agent": "Mozilla/5.0"})
            data = res.json()

            # 解析不同接口的返回格式
            items = []
            if "data" in data:
                items = data["data"]
            elif "list" in data:
                items = data["list"]

            if items:
                lines = []
                for i, item in enumerate(items[:10]):
                    title = item.get("title") or item.get("name") or item.get("word", "")
                    hot = item.get("hot") or item.get("hotness", "")
                    hot_str = f" 🔥{hot}" if hot else ""
                    lines.append(f"{i+1}. {title}{hot_str}")
                return "\n".join(lines)
        except Exception:
            continue

    return "微博热搜暂无数据（接口不可用）"


def send_wechat_msg():
    """企业微信推送消息"""
    webhook = os.getenv("WEWORK_WEBHOOK_URL")
    if not webhook:
        print("错误: 未设置 WEWORK_WEBHOOK_URL 环境变量")
        return False

    today = datetime.now().strftime("%Y-%m-%d")
    # 计算星期几
    weekday = ["一", "二", "三", "四", "五", "六", "日"][datetime.now().weekday()]

    content = (
        f"## 🌅 每日技术日报（{today} 星期{weekday}）\n\n"
        f"### 🔥 GitHub 今日热门\n"
        f"{get_github_trend()}\n\n"
        f"---\n\n"
        f"### 📰 Hacker News 科技热文\n"
        f"{get_hacker_news()}\n\n"
        f"---\n\n"
        f"### 🎬 B站热门（今日风向标）\n"
        f"{get_bilibili_hot()}\n\n"
        f"---\n\n"
        f"### 🔍 微博热搜\n"
        f"{get_weibo_hot()}\n\n"
        f"> 🤖 每日 {datetime.now().strftime('%H:%M')} 自动推送 | "
        f"[仓库地址](https://github.com/Mr1314LUO/news-github-trend-push)"
    )

    body = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }
    res = requests.post(webhook, json=body, timeout=15)
    success = res.json().get("errcode") == 0
    if success:
        print("推送成功！")
    else:
        print(f"推送失败: {res.text}")
    return success


if __name__ == "__main__":
    send_wechat_msg()
