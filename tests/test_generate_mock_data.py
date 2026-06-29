import pytest
import pandas as pd
from pathlib import Path

from generate_mock_data import (
    get_system_configurations,
    generate_company_full_name,
    generate_company_email,
    create_file_name,
    _corrupt_disk_extension,
    generate_environment,
    write_attachment_files,
    create_orphan_file,
)

### UNIT TESTS

# CONFIGURATION TESTS


def test_get_system_configurations_returns_expected_types():
    chars, accent_map, vocal_map = get_system_configurations()

    assert isinstance(chars, list)
    assert isinstance(accent_map, dict)
    assert isinstance(vocal_map, dict)


def test_get_system_configurations_contains_expected_forbidden_chars():
    chars, _, _ = get_system_configurations()

    expected_chars = {"!", "#", "@", "&", ";", ":", "–", "—"}

    assert expected_chars.issubset(set(chars))


# COMPANY NAME TESTS


def test_generate_company_full_name_adds_valid_suffix():
    allowed_suffixes = {"S.p.A.", "S.r.l.", "S.r.l.s.", "S.n.c.", "S.a.s."}

    for _ in range(250):
        company_name = generate_company_full_name("Test Company")

        assert any(company_name.endswith(suffix) for suffix in allowed_suffixes)


def test_generate_company_full_name_preserves_base_name():
    company_name = generate_company_full_name("Rossi")

    assert company_name.startswith("Rossi")


# EMAIL TESTS


def test_generate_company_email_removes_accents():
    _, accent_char_map, _ = get_system_configurations()

    found_valid_email = False

    for _ in range(250):

        email = generate_company_email("Café Agnelli", accent_char_map)

        is_corrupted = "@@" in email or email.count("@") != 1 or email != email.strip()

        if not is_corrupted:

            found_valid_email = True

            assert "é" not in email
            assert " " not in email
            assert email.islower()

            break

    assert found_valid_email


def test_generate_company_email_uses_allowed_domains():
    _, accent_char_map, _ = get_system_configurations()

    allowed_domains = {"legalmail.it", "pec.it", "postecert.it"}

    found_valid_email = False

    for _ in range(250):

        email = generate_company_email("Rossi", accent_char_map).strip()

        if email.count("@") == 1:

            found_valid_email = True

            domain = email.split("@")[1]

            if "." in domain:
                assert domain in allowed_domains

            break

    assert found_valid_email


# CORRUPTED EXTENSION TESTS


def test_corrupt_disk_extension_returns_only_expected_values():
    allowed = {"", "..pdf", ".pdf.pdf"}

    for _ in range(250):
        assert _corrupt_disk_extension() in allowed


# FILE NAME TESTS


def test_create_file_name_returns_three_strings():
    excel_name, disk_name, base_name = create_file_name(
        "Rossi", "IT12345678901", 0, ["!", "#"]
    )

    assert isinstance(excel_name, str)
    assert isinstance(disk_name, str)
    assert isinstance(base_name, str)


def test_base_name_contains_no_extension():
    _, _, base_name = create_file_name("Rossi", "IT12345678901", 0, ["!", "#"])

    assert not base_name.endswith(".pdf")


def test_disk_name_never_contains_filesystem_reserved_characters():
    reserved_chars = set('<>:"/\\|?*')

    for _ in range(250):
        _, disk_name, _ = create_file_name(
            "Rossi 24:7", "IT12345678901", 0, ["!", "#", "@", "&", ";", ":", "–", "—"]
        )

        assert not any(char in disk_name for char in reserved_chars)


def test_disk_name_never_has_trailing_spaces():
    for _ in range(250):

        _, disk_name, _ = create_file_name("Rossi", "IT12345678901", 0, ["!", "#"])

        assert disk_name == disk_name.strip()


def test_prefix_selection_for_first_attachment():
    _, _, base_name = create_file_name("Rossi", "IT12345678901", 0, ["!", "#"])

    assert base_name.startswith("Avviso per")


def test_prefix_selection_for_second_attachment():
    _, _, base_name = create_file_name("Rossi", "IT12345678901", 1, ["!", "#"])

    assert base_name.startswith("Accordo per")


def test_fallback_prefix_for_additional_attachments():
    _, _, base_name = create_file_name("Rossi", "IT12345678901", 999, ["!", "#"])

    assert base_name.startswith("Documento per")


