import re
from bs4 import BeautifulSoup


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for element in soup(["script", "style", "noscript", "iframe", "svg", "canvas", "header", "footer", "nav", "aside", "form", "button", "input", "select", "textarea", "meta", "link", "head", "title"]):
        element.decompose()

    for element in soup.find_all(class_=re.compile(r"(ad|ads|advert|banner|promo|popup|modal|cookie|consent|newsletter|subscribe|social|share|follow|widget|sidebar|navigation|menu|nav|header|footer)", re.I)):
        element.decompose()

    for element in soup.find_all(id=re.compile(r"(ad|ads|advert|banner|promo|popup|modal|cookie|consent|newsletter|subscribe|social|share|follow|widget|sidebar|navigation|menu|nav|header|footer)", re.I)):
        element.decompose()

    for element in soup.find_all("div", attrs={"role": re.compile(r"(banner|complementary|navigation|search)", re.I)}):
        element.decompose()

    text = soup.get_text(separator="\n", strip=True)

    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n\s+\n", "\n\n", text)

    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line and len(line) > 2]

    return "\n".join(lines)


def truncate_text(text: str, max_length: int) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "..."


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if end < len(text):
            last_period = max(chunk.rfind("."), chunk.rfind("?"), chunk.rfind("!"))
            if last_period > chunk_size * 0.5:
                chunk = chunk[:last_period + 1]
                end = start + last_period + 1

        chunks.append(chunk.strip())
        start = end - overlap

    return chunks