import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"

SEPARATORS = [" -- ", " – ", " | ", " · ", " ~ ", " - ", " —", " : "]
VIDEO_SITES = ["youtube.com", "vimeo.com"]
CODE_SITES = ["github.com", "gitlab.com", "bitbucket.org"]
PDF_DOMAINS = ["arxiv.org"]
PODCAST_WEBSITES = [
    "anchor.fm",
    "podcasts.apple.com",
    "open.spotify.com",
    "podcasts.google.com",
    "pca.st",
    "overcast.fm",
    "castro.fm",
    "pocketcasts.com",
    "radiopublic.com",
    "breaker.audio",
]
IMAGE_EXTENSIONS = [
    "jpg",
    "jpeg",
    "png",
    "gif",
    "webp",
    "svg",
    "bmp",
    "ico",
    "tiff",
    "tif",
    "heif",
    "heic",
    "avif",
    "apng",
    "jxl",
]

CONTENT_SUBSTITUTIONS = [
    (r"\[.*?\]", ""),
]

CONTENT_TYPE_RULES = [
    # url, domain
    (lambda url, domain: url.endswith(".pdf") or domain in PDF_DOMAINS, "[pdf]"),
    (lambda url, _: any(url.endswith(ext) for ext in IMAGE_EXTENSIONS), "[image]"),
    (lambda _, domain: any(site in domain for site in VIDEO_SITES), "[video]"),
    (lambda _, domain: any(site in domain for site in CODE_SITES), "[code]"),
    (lambda _, domain: any(site in domain for site in PODCAST_WEBSITES), "[podcast]"),
    (lambda _, domain: domain == "news.ycombinator.com", "[hn]"),
]


class URLRetrievalError(Exception):
    pass


class IncompleteRequestError(Exception):
    pass


def get_pretty_title(title: str = "", url: str = "") -> str:
    """
    Return a prettified title with the correct case.

    :param title: The title to normalize.
    :type title: str or None
    :param url: The URL to fetch the title from.
    :type url: str or None

    :return: The prettified title.
    :rtype: str
    """

    if not title and not url:
        raise IncompleteRequestError("Either title or URL must be provided")

    if not title:
        try:
            session = requests.Session()
            session.max_redirects = 3
            page = session.get(url, timeout=5, headers={"User-Agent": USER_AGENT})
            page.raise_for_status()
        except requests.exceptions.RequestException:
            raise URLRetrievalError("Failed to retrieve URL")

        soup = BeautifulSoup(page.content, "html.parser")

        if soup.title:
            title = soup.title.get_text().lower()
        elif soup.h1:
            title = soup.h1.get_text().lower()

        page_text = soup.get_text().strip()
        words = page_text.split()

        word_freq = {}

        for idx, word in enumerate(words):
            if word in word_freq:
                word_freq[word] += 1
            else:
                word_freq[word] = 1

        new_title = ""

        for idx, word in enumerate(title.split()):
            if (
                word_freq.get(word.lower(), 0) < word_freq.get(word.capitalize(), 0)
                or idx == 0
            ):
                new_title += word.capitalize()
            else:
                new_title += word.lower()

            new_title += " "

        title = new_title.strip()

        content_type = page.headers.get("Content-Type", "").split(";")[0].split("/")[1]

        if content_type == "pdf":
            title += " [pdf]"

    for sep in SEPARATORS:
        if sep in title:
            last_sep = title.rindex(sep)
            title = title[:last_sep]

            break

    for pattern, replacement in CONTENT_SUBSTITUTIONS:
        if not title.endswith(replacement):
            title = re.sub(pattern, replacement, title)

    title = title.rstrip(".")

    domain = urlparse(url).netloc if url else ""

    for rule in CONTENT_TYPE_RULES:
        if rule[0](url, domain):
            title += f" {rule[1]}"
            break

    # if title starts with [...], remove it
    title = re.sub(r"^\[.*?\]", "", title)

    return title.replace("  ", " ").strip()