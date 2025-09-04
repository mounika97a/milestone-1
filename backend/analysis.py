# backend/analysis.py
import math
import re
from typing import Dict

_SENT_SPLIT = re.compile(r"[.!?]+")
_WORD_SPLIT = re.compile(r"[^\w']+")

VOWELS = "aeiouy"

def _count_syllables(word: str) -> int:
    w = word.lower().strip()
    if not w:
        return 0
    # remove trailing e
    if w.endswith("e"):
        w = w[:-1]
    count = 0
    prev_is_vowel = False
    for ch in w:
        is_vowel = ch in VOWELS
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel
    return max(count, 1)

def _tokenize(text: str):
    sentences = [s.strip() for s in _SENT_SPLIT.split(text) if s.strip()]
    words = [w for w in _WORD_SPLIT.split(text) if w.strip()]
    return sentences, words

def _polysyllable_count(words):
    return sum(1 for w in words if _count_syllables(w) >= 3)

def readability_scores(text: str) -> Dict[str, float]:
    sentences, words = _tokenize(text)
    s_count = max(len(sentences), 1)
    w_count = max(len(words), 1)
    syllables = sum(_count_syllables(w) for w in words)

    words_per_sentence = w_count / s_count
    syllables_per_word = syllables / w_count

    # Flesch-Kincaid Reading Ease
    fk_re = 206.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word

    # Gunning Fog Index
    complex_words = _polysyllable_count(words)
    gf = 0.4 * (words_per_sentence + 100 * (complex_words / w_count))

    # SMOG (approximate for small samples)
    poly = max(complex_words, 1)
    smog = 1.0430 * math.sqrt(poly * (30.0 / s_count)) + 3.1291

    return {
        "flesch_kincaid_re": round(fk_re, 2),
        "gunning_fog": round(gf, 2),
        "smog": round(smog, 2),
        "sentences": s_count,
        "words": w_count,
        "syllables": syllables,
        "complex_words": complex_words,
    }