def test_disk_name_replaces_filesystem_reserved_characters():
    excel_name, disk_name, base_name = create_file_name(
        "Rossi 24:7", "IT12345678901", 0, ["!", "#"]
    )

    assert "24:7" in excel_name
    assert "24-7" in disk_name
    assert "/" not in disk_name
    assert ":" not in disk_name


# GENERATOR BEHAVIOUR TESTS


def test_corrupted_excel_names_are_generated_sometimes():
    corrupted_found = False

    for _ in range(250):

        excel_name, _, _ = create_file_name("Rossi", "IT12345678901", 0, ["!", "#"])

        if (
            "..pdf" in excel_name
            or ".pdf.pdf" in excel_name
            or '"' in excel_name
            or "!" in excel_name
            or "#" in excel_name
            or excel_name.endswith(" ")
        ):
            corrupted_found = True
            break

    assert corrupted_found


def test_excel_and_disk_name_can_differ():
    difference_found = False

    for _ in range(250):

        excel_name, disk_name, _ = create_file_name(
            "Rossi", "IT12345678901", 0, ["!", "#"]
        )

        if excel_name != disk_name:
            difference_found = True
            break

    assert difference_found


# ATTACHMENT FILE TESTS


def test_write_attachment_files_creates_expected_files(tmp_path):
    """
    Verify that the attachment writer creates
    the expected physical files on disk.
    """

    disk_names = ["test_1.pdf", "test_2.pdf"]
    clean_names = ["Test 1", "Test 2"]

    write_attachment_files(
        attachments_dir=str(tmp_path),
        disk_names=disk_names,
        clean_names=clean_names,
        company_name="Rossi S.r.l.",
        company_email="rossi@pec.it",
        company_vat="IT12345678901",
        allow_missing=False,
    )

    assert (tmp_path / "test_1.pdf").exists()
    assert (tmp_path / "test_2.pdf").exists()


def test_create_orphan_file_creates_attachment_files(tmp_path):
    """
    Verify that creating an orphan transaction
    generates attachment files without requiring
    an Excel record.
    """

    _, accent_char_map, vocal_map = get_system_configurations()

    create_orphan_file(
        attachments_dir=str(tmp_path),
        system_breaking_chars=["!", "#", "@", "&", ";", ":", "–", "—"],
        accent_char_map=accent_char_map,
        vocal_map=vocal_map,
    )

    assert len(list(tmp_path.iterdir())) >= 1


### INTEGRATION TESTS

# GENERATING OUTPUT FILES


def test_environment_generation_creates_output_files():
    """
    Verify that running the generator creates both
    the Excel workbook and attachment directory.
    """

    generate_environment(250)

    assert Path("richiesta.xlsx").exists()
    assert Path("doc").exists()


# GENERATING PHYSICAL ATTACHMENTS ON DISK


def test_environment_generation_creates_attachment_files():
    """
    Verify that at least one attachment file is
    physically generated on disk.
    """

    generate_environment(250)

    files = list(Path("doc").iterdir())

    assert len(files) > 0


# EXCEL NUMBER OF RECORDS


def test_excel_contains_requested_number_of_records():
    """
    Verify that the generated Excel file contains
    exactly the requested number of rows.
    """

    generate_environment(250)

    df = pd.read_excel("richiesta.xlsx")

    assert len(df) == 250


# EXCEL COLUMN HEADERS


def test_excel_contains_expected_columns():
    """
    Verify that the Excel export contains the
    expected schema used by downstream processing.
    """

    generate_environment(250)

    df = pd.read_excel("richiesta.xlsx")

    expected_columns = {"Azienda", "VAT", "Email", "Allegato 1", "Allegato 2"}

    assert set(df.columns) == expected_columns


# EXCEL MANDATORY FIELDS


def test_generated_records_have_required_fields():
    """
    Verify that all generated records contain
    mandatory company information.
    """

    generate_environment(250)

    df = pd.read_excel("richiesta.xlsx")

    assert df["Azienda"].notna().all()
    assert df["VAT"].notna().all()
    assert df["Email"].notna().all()
    assert df["Allegato 1"].notna().all()


# RECONCILIATION TESTS


def test_environment_generates_orphan_attachments():
    """
    Verify that at least one attachment exists
    on disk without a corresponding Excel record.
    """

    generate_environment(250)

    df = pd.read_excel("richiesta.xlsx")

    excel_files = set(
        df["Allegato 1"].dropna().tolist() + df["Allegato 2"].dropna().tolist()
    )

    disk_files = {file.name for file in Path("doc").iterdir() if file.is_file()}

    assert len(disk_files - excel_files) > 0
