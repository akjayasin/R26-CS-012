import re
from typing import Dict, List


class ClueExtractor:
    """
    Extracts technical clues from natural language prompts without using an AI model.

    Research purpose:
    This module converts unstructured natural language into technical signals that can be
    matched against code context. It supports middleware-level prompt understanding
    without depending on an LLM inside this component.
    """

    def __init__(self):
        self.stop_words = {
            "the", "is", "are", "was", "were", "a", "an", "and", "or", "to", "of",
            "in", "on", "for", "after", "before", "when", "why", "how", "please",
            "this", "that", "it", "be", "does", "do", "can", "you", "with", "from",
            "not", "user", "developer", "code", "function", "area", "related"
        }

        self.intent_patterns = {
            "debugging": [
                "fail", "failing", "failed", "error", "bug", "issue", "problem",
                "broken", "not loading", "crash", "exception"
            ],
            "explanation": [
                "explain", "describe", "understand", "how works", "what happens",
                "flow", "process"
            ],
            "optimisation": [
                "optimize", "optimise", "slow", "performance", "faster", "delay",
                "lag", "improve"
            ],
            "data_loading": [
                "loading", "load", "fetch", "refresh", "api", "response", "data"
            ],
            "ui_interaction": [
                "click", "button", "submit", "save", "type", "screen", "page"
            ]
        }

        self.domain_terms = {
            "login": ["login", "signin", "sign in", "authenticate", "authentication"],
            "profile": ["profile", "save", "update", "account"],
            "dashboard": ["dashboard", "customer", "refresh", "load"],
            "search": ["search", "keyword", "filter", "results"],
            "api": ["api", "request", "response", "fetch", "endpoint"]
        }

    def extract(self, normalized_prompt: str) -> Dict:
        prompt_lower = normalized_prompt.lower()

        tokens = self._tokenize(prompt_lower)
        keywords = self._extract_keywords(tokens)
        detected_intents = self._detect_intents(prompt_lower)
        domain_clues = self._detect_domain_clues(prompt_lower)

        weighted_clues = self._build_weighted_clues(
            keywords=keywords,
            detected_intents=detected_intents,
            domain_clues=domain_clues
        )

        return {
            "keywords": keywords,
            "detected_intents": detected_intents,
            "domain_clues": domain_clues,
            "weighted_clues": weighted_clues,
            "clue_extraction_status": "success"
        }

    def _tokenize(self, text: str) -> List[str]:
        raw_tokens = re.findall(r"[a-zA-Z0-9_]+", text)
        return [token for token in raw_tokens if len(token) > 2]

    def _extract_keywords(self, tokens: List[str]) -> List[str]:
        keywords = []

        for token in tokens:
            if token not in self.stop_words and token not in keywords:
                keywords.append(token)

        return keywords

    def _detect_intents(self, prompt_lower: str) -> List[str]:
        detected = []

        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in prompt_lower:
                    detected.append(intent)
                    break

        return detected if detected else ["general_request"]

    def _detect_domain_clues(self, prompt_lower: str) -> List[str]:
        detected = []

        for domain, terms in self.domain_terms.items():
            for term in terms:
                if term in prompt_lower:
                    detected.append(domain)
                    break

        return detected

    def _build_weighted_clues(
        self,
        keywords: List[str],
        detected_intents: List[str],
        domain_clues: List[str]
    ) -> Dict[str, int]:
        weighted = {}

        for keyword in keywords:
            weighted[keyword] = weighted.get(keyword, 0) + 2

        for intent in detected_intents:
            weighted[intent] = weighted.get(intent, 0) + 3

        for domain in domain_clues:
            weighted[domain] = weighted.get(domain, 0) + 5

        return weighted