import pandas as pd
import tempfile
import pytest
import os

from pipeline import (
    get_system_configurations,
    _normalize_pdf_extension, 
    _normalize_excel_filename,
    normalize_attachment_filenames,
    normalize_excel_filenames,
    detect_filename_ambiguities,
    load_excel_data,
    load_attachment_filenames,
    )

# ==========================
# UNIT TESTS
# ==========================

# Configuration test

def test_get_system_configurations_returns_expected_types():
    accent_map, system_breaking_chars = get_system_configurations()

    assert isinstance(accent_map, dict)
    assert isinstance(system_breaking_chars, list)

# PDF extension normalization helper function tests

def test_normalize_pdf_extension_fixes_double_dot_extension():
    assert _normalize_pdf_extension("filename..pdf") == "filename.pdf"

def test_normalize_pdf_extension_fixes_duplicate_extension():
    assert _normalize_pdf_extension("filename.pdf.pdf") == "filename.pdf"

def test_normalize_pdf_extension_keeps_valid_pdf():
    assert _normalize_pdf_extension("filename.pdf") == "filename.pdf"

def test_normalize_pdf_extension_adds_missing_extension():
    assert _normalize_pdf_extension("filename") == "filename.pdf"

# Excel filename helper function normalization tests

def test_normalize_excel_filename_removes_trailing_spaces():
    accent_map, _ = get_system_configurations()

    assert _normalize_excel_filename("filename.pdf  ", accent_map) == "filename.pdf"

def test_normalize_excel_filename_removes_quotes():
    accent_map, _ = get_system_configurations()

    assert _normalize_excel_filename('"filename.pdf"', accent_map) == "filename.pdf"

def test_normalize_excel_filename_fixes_accented_chars():
    accent_map, _ = get_system_configurations()

    assert _normalize_excel_filename("fìlènàmé.pdf", accent_map) == "filename.pdf"
    assert _normalize_excel_filename("FÌLÈNÀMÉ.pdf", accent_map) == "FILENAME.pdf"


def test_normalize_excel_filename_normalizes_malformed_pdf_extensions():
    accent_map, _ = get_system_configurations()

    assert _normalize_excel_filename("filename..pdf", accent_map) == "filename.pdf"
    assert _normalize_excel_filename("filename.pdf.pdf", accent_map) == "filename.pdf"
    assert _normalize_excel_filename("filename.pdf", accent_map) == "filename.pdf"
    assert _normalize_excel_filename("filename", accent_map) == "filename.pdf"


# Attachment disk filename normalization tests

def test_normalize_attachment_filenames_normalizes_list():
    raw_filenames = [
        "a.pdf",
        "b..pdf",
        "c.pdf.pdf",
        "d"
    ]

    assert normalize_attachment_filenames(raw_filenames) == [
        "a.pdf",
        "b.pdf",
        "c.pdf",
        "d.pdf"
    ]

# Normalize excel filenames outputs a dictionary

def test_normalize_excel_filenames_one_attachment():
    accent_map, _ = get_system_configurations()
    data_1 = {
        "Azienda" : ["Rossì S.p.A."],
        "VAT" : ["IT01234567891"],
        "Email" : ["rossi@pec.it"],
        "Allegato 1" : ["filename..pdf"],
    }
    df_1 = pd.DataFrame(data_1)

    assert normalize_excel_filenames(df_1, accent_map) == {
        "Allegato 1" : ["filename.pdf"],
    }

    data_2 = {
        "Azienda" : ["Rossì S.p.A."],
        "VAT" : ["IT01234567891"],
        "Email" : ["rossi@pec.it"],
        "Allegato 1" : ["filename..pdf"],
        "Allegato 2" : [None],
    }
    df_2 = pd.DataFrame(data_2)

    assert normalize_excel_filenames(df_2, accent_map) == {
        "Allegato 1" : ["filename.pdf"],
    }


def test_normalize_excel_filenames_two_attachments():
    accent_map, _ = get_system_configurations()
    data = {
        "Azienda" : ["Bianchì S.p.A."],
        "VAT" : ["IT01234567890"],
        "Email" : ["bianchi@pec.it"],
        "Allegato 1" : ["filename.pdf"],
        "Allegato 2" : ["filename.pdf.pdf"],
    }

    df = pd.DataFrame(data)

    assert normalize_excel_filenames(df, accent_map) == {
        "Allegato 1" : ["filename.pdf"],
        "Allegato 2" : ["filename.pdf"],
    }


