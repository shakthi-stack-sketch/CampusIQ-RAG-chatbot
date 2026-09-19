import os
from pathlib import Path
from typing import List, Dict, Any
import fitz  # PyMuPDF
from docx import Document as DocxDocument

from backend.app.config import DOCUMENTS_DIR

def detect_category(filename: str) -> str:
    """Infer category from filename for metadata indexing."""
    fn = filename.lower()
    if "menu" in fn or "mess" in fn:
        return "mess_menu"
    elif "bus" in fn or "transport" in fn or "boarding" in fn:
        return "transportation"
    elif "calendar" in fn or "academic" in fn or "sem" in fn:
        return "academics"
    elif "dress" in fn or "code" in fn:
        return "dress_code"
    elif "hostel" in fn:
        return "hostel"
    elif "club" in fn or "innovation" in fn or "hackathon" in fn:
        return "clubs_and_events"
    return "general_college_info"

# Verified transcription fallback for scanned PDFs that lack a digital text layer
SCANNED_PDF_TRANSCRIPTS: Dict[str, List[str]] = {
    "UG Academic Calendar Odd Sem 2026-27 PEC.pdf": [
        (
            "PRATHYUSHA ENGINEERING COLLEGE\n"
            "UG - ACADEMIC CALENDAR 2026-27 ODD SEMESTER - III/V/VII SEM\n\n"
            "MONTHLY CALENDAR (JULY, AUGUST, SEPTEMBER 2026):\n\n"
            "JULY 2026:\n"
            "- 09.07.2026 (Thursday): College Reopening for Odd Semester (III, V, VII Semester)\n"
            "- 27.07.2026: Unit 1 Syllabus Completion\n"
            "- 28.07.2026: Internal Assessment Test 1 (IAT 1) Commences\n"
            "- July Working Days: 17 days\n\n"
            "AUGUST 2026:\n"
            "- 10.08.2026: Group Presentation 1 (GP 1)\n"
            "- 14.08.2026: Unit 2 Syllabus Completion\n"
            "- 15.08.2026: Independence Day (Holiday)\n"
            "- 26.08.2026: Milad-un-Nabi (Holiday)\n"
            "- 28.08.2026: Group Presentation 2 (GP 2)\n"
            "- August Working Days: 21 days\n\n"
            "SEPTEMBER 2026:\n"
            "- 03.09.2026: Unit 3 Syllabus Completion\n"
            "- 04.09.2026: Krishna Jayanthi (Holiday)\n"
            "- 07.09.2026: Internal Assessment Test 2 (IAT 2) Commences\n"
            "- 14.09.2026: Vinayagar Chathurthi (Holiday)\n"
            "- 22.09.2026: Unit 4 Syllabus Completion\n"
            "- September Working Days: 22 days"
        ),
        (
            "PRATHYUSHA ENGINEERING COLLEGE\n"
            "UG - ACADEMIC CALENDAR 2026-27 ODD SEMESTER - III/V/VII SEM\n\n"
            "MONTHLY CALENDAR (OCTOBER, NOVEMBER, DECEMBER 2026):\n\n"
            "OCTOBER 2026:\n"
            "- 02.10.2026: Gandhi Jayanthi (Holiday)\n"
            "- 08.10.2026: Unit 5 Syllabus Completion\n"
            "- 12.10.2026: Internal Assessment Test 3 (IAT 3) Commences\n"
            "- 20.10.2026: Ayudha Pooja (Holiday)\n"
            "- 21.10.2026: Vijaya Dasami (Holiday)\n"
            "- 26.10.2026: Model Examination Commences\n"
            "- October Working Days: 19 days\n\n"
            "NOVEMBER 2026:\n"
            "- 02.11.2026: Practical Examinations Commence\n"
            "- 08.11.2026: Deepavali (Holiday)\n"
            "- 11.11.2026: Theory End Semester University Examinations Commence\n"
            "- 24.11.2026: Guru Nanak Jayanthi (Holiday)\n"
            "- November Working Days: 20 days\n\n"
            "DECEMBER 2026:\n"
            "- 25.12.2026: Christmas (Holiday)\n"
            "- December Working Days: 22 days"
        ),
        (
            "PRATHYUSHA ENGINEERING COLLEGE\n"
            "UG - ACADEMIC CALENDAR 2026-27 ODD SEMESTER - III/V/VII SEM\n\n"
            "SYLLABUS COMPLETION SCHEDULE:\n"
            "- Unit 1: 09.07.2026 to 27.07.2026 (13 working days) | Submission Date: 27.07.2026\n"
            "- Unit 2: 28.07.2026 to 14.08.2026 (15 working days) | Submission Date: 14.08.2026\n"
            "- Unit 3: 17.08.2026 to 03.09.2026 (14 working days) | Submission Date: 03.09.2026\n"
            "- Unit 4: 05.09.2026 to 22.09.2026 (13 working days) | Submission Date: 22.09.2026\n"
            "- Unit 5: 23.09.2026 to 08.10.2026 (12 working days) | Submission Date: 08.10.2026\n"
            "- Record Notebook Submission: Following Unit 5 completion\n\n"
            "EXAMINATION AND ASSESSMENT SCHEDULE:\n"
            "- Model Examination: 26.10.2026 to 30.10.2026\n"
            "- University Theory Examinations: 11.11.2026 onwards\n\n"
            "COLLEGE WORKING DAYS BREAKDOWN (TOTAL: 79 DAYS):\n"
            "- July: 17 working days\n"
            "- August: 21 working days\n"
            "- September: 22 working days\n"
            "- October: 19 working days\n"
            "- Total Semester Working Days: 79 days\n\n"
            "LIST OF OFFICIAL HOLIDAYS:\n"
            "- 15.08.2026: Independence Day\n"
            "- 26.08.2026: Milad-un-Nabi\n"
            "- 04.09.2026: Krishna Jayanthi\n"
            "- 14.09.2026: Vinayagar Chathurthi\n"
            "- 02.10.2026: Gandhi Jayanthi\n"
            "- 20.10.2026: Ayudha Pooja\n"
            "- 21.10.2026: Vijaya Dasami\n"
            "- 08.11.2026 & 24.11.2026: Deepavali & Guru Nanak Jayanthi\n"
            "- 25.12.2026: Christmas\n\n"
            "COLLEGE EVENTS:\n"
            "- 17.07.2026 & 18.07.2026: Prayoga Senior\n"
            "- 07.08.2026 & 08.08.2026: Prayoga Junior\n"
            "- Induction Day"
        ),
        (
            "PRATHYUSHA ENGINEERING COLLEGE\n"
            "UG - ACADEMIC CALENDAR 2026-27 ODD SEMESTER - III/V/VII SEM\n\n"
            "CLASS COMMITTEE MEETINGS (CCM):\n"
            "- CCM 1: 27.07.2026\n"
            "- CCM 2: 03.09.2026\n"
            "- CCM 3: 08.10.2026\n\n"
            "COURSE COMMITTEE MEETINGS (COCM):\n"
            "- Meeting 1 (BCS): 03.07.2026\n"
            "- Meeting 2: 02.09.2026\n"
            "- Meeting 3: 07.10.2026\n\n"
            "MENTOR MEETINGS:\n"
            "- Mentor Meeting 1 (MM1): 27.07.2026\n"
            "- Mentor Meeting 2 (MM2): 08.10.2026\n"
            "- Parents-Teachers Meeting (PTM): At Department Convenience\n\n"
            "ASSESSMENT AND IQAC AUDIT SCHEDULE:\n"
            "- IAT 1 (Internal Assessment Test 1): 28.07.2026 to 03.08.2026 (Audit: BCS)\n"
            "- IAT 2 (Internal Assessment Test 2): 07.09.2026 to 12.09.2026 (Audit: IAT 1)\n"
            "- IAT 3 (Internal Assessment Test 3): 12.10.2026 to 17.10.2026 (Audit: IAT 2)\n"
            "- Model Examination: 26.10.2026 to 31.10.2026"
        )
    ]
}

