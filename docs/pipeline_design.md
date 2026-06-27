# Pipeline Design

## Goal

The pipeline validates document-processing data, automatically corrects deterministic issues, optionally provides ML-assisted decision support for ambiguous cases, identifies records requiring manual review, and prepares validated data for downstream business processes.

## Input

Generated Excel workbook (richiesta.xlsx)

Generated attachment directory (doc/)

Business validation rules

## Pipeline Stages

1. Load Excel workbook
2. Scan attachment directory
3. Normalize data
4. Validate records
5. Reconcile Excel and attachments
6. Classify detected issues
7. Apply deterministic corrections
8. ML-assisted recommendations (optional)
9. Manual review (if required)
10. Generate output files
11. Generate audit log

## Expected Output

### Primary Outputs
* corrected attachment filenames
* corrected Excel workbook
* audit log

### Secondary Outputs
* Tracciato.csv
* validation summary
* statistics

## Decision Strategy

1. Apply deterministic business rules.
2. If the outcome is certain, continue.
3. If the outcome is ambiguous, consult the ML assistant (if available).
4. If confidence is insufficient, require manual review.
5. Only validated records are included in Tracciato.csv.