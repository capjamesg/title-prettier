# title-prettier

An opinionated Python tool to change titles into a consistent format, and to add useful context to titles.

This tool is ideal for bookmarking tools, where you may want to regularize titles given a specific set of rules.

This tool applies a few transformations:

- Text after common separators (i.e. ` | `, ` - `) is removed.
- [video] is appended to titles where the URL is from a listed video site.
- [code] is appended to titles where the URL is from a listed code sharing site.
- [podcast] is appended to titles where the URL is from a podcast hosting page.
- [image] is appended to titles if a source is an image.
- Titles are turned to lowercase _if_ a URL is provided. See "Preserving proper nouns in titles" later in this document for more information.

## Usage

First, install the package:

```
pip install title-prettier
```

Then, import the `get_pretty_title` function and specify either a title or a URL:

```python
from title_prettier import get_pretty_title
title = get_pretty_title(url="https://jamesg.blog/2024/06/20/python-packages/")
# Python packages I love
title = get_pretty_title(title="How the Square Root of 2 Became a Number | Hacker News")
# How the square root of 2 became a number
```

## Examples

```
Building a full-text search engine in 150 lines of Python code · Bart de Goede -> Building a full-text search engine in 150 lines of Python code
Poets’ Odd Jobs | Academy of American Poets -> Poets’ Odd Jobs
Python packages I love | James' Coffee Blog -> Python packages I love
```

## Preserving proper nouns in titles

When you provide a URL, `title-prettier` aims to turn the contents of the title to lowercase. But, you may wonder: what about proper nouns?

Suppose a page has the title:

```
My Review Of ‘The Tortured Poets Department’
```

`The Tortured Poets Department` is a proper noun; an album name.

This package aims to preserve proper nouns with a heuristic. If a word is used more in uppercase than lowercase, its capitalisation is retained.

After being run through `titke-prettier`, the title above will become:

```
My review of ‘The Tortured Poets Department’
```

## License

This project is licensed under an [MIT license](LICENSE).
