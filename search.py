#!/usr/bin/env python3
"""
Resource Finder for Peer Review Equilibrium Research
Downloads papers, creates documentation, sets up project structure.
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import os
import time
import re
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def clean_filename(title):
    title = re.sub(r"[^\\w\\s-]", "", title)
    title = re.sub(r"\\s+", "_", title)
    return title[:50]

def search_arxiv(query, max_results=10):
    base_url = "http://export.arxiv.org/api/query?"
    params = {"search_query": query, "start": 0, "max_results": max_results,
              "sortBy": "relevance", "sortOrder": "descending"}
    url = base_url + urllib.parse.urlencode(params)
    print(f"Searching: {query}")
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = resp.read()
        root = ET.fromstring(data)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        papers = []
        for entry in root.findall("atom:entry", ns):
            arxiv_id = entry.find("atom:id", ns).text.split("/abs/")[-1]
            title = " ".join(entry.find("atom:title", ns).text.strip().split())
            summary = entry.find("atom:summary", ns).text.strip()
            authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]
            pdf_link = None
            for link in entry.findall("atom:link", ns):
                if link.get("title") == "pdf":
                    pdf_link = link.get("href")
                    break
            papers.append({"arxiv_id": arxiv_id, "title": title, "summary": summary,
                          "authors": authors, "pdf_link": pdf_link})
        return papers
    except Exception as e:
        print(f"Error: {e}")
        return []

def download_pdf(paper, output_dir):
    arxiv_id = paper["arxiv_id"]
    pdf_link = paper["pdf_link"]
    if not pdf_link:
        return False
    filename = f"{arxiv_id.replace(\"/\", \"_\")}_{clean_filename(paper[\"title\"])}.pdf"
    filepath = os.path.join(output_dir, filename)
    if os.path.exists(filepath):
        print(f"Exists: {filename}")
        return True
    print(f"Downloading: {paper[\"title\"][:50]}...")
    try:
        urllib.request.urlretrieve(pdf_link, filepath)
        paper["filename"] = filename
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    papers_dir = os.path.join(BASE_DIR, "papers")
    os.makedirs(papers_dir, exist_ok=True)
    
    queries = [
        "all:peer+review+AND+all:mechanism+design",
        "all:peer+review+AND+all:game+theory",
        "all:peer+review+AND+all:noise",
        "all:peer+review+AND+all:equilibrium",
        "all:LLM+AND+all:peer+review"
    ]
    
    all_papers = {}
    for q in queries:
        for p in search_arxiv(q, 8):
            all_papers[p["arxiv_id"]] = p
        time.sleep(3)
    
    print(f"Found {len(all_papers)} unique papers")
    
    keywords = [("peer review", 10), ("mechanism", 6), ("game theory", 6),
                ("equilibrium", 6), ("noise", 4), ("LLM", 5)]
    for p in all_papers.values():
        score = sum(w * (p["title"] + " " + p["summary"]).lower().count(k.lower())
                   for k, w in keywords)
        p["score"] = score
    
    top = sorted(all_papers.values(), key=lambda x: x["score"], reverse=True)[:8]
    
    downloaded = []
    for i, p in enumerate(top, 1):
        print(f"[{i}/{len(top)}]")
        if download_pdf(p, papers_dir):
            downloaded.append(p)
        time.sleep(3)
    
    with open(os.path.join(papers_dir, "paper_info.json"), "w") as f:
        json.dump(downloaded, f, indent=2)
    
    print(f"\\nDownloaded {len(downloaded)} papers")

if __name__ == "__main__":
    main()

