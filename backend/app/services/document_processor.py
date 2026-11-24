"""Document processing service for PDF, DOCX, TXT, and Markdown files."""
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import pymupdf as fitz
import docx

class DocumentProcessor:
    """Extracts text, metadata, and page structure from multiple document formats."""

    @staticmethod
    def clean_text(text: str) -> str:
        """Normalize whitespace, remove invalid control characters and hyphenation artifacts."""
        if not text:
            return ""
        # Remove null bytes and control chars
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        # Fix hyphenated line breaks (e.g. "experi-\nment" -> "experiment")
        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
        # Normalize excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Normalize multiple spaces and tabs
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()

    @classmethod
    def extract_pdf(cls, file_path: str) -> List[Dict[str, Any]]:
        """Extract text page-by-page from PDF using PyMuPDF."""
        pages = []
        doc = fitz.open(file_path)
        try:
            for page_index in range(len(doc)):
                page = doc[page_index]
                page_text = page.get_text("text")
                cleaned = cls.clean_text(page_text)
                if cleaned:
                    pages.append({
                        "page_number": page_index + 1,
                        "text": cleaned,
                        "section": f"Page {page_index + 1}"
                    })
        finally:
            doc.close()
        return pages

    @classmethod
    def extract_docx(cls, file_path: str) -> List[Dict[str, Any]]:
        """Extract paragraphs and headings from DOCX using python-docx."""
        doc = docx.Document(file_path)
        sections = []
        current_section = "Introduction"
        current_text = []
        pseudo_page = 1
        char_count = 0

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            if para.style.name.startswith("Heading"):
                if current_text:
                    sections.append({
                        "page_number": pseudo_page,
                        "section": current_section,
                        "text": cls.clean_text("\n".join(current_text))
                    })
                    current_text = []
                current_section = text
            else:
                current_text.append(text)
                char_count += len(text)
                # Approximately 2500 characters per page
                if char_count > 2500:
                    sections.append({
                        "page_number": pseudo_page,
                        "section": current_section,
                        "text": cls.clean_text("\n".join(current_text))
                    })
                    current_text = []
                    char_count = 0
                    pseudo_page += 1

        if current_text:
            sections.append({
                "page_number": pseudo_page,
                "section": current_section,
                "text": cls.clean_text("\n".join(current_text))
            })

        return sections

    @classmethod
    def extract_text_or_markdown(cls, file_path: str) -> List[Dict[str, Any]]:
        """Extract plain text or markdown preserving section headers."""
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        lines = content.split("\n")
        sections = []
        current_section = "General"
        current_lines = []
        pseudo_page = 1
        char_count = 0

        for line in lines:
            line_str = line.strip()
            if line_str.startswith("#"):
                if current_lines:
                    sections.append({
                        "page_number": pseudo_page,
                        "section": current_section,
                        "text": cls.clean_text("\n".join(current_lines))
                    })
                    current_lines = []
                current_section = line_str.lstrip("#").strip()
            else:
                current_lines.append(line)
                char_count += len(line)
                if char_count > 2500:
                    sections.append({
                        "page_number": pseudo_page,
                        "section": current_section,
                        "text": cls.clean_text("\n".join(current_lines))
                    })
                    current_lines = []
                    char_count = 0
                    pseudo_page += 1

        if current_lines:
            sections.append({
                "page_number": pseudo_page,
                "section": current_section,
                "text": cls.clean_text("\n".join(current_lines))
            })

        return sections

    @classmethod
    def process_file(cls, file_path: str) -> List[Dict[str, Any]]:
        """Dispatch file extraction based on file extension."""
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            return cls.extract_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return cls.extract_docx(file_path)
        elif ext in [".txt", ".md", ".markdown"]:
            return cls.extract_text_or_markdown(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
