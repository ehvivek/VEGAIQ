"""
core/docling_service.py
PitMind — IBM Docling wrapper for document parsing and intelligence.
Extracts high-fidelity structured text (Markdown) from racing documents.
"""

import sys
import os
import re
from pathlib import Path

# Set up project path
_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Flags and cached converter
_DOCLING_AVAILABLE = False
_converter = None

try:
    # Try importing the official IBM Docling package
    from docling.document_converter import DocumentConverter
    _DOCLING_AVAILABLE = True
except ImportError:
    _DOCLING_AVAILABLE = False


def has_docling() -> bool:
    """Check if the native IBM Docling library is installed and available."""
    return _DOCLING_AVAILABLE


def parse_document(file_bytes: bytes, file_name: str) -> str:
    """
    Parse document content into clean Markdown format.
    Uses native IBM Docling if available, falling back to pure-python pypdf / native parsers.
    """
    global _converter

    ext = Path(file_name).suffix.lower()
    
    # 1. Native IBM Docling pipeline
    if _DOCLING_AVAILABLE:
        try:
            print(f"[Docling] Using native IBM Docling to parse: {file_name}")
            if _converter is None:
                _converter = DocumentConverter()
            
            # Save bytes to a temp file in data directory
            temp_dir = _PROJECT_ROOT / "data" / "temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_file_path = temp_dir / file_name
            
            with open(temp_file_path, "wb") as f:
                f.write(file_bytes)
            
            # Convert
            result = _converter.convert(temp_file_path)
            markdown_content = result.document.export_to_markdown()
            
            # Clean up temp file
            if temp_file_path.exists():
                os.remove(temp_file_path)
                
            return markdown_content
        except Exception as e:
            print(f"[Docling] Native parser failed: {e}. Falling back to standard parser.")

    # 2. Resilient fallback parsers
    print(f"[Docling-Fallback] Parsing file {file_name} with standard parser...")
    
    # Text or CSV files
    if ext in [".txt", ".csv", ".log", ".json", ".xml", ".yaml", ".yml"]:
        try:
            return file_bytes.decode("utf-8", errors="replace")
        except Exception as e:
            return f"Error reading text file: {e}"

    # PDF files
    elif ext == ".pdf":
        try:
            import pypdf
            # Read PDF bytes
            import io
            pdf_file = io.BytesIO(file_bytes)
            reader = pypdf.PdfReader(pdf_file)
            
            text_parts = []
            text_parts.append(f"# {file_name} (Standard PDF Extractor)")
            text_parts.append(f"*Note: Parsed using standard lightweight PDF extractor. To use layout-aware parsing, install the full ibm-docling suite.*")
            text_parts.append("---")
            
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"## Page {i + 1}\n{page_text}")
            
            return "\n\n".join(text_parts)
        except ImportError:
            # Fallback if pypdf is not installed either - extract readable ASCII characters
            ascii_chars = []
            for b in file_bytes[:100000]:  # Limit size
                if 32 <= b <= 126 or b in [10, 13, 9]:
                    ascii_chars.append(chr(b))
            raw_text = "".join(ascii_chars)
            # Basic cleanup of regex non-printable streams
            cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', raw_text)
            return (f"# {file_name} (Raw Extraction)\n\n"
                    f"*System Warning: Neither 'docling' nor 'pypdf' libraries are installed. Showing raw character stream.*\n\n"
                    f"--- \n\n"
                    f"{cleaned[:15000]}...\n\n[Truncated due to raw stream size]")
        except Exception as e:
            return f"Error extracting PDF: {e}"

    # HTML files
    elif ext in [".html", ".htm"]:
        try:
            html_text = file_bytes.decode("utf-8", errors="replace")
            # Strip tags
            clean_text = re.sub(r'<[^>]+>', ' ', html_text)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            return f"# {file_name} (HTML Extracted)\n\n{clean_text}"
        except Exception as e:
            return f"Error reading HTML: {e}"

    # Unknown format
    return (f"# {file_name}\n\n"
            f"*Format: {ext.upper()}*\n\n"
            f"Binary file content preview ({len(file_bytes)} bytes):\n"
            f"```\n{file_bytes[:1000]}...\n```")
