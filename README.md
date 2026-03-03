# BlueprintUE Scraper & AI Summarizer

A modular Python-based scraper that extracts Unreal Engine blueprint code from [blueprintue.com](https://blueprintue.com/type/blueprint/) and uses a LangGraph-powered AI agent to generate detailed technical summaries.

## Features

- **Automated Scraping**: Fetches blueprint titles, unique IDs, and full source code.
- **AI-Powered Summarization**: Uses OpenAI's advanced models (via LangChain/LangGraph) to provide:
  - **High-Level Summary**: Quick overview for UE developers.
  - **Detailed Breakdown**: Step-by-step technical analysis of nodes and logic flow.
- **Parallel Processing**: Efficiently processes blueprints in configurable batches.
- **Resume Capability**: Tracks processed blueprints to skip already scraped content if the script is restarted.
- **Modular Architecture**: Clean separation between scraping, processing, and AI logic.

## Prerequisites

- Python 3.8+
- [OpenAI API Key](https://platform.openai.com/api-keys)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd blueprint-scraper
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy the example environment file and fill in your details:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your `OPENAI_API_KEY`.

## Configuration (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | **Required** |
| `OPENAI_MODEL` | OpenAI model identifier | `gpt-4o-mini` |
| `MAX_CONCURRENCY`| Number of blueprints to process in parallel | `5` |
| `DEBUG` | Enable debug logging | `True` |

## Usage

Run the scraper using the entry point:

```bash
# Scrape the first 5 blueprints (default)
python3 main.py

# Scrape a specific number of blueprints
python3 main.py -n 25
```

The script will handle pagination automatically if `-n` is greater than 20.

## Output Structure

Scraped data is saved in the `output/` directory:
```text
output/
├── <blueprint-title>-<id>/
│   ├── blueprint.txt   # Raw blueprint code
│   ├── summary.md      # AI-generated technical report
│   └── metadata.json   # Source URL and title info
└── processed_blueprints.json # Tracks completed IDs
```

## How to Get an OpenAI API Key

1. Go to the [OpenAI Platform](https://platform.openai.com/).
2. Sign up or log in to your account.
3. Navigate to the **API Keys** section in the left sidebar (or under your profile icon).
4. Click **Create new secret key**.
5. Give the key a name (e.g., "Blueprint Scraper") and click **Create secret key**.
6. **Copy and save the key immediately**; you won't be able to see it again.
7. Ensure you have credits in your [Billing settings](https://platform.openai.com/account/billing) for the API to function.

## Project Structure

- `main.py`: Entry point for the CLI.
- `blueprint_scraper/`:
    - `processor.py`: Orchestrates the scraping and AI pipeline.
    - `scraper.py`: Handles HTTP requests and HTML parsing.
    - `agent.py`: LangGraph implementation of the summarization agent.
    - `output_handler.py`: Manages file saving and resume logic.
