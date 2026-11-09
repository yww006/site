#!/usr/bin/env python3
"""
Daily Resource Navigation - Auto generate daily content script
Run by GitHub Actions on schedule, append new entries to data/content.json
and generate daily archive pages.
"""

import json
import random
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

# Predefined resource pool: each topic paired with real accessible URL
TOPICS = [
    ("React Server Components", "前端框架", "React 开发者", 20,
     "https://react.dev/learn/server-components"),
    ("Rust Async Runtime", "系统编程", "后端工程师", 25,
     "https://rust-lang.github.io/async-book/"),
    ("Kubernetes Operator Pattern", "云原生", "平台工程师", 30,
     "https://kubernetes.io/docs/concepts/extend-kubernetes/operator/"),
    ("WebAssembly Component Model", "WebAssembly", "全栈开发者", 18,
     "https://github.com/WebAssembly/component-model"),
    ("PostgreSQL Logical Replication", "数据库", "DBA/后端", 15,
     "https://www.postgresql.org/docs/current/logical-replication.html"),
    ("eBPF Observability", "Linux 内核", "SRE/平台", 22,
     "https://ebpf.io/what-is-ebpf/"),
    ("GraphQL Federation", "API 设计", "架构师", 16,
     "https://www.apollographql.com/docs/federation/"),
    ("Temporal.io Workflow", "分布式系统", "后端工程师", 24,
     "https://docs.temporal.io/workflows"),
    ("Zig Language Basics", "编程语言", "系统程序员", 18,
     "https://ziglang.org/learn/"),
    ("SQLite Internals", "数据库", "存储引擎爱好者", 20,
     "https://www.sqlite.org/arch.html"),
    ("HTMX + Go Templates", "全栈开发", "Go Web 开发者", 14,
     "https://htmx.org/essays/"),
    ("Bun Native APIs", "运行时工具", "Node.js 开发者", 12,
     "https://bun.sh/docs/api/"),
    ("Tailwind CSS v4 Migration", "CSS 框架", "前端工程师", 10,
     "https://tailwindcss.com/docs/upgrade-guide"),
    ("Vite Plugin Development", "构建工具", "工具链工程师", 16,
     "https://vite.dev/guide/api-plugin.html"),
    ("OpenTelemetry Auto-Instrumentation", "可观测性", "SRE/后端", 18,
     "https://opentelemetry.io/docs/zero-code/"),
]

RESOURCE_POOL = []
for topic, category, audience, read_time, url in TOPICS:
    RESOURCE_POOL.append({
        "title": f"《{topic} 实战指南》—— 从入门到生产级应用",
        "description": f"深度解析 {topic} 核心原理、最佳实践、常见坑与性能调优。包含完整项目代码、架构图解、部署清单。适合 {audience} 系统学习。",
        "category": category,
        "readTime": str(read_time),
        "url": url,
    })

# 额外的单条资源模板（使用真实 URL）
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
        "url": "",
    }
]

# 工具名到真实文档/官网 URL 的映射
TOOL_URLS = {
    "VS Code": "https://code.visualstudio.com/docs",
    "Git": "https://git-scm.com/doc",
    "Docker": "https://docs.docker.com/",
    "Postman": "https://learning.postman.com/docs/",
    "Chrome DevTools": "https://developer.chrome.com/docs/devtools/",
}

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
        "url": TOOL_URLS.get(tool, f"https://github.com/{tool.lower().replace(' ', '-')}/{tool.lower().replace(' ', '-')}"),
    })

CATEGORIES = [
    "AI 编程工具", "前端框架", "后端架构", "数据库", "DevOps",
    "云原生", "系统设计", "编程语言", "Web 性能", "效率工具",
    "工程文化", "安全攻防", "可观测性", "WebAssembly", "边缘计算"
]

def load_existing_content(json_path: Path) -> dict:
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"generatedAt": "", "items": []}

def get_latest_date(items: list) -> str:
    if not items:
        return "2025-01-01"
    dates = [item["date"] for item in items]
    return max(dates)

def generate_next_date(latest_date: str) -> str:
    dt = datetime.strptime(latest_date, "%Y-%m-%d")
    next_dt = dt + timedelta(days=1)
    return next_dt.strftime("%Y-%m-%d")

def pick_random_resource(date_str: str) -> dict:
    entry = random.choice(RESOURCE_POOL)
    return {
        "date": date_str,
        "title": entry["title"],
        "description": entry["description"],
        "category": entry["category"],
        "readTime": int(entry["readTime"]),
        "url": entry["url"],
    }

