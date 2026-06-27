import os
from faker import Faker
import random
import re
import shutil
import pandas as pd

# initialize Faker with Italian locale for names with accents
fake = Faker("it_IT")


def main() -> None:
    """
    Entry point of the application.

    Requests the number of synthetic records from the user
    and delegates the generation process to the environment
    builder.

    Returns:
        None
    """
    # getting the validated number of records from user
    num_records = get_user_record_count()
    generate_environment(num_records)


def generate_environment(num_records: int) -> None:
    """
    Generates a complete synthetic document-processing environment.

    Creates a fresh attachment directory, generates the requested number
    of synthetic company records, writes attachment files to disk, and
    exports all generated metadata into an Excel workbook.

    The generated dataset intentionally contains controlled anomalies
    (invalid emails, malformed filenames, illegal characters, spacing
    issues, and extension errors) to support testing and training of
    data-cleaning pipelines.

    Args:
        num_records (int):
            Number of company records to generate.

    Returns:
        None
    """
    attachments_dir = "./doc"

    if os.path.exists(attachments_dir):
        shutil.rmtree(attachments_dir)

    os.makedirs(attachments_dir)

    system_breaking_chars, accent_char_map, vocal_map = get_system_configurations()

    # empty list for all records
    transaction_records = []

    print(
        f"\n--- Generating {num_records} transaction records into the environment ---\n"
    )

    # the loop dinamically runs up to the user-specified row count
    for _ in range(num_records):

        base_company = generate_base_company_name(vocal_map)
        company_name = generate_company_full_name(base_company)
        company_email = generate_company_email(base_company, accent_char_map)
        company_vat = generate_company_vat()

        generated_excel_names: list[str | None] = [None, None]
        generated_disk_names: list[str | None] = [None, None]
        generated_clean_names: list[str | None] = [None, None]

        # attachments
        num_attachments = random.choice([1, 2])

        for i in range(num_attachments):
            excel_name, disk_name, base_name = create_file_name(
                base_company, company_vat, i, system_breaking_chars
            )
            generated_excel_names[i] = excel_name
            generated_disk_names[i] = disk_name
            generated_clean_names[i] = base_name

        attachment_1 = generated_excel_names[0]
        attachment_2 = generated_excel_names[1]

        write_attachment_files(
            attachments_dir=attachments_dir,
            disk_names=generated_disk_names,
            clean_names=generated_clean_names,
            company_name=company_name,
            company_email=company_email,
            company_vat=company_vat,
            allow_missing=True,
        )

        # adding a dictionary with the company data
        transaction_records.append(
            {
                "Azienda": company_name,
                "VAT": company_vat,
                "Email": company_email,
                "Allegato 1": attachment_1,
                "Allegato 2": attachment_2,
            }
        )

        print(
            f"Company: {company_name}\nEmail: {company_email}\nVAT: {company_vat}\nAttachment 1: {attachment_1}\nAttachment 2: {attachment_2}"
        )
        print("-" * 60)

    # creating orphan files
    orphan_count = max(1, int(num_records * 0.03))

    for _ in range(orphan_count):
        create_orphan_file(
            attachments_dir=attachments_dir,
            system_breaking_chars=system_breaking_chars,
            accent_char_map=accent_char_map,
            vocal_map=vocal_map,
        )

    # creating excel files
    print("\n--- Saving records to Excel database ---")
    df = pd.DataFrame(transaction_records)

    excel_path = "./richiesta.xlsx"
    df.to_excel(excel_path, index=False)
    print(f"Successfully generated Excel database at: {excel_path}\n")


def get_system_configurations() -> (
    tuple[list[str], dict[str, str], dict[str, list[str]]]
):
    """Returns the forbidden characters and accent translation mappings."""
    system_breaking_chars = ["!", "#", "@", "&", ";", ":", "–", "—"]
    accent_char_map = {
        "à": "a",
        "è": "e",
        "é": "e",
        "ì": "i",
        "ò": "o",
        "ù": "u",
        "À": "A",
        "È": "E",
        "É": "E",
        "Ì": "I",
        "Ò": "O",
        "Ù": "U",
        "–": "-",
        "—": "-",
    }

    vocal_map = {"a": ["à"], "e": ["è", "é"], "u": ["ù"]}
    return system_breaking_chars, accent_char_map, vocal_map


def get_user_record_count() -> int:
    """
    Prompts the user until a valid positive integer is entered.

    Returns:
        int: Number of records to generate.
    """
    while True:
        user_input = input("Enter the number of records to generate: ").strip()

        if user_input.isdigit() and int(user_input) > 0:
            return int(user_input)

        print(
            "Error: Invalid input, please enter a whole positive number greater than 0."
        )


