# EduGen AI — AI Assignment & Study Assistant

EduGen AI is a Flask-based academic assistant. It can answer typed questions,
read uploaded assignment documents, generate formatted Word answers, and create
source-code solutions in the requested programming language.

## Project owner

**Arun Mahadev Kadam**  
Email: arunkadam827@gmail.com  
LinkedIn: https://www.linkedin.com/in/arun-kadam-14ba782a9  
GitHub: https://github.com/arunkadam827-prog

EduGen AI is maintained as a personal software project. Update this section if
the project ownership or contact details change.

## Features

- Assignment document upload: PDF, DOCX, DOC, TXT, and supported source files
- Text extraction from PDFs, Word documents, and code/text files
- Optional OCR for scanned PDFs (install EasyOCR separately if needed)
- AI question answering (GDB)
- Word document generation with headings and lists
- Code generation for C, C++, Java, Python, JavaScript, HTML, C#, PHP, Ruby, Go, and Rust
- Gemini, Groq, and OpenAI provider support
- API keys loaded from `.env`; no key is embedded in source code
- Windows-compatible temporary-file handling

## Requirements

Python 3.10 or newer is recommended. Python 3.11 is a good default for broad
compatibility with document and optional OCR packages.

## Windows setup (PowerShell)

```powershell
# 1. Extract the project and open its root directory
cd AI-Assignment-Generator-main

# 2. Create and activate a virtual environment
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Create your local environment file
Copy-Item .env.example .env

# 5. Edit .env and paste your own key after LLM_API_KEY=
notepad .env

# 6. Start the application
python app.py
```

Open http://localhost:8080 in your browser.

## Provider configuration

For Gemini, configure `.env` like this:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_private_key
GEMINI_MODEL=gemini-2.5-flash
```

The project also supports Groq and OpenAI-compatible providers.

Supported values for `LLM_PROVIDER`: `gemini`, `groq`, or `openai`.
The generator also accepts the legacy `OPENAI_API_KEY` variable for compatibility.
Never commit `.env` or share your API key.

## Optional OCR

Normal text-based PDFs do not need OCR. To enable OCR for scanned PDFs, install
a compatible EasyOCR/PyTorch build for your Python version:

```powershell
pip install easyocr
```

If OCR is unavailable, the app still starts; scanned-only pages may return no text.

## Run with Docker

Build and run with your local `.env` file:

```bash
docker build -t edugen-ai .
docker run --env-file .env -p 8080:8080 edugen-ai
```

## Important

AI-generated answers and code can contain mistakes. Review generated work,
test code, and follow your institution's academic-integrity requirements.
