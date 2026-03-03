import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

from blueprint_scraper.scraper import Scraper
from blueprint_scraper.agent import create_summarizer_agent
from blueprint_scraper.output_handler import OutputHandler

def process_single_blueprint(bp_info, scraper, agent, output_handler, base_url):
    """
    Worker function to process a single blueprint: scrape, summarize, and save.
    """
    title = bp_info['title']
    href = bp_info['href']
    bp_id = bp_info.get('id')
    
    if not href:
        return f"   {title}: href not found."
    
    detail_url = urljoin(base_url, href)
    code = scraper.scrape_detail_page(detail_url)
    
    if not code:
        return f"   {title}: code snippet not found."
    
    summary = "No summary generated."
    try:
        # Agent invoke is sync, but ThreadPoolExecutor handles it in parallel
        result = agent.invoke({"blueprint_code": code})
        summary = result.get("summary", "No summary generated.")
    except Exception as agent_err:
        return f"   {title}: error generating summary: {agent_err}"
    
    # Save to output folder
    metadata = {
        "title": title,
        "url": detail_url,
        "id": bp_id
    }
    save_path = output_handler.save_blueprint(title, code, summary, bp_id, metadata)
    
    return {
        "title": title,
        "save_path": save_path,
        "summary": summary
    }

def run_scraper(url, limit=None, page_limit=None):
    """
    Main scraping loop that coordinates scraper, agent, and output handler in batches.
    """
    count = 0
    pages_scraped = 0
    current_page_url = url
    
    # Get batch size from environment variable, default to 5
    batch_size = int(os.getenv('MAX_CONCURRENCY', 5))
    
    # Initialize components
    scraper = Scraper()
    agent = create_summarizer_agent()
    output_handler = OutputHandler()

    while current_page_url and (limit is None or count < limit) and (page_limit is None or pages_scraped < page_limit):
        print(f"\nScraping list page: {current_page_url}...")
        
        blueprints_on_page, next_page_url = scraper.scrape_list_page(current_page_url)
        
        # Filter blueprints based on overall limit and whether they've been processed
        blueprints_to_process = []
        for bp in blueprints_on_page:
            if limit is not None and count >= limit:
                break
            
            if output_handler.is_processed(bp['id']):
                continue
                
            blueprints_to_process.append(bp)
            
            # Limit what we add to the process list for this page
            if limit is not None and (count + len(blueprints_to_process)) >= limit:
                break
            
        # Process in batches of 'batch_size'
        for i in range(0, len(blueprints_to_process), batch_size):
            batch = blueprints_to_process[i:i + batch_size]
            print(f"\nProcessing batch of {len(batch)} blueprints:")
            for bp in batch:
                print(f" - {bp['title']} (ID: {bp['id']})")
            
            with ThreadPoolExecutor(max_workers=batch_size) as executor:
                futures = {
                    executor.submit(process_single_blueprint, bp, scraper, agent, output_handler, url): bp 
                    for bp in batch
                }
                
                for future in as_completed(futures):
                    result = future.result()
                    if isinstance(result, dict):
                        count += 1
                        # Mark as processed in the output handler and persist it
                        bp_obj = futures[future]
                        output_handler.mark_as_processed(bp_obj['id'])
                        
                        print("-" * 40)
                        print(f"[{count}] TITLE: {result['title']}")
                        print(f"SAVED TO: {result['save_path']}")
                        print("-" * 40)
                    else:
                        print(result)
        
        pages_scraped += 1
        current_page_url = next_page_url
        
        if limit is not None and count >= limit:
            break
        
        if page_limit is not None and pages_scraped >= page_limit:
            break
