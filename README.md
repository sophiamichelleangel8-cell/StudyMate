# StudyMate

**AI-Powered Personal Study Assistant**

## Overview
StudyMate turns a student's own PDF notes into an interactive study experience: ask questions grounded in the material (RAG), get structured summaries, take auto-generated quizzes, flip through flashcards, and track progress. It also works as a general AI tutor when no document is loaded.

## Features
- PDF upload and processing with a visible status and section count
- AI Tutor chat that retrieves relevant passages from your documents (RAG), or answers general questions
- Summary: main topics, concepts, definitions, important points, exam revision points
- 5-question MCQ quiz (no pre-selected answers, submit only when complete), score, review of correct and incorrect answers, retry
- 5 flashcards with Show Answer, Previous and Next
- Dashboard and Progress pages driven by real session data

## Tech Stack
Streamlit, pypdf, sentence-transformers (`all-MiniLM-L6-v2`), ChromaDB, Ollama (local) or Groq (deployed).

## Architecture
`app.py` routes to pages. `core/ai_client.py` hides the provider (Groq if `GROQ_API_KEY` exists, otherwise Ollama). `rag/` handles PDF, chunking and vector search. `features/` holds chat, summary, quiz, flashcards and progress. `ui/` holds layout and styling. State lives in `st.session_state`; there is no database.

## RAG Pipeline
PDF -> pypdf text extraction -> cleaning -> sentence-aware chunking (about 900 characters, 150 overlap) -> MiniLM embeddings -> ChromaDB (in-memory, one collection per session, unique chunk IDs) -> similarity search (top 4) -> context in prompt -> LLM answer.

## Local Setup
```bash
git clone <your-repo-url> StudyMate && cd StudyMate
python -m venv .venv
# Windows:  .venv\Scripts\activate      macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py
```
The first PDF you process downloads the embedding model (about 90 MB) once.

## Ollama Setup
1. Install from https://ollama.com
2. `ollama pull llama3.2`
3. Make sure Ollama is running (`ollama serve`, or the desktop app).
4. Do not set `GROQ_API_KEY`; StudyMate will use Ollama at `http://localhost:11434`.

## Groq Setup
1. Create a key at https://console.groq.com
2. Set it, either way:
   - Environment variable: `GROQ_API_KEY=your_key` (PowerShell: `$env:GROQ_API_KEY="your_key"`)
   - Or create `.streamlit/secrets.toml` containing `GROQ_API_KEY = "your_key"`
3. StudyMate then uses `openai/gpt-oss-20b`.

## Environment Variables
| Name | Purpose | Default |
|---|---|---|
| `GROQ_API_KEY` | Enables Groq mode | unset (Ollama) |
| `GROQ_MODEL` | Groq model | `openai/gpt-oss-20b` |
| `OLLAMA_URL` | Ollama address | `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama model | `llama3.2` |

## Running the Application
`python -m streamlit run app.py`

## Deployment (Streamlit Community Cloud)
1. Push the repo to GitHub (secrets and `.env` are git-ignored).
2. Go to https://share.streamlit.io, choose **New app**, select the repo, branch `main`, main file `app.py`.
3. Open **Advanced settings > Secrets** and paste: `GROQ_API_KEY = "your_key"`
4. Choose Python 3.11 or 3.12 and click **Deploy**.

## Project Structure
```
StudyMate/
├── app.py
├── core/      ai_client.py, prompts.py, session_state.py
├── rag/       pdf_loader.py, text_splitter.py, vector_store.py
├── features/  chat.py, summary.py, quiz.py, flashcards.py, progress.py
├── ui/        sidebar.py, dashboard.py, materials.py, settings.py, styles.py
├── .streamlit/config.toml
├── requirements.txt
└── README.md
```

## Future Improvements
Authentication, persistent database, personalized study plans, spaced repetition, multiple document collections, voice interaction.
