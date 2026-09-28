import asyncio
from urllib.parse import urlparse
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError

from config import config
from utils import clean_html, truncate_text


class ScrapingError(Exception):
    pass


class InvalidURLError(ScrapingError):
    pass


class PageLoadError(ScrapingError):
    pass


class BrowserError(ScrapingError):
    pass


def validate_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False


async def scrape_webpage(url: str) -> str:
    if not validate_url(url):
        raise InvalidURLError(f"Invalid URL: {url}")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                page.set_default_timeout(config.playwright_timeout)

                await page.goto(url, wait_until="networkidle", timeout=config.playwright_timeout)

                await page.wait_for_load_state("domcontentloaded", timeout=config.playwright_timeout)

                await asyncio.sleep(1)

                html = await page.content()

                if not html or len(html.strip()) < 100:
                    raise PageLoadError("Page content appears to be empty or too small")

                cleaned_text = clean_html(html)
                truncated_text = truncate_text(cleaned_text, config.max_content_length)

                return truncated_text

            except PlaywrightTimeoutError as e:
                raise PageLoadError(f"Page load timeout: {str(e)}")
            except PlaywrightError as e:
                raise BrowserError(f"Browser error: {str(e)}")
            finally:
                await browser.close()

    except ScrapingError:
        raise
    except Exception as e:
        raise BrowserError(f"Unexpected browser error: {str(e)}")