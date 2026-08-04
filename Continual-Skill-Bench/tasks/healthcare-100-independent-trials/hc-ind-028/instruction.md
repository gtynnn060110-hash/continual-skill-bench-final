## Task 28: Identify and report drug interactions for patients based on their medication records and a known interaction database.

Data files for this task are available in `/root/data/`.

# Medication Interaction Checker

## Description

You are given two CSV files in the workspace:

- `patient_medications.csv`: Contains patient medication records with columns:
  - `patient_id` (string)
  - `medication` (string)

- `interaction_db.csv`: Contains known drug interactions with columns:
  - `drug_a` (string)
  - `drug_b` (string)
  - `severity` (string, e.g., "low", "moderate", "high")
  - `effect` (string, description of the interaction)

Your task is to:

1. Read both CSV files.
2. For each patient, identify all pairs of medications they are taking.
3. Check if any pair matches an interaction in the interaction database (order of drugs does not matter).
4. Generate a JSON report file `interaction_report.json` in the workspace, with the following structure:

```json
{
  "patient_id_1": [
    {
      "drug_a": "med1",
      "drug_b": "med2",
      "severity": "high",
      "effect": "description"
    },
    ...
  ],
  "patient_id_2": [
    ...
  ],
  ...
}
```

If a patient has no interactions, their entry should be an empty list.

## Requirements

- Read input files from the workspace directory.
- Write the output JSON file to the workspace directory.
- Consider medication pairs as unordered ("med1" + "med2" is the same as "med2" + "med1").
- Each interaction should be reported once per patient.

## Input Files

- `/app/workspace/patient_medications.csv`
- `/app/workspace/interaction_db.csv`

## Output File

- `/app/workspace/interaction_report.json`

## Example

If `patient_medications.csv` contains:

```
patient_id,medication
p1,Aspirin
p1,Warfarin
p2,Ibuprofen
p2,Paracetamol
```

and `interaction_db.csv` contains:

```
drug_a,drug_b,severity,effect
Aspirin,Warfarin,high,Increased risk of bleeding
Ibuprofen,Paracetamol,low,Mild stomach upset
```

Then `interaction_report.json` should be:

```json
{
  "p1": [
    {
      "drug_a": "Aspirin",
      "drug_b": "Warfarin",
      "severity": "high",
      "effect": "Increased risk of bleeding"
    }
  ],
  "p2": [
    {
      "drug_a": "Ibuprofen",
      "drug_b": "Paracetamol",
      "severity": "low",
      "effect": "Mild stomach upset"
    }
  ]
}
```

If a patient has no interactions, their list should be empty.

---

## Notes

- Use case-insensitive matching for medication names.
- You may assume no duplicate medication entries per patient.
- The interaction database may contain drug pairs in any order.

Good luck!

Output requirements:
- Write your answer to `/app/task_028_output.json`
- JSON object with your key findings, citations, and conclusions
- You must write the output to the file. Only responding in chat will receive no score.
