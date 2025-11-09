#!/usr/bin/env python3
"""
Fetch links from src/content/achievements/temp.json and try to fill missing title and verify/update authors.
- For pages with meta tags (citation_title, og:title, dc.title), use them.
- For authors, prefer meta citation_author(s). If different from JSON authors[0], replace it (keeping '飯間等' as second element).
- For conference pages without metadata, attempt heuristics: find occurrences of the author name and extract nearby text as title.

This script needs 'requests' and 'beautifulsoup4'. If they're not installed, it will print instructions.
"""
import json
import re
import sys
from pathlib import Path

TMP = Path(__file__).resolve().parents[1] / 'src' / 'content' / 'achievements' / 'temp.json'

try:
    import requests
    from bs4 import BeautifulSoup
except Exception:
    print('This script requires requests and beautifulsoup4. Install with:')
    print('  pip3 install --user requests beautifulsoup4')
    sys.exit(1)

TIMEOUT = 10

META_TITLE_NAMES = [
    ('name', 'citation_title'),
    ('property', 'og:title'),
    ('name', 'dc.title'),
    ('name', 'title')
]
META_AUTHOR_NAMES = [
    ('name', 'citation_author'),
    ('name', 'author'),
    ('name', 'dc.creator')
]

# simple family name extraction for Japanese/Western: take last token after space or last kanji group
def family_from_full(name):
    name = name.strip()
    if not name:
        return name
    # if name contains spaces, assume last token is family or given; try heuristics
    if ' ' in name:
        parts = name.split()
        # if two parts, often 'Given Family' or 'Family Given' ambiguous; return last
        return parts[-1]
    # for CJK names, return last 2 characters if length <=4 else full
    if len(name) <= 4:
        return name
    # else try to split on non-kanji
    m = re.search(r'[一-龥]+$', name)
    if m:
        return m.group(0)
    return name


def get_url_title_authors(url):
    try:
        headers = {'User-Agent': 'iima-lab-bot/1.0 (+https://example.local)'}
        r = requests.get(url, timeout=TIMEOUT, headers=headers)
        r.raise_for_status()
        html = r.text
    except Exception as e:
        return {'title': '', 'authors': []}
    soup = BeautifulSoup(html, 'lxml') if 'lxml' in sys.modules else BeautifulSoup(html, 'html.parser')
    # try meta tags
    title = ''
    for attr, name in META_TITLE_NAMES:
        tag = soup.find('meta', attrs={attr: name})
        if tag and tag.get('content'):
            title = tag.get('content').strip()
            break
    if not title:
        # og:title fallback
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
    # collect authors
    authors = []
    for attr, name in META_AUTHOR_NAMES:
        tags = soup.find_all('meta', attrs={attr: name})
        for t in tags:
            if t.get('content'):
                authors.append(t.get('content').strip())
        if authors:
            break
    # some pages include <a class="author"> etc. Try to find author links
    if not authors:
        # look for elements that contain 'author' in class or id
        candidates = soup.find_all(attrs={'class': re.compile('author', re.I)}) + soup.find_all(attrs={'id': re.compile('author', re.I)})
        for c in candidates:
            text = c.get_text(separator=' ', strip=True)
            if text:
                # split by comma/、 and collect tokens
                parts = re.split(r'[、,;]', text)
                for p in parts:
                    p = p.strip()
                    if p:
                        authors.append(p)
        # dedupe
        authors = list(dict.fromkeys(authors))
    return {'title': title, 'authors': authors}


def heuristic_find_title_from_conference(url, page_html, json_author):
    # page_html is BeautifulSoup
    text = page_html.get_text(separator='\n')
    # search for lines containing the author's family name or full name
    family = json_author
    pattern = re.compile(re.escape(family))
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for i, line in enumerate(lines):
        if pattern.search(line):
            # try previous line as title candidate
            if i > 0 and len(lines[i-1]) > 10:
                return lines[i-1]
            # try same line removing author name
            candidate = pattern.sub('', line).strip(' -:—–\t')
            if len(candidate) > 10:
                return candidate
    return ''


def main():
    obj = json.loads(TMP.read_text(encoding='utf-8'))
    changed = 0
    total = 0
    for k, v in obj.items():
        link = v.get('link','').strip()
        if not link:
            continue
        total += 1
        res = get_url_title_authors(link)
        title = res.get('title','')
        scraped_authors = res.get('authors', [])
        # if no title found and it's likely a conference page, try heuristic
        if not title:
            try:
                r = requests.get(link, timeout=TIMEOUT, headers={'User-Agent':'iima-lab-bot/1.0'})
                from bs4 import BeautifulSoup
                page = BeautifulSoup(r.text, 'lxml') if 'lxml' in sys.modules else BeautifulSoup(r.text, 'html.parser')
                # use the first author name from json to search
                json_author = v.get('authors',[None])[0]
                if json_author:
                    h = heuristic_find_title_from_conference(link, page, json_author)
                    if h:
                        title = h
            except Exception:
                pass
        # normalize scraped author name(s)
        if scraped_authors:
            # use first scraped author as canonical
            first_scraped = scraped_authors[0]
            fam = family_from_full(first_scraped)
            # if different from existing first author, update
            existing_first = v.get('authors',[None])[0]
            if existing_first != fam:
                v['authors'] = [fam, '飯間等']
                changed += 1
        # set title if found and different
        if title and v.get('title','') != title:
            v['title'] = title
            changed += 1
    if changed:
        TMP.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+"\n", encoding='utf-8')
    print(f'Processed {total} links, changed {changed} fields, wrote file: {TMP}')

if __name__ == '__main__':
    main()
