import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
import arxiv
import io
import csv
import time
import ollama

def summarize_text(text, model='mistral'):
    prompt = f"Summarize the following text in 5 sentences:\n\n{text}"
    response = ollama.chat(
        model=model,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response['message']['content']

# Step 1: Scrape paper IDs from arXiv AI category page
base_url = "https://arxiv.org"
ai_url = f"{base_url}/list/cs.AI/recent"
response = requests.get(ai_url)
soup = BeautifulSoup(response.text, 'html.parser')

papers = []
for dt in soup.find_all('dt'):
    link_tag = dt.find('a', title='Abstract')
    if link_tag:
        paper_id = link_tag['href'].split('/')[-1]
        papers.append(paper_id)

# Step 2: Process papers and save to CSV
with open('ai_papers.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Title', 'Authors', 'Summary', 'PDF Link', 'Extracted Text', 'Ollama Summary'])

    for paper_id in papers[:5]:  # limit to first 5 papers
        try:
            # Get metadata from arxiv API
            paper = next(arxiv.Client().results(arxiv.Search(id_list=[paper_id])))
            title = paper.title
            authors = ', '.join([author.name for author in paper.authors])
            summary = paper.summary
            pdf_url = paper.pdf_url

            print(f"\nProcessing: {title}")

            # Download PDF
            pdf_resp = requests.get(pdf_url)
            if pdf_resp.status_code != 200:
                print(f"Failed to download {pdf_url}")
                continue

            # Extract text from PDF (first page)
            pdf_file = io.BytesIO(pdf_resp.content)
            reader = PdfReader(pdf_file)
            extracted_text = reader.pages[0].extract_text() if reader.pages else ''
            print("Extracted text from PDF.")

            # Summarize with Ollama
            ollama_summary = summarize_text(extracted_text)
            print("Generated Ollama summary.")

            # Write row to CSV (truncate extracted text to 500 chars)
            writer.writerow([title, authors, summary, pdf_url, extracted_text[:500], ollama_summary])

            time.sleep(2)  # polite delay to avoid hammering arXiv
        except Exception as e:
            print(f"Error processing {paper_id}: {e}")

