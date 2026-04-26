import io
import httpx
from fastapi import UploadFile, HTTPException
from pypdf import PdfReader
from docx import Document
from bs4 import BeautifulSoup
from tavily import AsyncTavilyClient
from ..config import settings


async def extract_text_from_file(file: UploadFile) -> str:
    """Extract plain text from an uploaded PDF or DOCX file."""
    content = await file.read()
    filename = (file.filename or "").lower()

    if filename.endswith(".pdf"):
        return _extract_from_pdf(content)
    elif filename.endswith(".docx"):
        return _extract_from_docx(content)
    elif filename.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")
    else:
        # Try PDF first, then DOCX
        try:
            return _extract_from_pdf(content)
        except Exception:
            try:
                return _extract_from_docx(content)
            except Exception:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported file format. Please upload PDF, DOCX, or TXT.",
                )


def _extract_from_pdf(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    text_parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)
    full_text = "\n".join(text_parts).strip()
    if not full_text:
        raise ValueError("PDF appears to be empty or image-based (no extractable text).")
    return full_text


def _extract_from_docx(content: bytes) -> str:
    doc = Document(io.BytesIO(content))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    full_text = "\n".join(paragraphs).strip()
    if not full_text:
        raise ValueError("DOCX appears to be empty.")
    return full_text


async def extract_text_from_url(url: str) -> str:
    """Scrape and extract clean text content from a job posting URL using Tavily Extract."""
    try:
        client = AsyncTavilyClient(api_key=settings.TAVILY_API_KEY)
        response = await client.extract(urls=[url])
        
        results = response.get("results", [])
        
        if results:
            text = results[0].get("raw_content", "")
            if text:
                return text[:8000]
                
        # Fallback to web search if extraction blocks
        search_response = await client.search(query=url, include_raw_content=True)
        search_results = search_response.get("results", [])
        
        if search_results:
            text = "\n\n".join([r.get("raw_content") or r.get("content", "") for r in search_results])
            if text.strip():
                return text[:8000]

        raise ValueError("Could not find any content for this URL even after web search fallback.")

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to extract content from URL: {str(e)}",
        )


def validate_file_size(file: UploadFile, max_mb: int = 10) -> None:
    """Raise HTTPException if the file exceeds max_mb."""
    # Note: file.size may be None for some clients; we rely on content-length header
    if hasattr(file, "size") and file.size and file.size > max_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed size is {max_mb}MB.",
        )
