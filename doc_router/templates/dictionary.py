"""字典类模板 - 词汇表、术语表、药品手册等按条目组织的文档"""
import re
from typing import List
from .base import BaseTemplate
from ..schemas.chunk import ChunkResult


class DictionaryTemplate(BaseTemplate):
    """字典/词典类文档模板"""

    name = "dictionary"
    description = "词汇表、术语表、药品手册等按条目组织的文档"
    detect_keywords = ["词汇", "术语", "名词解释", "释义", "glossary", "dictionary"]
    detect_patterns = [
        r"^[A-Za-z\u4e00-\u9fff]{2,10}\s*[：:（\(]",
        r"^[A-Za-z\u4e00-\u9fff]{2,10}\s*$",
    ]

    def detect(self, text: str, metadata: dict = None) -> float:
        score = 0.0
        features = metadata or {}

        if features.get("has_glossary"):
            score += 0.4

        lines = text.split("\n")[:200]
        entry_count = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            for p in self.detect_patterns:
                if re.match(p, line):
                    entry_count += 1
                    break

        if entry_count >= 10:
            score += 0.3
        elif entry_count >= 5:
            score += 0.15

        first_text = text[:1000]
        for kw in self.detect_keywords:
            if kw in first_text:
                score += 0.15
                break

        return min(score, 1.0)

    def split(self, text: str, metadata: dict = None) -> List[ChunkResult]:
        entries = self._split_by_entry(text)
        chunks = []
        for i, entry in enumerate(entries):
            chunk_metadata = (metadata or {}).copy()
            chunk_metadata.update({
                "entry_term": entry.get("term", ""),
                "entry_type": "dictionary_entry",
            })
            chunks.append(ChunkResult(
                text=entry["text"],
                metadata=chunk_metadata,
                chunk_index=i,
            ))
        return chunks

    def _split_by_entry(self, text: str) -> list:
        """按条目切分"""
        entry_patterns = [
            r"^([A-Za-z\u4e00-\u9fff][A-Za-z\u4e00-\u9fff\-\s]{1,15})\s*[：:（\(]",
            r"^([A-Za-z\u4e00-\u9fff][A-Za-z\u4e00-\u9fff\-\s]{1,15})\s*$",
        ]

        entries = []
        current_term = ""
        current_lines = []

        for line in text.split("\n"):
            stripped = line.strip()
            if not stripped:
                current_lines.append(line)
                continue

            matched_term = None
            for p in entry_patterns:
                m = re.match(p, stripped)
                if m:
                    matched_term = m.group(1).strip()
                    break

            if matched_term:
                if current_lines:
                    entries.append({
                        "term": current_term,
                        "text": "\n".join(current_lines),
                    })
                current_term = matched_term
                current_lines = [line]
            else:
                current_lines.append(line)

        if current_lines:
            entries.append({
                "term": current_term,
                "text": "\n".join(current_lines),
            })

        return entries if entries else [{"term": "", "text": text}]
