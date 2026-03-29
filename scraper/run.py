"""
run.py - Main runner for The Load Bench scraper pipeline.
Usage: python scraper/run.py [--skip-components] [--skip-forums] [--output-dir OUTPUT_DIR]
"""

import sys
import os
import argparse
import logging
from datetime import date

# Allow running from the repo root or scraper/ directory
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import components as comp_module
import forums as forums_module
import digest as digest_module

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def print_summary(components: dict, forums: dict, digest_path: str):
    """Print a human-readable summary to stdout."""
    today = date.today().isoformat()

    print("\n" + "=" * 60)
    print(f"  THE LOAD BENCH — Weekly Digest Summary ({today})")
    print("=" * 60)

    # Component summary
    total_comp = sum(len(v) for v in components.values())
    in_stock = sum(
        1 for items in components.values() for item in items if item.get("in_stock") is True
    )
    out_of_stock = sum(
        1 for items in components.values() for item in items if item.get("in_stock") is False
    )
    unknown = total_comp - in_stock - out_of_stock

    print(f"\n📦 Components Tracked: {total_comp}")
    print(f"   ✅ In Stock:    {in_stock}")
    print(f"   ❌ Out of Stock: {out_of_stock}")
    print(f"   ❓ Unknown/Check: {unknown}")

    # By category
    for cat, items in components.items():
        if items:
            print(f"\n   [{cat.upper()}] — {len(items)} records")
            for item in items[:3]:  # preview first 3
                status = "✅" if item.get("in_stock") else ("❌" if item.get("in_stock") is False else "❓")
                price = item.get("price") or "N/A"
                name = item.get("name", "?")[:50]
                print(f"     {status} {name} — {price}")
            if len(items) > 3:
                print(f"     ... and {len(items) - 3} more")

    # Forum summary
    print(f"\n💬 Forum Activity:")
    reddit_data = forums.get("reddit", {})
    for sub, posts in reddit_data.items():
        if posts:
            top = posts[0]
            print(f"\n   r/{sub} — {len(posts)} posts fetched")
            print(f"   Top: \"{top.get('title', 'N/A')[:60]}\"")
            print(f"        Score: {top.get('score', 0)} | Comments: {top.get('num_comments', 0)}")

    sh_data = forums.get("snipers_hide", [])
    if sh_data:
        print(f"\n   Sniper's Hide — {len(sh_data)} threads")
        for t in sh_data[:3]:
            print(f"   • {t.get('title', 'N/A')[:60]}")

    print(f"\n📄 Digest saved to: {digest_path}")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="The Load Bench weekly scraper pipeline")
    parser.add_argument("--skip-components", action="store_true", help="Skip component scraping")
    parser.add_argument("--skip-forums", action="store_true", help="Skip forum scraping")
    parser.add_argument(
        "--output-dir",
        default=os.path.join(os.path.dirname(script_dir), "output"),
        help="Output directory for digest files (default: ../output relative to scraper/)",
    )
    args = parser.parse_args()

    # 1. Component scraping
    if args.skip_components:
        logger.info("Skipping component scraping (--skip-components)")
        components = {"powders": [], "primers": [], "brass": [], "bullets": []}
    else:
        logger.info("Starting component scraping...")
        try:
            components = comp_module.run_all()
        except Exception as e:
            logger.error(f"Component scraping failed: {e}")
            components = {"powders": [], "primers": [], "brass": [], "bullets": []}

    # 2. Forum scraping
    if args.skip_forums:
        logger.info("Skipping forum scraping (--skip-forums)")
        forums = {"reddit": {}, "snipers_hide": []}
    else:
        logger.info("Starting forum scraping...")
        try:
            forums = forums_module.run_all()
        except Exception as e:
            logger.error(f"Forum scraping failed: {e}")
            forums = {"reddit": {}, "snipers_hide": []}

    # 3. Generate digest
    logger.info("Generating weekly digest...")
    try:
        digest_path = digest_module.generate_digest(components, forums, output_dir=args.output_dir)
    except Exception as e:
        logger.error(f"Digest generation failed: {e}")
        sys.exit(1)

    # 4. Print summary
    print_summary(components, forums, digest_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
