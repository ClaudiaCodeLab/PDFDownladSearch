# PDF Search and Download Tool

This repository contains two scripts for searching and downloading PDF documents from Google:
1. A basic version using web search
2. An advanced version using Google Custom Search API

## Requirements

- Python 3.6 or higher
- pip (Python package installer)

## Installation

1. Clone or download this repository
2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Create `.env` file and add your Google Custom Search API credentials:
     ```
     GOOGLE_API_KEY=your_api_key_here
     GOOGLE_CX_ID=your_cx_id_here
     ```

## Basic Version Usage (pdf_search_download.py)

Run the script using Python:
```bash
python pdf_search_download.py
```

The script will:
1. Prompt you to enter your search query
2. Ask for the number of results you want to retrieve (default is 10)
3. Create a `downloaded_pdfs` directory (if it doesn't exist)
4. Search for PDFs matching your query
5. Download the found PDFs to the `downloaded_pdfs` directory

## API Version Usage (pdf_search_download_api.py)

This version uses the Google Custom Search API for more reliable and permitted searching. To use this version:

1. Make sure you have set up your `.env` file with the required credentials
2. Run the script:
```bash
python pdf_search_download_api.py
```

The script will:
1. Load your API credentials from the `.env` file
2. Prompt for your search query
3. Ask for the number of results (default 10, maximum 100)
4. Save PDF links to a text file
5. Ask if you want to download the PDFs
6. If yes, download the PDFs to the `downloaded_pdfs` directory

### Getting API Credentials

1. **Get API Key**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Custom Search API
   - Create credentials (API key)

2. **Get Custom Search Engine ID**:
   - Go to [Google Programmable Search Engine](https://programmablesearch.google.com/create)
   - Create a new search engine
   - Get the Search Engine ID (cx value)

### Features

#### PDF Link Saving
- Automatically saves all found PDF links to a text file
- File name includes search query and timestamp
- Includes search metadata (query, date, number of results)
- Links are numbered for easy reference

#### PDF Download
- Browser-like headers to avoid download blocks
- Progress bar for each download
- Automatic PDF validation
- Detailed download logging
- Error handling for various scenarios:
  - Connection errors
  - Timeout issues
  - Invalid content types
  - Empty files
  - Server blocks

#### Log Files
The script creates two types of log files:

1. **PDF Links File** (`pdf_links_[query]_[timestamp].txt`):
   ```
   Search Query: your search query
   Date: 2024-03-21 15:30:45
   Number of PDFs found: 10
   --------------------------------------------------
   1. https://example.com/document1.pdf
   2. https://example.com/document2.pdf
   ...
   ```

2. **Download Log** (`download_log_[timestamp].txt`):
   ```
   Download Session: 2024-03-21 15:30:45
   Total URLs to download: 10
   --------------------------------------------------
   Attempting to download 1: https://example.com/document1.pdf
   Response Status Code: 200
   Response Headers: {...}
   Successfully downloaded to: downloaded_pdfs/document_1.pdf
   ...
   ```

### Troubleshooting

If you encounter "Not a valid PDF or unable to access" errors:

1. **Check the Download Log**:
   - Look for the specific error message
   - Check the response status code
   - Verify the content type in the headers

2. **Common Solutions**:
   - The script now uses browser-like headers to avoid blocks
   - Increased timeout to 30 seconds
   - Better PDF content type detection
   - Automatic retry for failed downloads
   - Verification of downloaded file size

3. **If Downloads Still Fail**:
   - Try downloading fewer files at once
   - Check your internet connection
   - Verify the PDF URLs are still valid
   - Some websites may block automated downloads

### Notes

- The script automatically adds `filetype:pdf` to your search query if not present
- Downloads are saved as `document_1.pdf`, `document_2.pdf`, etc.
- A progress bar shows the download progress for each file
- The script includes error handling for failed downloads
- There is a 1-second delay between downloads to avoid overwhelming servers
- Maximum of 100 results per search (API limitation)
- API credentials are loaded from `.env` file for security 