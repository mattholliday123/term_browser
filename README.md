## Overview

Koudelka is a terminal-based document search application that ingests content from curated RSS feeds,
indexes documents using an inverted index, and ranks results using BM25.

The project focuses on search relevance, performance tradeoffs, and systems-level design decisions
rather than web crawling or UI complexity. A Python Textual-based TUI acts as the primary client,
while core indexing and retrieval logic is implemented with performance in mind.

## Architecture

Koudelka is structured around three core components:

- **Ingestion**
  - Fetches documents from hand-picked RSS feeds
  - Normalizes and stores document metadata and content in SQLite

- **Indexing & Search**
  - Maintains an inverted index with `documents` and `postings` tables
  - Stores the term lexicon in memory to reduce disk I/O during queries
  - Uses BM25 for ranking search results

- **Client (TUI)**
  - Python Textual-based terminal UI
  - Accepts user queries and displays ranked results
  - Designed to emphasize responsiveness and low-latency feedback

## Design Decisions & Tradeoffs

### SQLite for Storage
SQLite was chosen for simplicity, portability, and ease of development.
For a single-node system with moderate document volume, SQLite provides sufficient performance
while keeping operational complexity low.

### In-Memory Lexicon
The term dictionary (lexicon) is stored in memory to avoid disk access on every query.
This significantly reduces query latency at the cost of a slightly longer startup time,
as the lexicon is rebuilt from persisted postings.

### RSS Feeds Instead of Web Crawling
The system intentionally avoids implementing a general-purpose web crawler.
Handling robots.txt, crawl politeness, and legal considerations introduces significant complexity.
Instead, Koudelka uses curated RSS feeds, which provide structured, ethical, and reliable access
to fresh content.

### BM25 Ranking
BM25 was selected for ranking due to its transparency, effectiveness, and tunability.
Unlike learned ranking models, BM25 allows clear reasoning about relevance and scoring behavior.

Demo of the browser



https://github.com/user-attachments/assets/52c99a01-8a81-4283-817b-e00e5f5558e7



This project started off as a CLI tool that fetches the wikipedia summary and sections, if desired, straight to the terminal as well as fetches news from The Guardian.
As I continued development it eventually turned into a minimal TUI browser. 

Demo of CLI tool:


https://github.com/user-attachments/assets/5a663055-f3c0-492c-becc-7a80e4af1ae7



Supports subprhase input. Example: 'Dune 19' will give the page for Dune(1984 film), or 'Dune novel' will give page for Dune(novel)


Use following command for more info 
```
info h
```
OR
```
info help
```
---------------------------------------------------------------------------------------------



NOTE: Must have these dependencies installed

```
pip install rich
```

```
pip install wikipedia-api
```

---------------------------------------------------------------------------------------------
Build instructions only for the CLI tool:


To work as system wide command:
install code
create virtual enviroment in project directory:
```
python -m venv my-venv
```
create bash script named info (or whatever you like) as 
```
#!/bin/bash
DIR="/home/username/info" #or wherever the code is located
source "$DIR/my-venv/bin/activate"
python "$DIR/info.py" "$@"
```
move script (if you named it differently, substitute info with your chosen file name)
```
sudo mv info /usr/local/bin
```

---------------------------------------------------------------------------------------------

NOTES:

I have explored creating a TUI browser using Textual to create the TUI and using Go to handle all of the backend logic. I have implemented bm25 ranking for results.
Some limitations include ranking is not perfect, as I do not implement any advanced ranking algorithms beyond bm25. 
Another limitation includes the lack of sources. I have to curate a list of rss feeds manually, therefore I only selected a small number of sites just to test with. 
