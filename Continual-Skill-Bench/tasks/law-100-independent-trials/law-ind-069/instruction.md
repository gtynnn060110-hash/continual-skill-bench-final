## Task 69: Extract and structure key contractual sections from a merger agreement document.

Data files for this task are available in `/root/data/`.

# M&A Due Diligence Document Analysis

## Objective

You are given a merger agreement document located at `/app/workspace/merger_agreement.txt`. Your task is to analyze this legal contract and extract the following key sections:

- `conditions_precedent`
- `representations_warranties`
- `indemnification_terms`
- `closing_timeline`
- `material_adverse_change_clause`

After extracting these sections, you must write them into a JSON file at `/app/workspace/due_diligence.json` with the following structure:

```json
{
  "conditions_precedent": "...",
  "representations_warranties": "...",
  "indemnification_terms": "...",
  "closing_timeline": "...",
  "material_adverse_change_clause": "..."
}
```

## Details

- The input file `merger_agreement.txt` contains a simulated merger agreement with multiple sections.
- Each section is clearly marked by a header line in uppercase, e.g., `CONDITIONS PRECEDENT`, `REPRESENTATIONS AND WARRANTIES`, etc.
- Extract the full text under each relevant header up to the next header or the end of the document.
- Preserve the original formatting and line breaks within each extracted section.
- If a section is missing, set its value to an empty string.

## Requirements

- Read from `/app/workspace/merger_agreement.txt`.
- Extract the five specified sections.
- Write the extracted data as JSON to `/app/workspace/due_diligence.json`.
- Ensure the output JSON is valid and UTF-8 encoded.

## Evaluation

Your solution will be tested on the provided synthetic merger agreement document. Correct extraction and JSON formatting are required to pass.

---

### Summary
- Input: `/app/workspace/merger_agreement.txt`
- Output: `/app/workspace/due_diligence.json`
- Extract sections: `conditions_precedent`, `representations_warranties`, `indemnification_terms`, `closing_timeline`, `material_adverse_change_clause`
- Preserve formatting
- Empty string if section missing

Good luck!

Output requirements:
- Write your answer to `/app/task_069_output.json`
- JSON object with your key findings, citations, and conclusions
- You must write the output to the file. Only responding in chat will receive no score.
