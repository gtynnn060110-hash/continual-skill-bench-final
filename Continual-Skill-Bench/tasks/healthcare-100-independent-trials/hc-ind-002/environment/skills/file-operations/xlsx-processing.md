# XLSX Processing Skill

## Overview
This skill covers reading and analyzing Excel (XLSX) workbooks, including
multi-sheet handling, column validation, and simple aggregations.

## Reading XLSX Files

### Using pandas
```python
import pandas as pd

# Read a single sheet
sheet = pd.read_excel("model.xlsx", sheet_name="Summary")

# Read all sheets
sheets = pd.read_excel("model.xlsx", sheet_name=None)
```

### Using openpyxl (cell-level access)
```python
from openpyxl import load_workbook

wb = load_workbook("model.xlsx", data_only=True)
ws = wb["Summary"]

headers = [cell.value for cell in ws[1]]
rows = [[cell.value for cell in row] for row in ws.iter_rows(min_row=2)]
```

## Column Validation

```python
required = {"date", "amount", "category"}
cols = {c.strip().lower() for c in sheet.columns}
missing = required - cols
if missing:
    raise ValueError(f"Missing columns: {sorted(missing)}")
```

## Aggregations and Checks

```python
# Total by category
by_cat = sheet.groupby("category")["amount"].sum().reset_index()

# Basic sanity checks
if (sheet["amount"] < 0).any():
    raise ValueError("Negative amounts found")
```

## Tips
- Use `data_only=True` when you want computed values, not formulas.
- Normalize column names to lowercase before validation.
- If sheet names are unknown, list with `wb.sheetnames` or `sheets.keys()`.
- For large files, load only necessary columns with `usecols` in pandas.

## Error Handling
- Catch `FileNotFoundError` and `InvalidFileException` for missing or corrupt files.
- Validate that numeric columns are parsed correctly (watch for strings).
- Handle empty sheets by checking `sheet.empty` (pandas) or row count (openpyxl).
