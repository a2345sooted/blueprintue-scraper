import os
import argparse
from dotenv import load_dotenv

from blueprint_scraper.processor import run_scraper

# Load environment variables from .env file
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="A simple Python scraper.")
    parser.add_argument("-n", "--limit", type=int, help="Number of blueprints to scrape", default=5)
    
    args = parser.parse_args()
    
    target_url = os.getenv('TARGET_URL', 'https://blueprintue.com/type/blueprint/')
    
    # Check for API Key
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not found in environment variables. Summarization may fail.")
    
    run_scraper(target_url, limit=args.limit)

if __name__ == '__main__':
    main()
