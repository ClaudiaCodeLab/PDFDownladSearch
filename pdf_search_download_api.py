import os
import requests
from tqdm import tqdm
import json
from urllib.parse import quote
import time
from datetime import datetime
from dotenv import load_dotenv

class GoogleCustomSearchPDFDownloader:
    def __init__(self, api_key=None, cx_id=None):
        """
        Initialize the downloader with Google Custom Search credentials.
        
        Args:
            api_key (str, optional): Google Custom Search API key
            cx_id (str, optional): Custom Search Engine ID
        """
        # Load environment variables
        load_dotenv()
        
        # Use provided credentials or get from environment variables
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.cx_id = cx_id or os.getenv('GOOGLE_CX_ID')
        
        if not self.api_key or not self.cx_id:
            raise ValueError("API key and CX ID are required. Please set them in .env file or provide them directly.")
            
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
    def save_links_to_file(self, urls, query):
        """
        Save PDF links to a text file with timestamp.
        
        Args:
            urls (list): List of PDF URLs
            query (str): Search query used
        """
        # Create a timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pdf_links_{timestamp}.txt"
        
        # Create a safe query for the filename
        safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if safe_query:
            filename = f"pdf_links_{safe_query}_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Search Query: {query}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Number of PDFs found: {len(urls)}\n")
            f.write("-" * 50 + "\n\n")
            
            for i, url in enumerate(urls, 1):
                f.write(f"{i}. {url}\n")
        
        print(f"\nPDF links saved to: {filename}")
        
    def search_pdfs(self, query, num_results=10):
        """
        Search for PDFs using Google Custom Search API.
        
        Args:
            query (str): Search query
            num_results (int): Number of results to retrieve (max 100)
        
        Returns:
            list: List of PDF URLs found
        """
        # Validate query
        if not query or query.strip() == "":
            print("Error: Search query cannot be empty")
            return []
            
        # Clean and encode the query
        query = query.strip()
        
        pdf_urls = []
        num_requests = min(10, (num_results + 9) // 10)
        
        for i in range(num_requests):
            start_index = i * 10 + 1
            
            # Prepare search parameters
            params = {
                'key': self.api_key,
                'cx': self.cx_id,
                'q': f"{query} filetype:pdf",
                'start': start_index,
                'fileType': 'pdf',
                'alt': 'json'
            }
            
            try:
                response = requests.get(self.base_url, params=params)
                
                # Add more detailed error handling
                if response.status_code == 400:
                    print("Error: Bad Request - Please check your API key and CX ID")
                    break
                elif response.status_code == 403:
                    print("Error: Authentication failed - Please verify your API key")
                    break
                elif response.status_code != 200:
                    print(f"Error: API request failed with status code {response.status_code}")
                    break
                    
                response.raise_for_status()
                search_results = response.json()
                
                if 'items' in search_results:
                    for item in search_results['items']:
                        if 'link' in item and item['link'].lower().endswith('.pdf'):
                            pdf_urls.append(item['link'])
                            if len(pdf_urls) >= num_results:
                                # Save links to file before returning
                                self.save_links_to_file(pdf_urls, query)
                                return pdf_urls[:num_results]
                                
            except requests.exceptions.RequestException as e:
                print(f"Error during API request: {str(e)}")
                break
            except json.JSONDecodeError as e:
                print(f"Error parsing API response: {str(e)}")
                break
                
            # Respect API rate limits
            time.sleep(1)
            
        # Save links to file if we have any results
        if pdf_urls:
            self.save_links_to_file(pdf_urls, query)
            
        return pdf_urls
    
    def download_pdfs(self, urls, output_dir="downloaded_pdfs"):
        """
        Download PDFs from the provided URLs.
        
        Args:
            urls (list): List of PDF URLs to download
            output_dir (str): Directory to save downloaded PDFs
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Create a timestamp for the download log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_log = f"download_log_{timestamp}.txt"
        
        with open(download_log, 'w', encoding='utf-8') as f:
            f.write(f"Download Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total URLs to download: {len(urls)}\n")
            f.write("-" * 50 + "\n\n")
            
            for i, url in enumerate(urls, 1):
                try:
                    filename = os.path.join(output_dir, f"document_{i}.pdf")
                    
                    print(f"\nDownloading: {url}")
                    f.write(f"\nAttempting to download {i}: {url}\n")
                    
                    # Add headers to mimic a browser request
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'application/pdf,application/x-pdf,application/octet-stream',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Connection': 'keep-alive',
                    }
                    
                    response = requests.get(url, stream=True, headers=headers, timeout=30)
                    
                    # Log response details for debugging
                    f.write(f"Response Status Code: {response.status_code}\n")
                    f.write(f"Response Headers: {dict(response.headers)}\n")
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '').lower()
                        content_length = response.headers.get('content-length', 0)
                        
                        # Check if the content type indicates a PDF
                        is_pdf = any(pdf_type in content_type for pdf_type in ['application/pdf', 'application/x-pdf', 'application/octet-stream'])
                        
                        if is_pdf or url.lower().endswith('.pdf'):
                            total_size = int(content_length) if content_length else 0
                            
                            with open(filename, 'wb') as pdf_file, tqdm(
                                desc=os.path.basename(filename),
                                total=total_size,
                                unit='iB',
                                unit_scale=True,
                                unit_divisor=1024,
                            ) as pbar:
                                for data in response.iter_content(chunk_size=1024):
                                    size = pdf_file.write(data)
                                    pbar.update(size)
                            
                            # Verify the downloaded file is a PDF
                            if os.path.getsize(filename) > 0:
                                print(f"Successfully downloaded: {filename}")
                                f.write(f"Successfully downloaded to: {filename}\n")
                            else:
                                print(f"Error: Downloaded file is empty")
                                f.write(f"Error: Downloaded file is empty\n")
                                os.remove(filename)
                        else:
                            print(f"Skipping {url} - Content type is not PDF: {content_type}")
                            f.write(f"Failed to download: {url} - Content type is not PDF: {content_type}\n")
                    else:
                        print(f"Skipping {url} - HTTP Status Code: {response.status_code}")
                        f.write(f"Failed to download: {url} - HTTP Status Code: {response.status_code}\n")
                        
                except requests.exceptions.Timeout:
                    print(f"Error downloading {url}: Request timed out")
                    f.write(f"Error downloading {url}: Request timed out\n")
                except requests.exceptions.ConnectionError:
                    print(f"Error downloading {url}: Connection error")
                    f.write(f"Error downloading {url}: Connection error\n")
                except Exception as e:
                    print(f"Error downloading {url}: {str(e)}")
                    f.write(f"Error downloading {url}: {str(e)}\n")
                
                # Add a small delay between downloads
                time.sleep(1)
        
        print(f"\nDownload log saved to: {download_log}")

def main():
    try:
        # Initialize downloader with credentials from .env file
        downloader = GoogleCustomSearchPDFDownloader()
        
        # Get search parameters
        query = input("Enter your search query: ").strip()
        if not query:
            print("Error: Search query cannot be empty")
            return
            
        num_results = input("Enter number of results to retrieve (default 10, max 100): ")
        
        try:
            num_results = min(int(num_results), 100)
        except (ValueError, TypeError):
            num_results = 10
        
        # Perform search
        print(f"\nSearching for: {query}")
        pdf_urls = downloader.search_pdfs(query, num_results)
        
        if not pdf_urls:
            print("No PDF results found.")
            return
            
        print(f"\nFound {len(pdf_urls)} PDF results.")
        
        # Ask user if they want to download the PDFs
        download_choice = input("\nDo you want to download these PDFs? (yes/no): ").strip().lower()
        if download_choice == 'yes':
            # Download PDFs
            downloader.download_pdfs(pdf_urls)
        else:
            print("\nPDF links have been saved to a text file. You can download them later.")
            
    except ValueError as e:
        print(f"Error: {str(e)}")
        print("\nPlease make sure you have created a .env file with your API credentials.")
        print("You can copy .env.example to .env and fill in your credentials.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main() 