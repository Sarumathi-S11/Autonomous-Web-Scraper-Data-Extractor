# 🚀 Autonomous Web Scraper & Data Extractor

## 📌 Project Overview
The Autonomous Web Scraper & Data Extractor is a Python-based web scraping application designed to automatically collect structured information from multi-page websites.

It uses Requests and BeautifulSoup4 to retrieve and parse HTML content, navigate pagination, and export extracted records into CSV and JSON formats.

## 🎯 Objectives
- Automate data extraction from paginated websites.
- Parse HTML elements using BeautifulSoup4.
- Handle HTTP errors and request retries.
- Extract structured product information.
- Export clean datasets in CSV and JSON formats.

## 🛠️ Technologies Used
- Python 3
- Requests
- BeautifulSoup4
- JSON
- CSV

## 📊 Dataset Information
**Source:** Books to Scrape

**Records extracted:** 1,000

**Attributes:**
- Title
- Price
- Availability
- Rating
- Category
- Product URL
- Source Page

## ⚙️ Key Features
- Automatic pagination handling
- User-Agent headers
- Retry and exception handling
- Duplicate record removal
- Structured CSV and JSON export

## ▶️ How to Run

```bash
pip install -r requirements.txt
python scraper.py
```

## 📁 Project Structure

```text
Autonomous-Web-Scraper-Data-Extractor/
├── scraper.py
├── requirements.txt
├── README.md
└── data/
    ├── scraped_books.csv
    └── scraped_books.json
```

## 📌 Output
The scraper generates:
- `scraped_books.csv`
- `scraped_books.json`

## ⚠️ Disclaimer
This project was developed for educational purposes using Books to Scrape, a practice website. Always respect website terms and access policies.

## 👩‍💻 Author
Sarumathi S

**GitHub:** [Sarumathi-S11](https://github.com/Sarumathi-S11)
