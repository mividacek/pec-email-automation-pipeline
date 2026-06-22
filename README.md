# pec-email-automation-pipeline
# Document Validation Pipeline

## Project Overview

This project recreates a document-processing workflow inspired by a real administrative environment where data accuracy was critical.

The current version generates synthetic datasets containing both valid and intentionally corrupted records. Future versions will add automated validation, cleaning, audit logging, and machine-learning assisted anomaly detection.

The generator creates:

* Company names
* Italian VAT numbers
* PEC email addresses
* Attachment files
* Excel database exports

The dataset intentionally includes realistic data-quality issues such as malformed filenames, invalid email addresses, spacing problems, extension errors, forbidden characters, and mismatches between database records and physical files.

---

## Project Status

This project is currently under active development.

Version 1 focuses on synthetic data generation and automated testing.

Future milestones include:

- Validation pipeline
- Data cleaning automation
- Machine-learning assisted anomaly detection
- Audit logging

---

## Motivation

This project was inspired by a document-processing workflow I previously automated in an administrative role.

The original process involved validating sender email addresses, matching document references, checking attachment names, detecting formatting issues, and preparing data for import into a document management system.

Because sensitive information was involved, the workflow required very high accuracy. The Excel automation I created at the time reduced manual work and helped prevent errors during data preparation.

This Python implementation recreates that type of workflow using synthetic data and serves as the foundation for a future automated validation and cleaning pipeline.

---

## Business Rules Recreated

The project is based on several real-world validation rules:

* Sender email addresses should not contain leading or trailing spaces.
* Invalid email addresses should be detected.
* Codes or identifiers from document references should match attachment names.
* Multiple attachment names may need to be joined into the same Excel cell.
* Attachments must use the `.pdf` extension.
* Malformed extensions such as `..pdf` or `.pdf.pdf` should be detected and corrected.
* Forbidden filename characters should be detected.
* Filename issues are corrected automatically when a safe correction is possible; otherwise they are flagged for manual review.
* File paths copied from the attachment folder should match the records in the Excel file.
* Invalid email addresses are detected and reported, but are not automatically corrected because the correct recipient cannot be determined safely.

Important note: the correct document name is stored inside the generated attachment file content. This reflects the real workflow, where the agent was expected to copy the same document name into both the file name and the Excel database, but manual copying could introduce mistakes.

Email addresses inside documents may also be incorrect because they represent data extracted from a company database. In the real workflow, such errors would need to be corrected at the source.

---

## Audit Log

The future validation pipeline will generate an audit log categorizing issues as:

### Automatically Corrected

- Duplicate PDF extensions
- Invalid filename characters
- Extra whitespace
- File naming normalization

### Manual Review Required

- Invalid email addresses
- Missing attachments
- Document reference mismatches
- Ambiguous filename corrections
- Attachments listed in Excel but missing from disk
- Attachments found on disk but not listed in Excel
- Ambiguous document-reference mismatches

This approach mirrors real-world business workflows where data can only be modified automatically when the correction is considered safe and deterministic.

---

## Features

Current functionality includes:

* Synthetic company generation using Faker
* Italian VAT number generation
* PEC email generation
* Physical attachment file creation
* Excel export generation using Pandas
* Controlled data corruption for testing purposes
* Unit testing with pytest
* Integration testing of the complete generation workflow

Examples of intentionally generated anomalies include:

* Invalid email formats
* Malformed file extensions
* Illegal filename characters
* Leading and trailing spaces
* Filename mismatches between Excel records and disk files

---

## Planned Pipeline

The future pipeline will include:

* Data validation
* Filename cleaning
* Email validation
* Attachment matching
* PDF extension correction
* Manual review flags
* Audit log generation
* Machine-learning assisted anomaly detection
* Machine-learning assisted data cleaning

The audit log will document detected issues, automatic corrections, and records requiring manual review.

---

## Project Structure

```text
generate_mock_data.py
test_generate_mock_data.py
README.md
doc/
richiesta.xlsx
```

---

## Technologies Used

* Python
* Faker
* Pandas
* openpyxl
* pytest

---

## Environment

The project is currently developed and tested in a Conda environment.

Required packages:

* Faker
* pandas
* openpyxl
* pytest

Example installation using Conda:

```bash
conda install pandas openpyxl pytest
conda install -c conda-forge faker
```

Alternatively, the packages may be installed using pip.

---

## Testing

The project contains both unit tests and integration tests.

### Unit Tests

Unit tests validate individual business rules, including:

* Configuration generation
* Email normalization
* Company name generation
* File naming logic
* Corrupted extension generation
* Filename consistency checks

### Integration Tests

Integration tests validate the complete workflow, including:

* Environment generation
* Attachment creation
* Excel export generation
* Output schema validation
* Required field validation

---

## How to Run Tests

Run all tests with:

```bash
pytest
```

For more detailed output:

```bash
pytest -v
```

For coverage reporting:

```bash
pytest --cov=generate_mock_data
```
---

## Quality Assurance

Current test suite:

- 22 automated tests
- Unit tests
- Integration tests
- 94% code coverage

---

## Fixed issues
The generator creates both valid and intentionally malformed records for testing data-cleaning pipelines. Generated attachment filenames are automatically sanitized for filesystem compatibility while preserving discrepancies between Excel records and physical files.
---

## Future Development

Planned improvements include:

* Missing attachment simulation
* Orphan attachment simulation
* Attachment reconciliation between Excel records and disk files
* Filename sanitization
* Automated validation pipeline
* Audit log generation
* Data quality reporting
* Attachment matching automation
* Machine-learning assisted anomaly detection
* Machine-learning assisted data cleaning

The current version focuses on synthetic data generation and automated testing. Machine-learning components will be introduced in future iterations after the validation and cleaning pipeline is completed.

---

## Lessons Learned

This project provided practical experience with:

* Python project structure
* Synthetic data generation
* File system operations
* Pandas workflows
* Automated testing with pytest
* Integration testing
* Debugging edge cases caused by random data generation

One of the most valuable findings was identifying a filesystem bug through integration testing, demonstrating how automated tests can uncover issues that are difficult to detect through manual testing alone.
