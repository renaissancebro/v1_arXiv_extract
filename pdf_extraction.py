import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
import arxiv
import csv
import io

# 1. Search arXiv
search = arxiv.Search(
    query="machine learning",
    max_results=5,
    sort_by=arxiv.SortCriterion.SubmittedDate
)

# 2. Prepare CSV
with open('arxiv_papers.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Title', 'Authors', 'Summary', 'PDF Link', 'Extracted Text'])

    for result in search.results():
        title = result.title
        authors = ', '.join([author.name for author in result.authors])
        summary = result.summary
        pdf_url = result.pdf_url

        print(f"Processing: {title}")

        # 3. Download PDF
        response = requests.get(pdf_url)
        if response.status_code != 200:
            print(f"Failed to download {pdf_url}")
            continue

        # Use BytesIO to treat bytes as file-like object
        pdf_file = io.BytesIO(response.content)
        reader = PdfReader(pdf_file)

        # Extract text (only first page to avoid huge output)
        extracted_text = reader.pages[0].extract_text() if reader.pages else ''

        # 4. Write to CSV
        writer.writerow([title, authors, summary, pdf_url, extracted_text[:500]])  # truncate text

print("Done! Data saved to arxiv_papers.csv")
