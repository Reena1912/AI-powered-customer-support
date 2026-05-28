# scraper.py
import asyncio
from playwright.async_api import async_playwright
from pathlib import Path
import re

URLS = [
    "https://thepadelcompany.in",
    "https://thepadelcompany.in/coaches",
    "https://thepadelcompany.in/blog",
    "https://thepadelcompany.in/marketplace",
     
]

async def scrape_page(page, url):
    await page.goto(url, wait_until="networkidle")
    # Extract visible text only (skip nav/footer noise if needed)
    text = await page.inner_text("body")
    # Clean up excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text.strip())
    return text

async def main():
    Path("docs").mkdir(exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        for url in URLS:
            print(f"Scraping {url}...")
            text = await scrape_page(page, url)
            slug = url.replace("https://", "").replace("/", "_")
            Path(f"docs/{slug}.md").write_text(
                f"# Source: {url}\n\n{text}",
                encoding="utf-8"
            )
        await browser.close()

asyncio.run(main())