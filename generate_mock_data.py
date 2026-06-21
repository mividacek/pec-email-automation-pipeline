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
    # getting the validated number of recorsa from user
    num_records = get_user_record_count()

    # creating a folder to store the attachments
    attachments_dir = "./test_attachments"
    os.makedirs(attachments_dir, exist_ok=True)

    system_breaking_chars, accent_char_map, vocal_map = get_system_configurations()

    print(f"\n--- Generating {num_records} transaction records into the environment ---")

    # the loop dinamically runs up to the user-specified row count
    for _ in range(num_records):

        base_company = generate_base_company_name(vocal_map)
        company_name = generate_company_full_name(base_company)
        company_email = generate_company_email(base_company, accent_char_map)
        company_VAT = generate_company_vat()
        generated_attachments = [None, None]
        attachment_1 = generated_attachments[0] 
        attachment_2 = generated_attachments[1]
        
        # attachments
        for i in range(random.choice([1, 2])):
            generated_attachments[i] = create_file_name(base_company, company_VAT, i, system_breaking_chars)

            attachment_1 = generated_attachments[0]
            attachment_2 = generated_attachments[1]
        
    print(f"Attachment 1: {attachment_1}\nAttachment 2: {attachment_2}\n" + "-"*30)



def get_system_configurations() -> tuple[list[str], dict[str, str], dict[str, list[str]]]:
    """Returns the forbidden characters and accent translation mappings."""
    system_breaking_chars = ["!", "#", "@", "&", ";", ":"]
    accent_char_map = {
        "à": "a", "è": "e", "é": "e", "ì": "i", "ò": "o", "ù": "u",
        "À": "A", "È": "E", "É": "E", "Ì": "I", "Ò": "O", "Ù": "U",
        "–": "-", "—": "-"
    }

    vocal_map = { "a": ["à"], "e": ["è", "é"], "u": ["ù"]}
    return system_breaking_chars, accent_char_map, vocal_map


def get_user_record_count() -> int:
    """
    Prompts the user for a number and strictly returns a valid positive integer.
    """
    while True:
        try:
            user_input = input("Enter the number of records to generate: ").strip()
            if user_input.isnumeric():
                num_records = int(user_input)
                if num_records > 0:
                    return num_records
                else:
                    raise ValueError("Number must be greather than 0.")
            else:
                raise ValueError("Invalid input, please enter a whole positive number.")
        except ValueError as error_message:
            print(f"Error: {error_message}")

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

    print(base_company)

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
    """Gnerates a standard corporate VAT code (Partita IVA)."""
    company_VAT = fake.company_vat()
    return company_VAT

def create_file_name(base_company: str, company_VAT: str, index: int, system_breaking_chars: list) -> str:
    """Constructs an individual attachment filename with a strict 15% error rate."""
    base_prefixes = ["Notice to", "Agreement for"]
    prefix = base_prefixes[index]

    if random.random() >= 0.15:
        return f"{prefix} {base_company} - {company_VAT}.pdf"
    mistake_type = random.choice(["chars", "no_ext", "double_dot_ext", "double_ext", "quotes", "spaces"])
    if mistake_type == "chars":
        chosen_char = random.choice(system_breaking_chars)
        return f"{prefix} {base_company} {chosen_char} {company_VAT}.pdf"
    if mistake_type == "no_ext":
        return f"{prefix} {base_company} - {company_VAT}"
    if mistake_type == "double_dot_ext":
        return f"{prefix} {base_company} - {company_VAT}..pdf"
    if mistake_type == "double_ext":
        return f"{prefix} {base_company} - {company_VAT}.pdf.pdf"
    if mistake_type == "quotes":
        return f'"{prefix} {base_company} - {company_VAT}.pdf"'
    if mistake_type == "spaces":
        return f"{prefix} {base_company} - {company_VAT}.pdf "
    
    
if __name__ == "__main__":
    main()