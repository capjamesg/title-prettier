import pytest

from title_normalizer import (
    IncompleteRequestError,
    URLRetrievalError,
    get_pretty_title,
)

TEST_CASES = [
    # title, url, expected
    (
        "Screen time causes shallow breathing. Here's how to fix screen apnea : Body Electric : NPR",
        "",
        "Screen time causes shallow breathing. Here's how to fix screen apnea : Body Electric",
    ),
    (
        "Factored Verification: Detecting and Reducing Hallucination in Summaries of Academic Papers",
        "https://arxiv.org/pdf/2310.10627",
        "Factored Verification: Detecting and Reducing Hallucination in Summaries of Academic Papers [pdf]",
    ),
    ("How MOSS Works", "", "How MOSS Works"),
    ("Down Bad", "https://www.youtube.com/watch?v=N61UALi1MuI", "Down Bad [video]"),
    (
        "Building a full-text search engine in 150 lines of Python code · Bart de Goede",
        "",
        "Building a full-text search engine in 150 lines of Python code",
    ),
    ("Visual Information Theory -- colah's blog", "", "Visual Information Theory"),
    ("", "https://colah.github.io/posts/2015-09-Visual-Information/", "Visual information theory"), # lowercase the title when a URL is provided and context is available
    ("", "https://coloradosun.com/2024/02/28/perelandra-bookshop-reader-in-residence/", "Fort Collins bookstore pays people to sit down and read quietly"),
    ("Poets’ Odd Jobs | Academy of American Poets", "", "Poets’ Odd Jobs"),
    ("[2310.01783] Can large language models provide useful feedback on research papers? A large-scale empirical analysis", "", "Can large language models provide useful feedback on research papers? A large-scale empirical analysis"),
]


def test_titles():
    for title, url, expected in TEST_CASES:
        print(f"Testing title: {title} and url: {url}")
        assert get_pretty_title(title=title, url=url) == expected


def test_incomplete_request_error():
    with pytest.raises(IncompleteRequestError):
        get_pretty_title()


def test_url_retrieval_error():
    with pytest.raises(URLRetrievalError):
        get_pretty_title(url="https://example.com/xzy")
