import pandas as pd
import os

def main():
    path = "/Users/mivi/Documents/Projects/data/generated/richiesta.xlsx"
    attachments_path = "/Users/mivi/Documents/Projects/data/generated/doc/"
    df = load_excel_data(path)
    attachments = load_attachment_filenames(attachments_path)
    accent_map, system_breaking_chars = get_system_configurations()
    _, normalization_disk_log = normalize_attachment_filenames(attachments)
    normalized_excel_filenames, normalization_excel_log = normalize_excel_filenames(df, accent_map)
    build_audit_log(normalization_disk_log, normalization_excel_log)
    flagged_excel_filenames = detect_filename_ambiguities(normalized_excel_filenames, df, system_breaking_chars)
    build_validated_data(df, normalized_excel_filenames, flagged_excel_filenames)


def get_system_configurations() -> tuple[dict[str, str], list[str]]:
    """
    Returns shared normalization and validation configuration used by the pipeline.

    Returns:
        accent_map (dict[str, str])
            Dictionary of accented characters to ASCII equivalents.
        system_breaking_chars (list[str])
            List of characters that require ambiguity detection.
    """
    accent_map = {
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
        }
    
    system_breaking_chars = ["!", "#", "@", "&", ";", ":", "–", "—"]

    return accent_map, system_breaking_chars


def load_excel_data(excel_path: str) -> pd.DataFrame:
    """
    Loads the generated Excel workbook used by the validation pipeline

    Args:
        excel_path (str)
            Path to the Excel workbook.

    Returns:
        pandas.DataFrame
            The loaded Excel workbook.
    """
    df = pd.read_excel(excel_path)
    REQUIRED_COLUMNS = ["Azienda", "VAT", "Email", "Allegato 1",]
    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in df.columns
    ]
    if len(missing_columns) > 0:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    return df

def load_attachment_filenames(attachments_path: str) -> list[str]:
    """
    Loads the content of the directory used by the validation pipeline and returns them as a list of strings.

    Args:
        attachments_path (str)
            Path to the document folder.

    Returns:
        attachments (list[str])
            List of loaded attachment filenames.
    """
    attachments = os.listdir(attachments_path)
    return attachments

def normalize_attachment_filenames(attachments: list[str]) -> tuple[list[str], list[dict[str, None | str | list[str]]]]:
    """
    Normalizes the attachment filenames by sanitizing the extension and returns them as a list of strings.
    Collects data for the audit log.

    Args:
        attachments (list[str])
            List of loaded attachment filenames.

    Returns:
        A tuple consisting of:
        - normalized_attachments (list[str]): 
            List of normalized attachment filenames.
        - normalization_log (list[dict[str, int | str | list[str]])
            The following data from each file that was modified:
            - row index
            - source
            - column name
            - original name
            - normalized name
            - list of performed normalization actions
    """
    normalized_attachments = []
    normalization_log = []
    for original_filename in attachments:
        normalized_filename = _normalize_pdf_extension(original_filename)
        normalized_attachments.append(normalized_filename)
        if original_filename != normalized_filename:
            filename_dict = {}
            filename_dict["row_index"] = None
            filename_dict["source"] = "Disk"
            filename_dict["column"] = "Cartella doc"
            filename_dict["original_name"] = original_filename
            filename_dict["normalized_name"] = normalized_filename
            filename_dict["actions"] = ["NORMALIZED_PDF_EXTENSION"]
            normalization_log.append(filename_dict)

    return normalized_attachments, normalization_log

