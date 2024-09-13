import time
import requests
import xml.etree.ElementTree as ET
import json

class ArxivScraper:

    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query?"
        self.max_results_per_query = 100  # arXiv allows up to 100 results per query
        self.delay = 3  # Delay between requests to avoid hitting rate limits

    def fetch_papers_by_keyword(self, keyword, subject_category="cs", start=0):
        """Fetch a batch of arXiv papers based on a keyword and subject category starting from a specific index."""
        query = f"search_query=cat:{subject_category}+all:%22{keyword}%22&start={start}&max_results={self.max_results_per_query}&sortBy=submittedDate&sortOrder=ascending"
        print(query)
        try:
            response = requests.get(self.base_url + query)
            response.raise_for_status()  # Check for HTTP errors
            # print(response, response.content)
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error fetching papers by keyword '{keyword}' in category '{subject_category}' at start={start}: {e}")
            return None

    def fetch_paper_by_url(self, url):
        """Fetch a specific paper's metadata by its arXiv URL."""
        paper_id = url.split('/')[-1]
        query = f"http://export.arxiv.org/api/query?id_list={paper_id}"
        try:
            response = requests.get(query)
            response.raise_for_status()  # Check for HTTP errors
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error fetching paper by URL '{url}': {e}")
            return None

    def parse_papers(self, data):
        """Parse the XML data returned by the arXiv API and extract paper information."""
        try:
            root = ET.fromstring(data)
            papers = []
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                paper = {}
                paper_id_url = entry.find('{http://www.w3.org/2005/Atom}id').text
                paper['id'] = paper_id_url.split('/')[-1]  # Extract the ID part from the URL
                paper['title'] = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
                paper['summary'] = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
                paper['published'] = entry.find('{http://www.w3.org/2005/Atom}published').text
                paper['authors'] = [author.find('{http://www.w3.org/2005/Atom}name').text for author in entry.findall('{http://www.w3.org/2005/Atom}author')]

                # arXiv ID and category
                # paper['cat'] = paper['id'].split('.')[0]
                # print(entry.find('{http://www.w3.org/2005/Atom}category'))
                paper['cat'] = entry.find('{http://www.w3.org/2005/Atom}category').attrib['term'].strip()
                paper['url'] = paper_id_url

                papers.append(paper)

            return papers
        except ET.ParseError as e:
            print(f"Error parsing XML data: {e}")
            return []

    def save_all_papers_as_json(self, all_papers):
        """Save all collected papers in a single JSON file."""
        try:
            cs_paper_info = {}
            for idx, paper in enumerate(all_papers, start=1):
                cs_paper_info[str(idx)] = {
                    "id": paper['id'],
                    "title": paper['title'],
                    "url": paper['url'],
                    "date": paper['published'],
                    "abs": paper['summary'],
                    "cat": paper['cat'],
                    "authors": paper['authors']
                }

            data = {"cs_paper_info": cs_paper_info}
            with open('arxiv_papers.json', 'w') as f:
                json.dump(data, f, indent=4)

            print("Successfully saved all papers to arxiv_papers.json")
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error saving papers to JSON: {e}")

    def save_urls_to_config(self, papers, keyword):
        """Save fetched URLs into a config file named after the keyword."""
        config_filename = f"{keyword.replace(' ', '_')}_urls.txt"
        try:
            with open(config_filename, 'w') as f:
                for paper in papers:
                    f.write(f"{paper['url']}\n")
            print(f"Successfully saved URLs to {config_filename}")
        except IOError as e:
            print(f"Error saving URLs to config file '{config_filename}': {e}")

    def read_urls_from_file(self, config_file):
        """Read arXiv paper URLs from a configuration file."""
        try:
            with open(config_file, 'r') as f:
                urls = [line.strip() for line in f.readlines() if line.strip()]
            return urls
        except IOError as e:
            print(f"Error reading URLs from config file '{config_file}': {e}")
            return []

    def search_papers_by_keyword(self, keyword, subject_category="cs"):
        """Search for papers on arXiv using a keyword and subject category, and save the URLs to a config file."""
        start = 0
        all_papers = []

        while True:
            print(f"Fetching papers for keyword '{keyword}' in category '{subject_category}' starting from {start}...")
            data = self.fetch_papers_by_keyword(keyword, subject_category, start=start)
            if data:
                papers = self.parse_papers(data)
                if not papers:
                    print(f"No more papers found for keyword '{keyword}' in category '{subject_category}'.")
                    break
                all_papers.extend(papers)

                start += self.max_results_per_query
                time.sleep(self.delay)
            else:
                break

        if all_papers:
            self.save_urls_to_config(all_papers, keyword)
            self.save_all_papers_as_json(all_papers)

    def process_papers_from_urls(self, config_file):
        """Fetch and process papers from arXiv based on URLs in a config file."""
        urls = self.read_urls_from_file(config_file)
        all_papers = []

        for url in urls:
            print(f"Fetching paper from {url}...")
            data = self.fetch_paper_by_url(url)
            if data:
                paper = self.parse_papers(data)
                all_papers.extend(paper)
                time.sleep(self.delay)

        if all_papers:
            self.save_all_papers_as_json(all_papers)

    def search_multiple_keywords(self, keywords, combine=False, subject_category="cs"):
        """Search for papers using multiple keywords and a subject category. Optionally combine the keywords into a single search."""
        if combine:
            combined_keywords = " OR ".join(keywords)
            print(f"Performing a combined search for keywords: {', '.join(keywords)} in category '{subject_category}'")
            self.search_papers_by_keyword(combined_keywords, subject_category)
        else:
            for keyword in keywords:
                print(f"Searching for papers with keyword: {keyword} in category '{subject_category}'")
                self.search_papers_by_keyword(keyword, subject_category)

def main():
    scraper = ArxivScraper()

    print("Choose an option:")
    print("1. Search for papers by single or multiple keywords")
    print("2. Search for papers by reading URLs from a config file")
    print("3. Fetch all papers (starting from the beginning)")

    option = input("Enter the option number (1/2/3): ").strip()

    # Subject category selection
    default_category = "cs"
    subject_category = input(f"Enter the subject category for arXiv (default is '{default_category}'): ").strip() or default_category

    try:
        if option == "1":
            multiple_keywords = input("Do you want to search with multiple keywords? (yes/no): ").strip().lower() == "yes"
            if multiple_keywords:
                keywords = input("Enter keywords separated by commas: ").strip().split(',')
                combine = input("Combine keywords into a single search? (yes/no): ").strip().lower() == "yes"
                scraper.search_multiple_keywords([kw.strip() for kw in keywords], combine=combine, subject_category=subject_category)
            else:
                keyword = input("Enter a keyword to search for papers: ").strip()
                scraper.search_papers_by_keyword(keyword, subject_category)

        elif option == "2":
            config_file = input("Enter the path to the config file (e.g., arxiv_urls.txt): ").strip()
            scraper.process_papers_from_urls(config_file)

        elif option == "3":
            # Search through all papers by starting from the beginning of arXiv
            scraper.search_papers_by_keyword("", subject_category)

        else:
            print("Invalid option. Please choose 1, 2, or 3.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()