def generate_base_company_name(vocal_map: dict[str, list[str]]) -> str:
    """
    Generates the core base name of the company.
    Enforces a conditional 40% chance for an Italian accent on the final character of the last name,
    then independently applies a 50% chance to append a business statement.
    """
    base_company = fake.last_name()
    last_char = base_company[-1]

    if last_char in vocal_map and random.random() < 0.4:
        accented_char = random.choice(vocal_map[last_char])
        base_company = base_company[:-1] + accented_char
    if random.random() < 0.5:
        base_company = f"{base_company} {fake.bs()}"

    return base_company


def generate_company_full_name(base_company: str) -> str:
    """Appends a uniform legal corporate suffix to the base company name."""
    allowed_suffixes = ["S.p.A.", "S.r.l.", "S.r.l.s.", "S.n.c.", "S.a.s."]
    suffix = random.choice(allowed_suffixes)
    company_name = f"{base_company} {suffix}"
    return company_name


def generate_company_email(base_company: str, accent_char_map: dict) -> str:
    """
    Generates a synthetic PEC email address.

    Normalizes accented characters, formats the company name
    into an email-compatible slug, and assigns a valid PEC
    domain.

    A small percentage of generated emails intentionally
    contain formatting errors to simulate real-world data
    quality issues.

    Args:
        base_company (str):
            Base company name.

        accent_char_map (dict):
            Mapping of accented characters to ASCII equivalents.

    Returns:
        str:
            Generated email address.
    """
    email_slug = base_company.lower().replace(" ", ".")
    for target, replacement in accent_char_map.items():
        email_slug = email_slug.replace(target, replacement)
    email_slug = re.sub(r"[^\w\.]", "", email_slug)
    chosen_domain = random.choice(["legalmail.it", "pec.it", "postecert.it"])
    if random.random() < 0.02:
        error_type = random.choice(["spaces", "double_at", "missing_at", "missing_dot"])

        if error_type == "spaces":
            return f" {email_slug}@{chosen_domain}.  "
        elif error_type == "double_at":
            return f"{email_slug}@@{chosen_domain}"
        elif error_type == "missing_at":
            return f"{email_slug}{chosen_domain}"
        elif error_type == "missing_dot":
            corrupted_domain = chosen_domain.replace(".", "")
            return f"{email_slug}@{corrupted_domain}"
    else:
        return f"{email_slug}@{chosen_domain}"


def generate_company_vat() -> str:
    """
    Generates a synthetic Italian VAT number.

    Returns:
        str:
            Randomly generated VAT identifier.
    """
    company_vat = fake.company_vat()
    return company_vat


def create_file_name(
    base_company: str, company_vat: str, index: int, system_breaking_chars: list[str]
) -> tuple[str, str, str]:
    """
    Constructs file naming profiles for database logging and physical storage.

    Generates a standardized base name using transaction-specific prefixes, the company name, and its VAT number. The Excel filename may contain intentional syntheric corruption, while the disk filename is made safe for filesystem creation.

    Args:
        base_company (str): The unmutated base name of the corporate entity.
        company_vat (str): The unique corporate Italian VAT identifier string.
        index (int): The relative position pointer used for structural prefix routing.
        system_breaking_chars (list[str]): Characters used to simulate Excel/database corruption.

    Returns:
        A tuple containg:
            excel_name (str): Raw name stored in Excel, possibly corrupted.
            disk_name (str): Filesystem-safe name used for the physical file.
            base_name (str): Clean extension-free reference name.
    """
    base_prefixes = ["Avviso per", "Accordo per"]
    prefix = (
        base_prefixes[index] if index < len(base_prefixes) else "Documento per"
    )  # fallback

    base_name = f"{prefix} {base_company} - {company_vat}"
    base_ext = ".pdf"

    # disk-safe version of the intended clean filename.
    disk_safe_base_name = re.sub(r'[<>:"/\\|?*]', "-", base_name).strip()

    # excel
    excel_is_corrupted = random.random() < 0.15

    if not excel_is_corrupted:
        excel_base = base_name
        excel_ext = base_ext

        disk_base = disk_safe_base_name
        disk_ext = base_ext

    else:
        excel_mistake = random.choice(["chars", "quotes", "spaces", "extension"])

        excel_mistake_ext = random.choices(
            [base_ext, _corrupt_disk_extension()], weights=[0.65, 0.35]
        )[0]

        if excel_mistake == "chars":
            chosen_char = random.choice(system_breaking_chars)

            excel_base = f"{prefix} {base_company} {chosen_char} {company_vat}"
            excel_ext = excel_mistake_ext

            disk_base = disk_safe_base_name
            disk_ext = excel_mistake_ext

        elif excel_mistake == "quotes":
            excel_base = f'"{base_name}'
            excel_ext = f'{excel_mistake_ext}"'

            disk_base = disk_safe_base_name
            disk_ext = excel_mistake_ext

        elif excel_mistake == "spaces":
            excel_base = base_name
            excel_ext = f"{excel_mistake_ext} "

            disk_base = disk_safe_base_name
            disk_ext = excel_mistake_ext.strip()

        else:
            excel_base = base_name
            excel_ext = _corrupt_disk_extension()

            disk_base = disk_safe_base_name
            disk_ext = excel_ext

    excel_name = f"{excel_base}{excel_ext}"

    # attachments
    disk_name = f"{disk_base}{disk_ext}"

    return excel_name, disk_name, base_name


