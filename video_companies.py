#!/usr/bin/env python3
"""Generate a CSV of YC companies that have a public video available."""

import json
import csv


def main():
    with open("/home/user/YCcombinator/companies_raw.json") as f:
        data = json.load(f)

    companies_with_video = [
        c for c in data
        if c.get("app_video_public") or c.get("demo_day_video_public")
    ]

    print(f"Total companies: {len(data)}")
    print(f"Companies with video: {len(companies_with_video)}")

    output_path = "/home/user/YCcombinator/video_companies.csv"
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["#", "Company", "YC URL"])
        for i, c in enumerate(companies_with_video, start=1):
            name = c.get("name", "")
            slug = c.get("slug", "")
            yc_url = f"https://www.ycombinator.com/companies/{slug}"
            writer.writerow([i, name, yc_url])

    print(f"CSV written to: {output_path}")


if __name__ == "__main__":
    main()
