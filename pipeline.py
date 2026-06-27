import pandas as pd
import os

def main():
    excel_path = "richiesta.xlsx"
    attachments_path = "doc/"
    df = load_excel_data(excel_path)
    attachments = load_attachment_filenames(attachments_path)



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

def load_attachment_filenames(attachments_path: str) -> set:
    """
    Loads the content of the directory used by the validation pipeline and returns them as a set.

    Args:
        attachments_path (str)
            Path to the document folder.

    Returns:
        set
            Set of attachment filenames.
    """
    attachments = set(os.listdir(attachments_path))
    return attachments

if __name__ == "__main__":
    main()