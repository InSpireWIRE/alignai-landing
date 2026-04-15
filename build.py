"""
AlignAI Landing Page Builder
Pulls live data from Supabase → renders index.html via Jinja2 template.
Run locally or via GitHub Actions on a schedule.
"""

import os
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

# ---------------------------------------------------------------------------
# 1. Connect to Supabase and pull live data
# ---------------------------------------------------------------------------

def fetch_supabase_data():
    """Pull stats, top tools, and categories from Supabase."""

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        print("⚠ No Supabase credentials found — using fallback data.")
        return get_fallback_data()

    try:
        from supabase import create_client
        sb = create_client(url, key)

        # Total published tools
        tools_resp = sb.table("tools").select("id", count="exact").eq("status", "published").execute()
        total_tools = tools_resp.count or 0

        # Total reviews
        reviews_resp = sb.table("validation_comments").select("id", count="exact").execute()
        total_reviews = reviews_resp.count or 0

        # Category count
        cats_resp = sb.table("category_keywords").select("category").execute()
        categories = list({row["category"] for row in cats_resp.data}) if cats_resp.data else []
        total_categories = len(categories)

        # Top-scored published tools (top 6 by critics_score)
        top_resp = (
            sb.table("tools")
            .select("name, slug, category, critics_score, verdict")
            .eq("status", "published")
            .not_.is_("critics_score", "null")
            .order("critics_score", desc=True)
            .limit(6)
            .execute()
        )
        top_tools = top_resp.data if top_resp.data else []

        # Category stats — tool counts per category (top 8)
        cat_stats_resp = (
            sb.table("tools")
            .select("category")
            .eq("status", "published")
            .execute()
        )
        cat_counts = {}
        if cat_stats_resp.data:
            for row in cat_stats_resp.data:
                cat = row.get("category")
                if cat:
                    cat_counts[cat] = cat_counts.get(cat, 0) + 1
        # Sort by count descending, take top 8
        top_categories = sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:8]

        return {
            "total_tools": f"{total_tools:,}",
            "total_reviews": f"{total_reviews:,}",
            "total_categories": total_categories,
            "top_tools": top_tools[:6],
            "top_categories": top_categories,
            "build_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "supabase_url": url,
            "supabase_anon_key": key,
        }

    except Exception as e:
        print(f"⚠ Supabase error: {e} — using fallback data.")
        return get_fallback_data()


def get_fallback_data():
    """Fallback data for local dev without Supabase credentials."""
    return {
        "total_tools": "2,427",
        "total_reviews": "7,411",
        "total_categories": 26,
        "top_tools": [
            {"name": "Notion", "slug": "notion", "category": "Project Management", "critics_score": 87, "verdict": "WORKED"},
            {"name": "Canva", "slug": "canva", "category": "Design & Creative", "critics_score": 84, "verdict": "WORKED"},
            {"name": "Zapier", "slug": "zapier", "category": "Automation", "critics_score": 81, "verdict": "WORKED"},
            {"name": "Grammarly", "slug": "grammarly", "category": "Writing & Content", "critics_score": 79, "verdict": "WORKED"},
            {"name": "HubSpot", "slug": "hubspot", "category": "CRM & Sales", "critics_score": 76, "verdict": "WORKED"},
            {"name": "Descript", "slug": "descript", "category": "Voice & Audio", "critics_score": 73, "verdict": "WORKED"},
        ],
        "top_categories": [
            ("Writing & Content", 142),
            ("Automation", 98),
            ("Design & Creative", 87),
            ("Email & Outreach", 76),
            ("Customer Support", 64),
            ("Payments & Invoicing", 51),
            ("CRM & Sales", 45),
            ("Voice & Audio", 10),
        ],
        "build_date": datetime.utcnow().strftime("%Y-%m-%d"),
        "supabase_url": os.environ.get("SUPABASE_URL", "https://your-project.supabase.co"),
        "supabase_anon_key": os.environ.get("SUPABASE_KEY", "your-anon-key"),
    }


# ---------------------------------------------------------------------------
# 2. Render the template
# ---------------------------------------------------------------------------

SITE_URL = "https://alignai.business"


def build_sitemap():
    """Generate dist/sitemap.xml with homepage + any known routes."""
    now_iso = datetime.utcnow().strftime("%Y-%m-%d")
    urls = [
        (SITE_URL + "/", now_iso, "daily", "1.0"),
        # Anchors within homepage also discoverable via these fragments;
        # add real routes here as the site grows (e.g. /about, /methodology).
    ]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for loc, lastmod, changefreq, priority in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <changefreq>{changefreq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    with open("dist/sitemap.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"   + dist/sitemap.xml ({len(urls)} url)")


def build_robots():
    """Generate dist/robots.txt with an explicit AI crawler allow-list."""
    content = f"""# AlignAI
# Allow all well-behaved crawlers including AI answer engines.

User-agent: *
Allow: /

# AI answer engines (explicit allow-listing for visibility)
User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Perplexity-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: CCBot
Allow: /

User-agent: Applebot
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: Bingbot
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""
    with open("dist/robots.txt", "w", encoding="utf-8") as f:
        f.write(content)
    print("   + dist/robots.txt")


def build():
    data = fetch_supabase_data()

    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("template.html")

    html = template.render(**data)

    os.makedirs("dist", exist_ok=True)
    with open("dist/index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Built dist/index.html — {data['total_tools']} tools, {data['total_reviews']} reviews, {data['total_categories']} categories")
    print(f"   Top tools: {', '.join(t['name'] for t in data['top_tools'])}")
    print(f"   Build date: {data['build_date']}")

    # SEO / AEO infrastructure
    build_sitemap()
    build_robots()


if __name__ == "__main__":
    build()
