from typing import List


class TextChunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> List[str]:
        text = text.strip()
        if not text:
            return []

        segments = self._split_hierarchically(text)
        chunks = []
        current = ""

        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue

            candidate = f"{current}\n\n{segment}".strip() if current else segment

            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)

                if len(segment) <= self.chunk_size:
                    current = segment
                else:
                    chunks.extend(self._split_large_segment(segment))
                    current = ""

        if current:
            chunks.append(current)

        return self._apply_overlap(chunks)

    def _split_hierarchically(self, text: str) -> List[str]:
        blocks = []

        for paragraph_block in text.split("\n\n"):
            paragraph_block = paragraph_block.strip()
            if not paragraph_block:
                continue

            if len(paragraph_block) <= self.chunk_size:
                blocks.append(paragraph_block)
                continue

            for line_block in paragraph_block.split("\n"):
                line_block = line_block.strip()
                if not line_block:
                    continue

                if len(line_block) <= self.chunk_size:
                    blocks.append(line_block)
                    continue

                sentence_parts = [s.strip() for s in line_block.split(". ") if s.strip()]
                for i, sentence in enumerate(sentence_parts):
                    if i < len(sentence_parts) - 1 and not sentence.endswith("."):
                        sentence += "."
                    blocks.append(sentence)

        return blocks

    def _split_large_segment(self, segment: str) -> List[str]:
        result = []
        start = 0

        while start < len(segment):
            end = min(start + self.chunk_size, len(segment))
            piece = segment[start:end].strip()
            if piece:
                result.append(piece)
            start = end

        return result

    def _apply_overlap(self, chunks: List[str]) -> List[str]:
        if not chunks or self.overlap <= 0:
            return chunks

        overlapped_chunks = [chunks[0]]

        for i in range(1, len(chunks)):
            previous_tail = chunks[i - 1][-self.overlap :]
            current_chunk = chunks[i]

            merged = f"{previous_tail} {current_chunk}".strip()
            overlapped_chunks.append(merged)

        return overlapped_chunks