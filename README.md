# Web Scraping Summarizer

A Python CLI application that scrapes webpages using Playwright and summarizes them using Ollama LLM.

## Features

- **Playwright-powered scraping** - Handles JavaScript-rendered content
- **Smart content extraction** - Removes scripts, styles, ads, navigation, and other noise
- **Ollama integration** - Uses local LLM for summarization
- **Chunking support** - Handles long pages by splitting into chunks
- **Rich CLI output** - Beautiful formatted summaries

## Installation

### 1. Clone and setup environment

```bash
cd web-scraping
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Install Playwright browsers

```bash
playwright install chromium
```

### 3. Install and setup Ollama

```bash
# Install Ollama (macOS)
brew install ollama

# Or download from https://ollama.ai

# Start Ollama service
ollama serve

# Pull the required model
ollama pull gpt-oss:20b-cloud
```

### 4. Configure (optional)

Create a `.env` file to customize settings:

```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gpt-oss:20b-cloud
OLLAMA_TIMEOUT=120
PLAYWRIGHT_TIMEOUT=30000
MAX_CONTENT_LENGTH=8000
CHUNK_SIZE=6000
CHUNK_OVERLAP=500
```

## Usage

```bash
python main.py "https://example.com"
```

### Example Output

```
Scraping: https://example.com
✓ Page scraped successfully (3245 chars)
Summarizing with LLM...

┌ Webpage Summary ──────────────────────────────────────┐
│ • Example Domain is a reserved domain for documentation │
│ • The page demonstrates basic HTML structure            │
│ • It contains a heading, paragraph, and link            │
│ • Used for testing and educational purposes             │
└─────────────────────────────────────────────────────────┘
```

## Project Structure

```
web-scraping/
├── main.py           # CLI entry point
├── scraper.py        # Playwright scraping logic
├── llm.py            # Ollama API integration
├── utils.py          # Text cleaning and chunking
├── config.py         # Configuration management
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Error Handling

The application handles:

- **Invalid URLs** - Validates URL format before scraping
- **Page load failures** - Timeouts, network errors, empty content
- **Browser errors** - Playwright/Chromium issues
- **Ollama connection errors** - Service not running, wrong host
- **LLM API errors** - Model not found, timeouts, bad responses

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `gpt-oss:20b-cloud` | Model to use for summarization |
| `OLLAMA_TIMEOUT` | `120` | Request timeout in seconds |
| `PLAYWRIGHT_TIMEOUT` | `30000` | Page load timeout in ms |
| `MAX_CONTENT_LENGTH` | `8000` | Max chars to send to LLM |
| `CHUNK_SIZE` | `6000` | Chunk size for long pages |
| `CHUNK_OVERLAP` | `500` | Overlap between chunks |

## Requirements

- Python 3.10+
- Playwright (Chromium)
- Ollama with `gpt-oss:20b-cloud` model
- 8GB+ RAM recommended for the model

## License

MIT