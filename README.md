# arxiv_loader
*arxiv_loader* is a Python module designed to scrape and save arXiv papers using the arXiv API. It provides functionality for searching by keywords, reading from a configuration file, and storing results in JSON format.

## Features
- Search for arXiv papers using keywords or phrases.
- Batch process multiple keywords.
- Save paper metadata (ID, title, URL, date, abstract, category, and authors) to a single JSON file.
- Supports saving and reading URLs from a configuration file.
- By default, searches are limited to the cs (Computer Science) category, but other categories can be specified.
## Installation
### Installing via pip

```shell
#Not yet available in PyPi. Use Git Clone Instead
pip install arxiv_loader
```
Alternatively, to install directly from the source:


```shell
git clone https://github.com/yourusername/arxiv_loader
cd arxiv_loader
pip install .
```
## Usage
1. Running from the Command Line
   The command-line tool arxiv-loader provides an interactive interface to scrape papers from arXiv.

```shell
arxiv-loader
```
You will be prompted with options to search by keyword, read from a config file, or fetch all papers.

2. Usage in Python Script
   You can also use arxiv_loader directly in your Python scripts:

```python
from arxiv_loader.arxiv_loader.loader import ArxivScraper

# Initialize the loader
loader = ArxivScrapper()

# Example: Search for papers using a keyword
loader.search_papers_by_keyword("machine learning")

# Example: Search for papers using multiple keywords. Uncomment to run next line
keywords = ["deep learning", "neural networks"]
# loader.search_multiple_keywords(keywords, combine=True)

# Example: Process papers from a config file. Uncomment to run next line
# loader.process_papers_from_urls('arxiv_urls.txt')
```
3. Options in the Command-Line Interface
   You will be presented with the following options after launching the arxiv-loader command:

   1. Search by Keywords: Enter one or more keywords to search for relevant arXiv papers. You can combine multiple keywords or run independent searches for each keyword.

        - Example input for multiple keywords: deep learning, neural networks.
        - Choose whether to combine the keywords into a single search or run independent searches. 
   2. Search by Configuration File: Provide a config file (e.g., arxiv_urls.txt) containing a list of arXiv URLs. The loader will scrape the paper metadata from the provided URLs.

   3. Fetch All Papers: Optionally, search through all papers in the arXiv database for a specific category, starting from the beginning.

4. Customizing the Search Category
   By default, the search is limited to papers in the cs (Computer Science) category. However, you can specify a different subject category when prompted, or pass it to the loader in your scripts:


```python
loader.search_papers_by_keyword("quantum computing", subject_category="physics")
```
5. Saving Results
   All the fetched paper metadata is saved to a JSON file in the following format:

```python
{
"cs_paper_info": {
"1": {
"id": "2105.02890",
"title": "An Introduction to Machine Learning",
"url": "https://arxiv.org/abs/2105.02890",
"date": "2023-08-12",
"abs": "This paper discusses...",
"cat": "cs.AI",
"authors": ["John Doe", "Jane Smith"]
},
...
}
}
```
6. Saving URLs in a Config File
   For keyword searches, the URLs of fetched papers can also be saved in a configuration file. The filename will be generated based on the search keyword(s).

Example:


```Enter a keyword: deep learning
URLs saved to config file: deep_learning_urls.txt
```

7. Generating FAISS Embeddings

```python
from arxiv_loader.arxiv_loader.loader import generate_faiss_embeddings

db_path = "path_to_your_database"
generate_faiss_embeddings(db_path)
```

8. Search with Embeddings

```python
from arxiv_loader.arxiv_loader.loader import search_by_embedding

db_path = "path_to_your_database"
query = "deep learning"
top_k = 5

results = search_by_embedding(db_path, query, top_k=top_k, search_by="title")

```


## License
This project is licensed under the MIT License.

This README.md includes installation instructions, usage examples for both the command-line tool and the Python script interface, and detailed descriptions of features. Adjust URLs, author details, and descriptions as needed for your specific project.










