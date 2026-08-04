## Task 70: Classify software license permissions and restrictions across commercial use, modification, distribution, sublicense, patent rights, attribution, share-alike, trademark, and liability disclaimers.

Data files for this task are available in `/root/data/`.

# Software License Rights and Restrictions Matrix

## Overview

You are provided with a software license agreement text file located at `/app/workspace/license_agreement.txt`. Your task is to analyze this license agreement and classify it according to specific permissions and restrictions related to intellectual property rights.

## Permissions to Identify

For the license agreement, determine whether the following permissions are explicitly granted or not:

- `commercial_use`: Permission to use the software commercially.
- `modification`: Permission to modify the software.
- `distribution`: Permission to distribute the software.
- `sublicense`: Permission to grant sublicenses to others.
- `patent_use`: Permission to use any patents covered by the license.

## Restrictions to Identify

Also determine whether the following restrictions apply:

- `attribution`: Requirement to attribute the original author(s).
- `share_alike`: Requirement that derivative works be licensed under the same terms.
- `no_trademark`: Restriction on use of trademarks.
- `no_liability`: Disclaimer of liability by the licensor.

## Input

- `/app/workspace/license_agreement.txt`: A text file containing the full license agreement.

## Output

You must produce two files:

1. `/app/workspace/rights_matrix.csv`: A CSV file with the following columns:

   | Category    | Permission/Restriction | Granted (Yes/No) |
   |-------------|------------------------|------------------|

   Each row corresponds to one permission or restriction. The "Category" column is either "Permission" or "Restriction".

2. `/app/workspace/license_summary.json`: A JSON file summarizing the license with keys for each permission and restriction and boolean values indicating whether they are granted or restricted.

Example of `rights_matrix.csv`:

```
Category,Permission/Restriction,Granted
Permission,commercial_use,Yes
Permission,modification,No
Restriction,attribution,Yes
...
```

Example of `license_summary.json`:

```json
{
  "commercial_use": true,
  "modification": false,
  "distribution": true,
  "sublicense": false,
  "patent_use": true,
  "attribution": true,
  "share_alike": false,
  "no_trademark": true,
  "no_liability": true
}
```

## Requirements

- Read and analyze the license text for explicit mentions or strong implications of each permission and restriction.
- Output must be exactly as specified, with correct CSV headers and JSON keys.
- Use "Yes" or "No" in the CSV for the Granted column.
- Boolean values in JSON must be `true` or `false`.

## Evaluation

Your submission will be evaluated on:

- Correctness of classification for each permission and restriction.
- Correct formatting of the CSV and JSON output files.
- Robustness to varied license text phrasing.

Good luck!

Output requirements:
- Write your answer to `/app/task_070_output.json`
- JSON object with your key findings, citations, and conclusions
- You must write the output to the file. Only responding in chat will receive no score.
