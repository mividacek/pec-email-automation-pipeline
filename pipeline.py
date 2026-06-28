import pandas as pd
import os

def main():
    excel_path = "richiesta.xlsx"
    attachments_path = "doc/"
    df = load_excel_data(excel_path)
    attachments = load_attachment_filenames(attachments_path)
    normalized_attachments = normalize_attachment_filenames(attachments)
    normalized_df = normalize_excel_filenames(df)

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

def normalize_attachment_filenames(attachments: list[str]) -> list[str]:
    """
    Normalizes the attachment filenames by sanitizing the extension and returns them as a list of strings.

    Args:
        attachments (list[str])
            List of loaded attachment filenames.

    Returns:
        normalized_attachments (list[str])
            List of normalized attachment filenames.
    """
    normalized_attachments = []
    for i in attachments:
        normalized_attachments.append(_normalize_pdf_extension(i))
    return normalized_attachments

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

def normalize_excel_filenames(df: pd.DataFrame) -> dict[str, list[str]]:
    """
    Normalizes the filenames in excel df:
    - no trailing spaces
    - removing quotes
    - replaces accented characters
    - normalization of extension

    Args:
        df (pandas.DataFrame)
            The loaded Excel workbook.
    
    Returns:
        dict[str, list[str]]
            The values or the column "Allegato 1" and if "Allegato 2" exists and is not empty in a dictonary where the column name is the key and the values are lists of normalized file names.
    """
    normalized_excel_filenames = {}
    normalized_excel_filenames_1 = []

    excel_filenames_1 = df["Allegato 1"].to_list()
    
    for i in excel_filenames_1:
        j = _normalize_excel_filename(i)
        normalized_excel_filenames_1.append(j)

    normalized_excel_filenames["Allegato 1"] = normalized_excel_filenames_1

    if "Allegato 2" in df and not df["Allegato 2"].isna().all():
        normalized_excel_filenames_2 = []
        excel_filenames_2 = df["Allegato 2"].fillna("").to_list()

        for i in excel_filenames_2:
            if i != "":
                j = _normalize_excel_filename(i)
                normalized_excel_filenames_2.append(j)
            else:
                normalized_excel_filenames_2.append(i)
        
        normalized_excel_filenames["Allegato 2"] = normalized_excel_filenames_2

    return normalized_excel_filenames

def _normalize_excel_filename(filename: str) -> str:
    """
    Normalizes the filename:
    - no trailing spaces
    - removing quotes
    - replaces accented characters
    - normalization of extension

    Args:
        filename (str)
            String representing the filename to normalize.
    
    Returns:
        normalized_filename (str)
            The normalized filename string.
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
    
    normalized_filename = filename.strip()
    
    if normalized_filename.startswith('"') and normalized_filename.endswith('"'):
        normalized_filename = normalized_filename[1:-1]
    
    for target, replacement in accent_map.items():
        normalized_filename = normalized_filename.replace(target, replacement)
    
    normalized_filename = _normalize_pdf_extension(normalized_filename)

    return(normalized_filename)


if __name__ == "__main__":
    main()