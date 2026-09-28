#👇🏻👇🏻This is my Demo video link of project

https://drive.google.com/file/d/170JL9ihzIqXCzvI5Qzyqagjwvi6_nfS_/view?usp=drive_link

# 📈 Financial News Simplifier
> **AI-Powered Educational Web Application for Translating Complex Financial News into Simple Language**
>
> *NASSCOM Capstone Project Standard*

---

## 📌 1. Project Overview & Description

**Financial News Simplifier** is an intelligent, educational web application designed to help students, beginners, retail investors, and everyday citizens understand dense and jargon-heavy financial news. Modern financial reporting from central banks, earnings calls, economic ministries, and market analysts is often filled with complicated terminology (such as *Repo Rate, Quantitative Easing, EBITDA, Hawkish Stance, Fiscal Deficit*) and confusing financial metrics that intimidate non-specialists.

This application acts as a transparent, educational translator. It extracts news articles directly from URLs or pasted text, breaks down complex concepts into beginner-friendly explanations, extracts key facts, explains difficult terminology with intuitive analogies, categorizes mentioned organizations, and assesses potential business and consumer implications—all while strictly adhering to ethical, non-advisory constraints.

---

## 🎯 2. Problem Statement & Proposed Solution

### The Problem
- **Financial Illiteracy Barrier**: Over 70% of beginners struggle to interpret macroeconomic news, central bank rate decisions, and corporate earnings disclosures.
- **Cognitive Overload**: News articles bury critical numbers and real-world implications under layers of financial jargon.
- **Unreliable "Trading Signals"**: Many online tools generate misleading stock predictions or high-risk trading advice rather than fostering foundational financial understanding.

### The Proposed Solution
- **Plain-English Translation**: Generates an **"In Simple Words"** narrative explanation for any complex financial article.
- **Structured Knowledge Extraction**: Identifies 5–8 key takeaways answering *what happened*, *who is involved*, *why it matters*, *key figures*, and *what remains uncertain*.
- **Integrated Glossary & Term Detection**: Automatically highlights specialized terminology and links it to clear, intuitive definitions with real-world examples.
- **Entity Categorization**: Extracts and categorizes companies, commercial banks, government bodies, countries, and economic metrics.
- **Ethical AI Boundaries**: Never produces personalized investment advice, trading calls, or guaranteed predictions. Market relevance is framed cautiously and neutrally.
- **Fail-Safe Offline Demo Mode**: Fully usable and demonstrable even when an OpenAI API key is unavailable.

---

## 🚀 3. Key Features

| Feature | Description |
| :--- | :--- |
| **Dual Input Methods** | Paste raw text or enter any public financial article URL. |
| **Intelligent Web Scraping** | Cleans HTML, removes scripts, ads, and footers, extracting clean story content with fallback guidance. |
| **📌 "In Simple Words" Card** | A dedicated, beginner-friendly narrative explaining the core news event. |
| **Readability Metrics** | Computes source vs. simplified word count and reading time saved (up to 75% faster). |
| **Categorized Entity Extraction** | Badges for Companies, Banks, Government Agencies, Countries, Leaders, and Indicators. |
| **Financial Terminology Breakdown** | Detects terms and provides plain-English definitions and article context. |
| **Possible Impact Breakdown** | Tabs for Business Impact, Consumer Impact, Economic Impact, and Market Relevance with disclaimers. |
| **Sentiment & Confidence Gauge** | Assesses news tone (Positive, Negative, Neutral, Mixed, Uncertain) with confidence scoring. |
| **Persistent History & Search** | Saves all analyses to SQLite; filter by sentiment, sector, and keywords. |
| **Interactive Analytics** | Plotly charts showing sentiment distribution, sector breakdown, top financial terms, and timeline. |
| **Multi-Format Export** | Download comprehensive plaintext summary reports (`.txt`) or structured JSON (`.json`). |
| **Built-in Financial Glossary** | Comprehensive searchable guide covering 30+ fundamental financial terms with analogies. |
| **Offline Demo Mode** | Instant 1-click demonstration with realistic RBI monetary policy and Tech infrastructure cases. |

---

## 🛠️ 4. Technology Stack

