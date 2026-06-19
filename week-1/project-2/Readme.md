# 🥇 Gold Data Agent (ETL + AI Chat)

An intelligent agent that fetches real-time gold futures data (`GC=F`) from Yahoo Finance, processes it into a structured SQLite database (ETL pipeline), and answers your questions using a mix of its internal data and live web searches. Built with LangGraph, Groq/LLaMA, and a Streamlit chat interface.

## ✨ Features

- **📊 ETL Pipeline**: Automatically fetches gold data, transforms it, and stores it in a local SQLite database.
- **🧠 Agentic AI**: Powered by LangGraph with short-term memory (maintains chat context until you refresh the page).
- **🔍 Web Search**: Equipped with a Tavily search tool to answer questions beyond the stored data.
- **⚙️ Dual LLM Support**: Works with **Groq Cloud** (for fast inference) or **local Ollama** models.
- **🖥️ Streamlit Client**: Beautiful, interactive chat UI with "New Conversation" reset functionality.

## 🛠️ Tech Stack

- **Framework**: LangChain / LangGraph
- **LLM Backend**: Groq (`llama-4-scout`) or Ollama (`qwen2.5`)
- **Data Source**: `yfinance` (Yahoo Finance)
- **Search Tool**: Tavily
- **Database**: SQLite (via SQLAlchemy)
- **Memory**: `InMemorySaver` (Short-term, session-based)
- **Frontend**: Streamlit

## 📋 Prerequisites

- Python 3.9+
- Poetry or pip (virtual environment recommended)
- API Keys for **Groq** and **Tavily**

## ⚙️ Environment Variables

Create a `.env` file in the project root directory and populate it with the following fields:

```env
# Groq API Key (required if LOCAL_MODEL=False)
GROQ_API_KEY = "gsk_..."

# Tavily API Key for web search functionality
TAVILY_API_KEY = "tvly-..."

# Ollama model name (used when LOCAL_MODEL=True)
MODEL_NAME = "qwen2.5-1.5b-instruct:latest"

# Groq model name (used when LOCAL_MODEL=False)
GROQ_MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"

# Path to the SQLite database file
DATABASE_PATH = "database/data.db"

# LLM temperature (creativity vs. determinism)
TEMPERATURE = 0.5

# Toggle between local Ollama and Groq Cloud
LOCAL_MODEL = False

# The ticker symbol for gold futures (Do NOT change unless you want silver/other)
TRICKER = "GC=F"

# Enable/disable proxy settings for network requests.
USE_PROXY = True
```

> **Note**: The variable is named `TRICKER` in the codebase (a playful typo for `TICKER`). Make sure to use exactly `TRICKER` in your `.env` file.

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/gold-data-agent.git
   cd gold-data-agent
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   *(If `requirements.txt` is not yet created, install these manually)*:
   ```bash
   pip install streamlit langchain langgraph langchain-groq langchain-community \
               tavily-python yfinance sqlalchemy python-dotenv
   ```

4. **Create the database directory**:
   ```bash
   mkdir database
   ```

5. **Set up the `.env`** file as described above.

## ▶️ Usage

To start the chat interface, run the following command in your terminal:

```bash
streamlit run app.py
```

### How to interact with the Agent

1. **Ask about gold prices**: e.g., *"What was the price of gold yesterday?"* – The agent will query the SQLite database.
2. **Ask for news or macroeconomic impacts**: e.g., *"What affects the gold price today?"* – The agent will trigger the Tavily web search tool.
3. **Complex multi-step tasks**: e.g., *"Fetch the latest GC=F data, transform it, save it to the DB, and tell me the average price of the last 3 entries."*
4. **Memory**: Try a two-part question:
   - *"Remember the closing price of gold today."*
   - *"Based on that, should I buy or sell?"* – The agent retains the context.

> **Reset Context**: To clear the agent's short-term memory, either click the **"🔄 New Conversation"** button in the UI, or refresh the browser page (F5).

## 🧠 Architecture & Memory

- **Short-Term Memory**: The agent uses `InMemorySaver` (a LangGraph checkpointer). Each Streamlit session gets a unique `thread_id`. As long as the page is not refreshed, all messages under that `thread_id` are passed to the LLM as context.
- **Refreshing the Page**: Generates a new `thread_id`. The previous conversation context is discarded automatically (since the memory lives in the server's RAM and the old thread is no longer referenced).

## 🔧 Advanced Configuration

- **Switch to Local Model**: Set `LOCAL_MODEL = True` in `.env`. Ensure you have Ollama running locally and the `MODEL_NAME` pulled (`ollama pull qwen2.5-1.5b-instruct`).
- **Change Asset**: If you want to track Silver (`SI=F`) or another future, change the `TRICKER` variable (though the code is highly optimized for `GC=F`).

## 🤝 Contributing

Feel free to fork this repository and submit pull requests for improvements, bug fixes, or additional tools.

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

Made with ❤️.