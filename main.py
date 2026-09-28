import sys
import asyncio
from rich.console import Console
from rich.rule import Rule

from scraper import scrape_webpage, InvalidURLError, PageLoadError, BrowserError
from llm import summarize_content, OllamaConnectionError, LLMAPIError

console = Console()


async def main():
    if len(sys.argv) < 2:
        console.print("[red]Usage:[/red] python main.py \"https://example.com\"")
        sys.exit(1)

    url = sys.argv[1]

    console.print(f"[cyan]Scraping:[/cyan] {url}")

    try:
        content = await scrape_webpage(url)
        console.print(f"[green]✓[/green] Page scraped successfully ({len(content)} chars)")

    except InvalidURLError as e:
        console.print(f"[red]Invalid URL:[/red] {e}")
        sys.exit(1)
    except PageLoadError as e:
        console.print(f"[red]Page load failed:[/red] {e}")
        sys.exit(1)
    except BrowserError as e:
        console.print(f"[red]Browser error:[/red] {e}")
        sys.exit(1)

    console.print("[cyan]Summarizing with LLM...[/cyan]")

    try:
        summary = await summarize_content(content)

    except OllamaConnectionError as e:
        console.print(f"[red]Ollama connection error:[/red] {e}")
        console.print("[yellow]Make sure Ollama is running at http://localhost:11434[/yellow]")
        sys.exit(1)
    except LLMAPIError as e:
        console.print(f"[red]LLM API error:[/red] {e}")
        sys.exit(1)

    console.print()
    console.print(Rule("[bold cyan]Webpage Summary[/bold cyan]"))
    console.print()
    
    for line in summary.strip().split("\n"):
        if line.strip():
            console.print(f"  {line.strip()}")

    console.print()


if __name__ == "__main__":
    asyncio.run(main())