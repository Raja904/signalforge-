# SignalForge AI 🚀
### AI-Powered B2B Outreach

**SignalForge AI** is an agentic sales research and drafting tool designed to turn cold prospects into warm conversations. By combining real-time web signals with advanced LLM reasoning, SignalForge identifies the perfect "hook" for any prospect in seconds.

## 🌟 Key Features
- **Agentic Research**: Uses LangGraph to orchestrate a multi-stage research process (Search → Analyze → Draft).
- **Signal-to-Hook**: Automatically detects funding news, recent interviews, LinkedIn activity, and company growth patterns.
- **Smart Edge Cases**:
    - **Ghost Detector**: Handles prospects with zero digital footprint.
    - **Stale Signal Warning**: Flags outdated news.
    - **Ambiguity Resolver**: Detects if multiple companies share the same name.
- **Unified Dashboard**: Keep track of all your research and lead quality in one place.
- **Human-in-the-Loop**: Edit and refine drafts before they ever hit an inbox.

## 🛠️ Tech Stack
- **Orchestration**: [LangGraph](https://github.com/langchain-ai/langgraph)
- **Intelligence**: [Mistral Large](https://mistral.ai/)
- **Search Engine**: [Serper.dev](https://serper.dev/)
- **UI Framework**: [Streamlit](https://streamlit.io/)
- **Database**: SQLite

## 🚀 Getting Started

### 1. Clone & Setup
```bash
git clone https://github.com/your-username/signalforge-ai.git
cd signalforge-ai
python -m venv .venv
source .venv/bin/activate  # Or .\.venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Configure API Keys
Create a `.env` file in the root directory:
```env
MISTRAL_API_KEY=your_mistral_api_key
SERPER_API_KEY=your_serper_api_key
```

### 3. Run the App
```bash
streamlit run app.py
```

## 📂 Architecture
- `app.py`: Main Streamlit application.
- `workflow/`: Core LangGraph agent logic.
- `services/`: API integration for Mistral and Serper.
- `db/`: Data persistence layer.
- `pages/`: Additional UI pages (Dashboard).

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).

---
