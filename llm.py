import json
from typing import Optional
from openai import OpenAI
from openai import APIConnectionError, APITimeoutError, APIStatusError

from config import config
from utils import chunk_text


class LLMError(Exception):
    """Base exception for LLM-related errors."""
    pass


class OpenAIConnectionError(LLMError):
    """Raised when unable to connect to the OpenAI/Ollama API."""
    pass


class LLMAPIError(LLMError):
    """Raised when the OpenAI/Ollama API returns an error."""
    pass


SUMMARY_SYSTEM_PROMPT = """You are a helpful assistant that summarizes webpages into clear, concise bullet points.

Given the following webpage content, provide a summary as bullet points covering the main topics, key information, and important details.

Rules:
- Return ONLY bullet points (one per line, starting with •)
- Keep each bullet point concise (1-2 sentences max)
- Focus on meaningful content, ignore navigation, ads, boilerplate
- Aim for 5-10 bullet points
- Do not include any introductory or concluding text"""


COMBINE_SYSTEM_PROMPT = """Combine and deduplicate the following summaries into a single coherent set of bullet points.
Return ONLY bullet points (one per line, starting with •).
Keep each bullet concise (1-2 sentences).
Aim for 5-10 bullet points total."""


def get_openai_client() -> OpenAI:
    """
    Create and return an OpenAI client configured for Ollama.
    
    Ollama provides an OpenAI-compatible API at /v1 endpoint.
    We use 'ollama' as the API key since Ollama doesn't require authentication.
    
    Returns:
        Configured OpenAI client instance
    """
    return OpenAI(
        api_key=config.openai_api_key,
        base_url=config.openai_base_url,
        timeout=config.ollama_timeout,
    )


def call_openai(client: OpenAI, system_prompt: str, user_prompt: str) -> str:
    """
    Make a chat completion request to the OpenAI/Ollama API.
    
    Args:
        client: Configured OpenAI client
        system_prompt: System message to guide the model's behavior
        user_prompt: User message containing the content to process
        
    Returns:
        The model's response content as a string
        
    Raises:
        OpenAIConnectionError: If unable to connect to the API
        LLMAPIError: If the API returns an error response
    """
    try:
        response = client.chat.completions.create(
            model=config.ollama_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            top_p=0.9,
            max_tokens=3000,
        )
        return response.choices[0].message.content.strip()
    
    except APIConnectionError as e:
        raise OpenAIConnectionError(f"Cannot connect to OpenAI/Ollama at {config.openai_base_url}: {str(e)}")
    except APITimeoutError as e:
        raise LLMAPIError(f"OpenAI/Ollama request timeout: {str(e)}")
    except APIStatusError as e:
        raise LLMAPIError(f"OpenAI/Ollama API error ({e.status_code}): {e.response.text if e.response else str(e)}")
    except Exception as e:
        raise LLMAPIError(f"Unexpected error calling OpenAI/Ollama: {str(e)}")


async def summarize_chunk(client: OpenAI, content: str) -> str:
    """
    Summarize a single chunk of content.
    
    Args:
        client: Configured OpenAI client
        content: Text content to summarize
        
    Returns:
        Summary as bullet points
    """
    user_prompt = f"Webpage content:\n{content}\n\nSummary:"
    return call_openai(client, SUMMARY_SYSTEM_PROMPT, user_prompt)


async def combine_summaries(client: OpenAI, summaries: list[str]) -> str:
    """
    Combine multiple summaries into a single coherent summary.
    
    Args:
        client: Configured OpenAI client
        summaries: List of individual summaries to combine
        
    Returns:
        Combined summary as bullet points
    """
    combined = "\n".join(summaries)
    user_prompt = f"Summaries:\n{combined}\n\nCombined Summary:"
    return call_openai(client, COMBINE_SYSTEM_PROMPT, user_prompt)


async def summarize_content(content: str) -> str:
    """
    Summarize webpage content using OpenAI/Ollama API.
    
    For content larger than chunk_size, splits into chunks, summarizes each,
    then combines the results.
    
    Args:
        content: Webpage text content to summarize
        
    Returns:
        Final summary as bullet points
        
    Raises:
        LLMError: If any error occurs during summarization
    """
    client = get_openai_client()
    
    if len(content) <= config.chunk_size:
        return await summarize_chunk(client, content)
    
    # Split large content into chunks
    chunks = chunk_text(content, config.chunk_size, config.chunk_overlap)
    summaries = []
    
    for chunk in chunks:
        summary = await summarize_chunk(client, chunk)
        summaries.append(summary)
    
    # Combine all chunk summaries
    return await combine_summaries(client, summaries)