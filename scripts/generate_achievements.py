#!/usr/bin/env python3
"""
Scan src/content/news/*.md and generate achievements JSON like src/content/achievements/temp.json
- Extract year from frontmatter `date:`
- Extract first content line and pull author(s) and publisher (text in [brackets] preferred)
- If title/tags unknown, leave blank/empty
- Avoid duplicate entries by (authors[0], year, publisher)
"""
import re
import json
from pathlib import Path

NEWS_DIR = Path(__file__).resolve().parents[1] / 'src' / 'content' / 'news'
OUT_FILE = Path(__file__).resolve().parents[1] / 'src' / 'content' / 'achievements' / 'temp.json'

KW_REGEX = re.compile(r'掲載|公開されました|で公開されました|で掲載されました|論文が|で研究発表を行いました')
BRACKET_RE = re.compile(r'\[([^\]]+)\]')
LINK_RE = re.compile(r'\[[^\]]+\]\(([^)]+)\)')
# Match optional separators/grade then the name before honorific (capture name)
AUTHOR_RE = re.compile(r'(?:[と、,\s]*)?(?:[MBD]\d+)?([一-龥ぁ-んァ-ンA-Za-z]+?)(?:君|さん|氏|先生)')


def parse_md(path: Path):
    text = path.read_text(encoding='utf-8')
    # frontmatter date
    date_match = re.search(r'^---\s*\n(.*?)\n---', text, re.S | re.M)
    year = ''
    if date_match:
        fm = date_match.group(1)
        m = re.search(r'date:\s*(\d{4})', fm)
        if m:
            year = m.group(1)
    # body - first non-empty line after frontmatter
    body = text[date_match.end():] if date_match else text
    lines = [l.strip() for l in body.splitlines() if l.strip()]
    first = lines[0] if lines else ''
    return year, first


def extract_link(first_line: str):
    # extract first markdown link URL if present
    m = LINK_RE.search(first_line)
    if m:
        return m.group(1).strip()
    return ''


def extract_info(first_line: str):
    # publisher: prefer bracket content
    pub = ''
    b = BRACKET_RE.search(first_line)
    if b:
        pub = b.group(1)
    else:
        # try patterns like '論文がXXXに掲載'
        m = re.search(r'論文が(.+?)(?:に|で)', first_line)
        if m:
            pub = m.group(1).strip()
        else:
            m2 = re.search(r'が(.+?)(?:で|に)', first_line)
            if m2:
                pub = m2.group(1).strip()
    # authors: find all occurrences like 'M1狭間君' -> extract the captured name
    raw_authors = [m.group(1).strip() for m in AUTHOR_RE.finditer(first_line)]
    authors = []
    for name in raw_authors:
        # remove any leading grade tokens left (safety), and any stray separators
        name = re.sub(r'^[MBDF]\d+', '', name)
        name = name.lstrip('と、, ').strip()
        if name and name not in authors:
            authors.append(name)
    return authors, pub


def load_existing_manual():
    # Load existing file but only keep manual entries (heuristic: entries with non-empty title)
    manual = {}
    if OUT_FILE.exists():
        try:
            existing = json.loads(OUT_FILE.read_text(encoding='utf-8'))
            for k, v in existing.items():
                if v.get('title'):
                    manual[k] = v
        except Exception:
            return {}
    return manual


def write_out(obj):
    OUT_FILE.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+"\n", encoding='utf-8')


def main():
    md_files = sorted(NEWS_DIR.glob('*.md'))
    # Do not preserve manual entries (remove previous manual entries like "研究A"/"研究B")
    manual_entries = {}
    new_entries = {}
    seen = set()
    next_idx = 1

    for p in md_files:
        year, first = parse_md(p)
        if not first:
            continue
        if not KW_REGEX.search(first):
            continue
        authors, pub = extract_info(first)
        if not authors and not pub:
            continue

        # For each author, create a separate entry (same publisher/year). Add '飯間等' after each author.
        link = extract_link(first)
        for a in authors:
            key = ((a,), year, pub)
            if key in seen:
                continue
            ach_key = f'new-{next_idx:03d}'
            new_entries[ach_key] = {
                'title': '',
                'tags': [],
                'authors': [a, '飯間等'],
                'year': year if year else '',
                'publisher': pub if pub else '',
                'link': link
            }
            seen.add(key)
            next_idx += 1

    # Merge manual_entries (preserve) with new_entries
    merged = {}
    merged.update(manual_entries)
    # add new entries
    merged.update(new_entries)

    # Sort merged entries by year (desc), then by publisher then by author for stable ordering
    def sort_key(item):
        k, v = item
        yr = v.get('year','')
        try:
            yint = int(yr)
        except:
            yint = 0
        pub = v.get('publisher','')
        auth = v.get('authors',[None])[0] if v.get('authors') else ''
        return (-yint, pub, auth)

    sorted_items = sorted(merged.items(), key=sort_key)

    # Renumber keys sequentially as achievement-001 ...
    ordered = {}
    for i, (old_k, v) in enumerate(sorted_items, start=1):
        new_k = f'achievement-{i:03d}'
        ordered[new_k] = v

    write_out(ordered)
    print(f'Wrote {len(ordered)} achievements to {OUT_FILE}')


if __name__ == '__main__':
    main()