def normalize_excel_filenames(df: pd.DataFrame, accent_map: dict[str, str]) -> tuple[dict[str, list[str]], list[dict[str, int | str | list[str]]]]:
    """
    Normalizes the filenames in excel df:
    - no trailing spaces
    - removing quotes
    - replaces accented characters
    - normalization of extension
    Collects data for the audit log.

    Args:
        df (pandas.DataFrame)
            The loaded Excel workbook.
        accent_map (dict[str, str])
            Dictionary of accented characters to ASCII equivalents.
    
    Returns:
        A tuple consisting of:
        - normalized_excel_filenames (dict[str, list[str]])
            The values or the column "Allegato 1" and if "Allegato 2" exists and is not empty in a dictionary where the column name is the key and the values are lists of normalized file names.
        - normalization_log (list[dict[str, int | str | list[str]])
            The following data from each file that was modified:
            - row index
            - source
            - column name
            - original name
            - normalized name
            - list of performed normalization actions
    """
    normalized_excel_filenames = {}
    normalization_log = []
    normalized_excel_filenames_1 = []

    excel_filenames_1 = df["Allegato 1"].to_list()
    
    for row_index, original_filename in enumerate(excel_filenames_1):
        normalized_filename, actions = _normalize_excel_filename(original_filename, accent_map)
        normalized_excel_filenames_1.append(normalized_filename)
        if actions:
            filename_dict = {}
            filename_dict["row_index"] = row_index
            filename_dict["source"] = "Excel"
            filename_dict["column"] = "Allegato 1"
            filename_dict["original_name"] = original_filename
            filename_dict["normalized_name"] = normalized_filename
            filename_dict["actions"] = actions
            normalization_log.append(filename_dict)

    normalized_excel_filenames["Allegato 1"] = normalized_excel_filenames_1

    if "Allegato 2" in df and not df["Allegato 2"].fillna("").eq("").all():
        normalized_excel_filenames_2 = []
        excel_filenames_2 = df["Allegato 2"].fillna("").to_list()

        for row_index, original_filename in enumerate(excel_filenames_2):
            if original_filename == "":
                normalized_excel_filenames_2.append(original_filename)
                continue
            else:
                normalized_filename, actions = _normalize_excel_filename(original_filename, accent_map)
                normalized_excel_filenames_2.append(normalized_filename)
            if actions:
                filename_dict = {}
                filename_dict["row_index"] = row_index
                filename_dict["source"] = "Excel"
                filename_dict["column"] = "Allegato 2"
                filename_dict["original_name"] = original_filename
                filename_dict["normalized_name"] = normalized_filename
                filename_dict["actions"] = actions
                normalization_log.append(filename_dict)
        
        normalized_excel_filenames["Allegato 2"] = normalized_excel_filenames_2

    return normalized_excel_filenames, normalization_log


def build_audit_log(normalization_disk_log: list[dict[str, str | None | list[str]]], normalization_excel_log: list[dict[str, str | int | list[str]]]) -> None:
    """
    Builds the audit log of normalized filenames.

    Args:
       - normalization_excel_log (list[dict[str, int | str | list[str]])
       - normalization_disk_log (list[dict[str, int | str | list[str]])
            Contains the following data from each file that was modified:
            - row index
            - source
            - column name
            - original name
            - normalized name
            - list of performed normalization actions
    
    Returns:
        None
            Exports the audit log as
            "./data/processed/audit_log.csv".
    """
    
    path = "./data/processed/audit_log.csv"

    columns = [
        "row_index",
        "source",
        "column",
        "original_name",
        "normalized_name",
        "actions",
    ]
    
    normalization_log = normalization_disk_log + normalization_excel_log
    for row in normalization_log:
        if row["actions"]:
            row["actions"] = ";".join(row["actions"])

    df = pd.DataFrame(normalization_log, columns=columns)
    
    if not df.empty:
        df = df.sort_values(by="row_index", na_position="first")
    
    df.to_csv(path, index=False)

def detect_filename_ambiguities(normalized_excel_filenames: dict[str, list[str]], df: pd.DataFrame, system_breaking_chars: list[str]) -> list[dict[str, str | int | list [str]]]:
    """
    Returns a list of Excel rows whose filenames containing system-breaking-characters.
    Each detected issue is represented by a dictionary containing:
    - row_index: row number starting from 0
    - column: name of the column where the filename was found
    - original_name: name before normalization
    - normalized_name: name after normalization
    - issue type: INVALID_CHARACTER

    Args:
        normalized_excel_filenames (dict[str, list[str]])
            The values of the column "Allegato 1" and if "Allegato 2" exists and is not empty in a dictionary where the column name is the key and the values are lists of normalized file names.
        df (pd.DataFrame) 
            The loaded Excel workbook.
        system_breaking_chars (list[str])
            List of characters that require ambiguity detection.

    Returns:
        list[dict]:
            A list of dictionaries describing every filename that contains a system-breaking character.
    """
    detected_ambiguities = []
    for column_name, filename_list in normalized_excel_filenames.items():
        for row_index, attachment in enumerate(filename_list):
            for character in system_breaking_chars:
                if character in attachment:
                    filename_dict = {}
                    filename_dict["row_index"] = row_index
                    filename_dict["column"] = column_name
                    filename_dict["original_name"] = df.at[row_index, column_name]
                    filename_dict["normalized_name"] = attachment
                    filename_dict["issue_type"] = ["INVALID_CHARACTER"]
                    detected_ambiguities.append(filename_dict)
                    break

    return detected_ambiguities

