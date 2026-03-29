"""
forums.py - Forum/Discussion Scraper for The Load Bench
Scrapes Reddit (via JSON API) and Sniper's Hide for content ideas.
"""

import requests
import time
import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Reddit requires a descriptive User-Agent
REDDIT_HEADERS = {
    "User-Agent": "TheLoadBench-Newsletter-Bot/1.0 (newsletter digest; contact: crashfpv@theloadbench.com)"
}

WEB_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

REQUEST_DELAY = 1.5


def safe_get(url: str, headers: dict, timeout: int = 15) -> Optional[requests.Response]:
    """GET with error handling."""
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp
    except requests.exceptions.HTTPError as e:
        logger.warning(f"HTTP {e.response.status_code} for {url}")
        return None
    except requests.exceptions.RequestException as e:
        logger.warning(f"Request failed for {url}: {e}")
        return None


# -------------------------------------------------------
# Reddit JSON API
# -------------------------------------------------------
def fetch_reddit_subreddit(subreddit: str, sort: str = "top", time_filter: str = "week",
                            limit: int = 10) -> List[Dict]:
    """Fetch top posts from a subreddit using the public JSON API."""
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?t={time_filter}&limit={limit}"
    logger.info(f"Reddit: fetching r/{subreddit} ({sort}/{time_filter})")

    resp = safe_get(url, REDDIT_HEADERS)
    time.sleep(REQUEST_DELAY)

    if not resp:
        logger.warning(f"Reddit: could not fetch r/{subreddit}")
        return []

    try:
        data = resp.json()
    except ValueError:
        logger.warning(f"Reddit: invalid JSON for r/{subreddit}")
        return []

    posts = []
    children = data.get("data", {}).get("children", [])

    for child in children:
        post = child.get("data", {})
        title = post.get("title", "")
        score = post.get("score", 0)
        permalink = post.get("permalink", "")
        post_url = f"https://www.reddit.com{permalink}" if permalink else ""
        external_url = post.get("url", "")
        num_comments = post.get("num_comments", 0)
        selftext = post.get("selftext", "")[:300] if post.get("selftext") else ""

        top_comment = fetch_top_reddit_comment(subreddit, post.get("id", ""))

        posts.append({
            "subreddit": subreddit,
            "title": title,
            "score": score,
            "url": post_url,
            "external_url": external_url,
            "num_comments": num_comments,
            "preview": selftext,
            "top_comment": top_comment,
        })

    logger.info(f"Reddit: fetched {len(posts)} posts from r/{subreddit}")
    return posts


def fetch_top_reddit_comment(subreddit: str, post_id: str) -> Optional[str]:
    """Fetch the top comment for a Reddit post."""
    if not post_id:
        return None

    url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json?limit=1&sort=top"
    resp = safe_get(url, REDDIT_HEADERS)
    time.sleep(0.5)  # shorter delay for comment fetches

    if not resp:
        return None

    try:
        data = resp.json()
        # data is [post_listing, comments_listing]
        if len(data) < 2:
            return None
        comments = data[1].get("data", {}).get("children", [])
        if comments:
            comment_data = comments[0].get("data", {})
            body = comment_data.get("body", "")
            if body and body != "[deleted]" and body != "[removed]":
                return body[:300]
    except (ValueError, IndexError, KeyError):
        pass

    return None


def scrape_reddit() -> Dict[str, List[Dict]]:
    """Scrape all relevant subreddits."""
    results = {}

    subreddits = [
        ("reloading", "top", "week"),
        ("longrange", "top", "week"),
        ("6gt", "new", "all"),
        ("PrecisionRifle", "top", "week"),
    ]

    for sub, sort, time_filter in subreddits:
        posts = fetch_reddit_subreddit(sub, sort=sort, time_filter=time_filter, limit=10)
        if posts:
            results[sub] = posts
        else:
            logger.info(f"Reddit: r/{sub} returned no posts (may not exist or be empty)")

    return results


# -------------------------------------------------------
# Sniper's Hide
# -------------------------------------------------------
def scrape_snipers_hide() -> List[Dict]:
    """Scrape Sniper's Hide reloading subforum for hot threads."""
    results = []

    # Sniper's Hide public forum URLs to try
    forum_urls = [
        "https://www.snipershide.com/shooting/forums/reloading-ammunition.6/",
        "https://www.snipershide.com/shooting/forums/handloading.6/",
        "https://www.snipershide.com/shooting/forums/",
    ]

    for forum_url in forum_urls:
        logger.info(f"Sniper's Hide: fetching {forum_url}")
        resp = safe_get(forum_url, WEB_HEADERS)
        time.sleep(REQUEST_DELAY)

        if not resp:
            logger.warning(f"Sniper's Hide: blocked or error for {forum_url}")
            continue

        soup = BeautifulSoup(resp.text, "lxml")

        # XenForo-style forum thread selectors
        threads = soup.select(
            ".structItem, .discussionListItem, [class*='thread'], "
            ".node-title, article[class*='post'], .listBlock"
        )

        if not threads:
            # Try generic link extraction from forum-like pages
            threads = soup.select("h3 a, h4 a, .title a")

        for thread in threads[:15]:
            if hasattr(thread, "select_one"):
                title_el = thread.select_one(
                    ".structItem-title a, .title a, h3 a, h4 a, [class*='title'] a, a[data-preview-url]"
                )
                replies_el = thread.select_one(
                    ".structItem-minor, .discussionListItem-stats, [class*='replies'], [class*='posts']"
                )
                date_el = thread.select_one("time, .structItem-startDate, [class*='date']")
            else:
                title_el = thread if thread.name == "a" else None
                replies_el = None
                date_el = None

            if not title_el:
                continue

            title = title_el.get_text(strip=True)
            href = title_el.get("href", "")
            thread_url = href if href.startswith("http") else "https://www.snipershide.com" + href
            replies = replies_el.get_text(strip=True) if replies_el else "unknown"
            date = date_el.get("datetime", date_el.get_text(strip=True)) if date_el else "unknown"

            if title and len(title) > 5:  # filter out junk
                results.append({
                    "source": "Sniper's Hide",
                    "title": title,
                    "url": thread_url,
                    "replies": replies,
                    "last_activity": date,
                })

        if results:
            logger.info(f"Sniper's Hide: found {len(results)} threads from {forum_url}")
            break  # stop once we get results

    if not results:
        logger.warning("Sniper's Hide: no threads found — site may require login or block scrapers")
        results.append({
            "source": "Sniper's Hide",
            "title": "Check site manually",
            "url": "https://www.snipershide.com/shooting/forums/",
            "replies": "N/A",
            "last_activity": "N/A",
            "note": "Sniper's Hide may require login to view threads",
        })

    return results


# -------------------------------------------------------
# Main runner
# -------------------------------------------------------
def run_all() -> Dict:
    """Run all forum scrapers and return combined results."""
    logger.info("=== Starting forum scraping ===")

    results = {
        "reddit": scrape_reddit(),
        "snipers_hide": scrape_snipers_hide(),
    }

    reddit_total = sum(len(v) for v in results["reddit"].values())
    sh_total = len(results["snipers_hide"])
    logger.info(f"=== Forum scraping complete: {reddit_total} Reddit posts, {sh_total} SH threads ===")

    return results


if __name__ == "__main__":
    import json
    results = run_all()
    print(json.dumps(results, indent=2))
