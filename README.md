# ArXiv Fetching

A repository focused on fetching and displaying research papers from ArXiv using their API.

## Features

- Fetches research papers from ArXiv based on a keyword.
- Displays the title, authors, abstract preview, and PDF link of the papers.
- Sorts results by the most recent submissions.

## Installation

To install and set up this project, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/git19112019/ArXiv-fetching.git
    ```

2. Navigate to the project directory:
    ```bash
    cd ArXiv-fetching
    ```

3. Ensure you have Python installed (preferably Python 3).

4. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To use this project, follow these instructions:

1. Run the Python script `arxiv_fetcher.py`:
    ```bash
    python arxiv_fetcher.py
    ```

2. When prompted, enter the search keyword and the number of results you want to display.

3. The script will query the ArXiv API and display the titles, authors, abstract previews, and PDF links of the research papers.

## Dependencies

This project requires the following dependencies:
- `urllib`
- `xml.etree.ElementTree`
- `requests`
- `argparse`

You can install the dependencies using the following command:
```bash
pip install urllib requests lxml argparse
```

## Contributing

If you would like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your changes.
3. Submit a pull request with your changes.

Thank you for your contributions!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
