## Task 31: Determine patient eligibility for a clinical trial based on inclusion and exclusion criteria.

Data files for this task are available in `/root/data/`.

# Clinical Trial Patient Screening

## Description

You are provided with two files in the workspace:

- `patients.csv`: Contains patient data with the following columns:
  - `patient_id` (string)
  - `age` (integer)
  - `gender` (string, e.g., "M" or "F")
  - `diagnosis` (string)
  - `lab_values_json` (JSON string representing a dictionary of lab test names to numeric values)

- `trial_criteria.json`: Contains the clinical trial's inclusion and exclusion criteria. The JSON structure includes:
  - `inclusion`: a dictionary specifying criteria that must be met.
  - `exclusion`: a dictionary specifying criteria that disqualify a patient.

The criteria keys can include:
- `age`: an object with optional `min` and/or `max` integer values.
- `gender`: a list of allowed genders.
- `diagnosis`: a list of allowed diagnoses.
- `lab_values`: a dictionary with lab test names as keys and each value is an object with optional `min` and/or `max` numeric thresholds.

## Task

Write a program that:

1. Reads `patients.csv` and `trial_criteria.json` from the workspace.
2. For each patient, determines if they are **eligible** or **ineligible** for the clinical trial based on the criteria.
3. For ineligible patients, provide a list of reasons explaining which criteria were not met.
4. Writes the results to `screening_report.json` in the workspace. The output JSON should be a list of objects, each with:
   - `patient_id` (string)
   - `eligible` (boolean)
   - `reasons` (list of strings; empty if eligible)

## Details

- Age criteria: patient age must be within the inclusive range specified.
- Gender criteria: patient gender must be one of the allowed genders.
- Diagnosis criteria: patient diagnosis must be one of the allowed diagnoses.
- Lab values criteria: each specified lab test must be within the inclusive min/max range.

If a criterion is not specified in the inclusion or exclusion criteria, it should be ignored.

## Example

If inclusion criteria specify age >= 18 and <= 65, gender in ["M", "F"], diagnosis in ["diabetes"], and lab_values with "HbA1c" max 7.0, then a patient aged 70 or with HbA1c 8.0 would be ineligible.

## Files

- Input:
  - `/app/workspace/patients.csv`
  - `/app/workspace/trial_criteria.json`
- Output:
  - `/app/workspace/screening_report.json`


## Evaluation

Your solution will be tested on multiple datasets to verify correct eligibility screening and proper reasons for ineligibility.


---

Good luck!

Output requirements:
- Write your answer to `/app/task_031_output.json`
- JSON object with your key findings, citations, and conclusions
- You must write the output to the file. Only responding in chat will receive no score.
