"""
matches.py — Match calendar scraper for The Load Bench
Pulls upcoming matches from PRS, NRL, USPSA, IDPA, GSSF, CMP, F-Class
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time

HEADERS = {
    'User-Agent': 'TheLoadBench/1.0 (theloadbench.com; newsletter match calendar)'
}

def scrape_prs():
    """Scrape PRS bolt gun match schedule"""
    results = []
    try:
        r = requests.get(
            'https://www.precisionrifleseries.com/bolt-gun/schedule/',
            headers=HEADERS, timeout=10
        )
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'lxml')
            # PRS uses various table/card structures — grab text blocks with dates
            for row in soup.select('tr, .match-row, .schedule-item, article'):
                text = row.get_text(' ', strip=True)
                if any(month in text for month in ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']):
                    if len(text) > 10 and len(text) < 300:
                        results.append({'source': 'PRS', 'text': text[:200]})
            if results:
                print(f"  PRS: found {len(results)} entries")
    except Exception as e:
        print(f"  PRS scrape failed: {e}")

    return results[:10]


def scrape_nrl():
    """Scrape NRL Hunter match schedule"""
    results = []
    try:
        r = requests.get(
            'https://nrlhunter.com/schedule/',
            headers=HEADERS, timeout=10
        )
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'lxml')
            for item in soup.select('.tribe-event, .tribe-events-calendar-list__event, article'):
                text = item.get_text(' ', strip=True)
                if len(text) > 15 and len(text) < 300:
                    results.append({'source': 'NRL', 'text': text[:200]})
            if results:
                print(f"  NRL: found {len(results)} entries")
    except Exception as e:
        print(f"  NRL scrape failed: {e}")

    return results[:5]


def scrape_uspsa():
    """USPSA match finder — returns org link since club matches aren't centrally listed"""
    return [{
        'source': 'USPSA',
        'text': 'Find local USPSA matches at uspsa.org/match-finder',
        'url': 'https://uspsa.org/match-finder'
    }]


def scrape_idpa():
    """IDPA match finder"""
    return [{
        'source': 'IDPA',
        'text': 'Find local IDPA matches and sanctioned events at idpa.com',
        'url': 'https://www.idpa.com/matches'
    }]


def get_matches():
    """Run all match scrapers and return combined results"""
    print("Scraping match calendars...")
    all_matches = {
        'precision_rifle': [],
        'pistol': [],
        'org_links': []
    }

    # Precision rifle
    time.sleep(1)
    prs = scrape_prs()
    all_matches['precision_rifle'].extend(prs)

    time.sleep(1)
    nrl = scrape_nrl()
    all_matches['precision_rifle'].extend(nrl)

    # Pistol org links
    all_matches['org_links'].extend(scrape_uspsa())
    all_matches['org_links'].extend(scrape_idpa())
    all_matches['org_links'].append({
        'source': 'GSSF',
        'text': 'GSSF match schedule at gssfonline.com',
        'url': 'https://www.gssfonline.com/matches'
    })
    all_matches['org_links'].append({
        'source': 'CMP',
        'text': 'CMP rifle matches at thecmp.org/competitions',
        'url': 'https://thecmp.org/competitions/matches/'
    })
    all_matches['org_links'].append({
        'source': 'F-Class',
        'text': 'F-Class Association matches at fclassnational.com',
        'url': 'https://www.fclassnational.com/matches'
    })

    return all_matches


def format_matches_section(matches):
    """Format match data for digest output"""
    lines = ["## 🗓 Match Calendar\n"]

    lines.append("### Precision Rifle (PRS / NRL / F-Class)")
    if matches['precision_rifle']:
        for m in matches['precision_rifle'][:8]:
            lines.append(f"- [{m['source']}] {m['text']}")
    else:
        lines.append("- Check precisionrifleseries.com/bolt-gun/schedule/ for current listings")
        lines.append("- NRL: nrlhunter.com/schedule/")
        lines.append("- F-Class: fclassnational.com/matches")

    lines.append("\n### Pistol (IDPA / USPSA / GSSF)")
    for link in matches['org_links']:
        if link['source'] in ['IDPA', 'USPSA', 'GSSF']:
            lines.append(f"- {link['text']}")

    lines.append("\n### Other")
    for link in matches['org_links']:
        if link['source'] in ['CMP', 'F-Class']:
            lines.append(f"- {link['text']}")

    lines.append("\n---")
    return "\n".join(lines)


if __name__ == "__main__":
    matches = get_matches()
    print(format_matches_section(matches))
