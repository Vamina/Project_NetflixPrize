import re
import string
import unicodedata
from typing import List, Set

import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt


STOPWORDS: Set[str] = {
    "the", "and", "a", "an", "in", "on", "of", "for", "to", "from", "with", "at",
    "by", "is", "it", "this", "that", "as", "be", "are", "was", "were", "or", "but",
    "if", "so", "than", "then", "there", "here", "when", "where", "how", "what",
    "which", "who", "whom", "why", "into", "out", "up", "down", "over", "under",
    "again", "once", "because", "about"
}


def fix_first_word(text: str) -> str:
    """
    Fix the first word in a paragraph if it contains an internal misplaced space
    between two adjacent letters. Example: 'W hen' → 'When'.

    Parameters
    ----------
    text : str
        The original paragraph text.

    Returns
    -------
    str
        The corrected paragraph text.
    """
    if (
        len(text) >= 3
        and text[0].isalpha()
        and text[1] == " "
        and text[2].isalpha()
    ):
        return text[0] + text[2] + text[3:]
    return text


def clean_for_wordcloud(text: str) -> List[str]:
    """
    Normalize and sanitize raw text so it can be used for word cloud generation.
    Removes accents, punctuation, non-alphanumeric characters and converts to lowercase.

    Parameters
    ----------
    text : str
        The full text extracted from the article.

    Returns
    -------
    List[str]
        A list of normalized words ready for frequency analysis or word clouds.
    """
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode("utf-8")
    text = text.lower()

    for punct in string.punctuation:
        text = text.replace(punct, " ")

    text = "".join(
        char if char.isalnum() or char.isspace() else " "
        for char in text
    )

    return text.split()


def generate_wordcloud(words: List[str]):
    """
    Generate and display a word cloud from a list of words.

    Parameters
    ----------
    words : List[str]
        A list of filtered, preprocessed words.

    Returns
    -------
    matplotlib.figure.Figure
        The matplotlib figure containing the word cloud.
    """
    joined = " ".join(words)
    wc = WordCloud(width=1200, height=800, background_color="white")
    wc = wc.generate(joined)

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    fig.tight_layout()
    plt.show()

    return fig


URL = (
    "https://www.theguardian.com/media/2025/aug/28/bland-easy-to-follow-for-fans-"
    "of-everything-what-has-the-netflix-algorithm-done-to-our-films"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/121.0 Safari/537.36"
    )
}

response = requests.get(URL, headers=HEADERS)
soup = BeautifulSoup(response.text, "html.parser")
article = soup.find("article")

if not article:
    print("Article tag not found.")
else:
    paragraphs = [p.get_text(" ", strip=True) for p in article.find_all("p")]
    cleaned = [re.sub(r"\s+", " ", para).strip() for para in paragraphs]
    cleaned = [fix_first_word(p) for p in cleaned]
    full_text = " ".join(cleaned)

    words = clean_for_wordcloud(full_text)
    words = [w for w in words if w not in STOPWORDS]

    generate_wordcloud(words)

