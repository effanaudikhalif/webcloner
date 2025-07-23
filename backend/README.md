# Backend Setup

This backend uses Python 3.12+ and requires several dependencies for web scraping and AI processing.

## Prerequisites

- Python 3.12 or higher
- Homebrew (for Python installation on macOS)

## Installation

1. **Install Python 3.12** (if not already installed):
   ```bash
   brew install python@3.12
   ```

2. **Create and activate virtual environment**:
   ```bash
   # Create virtual environment
   /opt/homebrew/opt/python@3.12/bin/python3.12 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**:
   ```bash
   playwright install
   ```

5. **Set up environment variables**:
   Create a `.env` file in the backend directory with your API keys:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key
   BROWSERBASE_API_KEY=your_browserbase_api_key
   BROWSERBASE_PROJECT_ID=your_browserbase_project_id
   ```

## Quick Start

1. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   # or use the convenience script:
   ./activate.sh
   ```

2. **Run the FastAPI server**:
   ```bash
   cd app
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## Dependencies

- **FastAPI**: Web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **Pydantic**: Data validation using Python type annotations
- **Python-dotenv**: Environment variable management
- **Anthropic**: Claude AI API client
- **Playwright**: Browser automation for web scraping
- **Aiohttp**: Async HTTP client/server
- **BeautifulSoup4**: HTML/XML parsing
- **Stagehand**: Browserbase SDK for AI-powered browser automation

## API Endpoints

The backend provides endpoints for:
- Web scraping and site recreation
- CSS filtering and processing
- AI-powered content analysis

## Troubleshooting

- If you get syntax errors with `match` statements, ensure you're using Python 3.10+
- If Playwright browsers aren't working, run `playwright install` again
- Make sure your `.env` file contains valid API keys 