def maybe_add_trending(date_str: str, items: list) -> dict | None:
    if random.random() < 0.3:
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
                "url": TOOL_URLS.get(tool, f"https://github.com/{tool.lower().replace(' ', '-')}/{tool.lower().replace(' ', '-')}"),
            }
    return None

def escape_html(text: str) -> str:
    return (text
        .replace("&", "&")
        .replace("<", "<")
        .replace(">", ">")
        .replace('"', "&")
        .replace("'", "'"))

def format_date_display(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    weekday_map = {
        "Monday": "星期一", "Tuesday": "星期二", "Wednesday": "星期三",
        "Thursday": "星期四", "Friday": "星期五", "Saturday": "星期六", "Sunday": "星期日"
    }
    return dt.strftime("%Y年%m月%d日 ") + weekday_map[dt.strftime("%A")]

def format_month_label(month: str) -> str:
    dt = datetime(2000, int(month), 1)
    return dt.strftime("%B")

def format_day_label(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%b %d %a")

def format_day_label_chinese(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    weekday_map = {
        "Monday": "周一", "Tuesday": "周二", "Wednesday": "周三",
        "Thursday": "周四", "Friday": "周五", "Saturday": "周六", "Sunday": "周日"
    }
    return dt.strftime("%m月%d日 ") + weekday_map[dt.strftime("%A")]

def generate_day_page(item: dict, template_path: Path, output_dir: Path) -> Path:
    date_str = item["date"]
    year, month, day = date_str.split('-')

    day_dir = output_dir / year / month / day
    day_dir.mkdir(parents=True, exist_ok=True)

    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    page_title = f"{item['title']} | 每日资源导航"
    page_description = item['description']
    day_badge = format_date_display(date_str)

    html = template.replace(
        '<title id="pageTitle">每日资源导航 | Daily Resource Navigation</title>',
        f'<title id="pageTitle">{escape_html(page_title)}</title>'
    )
    html = html.replace(
        '<meta name="description" id="pageDescription" content="每天精选一个优质资源：技术文章、开源工具、设计灵感、学习教程、效率神器">',
        f'<meta name="description" id="pageDescription" content="{escape_html(page_description)}">'
    )
    html = html.replace(
        '<div class="day-badge" id="dayBadge">历史精选</div>',
        f'<div class="day-badge" id="dayBadge">{day_badge}</div>'
    )
    html = html.replace(
        '<h1 class="day-title" id="dayTitle">加载中...</h1>',
        f'<h1 class="day-title" id="dayTitle">{escape_html(item["title"])}</h1>'
    )
    html = html.replace(
        '<p class="day-desc" id="dayDesc"></p>',
        f'<p class="day-desc" id="dayDesc">{escape_html(item["description"])}</p>'
    )
    html = html.replace(
        '<span class="day-category" id="dayCategory"></span>',
        f'<span class="day-category" id="dayCategory">{escape_html(item["category"])}</span>'
    )
    html = html.replace(
        '<span class="day-read-time" id="dayReadTime"></span>',
        f'<span class="day-read-time" id="dayReadTime">{item["readTime"]} 分钟阅读</span>'
    )
    html = html.replace(
        '<a href="#" class="day-cta" id="dayCta" target="_blank" rel="noopener noreferrer">',
        f'<a href="{escape_html(item["url"])}" class="day-cta" id="dayCta" target="_blank" rel="noopener noreferrer">'
    )

    # Breadcrumb
    breadcrumb = (
        '      <a href="../../">首页</a>\n'
        '      <svg class="breadcrumb-sep" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>\n'
        '      <a href="../../archive/">历史归档</a>\n'
        '      <svg class="breadcrumb-sep" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>\n'
        f'      <a href="../{year}/">{year}年</a>\n'
        '      <svg class="breadcrumb-sep" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>\n'
        f'      <a href="../{year}/{month}/">{int(month)}月</a>\n'
        '      <svg class="breadcrumb-sep" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>\n'
        f'      <span class="breadcrumb-current">{format_day_label_chinese(date_str)}</span>'
    )
    html = html.replace(
        '<nav class="breadcrumb" id="breadcrumb" aria-label="面包屑导航"></nav>',
        f'<nav class="breadcrumb" id="breadcrumb" aria-label="面包屑导航">{breadcrumb}</nav>'
    )

    output_path = day_dir / "index.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return output_path

def generate_month_index_pages(items: list, archive_dir: Path):
    """Generate month index pages (archive/YYYY/MM/index.html)"""
    by_year_month = defaultdict(list)
    for item in items:
        year, month = item['date'].split('-')[:2]
        by_year_month[(year, month)].append(item)

    for (year, month), month_items in by_year_month.items():
        month_dir = archive_dir / year / month
        month_dir.mkdir(parents=True, exist_ok=True)

        month_items_sorted = sorted(month_items, key=lambda x: x['date'], reverse=True)

        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{year}年{int(month)}月 归档 | 每日资源导航</title>
  <meta name="description" content="{year}年{int(month)}月 每日资源导航历史归档">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../../assets/style.css">
</head>
<body>
  <div class="bg-layer" aria-hidden="true">
    <div class="bg-image" id="bgImage"></div>
    <div class="bg-overlay"></div>
    <div class="bg-particles" id="bgParticles"></div>
  </div>
  <header class="header">
    <div class="container">
      <div class="header-content">
        <div class="logo">
          <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 6v6l4 2"/>
          </svg>
          <span class="logo-text">每日资源导航</span>
        </div>
        <nav class="header-nav">
          <a href="../../../" class="nav-link">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
            返回首页
          </a>
          <a href="../../../archive/" class="nav-link">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
            历史
          </a>
        </nav>
        <div class="header-meta">
          <span class="date" id="currentDate"></span>
        </div>
      </div>
    </div>
  </header>
  <main class="main">
    <div class="container">
      <nav class="breadcrumb" aria-label="面包屑导航">
        <a href="../../../">首页</a>
        <svg class="breadcrumb-sep" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
        <a href="../../../archive/">历史归档</a>
        <svg class="breadcrumb-sep" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
        <a href="../../{year}/">{year}年</a>
        <svg class="breadcrumb-sep" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
        <span class="breadcrumb-current">{int(month)}月</span>
      </nav>
      <section class="archive-hero">
        <h1 class="archive-title">{year}年{int(month)}月 归档</h1>
        <p class="archive-subtitle">本月共 {len(month_items)} 篇精选内容</p>
      </section>
      <section class="archive-list">
'''

        for item in month_items_sorted:
            day_label = format_day_label_chinese(item['date'])
            html += f'''        <article class="archive-day">
          <a href="../{item['date'].split('-')[2]}/" class="archive-day-link">
            <span class="archive-day-date">{day_label}</span>
            <span class="archive-day-title">{item['title']}</span>
            <span class="archive-day-category">{item['category']}</span>
            <svg class="archive-day-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </a>
        </article>
'''

        html += f'''      </section>
    </div>
  </main>
  <footer class="footer">
    <div class="container">
      <p>每日更新 · 数据来源：<a href="https://github.com/yww006/site" target="_blank">GitHub</a> · 部署：GitHub Pages</p>
    </div>
  </footer>
  <script src="../../../assets/script.js"></script>
</body>
</html>'''

        output_path = month_dir / "index.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  Generated month index: {output_path}")

def generate_year_index_pages(items: list, archive_dir: Path):
    """Generate year index pages (archive/YYYY/index.html)"""
    by_year = defaultdict(list)
    for item in items:
        year = item['date'].split('-')[0]
        by_year[year].append(item)

    for year, year_items in by_year.items():
        year_dir = archive_dir / year
        year_dir.mkdir(parents=True, exist_ok=True)

        month_counts = defaultdict(int)
        for item in year_items:
            month = item['date'].split('-')[1]
            month_counts[month] += 1

        months_sorted = sorted(month_counts.keys(), reverse=True)

        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{year}年 归档 | 每日资源导航</title>
  <meta name="description" content="{year}年 每日资源导航历史归档">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../assets/style.css">
</head>
<body>
  <div class="bg-layer" aria-hidden="true">
    <div class="bg-image" id="bgImage"></div>
    <div class="bg-overlay"></div>
    <div class="bg-particles" id="bgParticles"></div>
  </div>
  <header class="header">
    <div class="container">
      <div class="header-content">
        <div class="logo">
          <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 6v6l4 2"/>
          </svg>
          <span class="logo-text">每日资源导航</span>
        </div>
        <nav class="header-nav">
          <a href="../" class="nav-link">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
            返回首页
          </a>
          <a href="../archive/" class="nav-link">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
            历史
          </a>
        </nav>
        <div class="header-meta">
          <span class="date" id="currentDate"></span>
        </div>
      </div>
    </div>
  </header>
  <main class="main">
    <div class="container">
      <nav class="breadcrumb" aria-label="面包屑导航">
        <a href="../">首页</a>
        <svg class="breadcrumb-sep" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
        <a href="../archive/">历史归档</a>
        <svg class="breadcrumb-sep" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
        <span class="breadcrumb-current">{year}年</span>
      </nav>
      <section class="archive-hero">
        <h1 class="archive-title">{year}年 归档</h1>
        <p class="archive-subtitle">全年共 {len(year_items)} 篇精选内容，{len(month_counts)} 个月</p>
      </section>
      <section class="archive-year-months">
'''

        for month in months_sorted:
            count = month_counts[month]
            html += f'''        <a href="{month}/" class="archive-month-card">
          <span class="archive-month-card-label">{int(month)}月</span>
          <span class="archive-month-card-count">{count} 篇</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </a>
'''

        html += f'''      </section>
    </div>
  </main>
  <footer class="footer">
    <div class="container">
      <p>每日更新 · 数据来源：<a href="https://github.com/yww006/site" target="_blank">GitHub</a> · 部署：GitHub Pages</p>
    </div>
  </footer>
  <script src="../../assets/script.js"></script>
</body>
</html>'''

        output_path = year_dir / "index.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  Generated year index: {output_path}")

def generate_all_archive_pages(items: list, archive_dir: Path):
    """Generate all archive pages: year, month, day"""
    print("Generating archive index pages...")
    generate_year_index_pages(items, archive_dir)
    generate_month_index_pages(items, archive_dir)
    print("Archive index pages generated")

def generate_all_day_pages(items: list, template_path: Path, archive_dir: Path):
    print(f"Generating {len(items)} day detail pages...")
    for item in items:
        try:
            generate_day_page(item, template_path, archive_dir)
        except Exception as e:
            print(f"  Warning: Failed to generate {item['date']}: {e}")
    print("Day detail pages generated")
    
    # Generate redirect pages at root level: /YYYY-MM-DD/ -> /archive/YYYY/MM/DD/
    print("Generating redirect pages...")
    generate_redirect_pages(items)
    print("Redirect pages generated")

def generate_redirect_pages(items: list):
    """Generate redirect pages at root level and site/ subdirectory: /YYYY-MM-DD/ -> /archive/YYYY/MM/DD/"""
    for item in items:
        date_str = item["date"]
        year, month, day = date_str.split('-')
        
        # Root level redirect (for direct access)
        dir_name = f"{year}-{month}-{day}"
        redirect_dir = Path(dir_name)
        redirect_dir.mkdir(parents=True, exist_ok=True)
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=/site/archive/{year}/{month}/{day}/">
  <link rel="canonical" href="/site/archive/{year}/{month}/{day}/">
  <title>重定向中...</title>
</head>
<body>
  <p>正在跳转到 <a href="/site/archive/{year}/{month}/{day}/">{date_str}</a>...</p>
  <script>window.location.href = "/site/archive/{year}/{month}/{day}/";</script>
</body>
</html>'''
        
        output_path = redirect_dir / "index.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Also create under site/ subdirectory for GitHub Pages project site
        site_redirect_dir = Path("site") / dir_name
        site_redirect_dir.mkdir(parents=True, exist_ok=True)
        with open(site_redirect_dir / "index.html", 'w', encoding='utf-8') as f:
            f.write(html)
    
    print(f"  Generated {len(items)} redirect pages at root and site/ level")

def main():
    json_path = Path("data/content.json")
    data = load_existing_content(json_path)

    latest_date = get_latest_date(data.get("items", []))
    next_date = generate_next_date(latest_date)
    today = datetime.utcnow().strftime("%Y-%m-%d")

    if next_date > today:
        print(f"Already up to date (latest: {latest_date}, today: {today}), no generation needed")
        return 0

    new_item = pick_random_resource(next_date)
    trending_item = maybe_add_trending(next_date, data.get("items", []))

    items_to_add = []
    if trending_item:
        items_to_add.append(trending_item)
        day_after = (datetime.strptime(next_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        if day_after <= today:
            regular_item = pick_random_resource(day_after)
            items_to_add.append(regular_item)
    else:
        items_to_add.append(new_item)

    for item in reversed(items_to_add):
        data["items"].insert(0, item)

    data["generatedAt"] = datetime.utcnow().isoformat() + "Z"

    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(items_to_add)} new entries, date: {next_date}")
    for item in items_to_add:
        print(f"  - {item['title']} ({item['category']}) -> {item['url']}")

    template_path = Path("archive/day-template.html")
    archive_dir = Path("archive")
    if template_path.exists():
        generate_all_day_pages(data["items"], template_path, archive_dir)
        generate_all_archive_pages(data["items"], archive_dir)
    else:
        print(f"Warning: Template file not found: {template_path}")

    return 0

if __name__ == "__main__":
    sys.exit(main())