#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI-powered Rule Suggestions based on move history (Feature #4)"""

import os
import re
from collections import Counter, defaultdict
from core.history import HistoryManager
from core.rules_manager import RulesManager


class AISuggester:
    def __init__(self, history_manager=None, rules_manager=None):
        self.history = history_manager or HistoryManager()
        self.rules = rules_manager or RulesManager()

    def analyze_patterns(self):
        entries = self.history.get_entries(limit=1000)
        if not entries:
            return {"suggestions": [], "patterns": {}}

        category_origins = defaultdict(lambda: Counter())
        keyword_freq = Counter()
        folder_patterns = defaultdict(list)
        extension_categories = defaultdict(Counter)

        for entry in entries:
            category = entry.get("category", "")
            filename = entry.get("filename", "")
            dest = entry.get("dest", "")
            source = entry.get("source", "")

            ext = os.path.splitext(filename)[1].lower()
            if ext:
                extension_categories[ext][category] += 1

            base_name = os.path.splitext(filename)[0].lower()
            words = re.split(r'[_\-.\s]+', base_name)
            for word in words:
                if len(word) > 2:
                    keyword_freq[(word, category)] += 1

            parts = dest.replace("\\", "/").split("/")
            for part in parts:
                if part and part != filename:
                    folder_patterns[category].append(part)

            source_dir = os.path.dirname(source)
            if source_dir:
                category_origins[category][source_dir] += 1

        return {
            "keyword_freq": keyword_freq,
            "extension_categories": extension_categories,
            "folder_patterns": folder_patterns,
            "category_origins": category_origins,
        }

    def suggest_rules(self):
        analysis = self.analyze_patterns()
        suggestions = []

        existing_rules = self.rules.all()

        ext_cats = analysis.get("extension_categories", {})
        for ext, cats in ext_cats.items():
            if len(cats) < 2:
                continue
            top_cat = cats.most_common(1)[0]
            if top_cat[1] >= 3:
                suggestions.append({
                    "type": "extension_category",
                    "title": f"Extension '{ext}' mostly goes to '{top_cat[0]}'",
                    "description": f"{top_cat[1]} files with extension '{ext}' were sorted to '{top_cat[0]}'",
                    "confidence": min(top_cat[1] / max(sum(cats.values()), 1), 1.0),
                    "action": {
                        "category": top_cat[0],
                        "extensions": [ext],
                    },
                })

        kw_freq = analysis.get("keyword_freq", {})
        keyword_groups = defaultdict(list)
        for (word, cat), count in kw_freq.items():
            if count >= 2:
                keyword_groups[(cat,)].append((word, count))

        for cat, words in keyword_groups.items():
            if len(words) < 1:
                continue
            top_words = sorted(words, key=lambda x: x[1], reverse=True)[:5]
            category = cat[0] if isinstance(cat, tuple) else cat
            if category not in existing_rules:
                continue
            existing_kw = set(existing_rules[category].get("name_contains", []))
            new_words = [w for w, c in top_words if w.lower() not in [k.lower() for k in existing_kw]]
            if new_words:
                suggestions.append({
                    "type": "keyword_suggestion",
                    "title": f"Add keywords to '{category}' rule",
                    "description": f"Keywords: {', '.join(new_words[:5])}",
                    "confidence": 0.7,
                    "action": {
                        "category": category,
                        "add_keywords": new_words[:5],
                    },
                })

        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        return suggestions

    def apply_suggestion(self, suggestion):
        action = suggestion.get("action", {})
        category = action.get("category")
        if not category:
            return False

        rule = self.rules.get(category)
        if not rule:
            return False

        if "extensions" in action:
            existing = set(rule.get("extensions", []))
            for ext in action["extensions"]:
                existing.add(ext)
            rule["extensions"] = list(existing)

        if "add_keywords" in action:
            existing_kw = rule.get("name_contains", [])
            for kw in action["add_keywords"]:
                if kw not in existing_kw:
                    existing_kw.append(kw)
            rule["name_contains"] = existing_kw

        self.rules.update(category, rule)
        return True
