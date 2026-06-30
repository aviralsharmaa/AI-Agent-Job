"""
AI assistant powered by Groq (free, OpenAI-compatible LLM API).

Features:
- analyze_resume(): read a resume/CV PDF and draft a tailored subject + body
- body_from_description(): turn a short description into an email body
- improve_text(): paraphrase / upgrade existing text (QuillBot-style)

The Groq API key is read from Streamlit secrets ([groq] api_key = "...")
or the GROQ_API_KEY environment variable.
"""

import os
import json

try:
    import streamlit as st
    _STREAMLIT = True
except ImportError:
    _STREAMLIT = False

# Default Groq model — fast and capable. Override with [groq] model in secrets.
DEFAULT_MODEL = "llama-3.3-70b-versatile"


def get_groq_key():
    """Return the Groq API key from Streamlit secrets or environment."""
    if _STREAMLIT:
        try:
            if "groq" in st.secrets:
                key = st.secrets["groq"].get("api_key")
                if key:
                    return key
        except Exception:
            pass
    return os.environ.get("GROQ_API_KEY")


def get_groq_model():
    if _STREAMLIT:
        try:
            if "groq" in st.secrets:
                model = st.secrets["groq"].get("model")
                if model:
                    return model
        except Exception:
            pass
    return os.environ.get("GROQ_MODEL", DEFAULT_MODEL)


def ai_available() -> bool:
    """True if Groq is installed and an API key is configured."""
    if not get_groq_key():
        return False
    try:
        import groq  # noqa: F401
        return True
    except ImportError:
        return False


def _client():
    from groq import Groq
    return Groq(api_key=get_groq_key())


def _chat(system: str, user: str, temperature: float = 0.6, max_tokens: int = 900) -> str:
    """Single-turn chat completion, returns the text content."""
    client = _client()
    resp = client.chat.completions.create(
        model=get_groq_model(),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return (resp.choices[0].message.content or "").strip()


# --------------------------------------------------------------------------- #
# PDF / resume text extraction
# --------------------------------------------------------------------------- #
def extract_pdf_text(file_path: str, max_chars: int = 6000) -> str:
    """Extract text from a PDF (or .txt) file, truncated to max_chars."""
    path_lower = file_path.lower()
    text = ""
    if path_lower.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
        except Exception:
            text = ""
    elif path_lower.endswith(".txt"):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception:
            text = ""
    return text.strip()[:max_chars]


# --------------------------------------------------------------------------- #
# Generation helpers
# --------------------------------------------------------------------------- #
def analyze_resume(resume_text: str) -> dict:
    """Analyze a resume and return {'subject': ..., 'body': ...} for a job email."""
    system = (
        "You are an expert career assistant. You write concise, professional "
        "cold job-application emails that recruiters actually read."
    )
    user = (
        "Read the resume below and write a job-application email tailored to it.\n"
        "Return ONLY valid JSON with exactly two keys: \"subject\" and \"body\".\n"
        "- subject: short and specific (max ~12 words), based on the candidate's "
        "strongest role/skills.\n"
        "- body: a polished email under 180 words. Greet with 'Dear Hiring Manager,'. "
        "Highlight 2-3 key skills/achievements from the resume, express interest in "
        "opportunities, and mention the attached resume. End with a professional "
        "sign-off using the candidate's name if present.\n"
        "Do not invent fake experience.\n\n"
        f"RESUME:\n{resume_text}"
    )
    raw = _chat(system, user, temperature=0.5)
    return _parse_subject_body(raw)


def body_from_description(description: str, resume_text: str = "") -> str:
    """Turn a short description into a professional email body (body only)."""
    system = (
        "You write clear, professional emails. Output only the email body text "
        "(no subject line, no markdown, no commentary)."
    )
    context = f"\n\nFor context, the sender's resume:\n{resume_text}" if resume_text else ""
    user = (
        "Write a professional email body based on this description. Keep it concise "
        "(under 180 words), with a greeting and a sign-off.\n\n"
        f"DESCRIPTION: {description}{context}"
    )
    return _chat(system, user, temperature=0.7)


def improve_text(text: str) -> str:
    """Paraphrase and upgrade the given text (QuillBot-style). Returns text only."""
    system = (
        "You are a writing enhancer like QuillBot. Improve grammar, clarity, tone and "
        "professionalism while preserving the original meaning. Output only the improved "
        "text, nothing else."
    )
    user = f"Improve and polish this email text:\n\n{text}"
    return _chat(system, user, temperature=0.6)


def _parse_subject_body(raw: str) -> dict:
    """Best-effort parse of a model response into subject/body."""
    # Try strict JSON first
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        data = json.loads(raw[start:end])
        subject = str(data.get("subject", "")).strip()
        body = str(data.get("body", "")).strip()
        if subject or body:
            return {"subject": subject, "body": body}
    except Exception:
        pass
    # Fallback: treat the whole thing as the body
    return {"subject": "Job Application", "body": raw.strip()}
