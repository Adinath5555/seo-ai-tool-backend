import requests
from bs4 import BeautifulSoup


def audit_website_service(url):

    # -----------------------------------
    # 1. Download the website
    # -----------------------------------
    response = requests.get(
        url,
        timeout=5
    )

    response.raise_for_status()

    # -----------------------------------
    # 2. Parse the HTML
    # -----------------------------------
    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # Remove scripts and styles
    for tag in soup(["script", "style"]):
        tag.decompose()

    # Extract webpage text
    page_content = soup.get_text(
        separator=" ",
        strip=True
    )

    # Limit content sent to the AI model
    page_content = page_content[:2000]

    # -----------------------------------
    # 3. Extract SEO information
    # -----------------------------------

    # Title
    title = (
        soup.title.string
        if soup.title and soup.title.string
        else "No title found"
    )

    # Meta description
    meta_description = soup.find(
        "meta",
        attrs={"name": "description"}
    )

    meta_content = (
        meta_description.get("content")
        if meta_description
        else "No meta description found"
    )

    # H1 tags
    h1_tags = soup.find_all("h1")
    h1_count = len(h1_tags)

    # Images
    images = soup.find_all("img")
    total_images = len(images)

    # Count images without alt text
    missing_alt_tags = 0

    for image in images:
        if not image.get("alt"):
            missing_alt_tags += 1

    # -----------------------------------
    # 4. Calculate rule-based SEO score
    # -----------------------------------
    seo_score = 0

    if title != "No title found":
        seo_score += 30

    if meta_content != "No meta description found":
        seo_score += 30

    if h1_count > 0:
        seo_score += 20

    if missing_alt_tags == 0:
        seo_score += 20

    # -----------------------------------
    # 5. Create prompt for Llama
    # -----------------------------------
    prompt = f"""
Analyze this website's SEO.

Website SEO Data:

Title: {title}

Meta Description: {meta_content}

H1 Count: {h1_count}

Total Images: {total_images}

Missing Alt Tags: {missing_alt_tags}

Rule-Based SEO Score: {seo_score}/100

Webpage Content:

{page_content}

Provide the following:

1. SEO Score out of 100
2. Strengths
3. Weaknesses
4. Suggestions for improvement
"""

    # -----------------------------------
    # 6. Send prompt to Ollama / Llama
    # -----------------------------------
    try:
        ollama_response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:3b",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        ollama_response.raise_for_status()

        ollama_data = ollama_response.json()

        ai_feedback = ollama_data["response"]

    except Exception as e:
        print(f"Ollama error: {e}")

        ai_feedback = (
            "AI analysis temporarily unavailable. "
            "Please make sure Ollama is running and try again."
        )

    # -----------------------------------
    # 7. Return complete SEO audit result
    # -----------------------------------
    return {
        "title": title,
        "meta_description": meta_content,
        "h1_count": h1_count,
        "total_images": total_images,
        "missing_alt_tags": missing_alt_tags,
        "seo_score": seo_score,
        "ai_provider": "ollama",
        "ai_model": "llama3.2:3b",
        "ai_feedback": ai_feedback
    }