def build_validated_data(df: pd.DataFrame, normalized_excel_filenames: dict[str, list[str]], detected_filename_ambiguities: list[dict[str, str | int | list [str]]]) -> None:
    """
    Builds the validated dataset used as the output of the validation pipeline.
    The exported dataset contains:
    - the original Excel data
    - normalized filename columns
    - detected validation issues

    Args:
        df (pd.DataFrame)
            The loaded Excel workbook.

        normalized_excel_filenames (dict[str, list[str]])
            Dictionary containing the normalized filenames for each attachment column.

        detected_ambiguities (list[dict[str, str | int | list[str]]])
            List of detected filename ambiguities. Each dictionary contains:
            - row index
            - column name
            - original filename
            - normalized filename
            - list of detected issue types

    Returns:
        None
            Exports the validated dataset as
            "./data/processed/validated_data.csv".
    """
    path = "./data/processed/validated_data.csv"

    validated_df = df.copy().rename(columns={"Azienda" : "azienda","VAT" : "vat", "Email" : "email", "Allegato 1" : "allegato_1_original", "Allegato 2" : "allegato_2_original"})

    validated_df.insert(loc=0, column="row_index", value=validated_df.index)

    validated_df.insert(loc=5, column="allegato_1_normalized", value=normalized_excel_filenames["Allegato 1"])

    if "Allegato 2" in normalized_excel_filenames:
        validated_df.insert(loc=7, column="allegato_2_normalized", value=normalized_excel_filenames["Allegato 2"],)

    validated_df["issue_type"] = ""

    for issue in detected_filename_ambiguities:
        row_index = issue["row_index"]
        issue_type = ";".join(issue["issue_type"])
        validated_df.at[row_index, "issue_type"] = issue_type

    validated_df.to_csv(path, index=False)

def _normalize_pdf_extension(filename: str) -> str:
    """
    Normalizes the extension of file names.

    Args:
        filename (str)
            File name to normalize.

    Returns:
        normalized_filename (str)
            Normalized file name.
    """
    if filename.endswith("..pdf"):
        base_name = filename[:-5]
    elif filename.endswith(".pdf.pdf"):
        base_name = filename[:-8]
    elif filename.endswith(".pdf"):
        normalized_filename = filename
        return normalized_filename
    else:
        base_name = filename
    
    normalized_filename = base_name + ".pdf"
    return normalized_filename

def _normalize_excel_filename(filename: str, accent_map: dict[str, str]) -> tuple[str, list[str]]:
    """
    Normalizes the filename:
    - no trailing spaces
    - removing quotes
    - replaces accented characters
    - normalization of extension

    Args:
        filename (str)
            String representing the filename to normalize.
        accent_map (dict[str, str])    
            Dictionary of accented characters to ASCII equivalents.
    
   Returns:
        tuple[str, list[str]]
            A tuple containing:
            - normalized_filename (str): the normalized filename string.
            - actions (actions (list[str])): a list of actions describing the normalization actions that were applied.
    """
    actions = []
    filename_strip = filename.strip()

    if filename != filename_strip:
        actions.append("TRAILING_SPACES_REMOVED")
    
    if filename_strip.startswith('"') and filename_strip.endswith('"'):
        filename_quotes = filename_strip[1:-1]
        actions.append("QUOTES_REMOVED")

        filename_strip = filename_quotes.strip()
        if filename_strip != filename_quotes:
            actions.append("TRAILING_SPACES_INSIDE_QUOTES_REMOVED")
    
    filename_replacement = filename_strip
    for target, replacement in accent_map.items():
        filename_replacement = filename_replacement.replace(target, replacement)
    if filename_replacement != filename_strip:
        actions.append("ACCENTS_REMOVED")

    filename_extension = _normalize_pdf_extension(filename_replacement)
    if filename_extension != filename_replacement:
        actions.append("NORMALIZED_PDF_EXTENSION")

    return filename_extension, actions


if __name__ == "__main__":
    main()