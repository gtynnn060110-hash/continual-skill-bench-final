## Task 27: Determine abnormality and classify severity of lab test results based on reference ranges.

Data files for this task are available in `/root/data/`.

# Patient Lab Results Abnormality Detection

## Description

You are provided with a CSV file `/app/workspace/lab_results.csv` containing patient laboratory test results. Each row contains the following columns:

- `patient_id`: Unique identifier for the patient
- `test_name`: Name of the laboratory test
- `value`: Numeric test result value
- `unit`: Unit of the test result
- `reference_low`: Lower bound of the normal reference range
- `reference_high`: Upper bound of the normal reference range

Your task is to:

1. Read the `lab_results.csv` file from the workspace.
2. For each test result, determine if the `value` is abnormal (outside the reference range).
3. If abnormal, classify the severity of the abnormality based on how far the value is from the reference range:
   - **Mild**: The value is outside the reference range but within 20% beyond the closest boundary.
   - **Moderate**: The value is between 20% and 50% beyond the closest boundary.
   - **Severe**: The value is more than 50% beyond the closest boundary.

   The percentage beyond the boundary is calculated relative to the reference range width:

   ```
   range_width = reference_high - reference_low
   if value < reference_low:
       diff = reference_low - value
   else:
       diff = value - reference_high
   percentage = diff / range_width
   ```

4. Generate a JSON file `/app/workspace/clinical_alerts.json` containing a list of alerts for all abnormal test results. Each alert should be a JSON object with the following fields:

   - `patient_id`
   - `test_name`
   - `value`
   - `unit`
   - `severity` (one of "mild", "moderate", "severe")

5. If there are no abnormal results, write an empty JSON list (`[]`).

## Input

- `/app/workspace/lab_results.csv` (CSV file with columns: patient_id, test_name, value, unit, reference_low, reference_high)

## Output

- `/app/workspace/clinical_alerts.json` (JSON file with a list of alerts as described above)

## Constraints

- Use the exact filenames and paths as specified.
- Ensure numeric calculations handle floating point values correctly.
- The output JSON must be valid and well-formatted.

## Example

If a test result is:

```
patient_id: P001
 test_name: Hemoglobin
 value: 10.5
 unit: g/dL
 reference_low: 12.0
 reference_high: 16.0
```

The value is below the reference low by 1.5 units. The range width is 4.0 (16.0 - 12.0), so the difference percentage is 1.5 / 4.0 = 0.375 (37.5%). This falls into the "moderate" severity category.

The alert JSON object would be:

```json
{
  "patient_id": "P001",
  "test_name": "Hemoglobin",
  "value": 10.5,
  "unit": "g/dL",
  "severity": "moderate"
}
```


---

Complete the task by writing a program or script that performs the above steps and writes the output file.

Output requirements:
- Write your answer to `/app/task_027_output.json`
- JSON object with your key findings, citations, and conclusions
- You must write the output to the file. Only responding in chat will receive no score.
