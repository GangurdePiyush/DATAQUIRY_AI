# Simple Dataset Upload & Query System (Final Integration)

A clean, modular Python Computer Desktop Application built using **Tkinter**, **Pandas**, **SQLite3**, **Local AI (Ollama)**, **SpeechRecognition**, and **pyttsx3**. Designed specifically for college submissions and beginner Python developers with clean, well-commented, and extensible code architecture.

---

## 📌 Project Objective

The **Simple Dataset Upload & Query System** enables users to upload tabular dataset files (CSV or Excel) from their desktop, convert them into a local SQLite database (`data/app.db`), automatically detect database schemas, ask questions in natural language (or via voice input), translate those questions into safe read-only SQL queries using local AI, execute the queries, and inspect formatted result tables alongside spoken audio summaries.

---

## ✨ Features

- **100% Free & Zero Paid Cloud APIs**: Requires NO OpenAI, ChatGPT, Gemini, or paid speech/TTS subscription keys.
- **Desktop Tkinter Interface**: Responsive, clean desktop application with 5 organized card sections.
- **CSV & Excel Dataset Processing**: Supports loading `.csv`, `.xlsx`, and `.xls` files into memory via Pandas.
- **Automated SQLite Database Integration**: Writes uploaded DataFrames into a persistent local SQLite database file (`data/app.db`) under the table name `dataset`.
- **Automatic Schema Detection & Sanitization**: Cleans raw header names into safe SQL identifiers and detects SQLite data types (`INTEGER`, `REAL`, `TEXT`).
- **Local AI NL-to-SQL Translation**: Uses local Ollama LLM (`http://localhost:11434/api/generate`) to convert user questions into SQL statements.
- **Offline AI & Pattern Matcher Fallback**: If Ollama is offline or not installed, the application falls back gracefully to smart pattern matching without crashing, displaying `"Local AI service is unavailable. Please start Ollama or use SQL mode."`
- **Strict Read-Only Security Filter**: Enforces security validation (`is_safe_sql`), allowing ONLY `SELECT` and `WITH` statements and blocking destructive keywords (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`).
- **Manual SQL Entry Mode**: Allows users to directly type or edit SQL statements in the SQL Preview box.
- **Interactive Results Table**: Displays execution result rows and column counts in a styled `ttk.Treeview` table with vertical and horizontal scrollbars.
- **Voice Interaction (STT & TTS)**:
  - **Speech-to-Text**: Captures microphone input via `SpeechRecognition` to auto-populate the Question input box.
  - **Text-to-Speech**: Speaks concise query result summaries via offline `pyttsx3` (e.g. *"Query executed successfully and returned 7 records."*).
  - **Audio Hardware Resilience**: If audio hardware or PyAudio is absent, text-based querying remains 100% active without application crashes.

---

## 🛠️ Technologies Used

| Layer | Technology / Library | Description |
| :--- | :--- | :--- |
| **GUI Framework** | `tkinter`, `ttk` | Desktop user interface windows, cards, entries, buttons, and Treeview tables |
| **Data Processing** | `pandas`, `openpyxl`, `xlrd` | Loading, cleaning, and previewing CSV & Excel datasets |
| **Database Engine** | `sqlite3` (Python Standard Library) | Storing dataset tables, executing queries, and inspecting schemas |
| **Local AI LLM** | Ollama (`requests` HTTP API) | Local schema-aware natural language to SQL translation |
| **Speech-to-Text** | `SpeechRecognition` | Audio capture and speech recognition |
| **Text-to-Speech** | `pyttsx3` | Offline voice synthesis for audio summaries |

---

## 🏗️ Project Architecture & Directory Structure

```
dataset_query_system/
├── app.py                 # Main entry point launcher script
├── config.py              # Central application settings, UI styling & Ollama parameters
├── requirements.txt       # Project dependency manifest
├── README.md              # Project documentation & setup guide
├── test_final.py          # Master automated integration test script (Parts 1-7)
├── test_part2.py          # Part 2 dataset loader test script
├── test_part3.py          # Part 3 SQLite test script
├── test_part4.py          # Part 4 NL to SQL test script
├── test_part5.py          # Part 5 SQL execution test script
├── test_part6.py          # Part 6 Voice interaction test script
├── data/                  # Storage directory for datasets and SQLite DB
│   ├── app.db             # Local SQLite database file
│   ├── sample_employees.csv
│   ├── sample_sales.xlsx
│   ├── empty_test.csv
│   └── corrupt_test.csv
├── dataset/               # Dataset loading & Pandas package
│   ├── __init__.py
│   ├── dataset_handler.py # High-level dataset manager wrapper
│   └── dataset_loader.py  # File reader & error validator
├── database/              # SQLite database management package
│   ├── __init__.py
│   ├── db_handler.py      # Database handler wrapper
│   ├── db_manager.py      # SQLite connection & table creation manager
│   └── schema.py          # Schema detection & column sanitization helper
├── query/                 # Query processing package
│   ├── __init__.py
│   ├── query_engine.py    # Query engine facade
│   ├── nl_to_sql.py       # Local Ollama AI & SQL safety validator
│   └── sql_executor.py    # Safe SQL query executor
├── voice/                 # Voice interaction package
│   ├── __init__.py
│   ├── voice_handler.py   # High-level voice manager facade
│   ├── speech_to_text.py  # Microphone recording & STT engine
│   └── text_to_speech.py  # Offline pyttsx3 TTS audio engine
└── ui/                    # Desktop GUI package
    ├── __init__.py
    └── main_window.py     # Desktop GUI main window with 5 card sections
```

---

## 🔄 End-to-End Execution Workflow

```
User (Text or Voice Input)
            │
            ▼
Speech-to-Text (if Voice Input used)
            │
            ▼
Question Textbox Auto-filled
            │
            ▼
1. "Generate SQL" (Local Ollama AI / Pattern Matcher)
            │
            ▼
2. SQL Preview Box (User inspects / edits query)
            │
            ▼
3. "▶️ Execute Query" Button
            │
            ▼
4. Security Validator (is_safe_sql: rejects DROP, DELETE, etc.)
            │
            ▼
5. SQLite Database (data/app.db via pandas.read_sql_query)
            │
            ▼
6. Query Results Table (ttk.Treeview)
            │
            ▼
7. "Speak Result" (Optional offline pyttsx3 summary)
```

---

## 📥 Installation

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12 installed.
- Pip package manager.

### 2. Install Project Dependencies
Run the following command in your terminal from the project directory:

```bash
pip install -r requirements.txt
```

*(Includes `pandas`, `openpyxl`, `xlrd`, `requests`, `SpeechRecognition`, `pyttsx3`)*

### 3. Optional: Live Microphone Recording Package (`pyaudio`)
To enable live microphone input on Windows:

```bash
pip install pyaudio
```

---

## 🦙 Installing & Configuring Local Ollama AI

To enable local AI natural-language query generation:

1. **Download Ollama**: Install Ollama from [https://ollama.com/download](https://ollama.com/download).
2. **Pull a SQL Model**: Run in your terminal:
   ```bash
   ollama pull qwen2.5-coder:latest
   ```
3. **Configure `config.py`**:
   Verify or edit model settings in `config.py`:
   ```python
   OLLAMA_URL = "http://localhost:11434/api/generate"
   OLLAMA_MODEL = "qwen2.5-coder:latest"
   OLLAMA_TIMEOUT = 5
   ```
4. **Offline AI Notice**: If Ollama is not running, the application displays:
   `"Local AI service is unavailable. Please start Ollama or use SQL mode."`
   and uses built-in pattern matching or manual SQL mode.

---

## 🚀 How to Run the Application

Execute the main application launcher:

```bash
python app.py
```

---

## 🧪 Master Automated Test Suite

Run the master integration test script to verify all 15 system workflows programmatically:

```bash
python test_final.py
```

---

## ❓ Troubleshooting

| Issue / Symptom | Possible Cause | Solution |
| :--- | :--- | :--- |
| **"Please upload a dataset file first"** | No dataset uploaded yet | Click **Browse...** in Section 1, pick a CSV/Excel file, and click **Upload & Build SQLite DB**. |
| **"Local AI service is unavailable..."** | Ollama service is offline | Start Ollama (`ollama serve`) or use **Manual SQL Mode**. |
| **"Security Violation: Forbidden SQL..."** | Query contains prohibited words (`DROP`, `DELETE`) | Only read-only `SELECT` and `WITH` statements are allowed. |
| **"⚠️ Microphone unavailable"** | Missing `pyaudio` or no microphone connected | Install `pyaudio` via `pip install pyaudio` or use text input mode. |
| **"No records found"** | Query returned 0 rows | Check filter values or table names in your query. |

# DATAQUIRY_AI
