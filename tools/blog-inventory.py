#!/usr/bin/env python3
"""Write a reviewable inventory of the published Crossroads blog articles."""

import csv
from pathlib import Path

import blog
import blogposts


FIELDS = (
    "title", "url", "html_path", "author", "credit_source", "category",
    "issue", "publication_date", "excerpt", "image", "issue_pdf",
    "reading_time_minutes",
)


def main():
    output = Path(__file__).with_name("blog-inventory.csv")
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for post in blogposts.POSTS:
            writer.writerow({
                "title": post["title"],
                "url": f"https://cirs-website.vercel.app/{post['slug']}",
                "html_path": f"{post['slug']}.html",
                "author": post["author"] or "",
                "credit_source": post.get("credit_source", "printed" if post["author"] else "none printed"),
                "category": post["section"],
                "issue": post["issue"],
                "publication_date": post["date"] or "",
                "excerpt": post["excerpt"],
                "image": f"assets/img/blog/{post['image']}" if post.get("image") else "",
                "issue_pdf": blog.issue_pdf(post),
                "reading_time_minutes": blog.reading_time(post),
            })
    print(f"wrote {len(blogposts.POSTS)} articles to {output}")


if __name__ == "__main__":
    main()
