import pandas as pd
import os

def main():
    excel_path = "richiesta.xlsx"
    attachments_path = "doc/"
    df = load_excel_data(excel_path)
    attachments = load_attachment_filenames(attachments_path)
    normalized_attachments = normalize_attachment_filenames(attachments)

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

if __name__ == "__main__":
    main()