- **Python Version**: Python 3.11+ (Tested on Python 3.13)
- **Frontend / UI**: [Streamlit](https://streamlit.io/) with custom CSS styling and responsive layout
- **Visualization**: [Plotly](https://plotly.com/) (donut charts, horizontal bar charts, timeline area charts)
- **Data Manipulation**: [Pandas](https://pandas.pydata.org/)
- **Database ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) with SQLite database (`data/news_history.db`)
- **AI / LLM Integration**: Official [OpenAI Python SDK](https://github.com/openai/openai-python) with configurable models (`OPENAI_MODEL`)
- **Web Parsing & Scraping**: `requests` & `BeautifulSoup4` with custom headers and error handling
- **Data Validation & Schemas**: [Pydantic v2](https://docs.pydantic.dev/)
- **Configuration**: `python-dotenv` for secure environment variable isolation
- **Automated Testing**: `pytest` for unit and integration testing

---

## 🏗️ 5. System Architecture

```
User Input (Paste Text or News URL)
                │
                ▼
  ┌───────────────────────────────┐
  │         news_parser.py        │  ◄── Extracts HTML, cleans text, validates length
  └───────────────┬───────────────┘
                  │ Clean Text
                  ▼
  ┌───────────────────────────────┐
  │          analyzer.py          │  ◄── Orchestrates pipeline & handles Demo Mode
  └───────┬───────────────┬───────┘
          │               │
  (If API Key)       (If Demo Mode)
          │               │
          ▼               ▼
┌──────────────────┐ ┌──────────────────┐
│   ai_service.py  │ │  DEMO_ARTICLES   │
│   (OpenAI SDK)   │ │  (Pre-computed)  │
└─────────┬────────┘ └────────┬─────────┘
          │                   │
          ▼                   ▼
  ┌───────────────────────────────┐
  │      utils/validators.py      │  ◄── Validates JSON against Pydantic AnalysisResult
  └───────────────┬───────────────┘
                  │
                  ▼
  ┌───────────────────────────────┐
  │          database.py          │  ◄── Persists to SQLite via SQLAlchemy ORM
  └───────────────┬───────────────┘
                  │
                  ▼
  ┌───────────────────────────────┐
  │            app.py             │  ◄── Interactive Streamlit Multi-Page UI & Charts
  └───────────────────────────────┘
```

---

## 📁 6. Complete Project Structure

```
Financial-News-Simplifier/
│
├── app.py                      # Main Streamlit web application & multi-page dashboard
├── config.py                   # Centralized configuration, paths, and environment loader
├── database.py                 # SQLite ORM models, migrations, CRUD, and analytics queries
├── ai_service.py               # OpenAI client, system prompt constraints, and JSON schema parsing
├── news_parser.py              # Web scraping, HTML sanitation, and text cleaning
├── analyzer.py                 # Main orchestrator linking parsing, AI, demo mode, and database
├── requirements.txt            # Pinned dependency requirements
├── README.md                   # Comprehensive project documentation
├── .env.example                # Template for environment variables
├── .gitignore                  # Git exclusions for keys, databases, virtual environments
│
├── data/
│   ├── .gitkeep                # Preserves folder in version control
│   └── news_history.db         # SQLite database file (created automatically on startup)
│
├── modules/
│   ├── __init__.py             # Module exports
│   ├── summarizer.py           # Readability metrics and "In Simple Words" formatting
│   ├── financial_terms.py      # Master financial dictionary (30+ terms) and text scanner
│   ├── impact_analyzer.py      # Business/consumer impact structuring and disclaimers
│   └── entity_extractor.py     # Categorized organization and leadership entity extraction
│
├── utils/
│   ├── __init__.py             # Utilities init
│   ├── validators.py           # Pydantic schemas, URL validation, and text bounds checking
│   └── helpers.py              # Export generators (.txt, .json), date formatters, and badges
│
├── assets/
│   └── README.md               # Static asset documentation
│
└── tests/
    ├── test_validators.py      # Unit tests for URL and text validation logic
    ├── test_database.py        # Tests for database model persistence, search, and deletion
    └── test_parser.py          # Tests for HTML text cleaning and offline demo analysis
```

---

## 💻 7. Installation & Setup Guide

### Prerequisites
- Python 3.11 or higher (Python 3.11, 3.12, and 3.13 supported)
- Visual Studio Code (or any standard code editor)
- Git (optional, for version control)

### Step 1: Clone or Navigate to the Project Folder
Open your terminal (PowerShell, Command Prompt, or Bash) and navigate to the project directory:

```bash
cd "c:\Users\om\Documents\Financial News Simplifier-Abhi\Financial-News-Simplifier"
```

### Step 2: Create a Python Virtual Environment

**On Windows (PowerShell / Command Prompt):**
```powershell
python -m venv venv
```

**Activate the Virtual Environment:**
```powershell
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Windows Command Prompt (cmd.exe):
venv\Scripts\activate.bat

# macOS / Linux:
source venv/bin/activate
```

*(Note for PowerShell users: If script execution is disabled, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once).*

### Step 3: Install Required Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 8. How to Configure the OpenAI API Key

1. Copy `.env.example` to create your active `.env` file:
   ```powershell
   # Windows PowerShell:
   Copy-Item .env.example .env

   # Command Prompt / Bash:
   copy .env.example .env
   ```
2. Open `.env` in VS Code.
3. Replace the placeholder with your actual OpenAI API key:
   ```ini
   OPENAI_API_KEY=sk-proj-yourActualKeyHere...
   OPENAI_MODEL=gpt-4o-mini
   DATABASE_URL=sqlite:///data/news_history.db
   ```
4. Save the file. The application automatically detects and reloads settings.

> 🔒 **Security Notice:** The `.env` file is included in `.gitignore` and must **never** be committed to GitHub or shared publicly.

---

## ⚡ 9. How to Run Demo Mode (No API Key Required)

If you do not have an OpenAI API key or wish to demonstrate the tool offline:

1. You **do not need** to enter an API key in `.env`.
2. Launch the Streamlit application.
3. Navigate to **📰 Analyze News** in the sidebar.
4. Select an example topic (e.g., *RBI Keeps Repo Rate Unchanged at 6.50%* or *Tech Leader AI Data Center Expansion*).
5. Click **⚡ Run Demo Analysis**.
6. The entire analysis view—including In Simple Words, Key Points, Financial Terms, Categorized Entities, Impact Tabs, Readability Metrics, and Exports—will render immediately using pre-computed, verified financial datasets.

---

## ▶️ 10. Running the Application

To launch the web dashboard:

```bash
streamlit run app.py
```

The application will start and automatically open in your default web browser at:
```
http://localhost:8501
```

---

## 🧪 11. Running Automated Tests

Run the automated test suite with pytest:

```bash
python -m pytest tests/ -v
```

All 9 unit tests cover:
- URL structure and safety verification
- Minimum and maximum text bounds
- Database creation, querying, and deletion
- HTML cleaning and formatting
- Offline demo mode data integrity

---

## 📖 12. Application Workflow & Pages

### 🏠 Dashboard
- Top KPI metrics: Total articles analyzed, analyses performed today, glossary size, system mode.
- Interactive Plotly visualizations:
  - **Sentiment Distribution** (Donut Chart)
  - **Articles by Sector** (Horizontal Bar Chart)
  - **Most Common Financial Terms** (Frequency Bar Chart)
  - **Analysis Activity Over Time** (Timeline Area Chart)
- Quick links to recently analyzed articles.

### 📰 Analyze News
- Choose between **📝 Paste Article Text** or **🔗 Article URL**.
- Click **📋 Load Example News** to quickly test realistic central bank rate articles.
- Click **🚀 Analyze News** to invoke the AI pipeline, or **⚡ Run Demo Analysis** for instant results.
- View the **📌 In Simple Words** narrative, readability reduction stats, key points, terms, categorized entities, and impact breakdown.
- Export results as **Plaintext (.txt)** or **JSON (.json)**.

### 📚 News History
- Browse all previously simplified articles stored in SQLite.
- Search articles by keyword or phrase.
- Filter by sentiment (Positive, Negative, Neutral, Mixed, Uncertain) or sector.
- Expand any record to inspect the complete breakdown.
- Delete individual analyses with one click.

### 📖 Financial Glossary
- Searchable directory of 30+ core financial concepts (GDP, Repo Rate, Inflation, P/E Ratio, EBITDA, EPS, Fiscal Deficit, Bull/Bear Markets, Liquidity, Volatility, etc.).
- Filter by topic: Macroeconomics, Monetary Policy, Stock Markets, Corporate Finance, Fixed Income, Risk & Trading, Financial System.
- Each term includes a beginner-friendly analogy, formal definition, and real-world example.

### ℹ️ About Project
- Detailed capstone context, NASSCOM criteria mapping, architecture diagram, and ethical AI safeguards.

---

## ⚖️ 13. Ethical Safeguards & Non-Advisory Guarantee

1. **Non-Advisory Mandate**: This system strictly serves an educational purpose. It never provides stock buy/sell calls, target prices, or portfolio advice.
2. **Hallucination Prevention**: The system prompt enforces strict fidelity to source text numbers, dates, and statements.
3. **Probabilistic Language**: Replaces deterministic predictions with cautious phrasing (*"may affect"*, *"could influence"*, *"the article suggests"*).
4. **Tone vs. Performance**: Sentiment reflects article tonality, not stock market trajectory.

---

## 🎓 14. NASSCOM Capstone Project Alignment

This project satisfies all key criteria for modern AI Capstone evaluations:
- **Real-World Problem**: Addresses financial literacy gaps using modern generative AI.
- **Full-Stack Implementation**: Clean separation of frontend (Streamlit), backend logic, database ORM (SQLAlchemy), and LLM integration (OpenAI).
- **Engineering Rigor**: Pydantic schema validation, resilient web scraping, unit tests, and structured exception handling.
- **Fail-Safe Architecture**: Graceful degradation with zero crashes when keys are missing or websites block scraping.

---

## 📤 15. Pushing the Project to GitHub

Initialize git, add files, and push to your repository:

```bash
# 1. Initialize git in the project root
git init

# 2. Stage all files (respecting .gitignore)
git add .

# 3. Create initial commit
git commit -m "Initial commit: Complete Financial News Simplifier Capstone Project"

# 4. Link your remote repository and push
git remote add origin https://github.com/your-username/Financial-News-Simplifier.git
git branch -M main
git push -u origin main
```

*(Verify that `.env` and `*.db` are not pushed to GitHub).*

---

## 📄 License & Disclaimer

This project is licensed for educational and academic evaluation purposes.
*Disclaimer: Financial News Simplifier is an educational tool. All financial data, summaries, and impact analyses are generated for informational purposes only and do not constitute financial advice.*