def parse_pdf(file_path: Path) -> List[Dict[str, Any]]:
    """Parse PDF using PyMuPDF (fitz) preserving page numbers and formatting. Does not silently skip pages."""
    docs = []
    category = detect_category(file_path.name)
    title = file_path.stem.replace("_", " ").title()

    try:
        doc = fitz.open(str(file_path))
        total_pages = len(doc)
        total_chars = 0
        fallback_pages = SCANNED_PDF_TRANSCRIPTS.get(file_path.name, [])

        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text("text").strip()

            # If page text is empty (scanned image page), check verified transcript fallback
            if not text and page_num < len(fallback_pages):
                text = fallback_pages[page_num].strip()

            if text:
                total_chars += len(text)
                docs.append({
                    "content": text,
                    "metadata": {
                        "source": file_path.name,
                        "title": f"{title} (Page {page_num + 1})",
                        "category": category,
                        "source_type": "official_document",
                        "source_platform": "Official PEC Document",
                        "page": page_num + 1,
                        "total_pages": total_pages,
                        "file_path": str(file_path)
                    }
                })
            else:
                print(f"[DocParser] Warning: Page {page_num + 1} of {file_path.name} contains no readable text.")

        doc.close()
        print(f"[DocParser] Parsed PDF '{file_path.name}' (PyMuPDF): {len(docs)}/{total_pages} pages, {total_chars} chars.")
    except Exception as e:
        print(f"[DocParser] ERROR: Failed reading PDF '{file_path.name}': {e}")

    return docs

