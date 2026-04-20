import io
import re
from pathlib import Path

import fitz  # PyMuPDF
from docx import Document
from fastapi import UploadFile


class DocumentProcessor:
    ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

    async def extract_text(self, file: UploadFile) -> str:
        extension = Path(file.filename).suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {extension}")

        content = await file.read()

        if not content:
            raise ValueError("Uploaded file is empty")

        if extension == ".pdf":
            text = self._extract_pdf_text(content)
        elif extension == ".docx":
            text = self._extract_docx_text(content)
        elif extension == ".txt":
            text = self._extract_txt_text(content)
        else:
            raise ValueError(f"Unsupported file type: {extension}")

        cleaned = self._clean_text(text)

        if not cleaned.strip():
            raise ValueError("No readable text could be extracted from the file")

        await file.seek(0)
        return cleaned

    def _extract_pdf_text(self, content: bytes) -> str:
        text_parts = []
        pdf_stream = io.BytesIO(content)

        with fitz.open(stream=pdf_stream.read(), filetype="pdf") as pdf:
            for page in pdf:
                page_text = page.get_text("text")
                if page_text:
                    text_parts.append(page_text)

        return "\n".join(text_parts)

    def _extract_docx_text(self, content: bytes) -> str:
        doc_stream = io.BytesIO(content)
        document = Document(doc_stream)
        paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)

    def _extract_txt_text(self, content: bytes) -> str:
        return content.decode("utf-8", errors="ignore")

    def _clean_text(self, text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = text.replace("\u00a0", " ")
        text = text.replace("\ufeff", "")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[^\S\n]+", " ", text)
        return text.strip()