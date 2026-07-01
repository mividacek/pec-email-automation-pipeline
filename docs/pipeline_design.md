# Pipeline Design

## Goal

The validation pipeline prepares document-processing data for downstream
processing by:

- normalizing deterministic filename inconsistencies
- detecting rule-based validation issues
- creating a complete audit trail
- exporting a validated dataset for subsequent pipelines
---
## Workflow

richiesta.xlsx        doc/
       │               │
       └──────┬────────┘
              │
      Validation Pipeline
              │
      ├── audit_log.csv
      └── validated_data.csv
              │
              ▼
        ML Validation
              │
              ▼
        Reconciliation
              │
              ▼
         Tracciato.csv

The project is intentionally divided into independent pipelines to separate deterministic validation, ML-assisted decision support, and document reconciliation.

---

## Input Files

data/
└── generated/
    ├── richiesta.xlsx
    └── doc/
        ├── document1.pdf
        ├── document2.pdf
        └── ...

---

## Pipeline 1 – Validation

### Stage 1 – Load data

- Load the Excel workbook.
- Scan the attachment directory.

### Stage 2 – Normalize filenames

Normalize Excel filenames by:

- removing trailing spaces
- removing surrounding quotes
- replacing accented characters
- normalizing PDF extensions

Normalize attachment filenames by:

- normalizing PDF extensions

Every performed normalization is recorded for auditing.

### Stage 3 – Audit logging

Generate `audit_log.csv` containing:

- row index
- source
- column
- original filename columns:
    - allegato_1_original
    - allegato_2_original
- normalized filename columns:
    - allegato_1_normalized
    - allegato_2_normalized
- performed normalization actions

### Stage 4 – Rule-based validation

Detect deterministic validation issues, including:

- invalid filename characters

### Stage 5 – Generate validated dataset

Export `validated_data.csv` containing:

- row index
- original business data:
    - company name
    - company VAT number
    - company email
- original filename columns:
    - allegato 1 original
    - allegato 2 original
- normalized filename columns:
    - allegato 1 normalized
    - allegato 2 normalized
- detected validation issues

---

## Future Pipeline 2 – ML Validation

Purpose:

- analyze ambiguous validation cases
- provide confidence scores
- recommend corrections
- reduce manual review workload

Input:

- `validated_data.csv`

Output:

- ML recommendations
- confidence scores

---

## Future Pipeline 3 – Reconciliation

Purpose:

- compare validated Excel filenames with attachment filenames
- identify missing or mismatched documents
- generate reconciliation reports

Input:

- validated_data.csv
- normalized attachment metadata

Output:

- reconciliation report

---

## Output Files

### Current Pipeline

data/
└── processed/
    ├── audit_log.csv
    └── validated_data.csv

### Future Pipelines

- reconciliation report
- business export (`Tracciato.csv`)
- validation statistics