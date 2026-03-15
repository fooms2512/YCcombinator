#!/usr/bin/env python3
"""Process YC companies data and generate a CSV table."""

import json
import csv
import re


def parse_location(all_locations):
    """Parse location string into city and country."""
    if not all_locations:
        return "", ""
    # Take the first location if multiple (separated by ';')
    first_loc = all_locations.split(";")[0].strip()
    parts = [p.strip() for p in first_loc.split(",")]
    if len(parts) >= 3:
        city = parts[0]
        country = parts[-1]
    elif len(parts) == 2:
        city = parts[0]
        country = parts[-1]
    elif len(parts) == 1:
        city = ""
        country = parts[0]
    else:
        city = ""
        country = ""
    return city, country


def classify_business_type(tags, industries, industry_field):
    """Classify as B2B, B2C, or B2B2C based on tags and industry fields."""
    tags_set = set(t.lower() for t in (tags or []))
    industries_set = set(i.lower() for i in (industries or []))
    industry_lower = (industry_field or "").lower()

    has_b2b = (
        "b2b" in tags_set
        or "enterprise" in tags_set
        or "enterprise software" in tags_set
        or "b2b" in industries_set
        or industry_lower == "b2b"
    )
    has_b2c = (
        "consumer" in tags_set
        or any("consumer" in t for t in tags_set)
        or "consumer" in industries_set
        or industry_lower == "consumer"
    )

    if has_b2b and has_b2c:
        return "B2B2C"
    elif has_b2b:
        return "B2B"
    elif has_b2c:
        return "B2C"
    else:
        # Infer from combined text
        all_text = " ".join(tags_set | industries_set) + " " + industry_lower
        if "saas" in all_text or "enterprise" in all_text:
            return "B2B"
        elif "marketplace" in all_text and "consumer" in all_text:
            return "B2C"
        return "Unknown"


def main():
    with open("/home/user/YCcombinator/companies_raw.json") as f:
        data = json.load(f)

    print(f"Total companies: {len(data)}")

    rows = []
    for c in data:
        name = c.get("name", "")
        batch = c.get("batch", "")
        all_locations = c.get("all_locations", "")
        team_size = c.get("team_size", "")
        industry = c.get("industry", "")
        subindustry = c.get("subindustry", "")
        tags = c.get("tags", [])
        industries = c.get("industries", [])
        status = c.get("status", "")
        stage = c.get("stage", "")
        app_video_public = c.get("app_video_public", False)
        demo_day_video_public = c.get("demo_day_video_public", False)
        is_hiring = c.get("isHiring", False)
        website = c.get("website", "")
        one_liner = c.get("one_liner", "")

        city, country = parse_location(all_locations)
        business_type = classify_business_type(tags, industries, industry)

        # Company size bucket
        if team_size == "" or team_size is None:
            size_label = "Unknown"
        elif team_size <= 10:
            size_label = "1-10"
        elif team_size <= 50:
            size_label = "11-50"
        elif team_size <= 200:
            size_label = "51-200"
        elif team_size <= 500:
            size_label = "201-500"
        elif team_size <= 1000:
            size_label = "501-1000"
        else:
            size_label = "1000+"

        rows.append({
            "Company Name": name,
            "Batch": batch,
            "Location": all_locations,
            "City": city,
            "Country": country,
            "Industry": industry,
            "Sub-Industry": subindustry,
            "Business Type": business_type,
            "Team Size": team_size if team_size else "",
            "Size Range": size_label,
            "Stage": stage,
            "Status": status,
            "Is Hiring": "Yes" if is_hiring else "No",
            "App Video Public": "Yes" if app_video_public else "No",
            "Demo Day Video Public": "Yes" if demo_day_video_public else "No",
            "Website": website,
            "One Liner": one_liner,
            "Tags": "; ".join(tags),
        })

    # Write CSV
    output_path = "/home/user/YCcombinator/yc_companies.csv"
    fieldnames = [
        "Company Name", "Batch", "Location", "City", "Country",
        "Industry", "Sub-Industry", "Business Type",
        "Team Size", "Size Range", "Stage", "Status", "Is Hiring",
        "App Video Public", "Demo Day Video Public",
        "Website", "One Liner", "Tags"
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"CSV written to: {output_path}")
    print(f"Total rows: {len(rows)}")

    # Print summary stats
    from collections import Counter
    types = Counter(r["Business Type"] for r in rows)
    print("\nBusiness Type Distribution:")
    for k, v in types.most_common():
        print(f"  {k}: {v}")

    batches = Counter(r["Batch"] for r in rows)
    print(f"\nTop 10 Batches:")
    for k, v in batches.most_common(10):
        print(f"  {k}: {v}")

    countries = Counter(r["Country"] for r in rows if r["Country"])
    print(f"\nTop 15 Countries:")
    for k, v in countries.most_common(15):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
