#!/usr/bin/env python3
"""
每日资源导航 - 自动生成每日内容脚本
由 GitHub Actions 定时运行，向 data/content.json 追加新条目
"""

import json
import os
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 预置资源池（实际使用时可替换为爬虫/API获取）
TOPICS = [
    ("React Server Components", "前端框架", "React 开发者", 20),
    ("Rust Async Runtime", "系统编程", "后端工程师", 25),
    ("Kubernetes Operator Pattern", "云原生", "平台工程师", 30),
    ("WebAssembly Component Model", "WebAssembly", "全栈开发者", 18),
    ("PostgreSQL Logical Replication", "数据库", "DBA/后端", 15),
    ("eBPF Observability", "Linux 内核", "SRE/平台", 22),
    ("GraphQL Federation", "API 设计", "架构师", 16),
    ("Temporal.io Workflow", "分布式系统", "后端工程师", 24),
    ("Zig Language Basics", "编程语言", "系统程序员", 18),
    ("SQLite Internals", "数据库", "存储引擎爱好者", 20),
    ("HTMX + Go Templates", "全栈开发", "Go Web 开发者", 14),
    ("Bun Native APIs", "运行时工具", "Node.js 开发者", 12),
    ("Tailwind CSS v4 Migration", "CSS 框架", "前端工程师", 10),
    ("Vite Plugin Development", "构建工具", "工具链工程师", 16),
    ("OpenTelemetry Auto-Instrumentation", "可观测性", "SRE/后端", 18),
]

RESOURCE_POOL = []
for topic, category, audience, read_time in TOPICS:
    RESOURCE_POOL.append({
        "title": f"《{topic} 实战指南》—— 从入门到生产级应用",
        "description": f"深度解析 {topic} 核心原理、最佳实践、常见坑与性能调优。包含完整项目代码、架构图解、部署清单。适合 {audience} 系统学习。",
        "category": category,
        "readTime": str(read_time),
        "url": f"https://github.com/trending/{topic.lower().replace(' ', '-').replace('.', '')}",
    })

# 额外的单条资源模板
SINGLE_RESOURCES = [
    {
        "title": "GitHub Trending 今日榜单：{date} 最热开源项目",
        "description": "GitHub 官方 Trending 页面今日榜单精选：{count} 个最值得关注的新项目，涵盖 AI、基础设施、开发工具、前端框架等方向。附带 Star 增长趋势分析。",
        "category": "技术趋势",
        "readTime": 8,
        "url": "https://github.com/trending",
    },
    {
        "title": "《{tool} 进阶技巧》—— 提升 {percent}% 开发效率的 {count} 个隐藏功能",
        "description": "挖掘 {tool} 官方文档很少提及的高级用法：{features}。实测可减少 {percent}% 样板代码、加速调试循环。配合示例配置文件直接落地。",
        "category": "效率工具",
        "readTime": 12,
        "url": "https://github.com/{tool_lower}/{tool_lower}",
    }
]

TOOLS_DATA = [
    ("VS Code", 40, 12, "多光标重构、任务自动化、远程隧道、内置终端分屏"),
    ("Git", 35, 10, "工作树分离、bisect 自动化、reflog 恢复、commit-graph 加速"),
    ("Docker", 30, 8, "BuildKit 缓存挂载、多阶段构建优化、Compose Watch、Buildx 多平台"),
    ("Postman", 25, 7, "预请求脚本、动态变量、集合运行器、Mock Server 自动生成"),
    ("Chrome DevTools", 45, 15, "性能面板火焰图、内存堆快照对比、网络条件模拟、Lighthouse CI"),
]

for tool, percent, count, features in TOOLS_DATA:
    SINGLE_RESOURCES.append({
        "title": f"《{tool} 进阶技巧》—— 提升 {{percent}}% 开发效率的 {{count}} 个隐藏功能",
        "description": f"挖掘 {tool} 官方文档很少提及的高级用法：{{features}}。实测可减少 {{percent}}% 样板代码、加速调试循环。配合示例配置文件直接落地。",
        "category": "效率工具",
        "readTime": 12,
        "url": f"https://github.com/{tool.lower().replace(' ', '-')}/{tool.lower().replace(' ', '-')}",
    })

CATEGORIES = [
    "AI 编程工具", "前端框架", "后端架构", "数据库", "DevOps",
    "云原生", "系统设计", "编程语言", "Web 性能", "效率工具",
    "工程文化", "安全攻防", "可观测性", "WebAssembly", "边缘计算"
]

