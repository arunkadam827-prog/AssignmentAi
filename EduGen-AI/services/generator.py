
"""EduGen AI generation service: Gemini, Groq, and OpenAI."""

from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from docx import Document
from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def _provider_config():
    load_dotenv(PROJECT_ROOT / ".env", override=False)

    provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()

    if provider == "gemini":
        key = (
            os.getenv("GEMINI_API_KEY")
            or os.getenv("LLM_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or ""
        ).strip()
    elif provider == "groq":
        key = (os.getenv("GROQ_API_KEY") or os.getenv("LLM_API_KEY") or "").strip()
    elif provider == "dahl":
        key = (os.getenv("DAHL_API_KEY") or os.getenv("LLM_API_KEY") or "").strip()
    else:
        key = (os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or "").strip()

    if not key or key.startswith("YOUR_"):
        raise RuntimeError(
            "API key is missing. Add your provider API key to the project-root .env file."
        )

    providers = {
        "gemini": (
            "https://generativelanguage.googleapis.com/v1beta/openai/",
            "gemini-3.8-flash",
        ),
        "groq": (
            "https://api.groq.com/openai/v1",
            "llama-3.3-70b-versatile",
        ),
        "openai": (
            os.getenv("LLM_BASE_URL"),
            "gpt-4o-mini",
        ),
        "dahl": (
            "https://inference.dahl.global/v1",
            "MiniMaxAI/MiniMax-M2.7",
        ),
    }

    if provider not in providers:
        raise RuntimeError(
            "LLM_PROVIDER must be gemini, groq, openai, or dahl."
        )

    base_url, default_model = providers[provider]

    if provider == "gemini":
        model = os.getenv("GEMINI_MODEL") or os.getenv("LLM_MODEL") or default_model
    else:
        model = os.getenv("LLM_MODEL") or default_model
    model = model.strip()
    code_model = os.getenv("LLM_CODE_MODEL", model).strip()

    return key, base_url, model, code_model, provider


def _get_client_and_model(code: bool = False):
    key, base_url, model, code_model, provider = _provider_config()

    client = OpenAI(
        api_key=key,
        base_url=base_url,
        timeout=60.0,
        max_retries=0,
    )

    return client, code_model if code else model, provider


def _call_ai(system_prompt: str, user_prompt: str, code: bool = False) -> str:
    client, model, provider = _get_client_and_model(code=code)

    retries = max(1, int(os.getenv("LLM_MAX_RETRIES", "3")))

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2 if code else 0.35,
            )

            result = response.choices[0].message.content

            if not result or not result.strip():
                raise RuntimeError(
                    "The AI provider returned an empty response."
                )

            return result.strip()

        except Exception as exc:
            message = str(exc).lower()

            permanent_errors = (
                "401",
                "403",
                "unauthorized",
                "invalid api key",
                "authentication",
                "model_not_found",
                "404",
            )

            if (
                any(error in message for error in permanent_errors)
                or attempt == retries - 1
            ):
                raise RuntimeError(
                    f"{provider.title()} request failed. "
                    f"Check your API key, model, and quota. Details: {exc}"
                ) from exc

            time.sleep(min(2 ** attempt, 8))

    raise RuntimeError("AI generation failed.")


def generate_text_answer(question: str) -> str:
    question = (question or "").strip()

    if not question:
        raise ValueError("Please enter a question.")

    target = os.getenv("WORD_TARGET_WORDS", "300-450")

    return _call_ai(
        "You are EduGen AI, a reliable academic learning assistant. "
        "Explain concepts accurately in student-friendly language. "
        "Structure answers with headings and examples when useful. "
        "Do not invent facts or citations.",
        f"Answer this academic question in approximately "
        f"{target} words:\n\n{question}",
    )


def _detect_file_extension_requirement(text: str) -> str:
    """Detect requested programming language when implementation is requested."""

    value = (text or "").lower()

    code_cues = (
        "write a program",
        "write program",
        "implement",
        "develop a program",
        "write code",
        "code for",
        "program to",
        "create a program",
        "source code",
    )

    if not any(cue in value for cue in code_cues):
        return "docx"

    language_patterns = [
        (r"\bc\+\+\b|\bcpp\b", "cpp"),
        (r"\bpython\b", "py"),
        (r"\bjava\b", "java"),
        (r"\bjavascript\b|\bjs\b", "js"),
        (r"\bhtml\b", "html"),
        (r"\bc#\b|\bc-sharp\b", "cs"),
        (r"\bphp\b", "php"),
        (r"\bruby\b", "rb"),
        (r"\bgolang\b|\bgo language\b", "go"),
        (r"\brust\b", "rs"),
        (r"\blanguage c\b|\bin c\b", "c"),
    ]

    for pattern, extension in language_patterns:
        if re.search(pattern, value):
            return extension

    return "docx"


def _extract_code(answer: str) -> str:
    match = re.search(
        r"```[^\n]*\n(.*?)```",
        answer,
        flags=re.S,
    )

    return (match.group(1).strip() if match else answer.strip()) + "\n"


def generate_code_solution(
    text: str,
    language: str = "py",
    filename: Optional[str] = None,
) -> str:

    language_names = {
        "cpp": "C++",
        "py": "Python",
        "java": "Java",
        "c": "C",
        "js": "JavaScript",
        "html": "HTML",
        "cs": "C#",
        "php": "PHP",
        "rb": "Ruby",
        "go": "Go",
        "rs": "Rust",
    }

    language_name = language_names.get(language.lower(), language)

    answer = _call_ai(
        f"You are an expert {language_name} programming tutor. "
        "Return one complete, runnable solution in a single fenced code block. "
        "Include necessary imports and a main entry point where appropriate. "
        "Respect names and constraints specified in the assignment. "
        "Do not add prose outside the code block.",
        f"Implement this assignment in {language_name}:\n\n{text}",
        code=True,
    )

    code = _extract_code(answer)

    if filename:
        Path(filename).write_text(code, encoding="utf-8")

    return code


def generate_word_solution(
    text: str,
    filename: Optional[str] = None,
) -> str:

    target = os.getenv("WORD_TARGET_WORDS", "300-450")

    answer = _call_ai(
        "You are EduGen AI, an accurate academic writing assistant. "
        "Write a clear assignment solution with a title, section headings, "
        "explanations, examples and bullet points where appropriate. "
        "Do not invent facts or references.",
        f"Prepare a well-structured answer of approximately "
        f"{target} words:\n\n{text}",
    )

    if filename:
        document = Document()
        document.add_heading("Assignment Solution", level=0)

        for line in answer.splitlines():
            line = line.strip()

            if not line:
                continue

            if line.startswith("### "):
                document.add_heading(line[4:], level=2)

            elif line.startswith("## "):
                document.add_heading(line[3:], level=1)

            elif line.startswith("# "):
                document.add_heading(line[2:], level=1)

            elif line.startswith(("- ", "* ")):
                document.add_paragraph(
                    line[2:],
                    style="List Bullet",
                )

            elif re.match(r"^\d+[.)]\s+", line):
                document.add_paragraph(
                    re.sub(r"^\d+[.)]\s+", "", line),
                    style="List Number",
                )

            else:
                document.add_paragraph(line)

        document.save(filename)

    return answer
