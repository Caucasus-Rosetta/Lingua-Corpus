import requests
from bs4 import BeautifulSoup
import os
import time

# Base URL of the website
base_url = "https://www.smikbr.ru"

# URL of the page you want to scrape
starting_url = "https://www.smikbr.ru/arhivap"

# Directory to save the PDFs
download_dir = "downloaded_pdfs"
os.makedirs(download_dir, exist_ok=True)

# Function to download a PDF
def download_pdf(pdf_url, unique_identifier):
    try:
        response = requests.get(pdf_url, timeout=10)
        if response.status_code == 200:
            # Extract the PDF file name from the URL (e.g., the last part "24.pdf" or "27.pdf")
            pdf_file_name = pdf_url.split('/')[-1]  # This will get "24.pdf" from "/03/24.pdf"
            # Create a unique name by combining the unique identifier and the extracted PDF name
            pdf_name = f"{unique_identifier}_{pdf_file_name}"
            pdf_path = os.path.join(download_dir, pdf_name)
            
            with open(pdf_path, 'wb') as pdf_file:
                pdf_file.write(response.content)
            print(f"Downloaded: {pdf_name}")
        else:
            print(f"Failed to download: {pdf_url} (status code: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {pdf_url}: {e}")
        time.sleep(5)  # Wait 5 seconds before retrying

# Function to scrape a page and find PDF links
def scrape_page(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.content, "html.parser")

        # Find all <a> tags that contain the href to PDF pages
        pdf_page_links = soup.find_all('a', href=True)

        for link in pdf_page_links:
            href = link['href']
            if href.startswith("/ap"):  # Assuming the PDF links start with "/ap"
                pdf_page_url = base_url + href
                print(f"Found PDF page: {pdf_page_url}")

                # Now visit this page to find the actual PDF link
                pdf_page_response = requests.get(pdf_page_url, timeout=10)
                pdf_page_soup = BeautifulSoup(pdf_page_response.content, "html.parser")

                # Extract all links that lead to PDF files
                pdf_links = pdf_page_soup.find_all('a', href=lambda x: x and x.endswith('.pdf'))

                # Iterate over each found PDF link
                for pdf_link in pdf_links:
                    pdf_url = base_url + pdf_link['href']
                    
                    # Use the unique identifier from the original link (e.g., "ap2024_125")
                    unique_identifier = href.split('/')[-1]
                    print(f"Found PDF: {pdf_url}")
                    
                    # Download the PDF using the unique name
                    download_pdf(pdf_url, unique_identifier)

    except requests.exceptions.RequestException as e:
        print(f"Error scraping page {url}: {e}")
        time.sleep(5)  # Wait 5 seconds before retrying

# Iterate over the pages with pagination (if any)
def scrape_all_pages(starting_url):
    current_page = 0
    while True:
        page_url = f"{starting_url}?page={current_page}"
        print(f"Scraping page: {page_url}")
        
        try:
            response = requests.get(page_url, timeout=10)
            response.raise_for_status()  # Raise an error for bad status codes
            
            # Scrape the current page
            scrape_page(page_url)

            # Check if there's a next page by looking for the "next" button
            soup = BeautifulSoup(response.content, "html.parser")
            next_button = soup.find('a', text='next')  # Adjust this based on the site's pagination
            if not next_button:
                print("No more pages found.")
                break

            current_page += 1

        except requests.exceptions.RequestException as e:
            print(f"Error loading page {page_url}: {e}")
            time.sleep(5)  # Wait 5 seconds before retrying

# Start scraping
scrape_all_pages(starting_url)
