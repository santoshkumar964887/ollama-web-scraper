import httpx
from typing import Optional

from config import config
from utils import chunk_text


class LLMError(Exception):
    pass


class OllamaConnectionError(LLMError):
    pass


class LLMAPIError(LLMError):
    pass


SUMMARY_PROMPT = """You are a helpful assistant that summarizes webpages into clear, concise bullet points.

Given the following webpage content, provide a summary as bullet points covering the main topics, key information, and important details.

Rules:
- Return ONLY bullet points (one per line, starting with •)
- Keep each bullet point concise (1-2 sentences max)
- Focus on meaningful content, ignore navigation, ads, boilerplate
- Aim for 5-10 bullet points
- Do not include any introductory or concluding text

Webpage content:
{content}

Summary:"""


async def call_ollama(prompt: str) -> str:
    url = f"{config.ollama_host}/api/generate"
    payload = {
        "model": config.ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9,
            "num_predict": 3000,
        }
    }

    try:
        async with httpx.AsyncClient(timeout=config.ollama_timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            if "response" not in data:
                raise LLMAPIError(f"Unexpected response format: {data}")

            return data["response"].strip()

    except httpx.ConnectError as e:
        raise OllamaConnectionError(f"Cannot connect to Ollama at {config.ollama_host}: {str(e)}")
    except httpx.TimeoutException as e:
        raise LLMAPIError(f"Ollama request timeout: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise LLMAPIError(f"Ollama API error ({e.response.status_code}): {e.response.text}")
    except Exception as e:
        raise LLMAPIError(f"Unexpected error calling Ollama: {str(e)}")


async def summarize_content(content: str) -> str:
    if len(content) <= config.chunk_size:
        prompt = SUMMARY_PROMPT.format(content=content)
        return await call_ollama(prompt)

    chunks = chunk_text(content, config.chunk_size, config.chunk_overlap)
    summaries = []

    for i, chunk in enumerate(chunks):
        chunk_prompt = SUMMARY_PROMPT.format(content=chunk)
        try:
            summary = await call_ollama(chunk_prompt)
            summaries.append(summary)
        except LLMError:
            raise

    combined = "\n".join(summaries)

    final_prompt = f"""Combine and deduplicate the following summaries into a single coherent set of bullet points.
Return ONLY bullet points (one per line, starting with •).
Keep each bullet concise (1-2 sentences).
Aim for 5-10 bullet points total.

Summaries:
{combined}

Combined Summary:"""

    return await call_ollama(final_prompt)