def load_existing_content(json_path: Path) -> dict:
    """加载现有内容"""
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"generatedAt": "", "items": []}

def get_latest_date(items: list) -> str:
    """获取最新日期"""
    if not items:
        return "2025-01-01"
    dates = [item["date"] for item in items]
    return max(dates)

def generate_next_date(latest_date: str) -> str:
    """生成下一个日期"""
    dt = datetime.strptime(latest_date, "%Y-%m-%d")
    next_dt = dt + timedelta(days=1)
    return next_dt.strftime("%Y-%m-%d")

def pick_random_resource(date_str: str) -> dict:
    """从资源池随机挑选并填充模板"""
    template = random.choice(RESOURCE_POOL)
    topic = random.choice([t[0] for t in TOPICS])
    category = random.choice(CATEGORIES)
    read_time = random.randint(10, 30)

    return {
        "date": date_str,
        "title": template["title"].format(topic=topic),
        "description": template["description"].format(
            topic=topic,
            audience="相关开发者",
            category=category,
            read_time=str(read_time)
        ),
        "category": category,
        "readTime": read_time,
        "url": template["url"].format(topic_lower=topic.lower().replace(" ", "-").replace(".", "")),
    }

def maybe_add_trending(date_str: str, items: list) -> dict | None:
    """一定概率添加 Trending 类内容"""
    if random.random() < 0.3:  # 30% 概率
        template = random.choice(SINGLE_RESOURCES)
        if "Trending" in template["title"]:
            return {
                "date": date_str,
                "title": template["title"].format(date=date_str),
                "description": template["description"].format(count=random.randint(8, 15)),
                "category": template["category"],
                "readTime": template["readTime"],
                "url": template["url"],
            }
        else:
            tool = random.choice(["VS Code", "Git", "Docker", "Postman", "Chrome DevTools"])
            return {
                "date": date_str,
                "title": template["title"].format(tool=tool, percent=random.randint(20, 50), count=random.randint(7, 15)),
                "description": template["description"].format(
                    tool=tool,
                    percent=random.randint(20, 50),
                    count=random.randint(7, 15),
                    features="、".join(random.sample([
                        "多光标重构", "任务自动化", "远程隧道", "内置终端分屏",
                        "工作树分离", "bisect 自动化", "reflog 恢复", "commit-graph 加速",
                        "BuildKit 缓存挂载", "多阶段构建优化", "Compose Watch", "Buildx 多平台",
                        "预请求脚本", "动态变量", "集合运行器", "Mock Server 自动生成",
                        "性能面板火焰图", "内存堆快照对比", "网络条件模拟", "Lighthouse CI"
                    ], random.randint(4, 8)))
                ),
                "category": template["category"],
                "readTime": template["readTime"],
                "url": template["url"].format(tool_lower=tool.lower().replace(" ", "-")),
            }
    return None

def main():
    json_path = Path("data/content.json")
    data = load_existing_content(json_path)

    latest_date = get_latest_date(data.get("items", []))
    next_date = generate_next_date(latest_date)
    today = datetime.utcnow().strftime("%Y-%m-%d")

    # 如果已经是最新日期，不重复生成
    if next_date > today:
        print(f"已是最新内容（最新：{latest_date}，今天：{today}），无需生成")
        return 0

    # 生成新条目
    new_item = pick_random_resource(next_date)
    trending_item = maybe_add_trending(next_date, data.get("items", []))

    # 如果生成了 trending，今天放 trending，明天放常规
    items_to_add = []
    if trending_item:
        items_to_add.append(trending_item)
        # 常规内容放到后一天
        day_after = (datetime.strptime(next_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        if day_after <= today:
            regular_item = pick_random_resource(day_after)
            items_to_add.append(regular_item)
    else:
        items_to_add.append(new_item)

    # 追加到列表开头（最新在前）
    for item in reversed(items_to_add):
        data["items"].insert(0, item)

    # 更新生成时间
    data["generatedAt"] = datetime.utcnow().isoformat() + "Z"

    # 写回文件
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"已生成 {len(items_to_add)} 条新内容，日期：{next_date}")
    for item in items_to_add:
        print(f"  - {item['title']} ({item['category']})")

    return 0

if __name__ == "__main__":
    sys.exit(main())