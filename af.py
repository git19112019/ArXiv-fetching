import spacy
from collections import Counter
import urllib.error
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

def preprocess_text(text):
    """
    Preprocess text by removing stop words using SpaCy.
    """
    doc = nlp(text)
    return " ".join([token.text for token in doc if token.is_alpha and not token.is_stop])

def extract_keywords(text, top_n=10):
    """
    Extract keywords based on frequency from the processed text.
    """
    doc = nlp(text)
    keywords = [token.text for token in doc if token.is_alpha and not token.is_stop]
    keyword_freq = Counter(keywords)
    return keyword_freq.most_common(top_n)

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

def save_to_file(papers, filename="papers.json"):
    """
    Save paper data to a JSON file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving data: {e}")

def summarize_papers(papers):
    """
    Apply text processing framework to ArXiv paper summaries.
    """
    for paper in papers:
        print(f"Title: {paper['title']}")
        print(f"Authors: {', '.join(paper['authors'])}")
        processed_text = preprocess_text(paper['summary'])
        keywords = extract_keywords(processed_text)
        svos = extract_svo(paper['summary'])

        print("Keywords:")
        for word, freq in keywords:
            print(f"- {word}: {freq} occurrences")

        print("SVO Structures:")
        for svo in svos:
            print(f"- {svo[0]} → {svo[1]} → {svo[2]}")
        print("=" * 50)

    # Lưu dữ liệu vào file JSON
    save_to_file(papers)

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
