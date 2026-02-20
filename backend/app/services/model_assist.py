from __future__ import annotations

import re


_TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")


def _tokenize(text: str) -> set[str]:
    return set(_TOKEN_RE.findall((text or "").lower()))


def score_keywords_with_model_assist(text: str, keywords: list[str]) -> tuple[float, list[str]]:
    """
    Lightweight model-assist approximation:
    - token overlap on text
    - synonym expansion for broad semantic matching
    Returns confidence in [0,1] and matched terms.
    """
    synonyms = {
        "tax": {"irs", "filing", "refund", "w2", "1099"},
        "doctor": {"clinic", "provider", "physician"},
        "lab": {"panel", "diagnostic", "result", "blood"},
        "project": {"sprint", "milestone", "roadmap", "blocker"},
        "financial": {"bank", "invoice", "payment", "statement", "bill"},
    }

    tokens = _tokenize(text)
    if not tokens:
        return 0.0, []

    expanded_keywords: set[str] = set()
    for kw in keywords:
        kw_norm = kw.lower()
        expanded_keywords.add(kw_norm)
        expanded_keywords.update(synonyms.get(kw_norm, set()))

    matched = sorted(tokens & expanded_keywords)
    confidence = min(1.0, len(matched) / max(2, len(keywords)))
    return confidence, matched
