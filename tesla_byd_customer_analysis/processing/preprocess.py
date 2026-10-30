"""Text quality filtering and notebook-compatible NLP preprocessing."""

from __future__ import annotations

import re
import unicodedata

import pandas as pd

from .. import config

try:
    import nltk
    from nltk.corpus import stopwords, wordnet
    from nltk.stem import WordNetLemmatizer
    from nltk.tag import pos_tag
    from nltk.tokenize import wordpunct_tokenize
except ModuleNotFoundError:  # pragma: no cover
    nltk = None


SOURCE_NOISE = {"deleted", "removed", "edit", "amp", "https", "http", "www"}
FALLBACK_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by", "for", "from", "had", "has",
    "have", "he", "her", "his", "i", "if", "in", "is", "it", "its", "me", "my", "not", "of", "on",
    "or", "our", "she", "so", "that", "the", "their", "them", "there", "they", "this", "to", "was",
    "we", "were", "with", "you", "your",
}


def ensure_nltk() -> None:
    if nltk is None:
        raise ModuleNotFoundError("Install nltk from requirements.txt")


def get_stopwords() -> set[str]:
    if nltk is None:
        return FALLBACK_STOPWORDS - config.IMPORTANT_AUTOMOTIVE_WORDS
    try:
        return set(stopwords.words("english")) - config.IMPORTANT_AUTOMOTIVE_WORDS
    except LookupError:
        return FALLBACK_STOPWORDS - config.IMPORTANT_AUTOMOTIVE_WORDS


def simple_lemma(token: str) -> str:
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 4 and token.endswith("ing"):
        return token[:-3]
    if len(token) > 3 and token.endswith("ed"):
        return token[:-2]
    if len(token) > 3 and token.endswith("s"):
        return token[:-1]
    return token


def classify_quality(text: str) -> str:
    text = str(text).strip()
    if not text or text.lower() in {"[deleted]", "[removed]"}:
        return "spam"
    tokens = re.findall(r"[A-Za-z0-9$]+", text)
    alpha_tokens = [t for t in tokens if re.search(r"[A-Za-z]", t)]
    comparison_signal = bool(re.search(r"\b(cheaper|expensive|better|worse|vs|versus|value|range|service|quality|\$|aud)\b", text, flags=re.I))
    if len(alpha_tokens) < 3 and not comparison_signal:
        return "low_information"
    if len(set(t.lower() for t in alpha_tokens)) <= 2 and not comparison_signal:
        return "low_information"
    return "usable"


def _wordnet_pos(tag: str) -> str:
    if tag.startswith("J"):
        return wordnet.ADJ
    if tag.startswith("V"):
        return wordnet.VERB
    if tag.startswith("N"):
        return wordnet.NOUN
    if tag.startswith("R"):
        return wordnet.ADV
    return wordnet.NOUN


def clean_and_tokenise(text: str) -> tuple[str, list[str]]:
    ensure_nltk()
    raw = unicodedata.normalize("NFKC", str(text))
    raw = re.sub(r"https?://\S+|www\.\S+", " ", raw)
    raw = raw.lower()
    raw = re.sub(r"[^a-z0-9$%\s-]", " ", raw)
    tokens = [t for t in wordpunct_tokenize(raw) if re.fullmatch(r"[a-z0-9$%]+(?:-[a-z0-9]+)?", t)]
    stops = get_stopwords()
    try:
        lemmatiser = WordNetLemmatizer()
        tagged = pos_tag(tokens)
        use_wordnet = True
    except Exception:
        tagged = [(token, "N") for token in tokens]
        use_wordnet = False
    cleaned = []
    for token, tag in tagged:
        lemma = lemmatiser.lemmatize(token, _wordnet_pos(tag)) if use_wordnet else simple_lemma(token)
        if lemma in stops or lemma in SOURCE_NOISE or len(lemma) <= 1:
            continue
        cleaned.append(lemma)
    return " ".join(cleaned), cleaned


def preprocess_text(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["text_quality"] = df["text"].fillna("").map(classify_quality)
    cleaned = df["text"].fillna("").map(clean_and_tokenise)
    df["clean_text"] = cleaned.map(lambda item: item[0])
    df["tokens"] = cleaned.map(lambda item: " ".join(item[1]))
    df["word_count"] = cleaned.map(lambda item: len(item[1]))
    return df
