import os
from faker import Faker
import random
import re

# initialize Faker with Italian locale for names with accents
fake = Faker("it_IT")

def main() -> None:
    """
    Main Orchestration Function: Collects data from all modular functions and unifies them into the final Excel sheet.
    """
    # getting the validated number of records from user
    num_records = get_user_record_count()

    # creating a folder to store the attachments
    attachments_dir = "./doc"
    os.makedirs(attachments_dir, exist_ok=True)

    system_breaking_chars, accent_char_map, vocal_map = get_system_configurations()

    print(f"\n--- Generating {num_records} transaction records into the environment ---\n")

    # the loop dinamically runs up to the user-specified row count
    for _ in range(num_records):

        base_company = generate_base_company_name(vocal_map)
        company_name = generate_company_full_name(base_company)
        company_email = generate_company_email(base_company, accent_char_map)
        company_VAT = generate_company_vat()

        generated_excel_names = [None, None]
        generated_disk_names = [None, None]
        generated_clean_names = [None, None]

        # attachments
        num_attachments = random.choice([1, 2])

        for i in range(num_attachments):
            excel_name, disk_name, base_name = create_file_name(base_company, company_VAT, i, system_breaking_chars)
            generated_excel_names[i] = excel_name
            generated_disk_names[i] = disk_name
            generated_clean_names[i] = base_name
        
        clean_attachment_1, clean_attachment_2 = generated_clean_names
        attachment_1, attachment_2 = generated_excel_names

        if num_attachments == 1:
            attachment_text = f"Allegato: {clean_attachment_1}"
        else:
            attachment_text = f"Allegati: {clean_attachment_1}\n          {clean_attachment_2}"

        for i in range(num_attachments):
            disk_name = generated_disk_names[i]
            clean_title = generated_clean_names[i]

            file_content = (
                f"{clean_title}\n"
                f"Azienda: {company_name}\n"
                f"Email: {company_email}\n"
                f"VAT: {company_VAT}\n"
                f"{attachment_text}"
            )

            file_path = os.path.join(attachments_dir, disk_name)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file_content)

        print(f"Company: {company_name}\nEmail: {company_email}\nVAT: {company_VAT}\nAttachment 1: {attachment_1}\nAttachment 2: {attachment_2}")
        print("-" * 60)


def get_system_configurations() -> tuple[list[str], dict[str, str], dict[str, list[str]]]:
    """Returns the forbidden characters and accent translation mappings."""
    system_breaking_chars = ["!", "#", "@", "&", ";", ":", "–", "—"]
    accent_char_map = {
        "à": "a", "è": "e", "é": "e", "ì": "i", "ò": "o", "ù": "u",
        "À": "A", "È": "E", "É": "E", "Ì": "I", "Ò": "O", "Ù": "U",
        "–": "-", "—": "-"
    }

    vocal_map = { "a": ["à"], "e": ["è", "é"], "u": ["ù"]}
    return system_breaking_chars, accent_char_map, vocal_map


def get_user_record_count() -> int:
    """Prompts the user for a number and strictly returns a valid positive integer."""
    while True:
        user_input = input("Enter the number of records to generate: ").strip()
        
        if user_input.isdigit() and int(user_input) > 0:
            return int(user_input)
            
        print("Error: Invalid input, please enter a whole positive number greater than 0.")

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
    """Cleans accents and generates a PEC email with a rare 2%"""
    email_slug = base_company.lower().replace(" ",".")
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
    """Generates a standard corporate VAT code (Partita IVA)."""
    company_VAT = fake.company_vat()
    return company_VAT

def create_file_name(base_company: str, company_VAT: str, index: int, system_breaking_chars: list) -> tuple[str, str]:
    """
    Constructs file naming profiles for database logging and physical storage.

    Generates a standardized base name using transaction-specific prefixes, 
    the company name, and its VAT number. It introduces synthetic data corruption 
    (syntax anomalies, illegal characters, quote clipping, spacing issues, and 
    malformed extensions) into the database string track based on a 15% probability.
    
    The physical storage track independently filters these anomalies to respect 
    Operating System (OS) file system rules, while preserving allowed test characters 
    and factoring in a rare 1% discrepancy drift.

    Args:
        base_company (str): The unmutated base name of the corporate entity.
        company_VAT (str): The unique corporate Italian VAT identifier string.
        index (int): The relative position pointer used for structural prefix routing.
        system_breaking_chars (list[str]): A collection of allowed non-alphanumeric syntax markers.

    Returns:
        tuple[str, str, str]: A synchronized tuple containing:
            - excel_name: The raw syntactic string designated for the Excel database log.
            - disk_name: The OS-sanitized path-safe string for physical disk storage.
            - base_name: The pristine, extension-free string acting as an immutable metadata token.
    """
    base_prefixes = ["Avviso per", "Accordo per"]
    prefix = base_prefixes[index] if index < len(base_prefixes) else "Documento per" # fallback

    # creating base name with no mistakes
    base_name = f"{prefix} {base_company} - {company_VAT}"
    base_ext = ".pdf"

    # setting up chances of name in excel file being corrupted
    excel_is_corrupted = random.random() < 0.15

    # generating name for excel file
    if not excel_is_corrupted:
        excel_base = base_name
        excel_ext = base_ext
    else:
        excel_mistake = random.choice(["chars", "quotes", "spaces", "extension"])
        excel_mistake_ext = random.choices([base_ext, _corrupt_disk_extension()], weights = [0.65, 0.35])[0]
        if excel_mistake == "chars":
            chosen_char = random.choice(system_breaking_chars)
            excel_base = f"{prefix} {base_company} {chosen_char} {company_VAT}"
            excel_ext = excel_mistake_ext
        elif excel_mistake == "quotes":
            excel_base = f'"{base_name}'
            excel_ext = f'{excel_mistake_ext}"'
        elif excel_mistake == "spaces":
            excel_base = base_name
            excel_ext = f"{excel_mistake_ext} "
        else:
            excel_base = base_name
            excel_ext = _corrupt_disk_extension()

    excel_name = f"{excel_base}{excel_ext}"
    
    # generating disk file name
    if not excel_is_corrupted:
        disk_base = excel_base
        disk_ext = excel_ext
    else:
        disk_base = excel_base.replace('"', '').replace(':', '')
        disk_ext = excel_ext.replace('"', '').strip()
    
    if random.random() < 0.01:
        disk_ext = _corrupt_disk_extension()

    disk_name = f"{disk_base}{disk_ext}"

    return excel_name, disk_name, base_name


def _corrupt_disk_extension() -> str:
    """Helper function that returns only the corrupted extension string."""
    disk_mistake = random.choice(["no_ext", "double_dot_ext", "double_ext"])
    if disk_mistake == "no_ext":
        return ""
    if disk_mistake == "double_dot_ext":
        return "..pdf"
    return ".pdf.pdf"
    
if __name__ == "__main__":
    main()