def parse_docx(file_path: Path) -> List[Dict[str, Any]]:
    """Parse DOCX using python-docx extracting all paragraphs and table rows."""
    category = detect_category(file_path.name)
    title = file_path.stem.replace("_", " ").title()
    try:
        doc = DocxDocument(str(file_path))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        
        # Also extract all table cells cleanly
        table_lines = []
        for table in doc.tables:
            for row in table.rows:
                cells = [c.text.strip() for c in row.cells if c.text.strip()]
                if cells:
                    table_lines.append(" | ".join(cells))

        all_text_elements = paragraphs + table_lines
        text = "\n".join(all_text_elements)
        if text:
            print(f"[DocParser] Parsed DOCX '{file_path.name}' (python-docx): {len(paragraphs)} paragraphs, {len(table_lines)} table rows, {len(text)} chars.")
            return [{
                "content": text,
                "metadata": {
                    "source": file_path.name,
                    "title": title,
                    "category": category,
                    "source_type": "official_document",
                    "source_platform": "Official PEC Document",
                    "page": 1,
                    "file_path": str(file_path)
                }
            }]
        else:
            print(f"[DocParser] Warning: DOCX '{file_path.name}' is empty.")
    except Exception as e:
        print(f"[DocParser] ERROR: Failed reading DOCX '{file_path.name}': {e}")
    return []

def parse_txt(file_path: Path) -> List[Dict[str, Any]]:
    """Parse TXT file with standard Python file handling."""
    category = detect_category(file_path.name)
    title = file_path.stem.replace("_", " ").title()
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read().strip()
        if text:
            print(f"[DocParser] Parsed TXT '{file_path.name}': {len(text)} chars.")
            return [{
                "content": text,
                "metadata": {
                    "source": file_path.name,
                    "title": title,
                    "category": category,
                    "source_type": "official_document",
                    "source_platform": "Official PEC Document",
                    "page": 1,
                    "file_path": str(file_path)
                }
            }]
        else:
            print(f"[DocParser] Warning: TXT '{file_path.name}' is empty.")
    except Exception as e:
        print(f"[DocParser] ERROR: Failed reading TXT '{file_path.name}': {e}")
    return []

def parse_all_documents() -> List[Dict[str, Any]]:
    """Parse all college documents (PDF, DOCX, TXT) from the documents directory with comprehensive logging."""
    all_docs = []
    if not DOCUMENTS_DIR.exists():
        print(f"[DocParser] ERROR: Directory does not exist: {DOCUMENTS_DIR}")
        return all_docs

    for file_path in sorted(DOCUMENTS_DIR.iterdir()):
        if not file_path.is_file():
            continue

        ext = file_path.suffix.lower()
        if ext == ".pdf":
            all_docs.extend(parse_pdf(file_path))
        elif ext == ".docx":
            all_docs.extend(parse_docx(file_path))
        elif ext == ".txt":
            all_docs.extend(parse_txt(file_path))
        else:
            print(f"[DocParser] Skipping unsupported file extension: {file_path.name}")

    print(f"[DocParser] Ingestion complete: Parsed {len(all_docs)} raw document sections from {DOCUMENTS_DIR}.")
    return all_docs
