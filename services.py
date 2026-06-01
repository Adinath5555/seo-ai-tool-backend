import requests
from bs4 import BeautifulSoup


def audit_website_service(url):

    response = requests.get(
        url,
        timeout=5
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    title = soup.title.string if soup.title else "No title found"

    meta_description = soup.find(
        "meta",
        attrs={"name": "description"}
    )

    meta_content = (
        meta_description.get("content")
        if meta_description
        else "No meta description found"
    )

    h1_tags = soup.find_all("h1")
    h1_count = len(h1_tags)

    images = soup.find_all("img")
    total_images = len(images)

    missing_alt_tags = 0

    for image in images:
        if not image.get("alt"):
            missing_alt_tags += 1

    seo_score = 0

    if title != "No title found":
        seo_score += 30

    if meta_content != "No meta description found":
        seo_score += 30

    if h1_count > 0:
        seo_score += 20

    if missing_alt_tags == 0:
        seo_score += 20

    return {
        "title": title,
        "meta_description": meta_content,
        "h1_count": h1_count,
        "total_images": total_images,
        "missing_alt_tags": missing_alt_tags,
        "seo_score": seo_score
    }