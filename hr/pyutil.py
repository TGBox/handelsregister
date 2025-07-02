# Adjusted methods to allow for easier tests!

from dataclasses import dataclass
import re
from typing import List, Optional
import fitz

@dataclass
class CompanyPdfData:
    ceos: List[str]
    name: str
    address: str

def extract_company_data_from_pdf(pdf_path: str, _test_text: Optional[str] = None) -> CompanyPdfData:
    """
    Main function to extract company data from the text of a Handelsregister PDF.

    This function orchestrates the extraction of the company name, address, and
    management personnel (CEOs, partners, etc.) by calling specialized functions.

    Args:
        pdf_path: The path to the PDF file that was downloaded from the Handelsregister BundesAPI.

    Returns:
        A CompanyPdfData object containing the extracted information.
    """
    full_text = ""
    if _test_text:
        full_text = _test_text
    else:
        try:
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    if isinstance(page, fitz.Page):
                        full_text += page.get_text() # type: ignore
        except Exception as e:
            print(f"Fehler beim Öffnen oder Lesen der PDF-Datei: {e}")
            
    
    tmp_name = extract_company_name(full_text)
    tmp_address = extract_company_address(full_text)
    tmp_ceos = extract_management_data(full_text)
    ceos = []
    name = ""
    address = ""
    if tmp_ceos:
        ceos = tmp_ceos
    if tmp_name:
        name = tmp_name
    if tmp_address:
        address = tmp_address
    return CompanyPdfData(ceos, name, address)

def extract_management_data(full_text: str) -> List[str]:
    """
    Extracts the names of managers (Geschäftsführer, Partner, etc.) from the text.

    It first identifies the block of text containing management information and
    then extracts each person's name from that block.

    Args:
        full_text: The text content of the Handelsregister excerpt.

    Returns:
        A list of names of the management personnel.
    """
    # This regex identifies the section listing the management personnel.
    # It starts with keywords like "Vorstand" or "Partner" and ends before the next
    # numbered section (e.g., "5. Prokura:", "4. a) Rechtsform:").
    # This is more flexible than the original hardcoded pattern.
    section_regex = re.compile(
        r"b\)\s*(?:Vorstand, Leitungsorgan|Partner, Vertretungsberechtigte).*?(?=\n\s*\d\.\s)",
        re.DOTALL
    )
    management_section = section_regex.search(full_text)

    if not management_section:
        return []

    section_text = management_section.group(0)

    # This regex finds all individual person entries within the management section.
    # It looks for lines that contain a name followed by a date of birth (*dd.mm.yyyy),
    # which is a reliable pattern for these entries.
    # It correctly captures names even when they have titles or multiple first names.
    # The 're.MULTILINE' flag allows '^' to match the start of each line.
    person_regex = re.compile(
        r"^\s*(?:(?:Einzelvertretungsberechtigt|Geschäftsführer|Partner):?)?\s*(.*?,\s*.*?),\s*.*?\s*\*\d{2}\.\d{2}\.\d{4}",
        re.MULTILINE
    )
    
    found_persons = person_regex.findall(section_text)
    
    # Clean up any extra whitespace from the extracted names.
    return [name.strip() for name in found_persons]

    
def extract_company_name(full_text: str) -> Optional[str]:
    """
    Extracts the company name from the text.

    Args:
        full_text: The text content of the Handelsregister excerpt.

    Returns:
        The company name as a string, or an empty string if not found.
    """
    # This improved regex looks for either "Firma:" or "Name:" and is not
    # dependent on newlines or specific numbering, making it more robust.
    pattern = re.compile(r"a\)\s*(?:Firma|Name):?\s*([^\n]+)")
    match = pattern.search(full_text)
    return match.group(1).strip() if match else ""

def extract_company_address(full_text: str) -> Optional[str]:
    """
    Extracts the company's business address from the text.

    Args:
        full_text: The text content of the Handelsregister excerpt.

    Returns:
        The company address as a string, or an empty string if not found.
    """
    # The primary pattern looks for the explicit "Geschäftsanschrift:" label.
    # This is the most common format.
    primary_pattern = re.compile(r"Geschäftsanschrift:\s*([^\n]+)")
    match = primary_pattern.search(full_text)
    if match:
        return match.group(1).strip()

    # A fallback pattern for cases (like the Lübeck example) where the address
    # appears on the line directly following the city, under the "Sitz" section.
    fallback_pattern = re.compile(r"b\)\s*Sitz,[^\n]+\n[^\n]+\n\s*([^\n]+)")
    match = fallback_pattern.search(full_text)
    return match.group(1).strip() if match else ""
