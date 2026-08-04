## Task 61: Audit data processing records for GDPR compliance across lawful basis, consent, retention, and third-party sharing rules.

Data files for this task are available in `/root/data/`.

# GDPR Data Processing Records Audit

You are provided with a CSV file `processing_records.csv` located in the workspace directory. This file contains records of data processing activities with the following columns:

- `activity`: Description of the data processing activity.
- `data_type`: Type of personal data processed.
- `lawful_basis`: The lawful basis for processing (e.g., consent, contract, legal_obligation, legitimate_interest).
- `retention_days`: Number of days the data is retained.
- `consent_obtained`: Whether consent was obtained (`yes` or `no`).
- `third_party_sharing`: Whether data is shared with third parties (`yes` or `no`).

Your task is to:

1. Read the `processing_records.csv` file.
2. Check each record for GDPR compliance based on the following rules:
   - The `lawful_basis` must be one of the valid bases: `consent`, `contract`, `legal_obligation`, `legitimate_interest`, or `vital_interest`.
   - If the lawful basis is `consent`, then `consent_obtained` must be `yes`.
   - `retention_days` must be a positive integer and should not exceed 1095 days (3 years).
   - If `third_party_sharing` is `yes`, there must be a lawful basis.

3. Determine for each record if it is compliant or non-compliant.
4. Calculate the overall risk level:
   - `low` if all records are compliant.
   - `medium` if up to 20% of records are non-compliant.
   - `high` if more than 20% of records are non-compliant.

5. Write a JSON file `gdpr_audit.json` in the workspace with the following structure:

```json
{
  "findings": [
    {
      "activity": "...",
      "compliant": true
    },
    ...
  ],
  "compliant_count": <number>,
  "non_compliant_count": <number>,
  "risk_level": "low|medium|high"
}
```

Make sure your output JSON is valid and formatted as shown.

---

**Note:** The workspace directory path is provided as the environment variable or argument. Use it to read/write files.

Good luck!

Output requirements:
- Write your answer to `/app/task_061_output.json`
- JSON object with your key findings, citations, and conclusions
- You must write the output to the file. Only responding in chat will receive no score.
