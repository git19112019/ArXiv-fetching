import spacy
from collections import Counter
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Constants: URL cơ bản cho ArXiv API
API_URL = "http://export.arxiv.org/api/query?"

# Tải mô hình ngôn ngữ của SpaCy
nlp = spacy.load("en_core_web_sm")

def fetch_arxiv_papers(keyword, num_results=5):
    """
    Fetch papers from ArXiv using the API sorted by the most recent submission date.
    """
    query_params = {
        'search_query': f"all:{keyword}",
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
    root = ET.fromstring(data)
    namespace = {'atom': 'http://www.w3.org/2005/Atom'}
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

def save_papers_to_file(papers, filename="papers.json"):
    """
    Save the fetched papers to a JSON file.
    """
    try:
        with open(filename, 'w') as file:
            json.dump(papers, file, indent=4)
        print(f"Papers saved to {filename}")
    except Exception as e:
        print(f"Error saving papers: {e}")

def filter_papers_by_author(papers, author_name):
    """
    Filter the list of papers to include only those written by the specified author.
    """
    return [paper for paper in papers if author_name.lower() in (author.lower() for author in paper['authors'])]

def search_papers_by_title(papers, keyword):
    """
    Search for papers with the specified keyword in their title.
    """
    return [paper for paper in papers if keyword.lower() in paper['title'].lower()]

def rank_papers_by_keyword(papers, keyword):
    """
    Rank papers by the frequency of a specific keyword in their summaries.
    """
    def keyword_count(summary):
        return summary.lower().count(keyword.lower())

    return sorted(papers, key=lambda paper: keyword_count(paper['summary']), reverse=True)

def generate_word_cloud(text):
    """
    Generate a word cloud from the given text.
    """
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

def interactive_menu():
    """
    Display an interactive menu for the user to choose actions.
    """
    papers = []
    while True:
        print("\nMenu:")
        print("1. Fetch papers")
        print("2. Save papers to file")
        print("3. Filter papers by author")
        print("4. Search papers by title")
        print("5. Rank papers by keyword")
        print("6. Generate word cloud")
        print("7. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            keyword = input("Enter search keyword: ")
            num_results = int(input("Enter number of results to display: "))
            papers = fetch_arxiv_papers(keyword, num_results)
            if papers:
                summarize_papers(papers)
            else:
                print("No papers found.")
        elif choice == "2":
            if papers:
                filename = input("Enter filename to save papers (default: papers.json): ") or "papers.json"
                save_papers_to_file(papers, filename)
            else:
                print("No papers to save.")
        elif choice == "3":
            if papers:
                author = input("Enter author name: ")
                filtered = filter_papers_by_author(papers, author)
                summarize_papers(filtered)
            else:
                print("No papers to filter.")
        elif choice == "4":
            if papers:
                keyword = input("Enter keyword to search in titles: ")
                results = search_papers_by_title(papers, keyword)
                summarize_papers(results)
            else:
                print("No papers to search.")
        elif choice == "5":
            if papers:
                keyword = input("Enter keyword to rank papers by: ")
                ranked = rank_papers_by_keyword(papers, keyword)
                summarize_papers(ranked)
            else:
                print("No papers to rank.")
        elif choice == "6":
            if papers:
                all_summaries = " ".join([paper['summary'] for paper in papers])
                generate_word_cloud(all_summaries)
            else:
                print("No papers to generate word cloud.")
        elif choice == "7":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    interactive_menu()
