import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"

SEPARATORS = [" – ", " | ", " · ", " ~ ", " - "]
VIDEO_SITES = ["youtube.com", "vimeo.com"]
CODE_SITES = ["github.com", "gitlab.com", "bitbucket.org"]
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
    (lambda url, _: url.endswith(".pdf"), "[pdf]"),
    (lambda url, _: any(url.endswith(ext) for ext in IMAGE_EXTENSIONS), "[image]"),
    (lambda _, domain: any(site in domain for site in VIDEO_SITES), "[video]"),
    (lambda _, domain: any(site in domain for site in CODE_SITES), "[code]"),
    (lambda _, domain: domain == "news.ycombinator.com", "[hn]"),
]


class URLRetrievalError(Exception):
    pass


class IncompleteRequestError(Exception):
    pass


# CASES: If home page, get text after last separator


def get_normalized_title(title: str = None, url: str = None) -> str:
    """
    Return a normalized title with the correct case.

    :param title: The title to normalize.
    :type title: str or None
    :param url: The URL to fetch the title from.
    :type url: str or None

    :return: The normalized title.
    :rtype: str
    """

    if not title and not url:
        raise IncompleteRequestError("Either title or URL must be provided")

    if not title:
        try:
            page = requests.get(url, timeout=5, headers={"User-Agent": USER_AGENT})
        except requests.exceptions.RequestException:
            raise URLRetrievalError("Failed to retrieve URL")

        soup = BeautifulSoup(page.content, "html.parser")

        if soup.title:
            title = soup.title.get_text()
        elif soup.h1:
            title = soup.h1.get_text()

    for sep in SEPARATORS:
        if sep in title:
            last_sep = title.rindex(sep)
            title = title[:last_sep]

            break

    for pattern, replacement in CONTENT_SUBSTITUTIONS:
        title = re.sub(pattern, replacement, title)

    title = title.rstrip(".")

    domain = urlparse(url).netloc if url else None

    for rule in CONTENT_TYPE_RULES:
        if rule[0](url, domain):
            title += f" {rule[1]}"
            break

    return title.replace("  ", " ").strip()
