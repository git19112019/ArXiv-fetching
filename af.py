import spacy
from collections import Counter
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import json

# Constants: URL cơ bản cho ArXiv API
API_URL = "http://export.arxiv.org/api/query?"

# Tải mô hình ngôn ngữ của SpaCy
nlp = spacy.load("en_core_web_sm")

def fetch_arxiv_papers(keyword, num_results=5):
    """
    Fetch papers from ArXiv using the API sorted by the most recent submission date.
    """
    query_params = {
        'search_query': f"all:{keyword.strip()}",
        'start': 0,
        'max_results': num_results,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    query_url = API_URL + urllib.parse.urlencode(query_params)

    try:
        response = urllib.request.urlopen(query_url)
        data = response.read().decode('utf-8')
        return parse_arxiv_results(data)
    except Exception as e:
        print(f"Error fetching papers: {e}")
        return []

def parse_arxiv_results(data):
    """
    Parse XML data returned from ArXiv API and extract paper details.
    """
    namespace = {'atom': 'http://www.w3.org/2005/Atom'}
    root = ET.fromstring(data)
    entries = root.findall('atom:entry', namespace)

    papers = []
    for entry in entries:
        try:
            title = entry.find('atom:title', namespace).text.strip()
            authors = [author.find('atom:name', namespace).text for author in entry.findall('atom:author', namespace)]
            summary = entry.find('atom:summary', namespace).text.strip()
            papers.append({'title': title, 'authors': authors, 'summary': summary})
        except AttributeError:
            continue
    return papers

def extract_svo(text):
    """
    Extract Subject-Verb-Object structures from text using SpaCy.
    """
    doc = nlp(text)
    svos = []
    for token in doc:
        if token.dep_ == "ROOT":
            subjects = [w.text for w in token.lefts if w.dep_ in ("nsubj", "nsubjpass")]
            objects = [w.text for w in token.rights if w.dep_ in ("dobj", "pobj", "attr")]
            if subjects and objects:
                svos.append((subjects[0], token.text, objects[0]))
    return svos

def emphasize_keywords(svos):
    """
    Emphasize the object in SVO structures for keyword extraction.
    """
    emphasized = []
    for svo in svos:
        # Chỉ nhấn mạnh đối tượng (object)
        emphasized.append(svo[2])
    return emphasized

def summarize_papers(papers):
    """
    Apply text processing framework to ArXiv paper summaries.
    """
    for paper in papers:
        print(f"Title: {paper['title']}")
        print(f"Authors: {', '.join(paper['authors'])}")
        
        # Phân tích SVO
        svos = extract_svo(paper['summary'])
        
        # Nhấn mạnh từ khóa (object)
        keywords = emphasize_keywords(svos)

        print("Extracted Keywords:")
        for keyword in keywords:
            print(f"- {keyword}")
        
        print("=" * 50)

def main():
    """
    Entry point of the program. Fetch ArXiv papers and process their summaries.
    """
    keyword = input("Enter search keyword: ").strip()
    try:
        num_results = int(input("Enter number of results to display: "))
        papers = fetch_arxiv_papers(keyword, num_results)
        if papers:
            summarize_papers(papers)
        else:
            print("No papers found.")
    except ValueError:
        print("Please enter a valid number for results.")

if __name__ == '__main__':
    main()