def _corrupt_disk_extension() -> str:
    """
    Returns a deliberately malformed file extension.

    Used to simulate common user or system mistakes
    encountered in document management workflows.

    Returns:
        str:
            Corrupted extension variant.
    """
    disk_mistake = random.choice(["no_ext", "double_dot_ext", "double_ext"])
    if disk_mistake == "no_ext":
        return ""
    if disk_mistake == "double_dot_ext":
        return "..pdf"
    return ".pdf.pdf"


def write_attachment_files(
    attachments_dir: str,
    disk_names: list[str | None],
    clean_names: list[str | None],
    company_name: str,
    company_email: str,
    company_vat: str,
    allow_missing: bool = False,
) -> None:
    """
    Writes generated attachment files to disk.

    Creates physical attachment files using generated company metadata
    and attachment names. If allow_missing is True, some files are
    intentionally skipped to simulate Excel records that reference
    attachments missing from disk.

    Args:
        attachments_dir (str):
            Directory where attachment files will be created.

        disk_names (list[str | None]):
            Disk-safe attachment filenames. The second item may be None
            when the company has only one attachment.

        clean_names (list[str | None]):
            Clean attachment titles written inside the file content.
            The second item may be None when the company has only one
            attachment.

        company_name (str):
            Generated full company name.

        company_email (str):
            Generated company PEC email address.

        company_vat (str):
            Generated company VAT number.

        allow_missing (bool):
            If True, randomly skips some files to simulate missing
            attachments. If False, writes all generated attachments.

    Returns:
        None

        The function creates files directly on disk as a side effect.
        The created files are the output of the operation, so no return
        value is needed.
    """
    clean_attachment_1, clean_attachment_2 = clean_names

    if clean_attachment_2 is None:
        attachment_text = f"Allegato: {clean_attachment_1}"
    else:
        attachment_text = (
            f"Allegati: {clean_attachment_1}\n" f"          {clean_attachment_2}"
        )

    for i, disk_name in enumerate(disk_names):
        if disk_name is None:
            continue

        if allow_missing and random.random() < 0.03:
            continue

        clean_title = clean_names[i]

        file_content = (
            f"{clean_title}\n"
            f"Azienda: {company_name}\n"
            f"Email: {company_email}\n"
            f"VAT: {company_vat}\n"
            f"{attachment_text}"
        )

        file_path = os.path.join(attachments_dir, disk_name)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_content)


def create_orphan_file(
    attachments_dir: str,
    system_breaking_chars: list[str],
    accent_char_map: dict[str, str],
    vocal_map: dict[str, list[str]],
) -> None:
    """
    Creates one orphan company attachment set.

    Orphan attachments are valid physical files on disk, but they are
    not represented by any row in the Excel export.

    Args:
        attachments_dir (str):
            Directory where orphan attachment files will be created.

        system_breaking_chars (list[str]):
            Characters used to simulate Excel/database filename
            corruption.

        accent_char_map (dict[str, str]):
            Mapping used to normalize accented characters in generated
            email addresses.

        vocal_map (dict[str, list[str]]):
            Mapping used to optionally add accented vowels to generated
            company names.

    Returns:
        None

        The function writes orphan files directly to disk. It does not
        return data because the purpose is to create physical files that
        are intentionally missing from the Excel export.
    """
    base_company = generate_base_company_name(vocal_map)
    company_name = generate_company_full_name(base_company)
    company_email = generate_company_email(base_company, accent_char_map)
    company_vat = generate_company_vat()

    generated_disk_names = [None, None]
    generated_clean_names = [None, None]

    num_attachments = random.choice([1, 2])

    for i in range(num_attachments):
        _, disk_name, base_name = create_file_name(
            base_company,
            company_vat,
            i,
            system_breaking_chars,
        )

        generated_disk_names[i] = disk_name
        generated_clean_names[i] = base_name

    write_attachment_files(
        attachments_dir=attachments_dir,
        disk_names=generated_disk_names,
        clean_names=generated_clean_names,
        company_name=company_name,
        company_email=company_email,
        company_vat=company_vat,
        allow_missing=False,
    )


if __name__ == "__main__":
    main()
