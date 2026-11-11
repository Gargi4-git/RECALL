
from pathlib import Path

import fitz
from docx import Document
from pptx import Presentation


def extract_pdf(file_path: Path) -> list[dict]:
    """Extract text from each PDF page."""

    extracted_content = []

    with fitz.open(file_path) as pdf:
        for page_index, page in enumerate(pdf):
            text = page.get_text("text").strip()

            extracted_content.append({
                "source_type": "page",
                "source_number": page_index + 1,
                "text": text,
            })

    return extracted_content


def extract_pptx(file_path: Path) -> list[dict]:
    """Extract text from each PowerPoint slide."""

    presentation = Presentation(file_path)
    extracted_content = []

    for slide_index, slide in enumerate(presentation.slides):
        slide_text = []

        for shape in slide.shapes:
            if shape.has_text_frame:
                text = shape.text.strip()

                if text:
                    slide_text.append(text)

            if shape.has_table:
                for row in shape.table.rows:
                    cells = [
                        cell.text.strip()
                        for cell in row.cells
                    ]

                    row_text = " | ".join(
                        cell for cell in cells if cell
                    )

                    if row_text:
                        slide_text.append(row_text)

        extracted_content.append({
            "source_type": "slide",
            "source_number": slide_index + 1,
            "text": "\n".join(slide_text),
        })

    return extracted_content


def extract_docx(file_path: Path) -> list[dict]:
    """Extract paragraphs and tables from a Word document."""

    document = Document(file_path)
    extracted_content = []

    for paragraph_index, paragraph in enumerate(
        document.paragraphs
    ):
        text = paragraph.text.strip()

        if text:
            extracted_content.append({
                "source_type": "paragraph",
                "source_number": paragraph_index + 1,
                "text": text,
            })

    for table_index, table in enumerate(document.tables):
        rows = []

        for row in table.rows:
            cells = [
                cell.text.strip()
                for cell in row.cells
            ]

            rows.append(" | ".join(cells))

        table_text = "\n".join(rows).strip()

        if table_text:
            extracted_content.append({
                "source_type": "table",
                "source_number": table_index + 1,
                "text": table_text,
            })

    return extracted_content


def extract_document(file_path: Path) -> list[dict]:
    """Detect document format and extract structured content."""

    extension = file_path.suffix.lower()

    extractors = {
        ".pdf": extract_pdf,
        ".pptx": extract_pptx,
        ".docx": extract_docx,
    }

    extractor = extractors.get(extension)

    if extractor is None:
        raise ValueError(
            f"Unsupported document format: {extension}"
        )

    return extractor(file_path)