# Detect filename ambiguities outputs

def test_detect_filename_ambiguities_positive():
    _, system_breaking_chars = get_system_configurations()
    normalized_excel_filenames = {"Allegato 1": ["Accordo per Rossi ! IT01234567891.pdf"]}
    data = {
        "Azienda" : ["Rossi S.p.A"],
        "VAT" : ["IT01234567891"],
        "Email" : ["rossi@pec.it"],
        "Allegato 1" : ["Accordo per Rossi ! IT01234567891.pdf"],
        "Allegato 2" : ["Avviso per Rossi - IT01234567891.pdf"],
    }

    df = pd.DataFrame(data)
    assert detect_filename_ambiguities(normalized_excel_filenames, df, system_breaking_chars) == [
        {
            "row_index": 0,
            "column": "Allegato 1",
            "original_name": "Accordo per Rossi ! IT01234567891.pdf",
            "normalized_name": "Accordo per Rossi ! IT01234567891.pdf",
            "issue_type": "INVALID_CHARACTER",
        }
    ]

def test_detect_filename_ambiguities_negative():
    _, system_breaking_chars = get_system_configurations()

    normalized_excel_filenames = {"Allegato 1": ["Accordo per Bianchi - IT01234567890.pdf"]}

    data = {
        "Azienda" : ["Bianchi S.p.A"],
        "VAT" : ["IT01234567890"],
        "Email" : ["bianchi@pec.it"],
        "Allegato 1" : ["Accordo per Bianchi - IT01234567890.pdf"],
        "Allegato 2" : ["Avviso per Bianchi - IT01234567890.pdf"],
    }

    df = pd.DataFrame(data)

    assert detect_filename_ambiguities(normalized_excel_filenames, df, system_breaking_chars) == []

# ==========================
# LOADING TESTS
# ==========================

# Loading Excel file test

def test_load_excel_data_positive():
    data = {
        "Azienda" : ["Rossì S.p.A."],
        "VAT" : ["IT01234567891"],
        "Email" : ["rossi@pec.it"],
        "Allegato 1" : ["filename..pdf"],
    }

    df = pd.DataFrame(data)

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=True) as tmp:
        df.to_excel(tmp.name, index=False)
        loaded_df = load_excel_data(tmp.name)
        assert isinstance(loaded_df, pd.DataFrame)
        assert list(loaded_df.columns) == ["Azienda", "VAT", "Email", "Allegato 1",]
        assert len(loaded_df) == 1
        assert loaded_df.at[0, "VAT"] == "IT01234567891"

def test_load_excel_data_negative():
    data = {
        "Azienda" : ["Rossì S.p.A."],
        "Email" : ["rossi@pec.it"],
        "Allegato 1" : ["filename..pdf"],
    }

    df = pd.DataFrame(data)

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=True) as tmp:
        df.to_excel(tmp.name, index=False)        
        with pytest.raises(ValueError, match="Missing required columns: "):
            load_excel_data(tmp.name)

# Loading disk filenames test

def test_load_attachment_filenames_positive():
    with tempfile.TemporaryDirectory() as temp_dir:
        doc_dir = os.path.join(temp_dir, "doc")
        os.makedirs(doc_dir, exist_ok=True)
        first_pdf = os.path.join(doc_dir, "first.pdf")
        with open (first_pdf, "w"):
            pass
        filenames = load_attachment_filenames(doc_dir)
        assert filenames == ["first.pdf"]

def test_load_attachment_filenames_no_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        doc_dir = os.path.join(temp_dir, "doc")
        os.makedirs(doc_dir, exist_ok=True)
        filenames = load_attachment_filenames(doc_dir)
        assert filenames == []

# ==========================
# WORKFLOW TEST
# ==========================

# Excel filename helper function combined normalization

def test_normalize_excel_filename_combined_normalization():
    accent_map, _ = get_system_configurations()

    assert _normalize_excel_filename('"fìlènàmé..pdf "', accent_map) == "filename.pdf"
    assert _normalize_excel_filename('"fìlènàmé.pdf.pdf "', accent_map) == "filename.pdf"
    assert _normalize_excel_filename('"fìlènàmé.pdf "', accent_map) == "filename.pdf"
    assert _normalize_excel_filename('"fìlènàmé "', accent_map) == "filename.pdf"
    assert _normalize_excel_filename("filename.pdf", accent_map) == "filename.pdf"
