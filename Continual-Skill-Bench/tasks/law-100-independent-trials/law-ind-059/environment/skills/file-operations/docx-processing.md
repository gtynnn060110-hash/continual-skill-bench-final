# DOCX Processing Skill

## Overview
This skill provides guidance on reading and extracting content from DOCX files,
including paragraphs, headings, and tables.

## Reading DOCX Files

### Using python-docx
```python
from docx import Document

_doc = Document("contract.docx")

# Extract plain text paragraphs
paragraphs = [p.text for p in _doc.paragraphs if p.text.strip()]
text = "\n".join(paragraphs)
```

### Key Considerations
- Preserve paragraph order; it often reflects the clause structure.
- DOCX text can be split across runs; prefer paragraph-level extraction.
- If headings are important, read `paragraph.style.name` to detect them.

## Extracting Headings and Sections

```python
from docx import Document

_doc = Document("contract.docx")
sections = []
current = {"heading": None, "body": []}

for p in _doc.paragraphs:
    style = p.style.name or ""
    if style.startswith("Heading") and p.text.strip():
        if current["heading"] or current["body"]:
            sections.append(current)
        current = {"heading": p.text.strip(), "body": []}
    else:
        if p.text.strip():
            current["body"].append(p.text.strip())

if current["heading"] or current["body"]:
    sections.append(current)
```

## Extracting Tables

```python
from docx import Document

_doc = Document("contract.docx")
rows = []
for table in _doc.tables:
    for row in table.rows:
        rows.append([cell.text.strip() for cell in row.cells])
```

### Tips
- For clause matching, normalize whitespace and strip bullet characters.
- When extracting tables, watch for merged cells (duplicate text may appear).
- If the file is large, extract only required sections by heading keywords.

## Error Handling
- Catch `PackageNotFoundError` for missing or corrupt files.
- Validate that the extracted text is not empty before downstream use.
- Handle unexpected encoding artifacts by normalizing Unicode if needed.
