# Adjusted methods with added _test_text to allow for easier tests via data injection!

from dataclasses import dataclass
import re
from typing import List, Optional
import fitz
from nameparser import HumanName
import unicodedata

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
        pdf_path (str): The path to the PDF file that was downloaded from the Handelsregister BundesAPI.
        _test_text (Optional[str]): Optional string test text parameter that is only used for testing the methods in this file more efficiently.

    Returns:
        CompanyPdfData: A CompanyPdfData object containing the extracted information.
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
    Function to extract the names of the ceos of a company from the provided text input parameter.
    The text should have been extracted from the document that was downloaded after calling the Handelsregister BundesAPI.
    Can process different format patterns of company data.
    
    Args:
        full_text (str): The extracted text string from the document.
    
    Returns:
        List[str]: A list containing all of the ceos that could get extracted from the document text.
    """
    
    # 1. Isolating the part of the document that contains the ceo(s) of the company.
    # The pattern now uses a capturing group to get ONLY the lines with manager data,
    # excluding the section header itself.
    section_pattern = re.compile(
        # Group 1: Match the header line (non-capturing)
        r"(?:b\)\s*(?:Vorstand, Leitungsorgan|Geschäftsführer|persönlich haften|Vertretungsberechtigte)[\s\S]*?\n)"
        # Group 2: Capture the actual manager data lines that follow the header
        r"([\s\S]+?)"
        # Stop before the next numbered section
        r"(?=\n\s*\d+\.\s*)",
        re.DOTALL | re.IGNORECASE
    )
    management_section_match = section_pattern.search(full_text)
    
    # If no match or the capturing group for the data is empty, return.
    if not management_section_match or not management_section_match.group(1):
        return []
    
    # source_text now contains ONLY the relevant lines with manager names.
    source_text = management_section_match.group(1)

    all_managers = []
    
    # Patterns for cleaning the extracted lines
    junk_pattern_city_first = re.compile(r',\s*[^,]+,\s*\*\d{2}\.\d{2}\.\d{4}.*$', re.IGNORECASE)
    junk_pattern_date_first = re.compile(r',\s*\*\d{2}\.\d{2}\.\d{4}.*$', re.IGNORECASE)
    prefix_pattern = re.compile(r"^\s*(?:Geschäftsführer|Liquidator|Vorstand|Partner|persönlich hafte.* Gesellschafter):\s*", re.IGNORECASE)

    # 2. Iterate through the now clean list of lines.
    for line in source_text.splitlines():
        name_part = prefix_pattern.sub('', line.strip())
        
        if not name_part or ',' not in name_part:
            continue
            
        final_name = ""
        
        # Case A: The line contains a birth date (*DD.MM.YYYY).
        if '*' in name_part:
            temp_line = junk_pattern_city_first.sub('', name_part)
            if temp_line == name_part:
                temp_line = junk_pattern_date_first.sub('', name_part)
            final_name = temp_line.strip()
        
        # Case B: The line does not contain a birth date.
        else:
            parts = name_part.split(',')
            if len(parts) >= 2:
                name_candidate = f"{parts[0].strip()}, {parts[1].strip()}"
                if len(name_candidate) > 4 and " " in name_candidate:
                    final_name = name_candidate

        if final_name and final_name not in all_managers:
            all_managers.append(final_name)
            
    return all_managers
    
def extract_company_name(full_text: str) -> Optional[str]:
    """
    Extracts the company name from the text.

    Args (str):
        full_text: The text content of the Handelsregister excerpt.

    Returns:
        Optional[str]: The company name as a string, or an empty string if not found.
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
        full_text (str): The text content of the Handelsregister excerpt.

    Returns:
        Optional[str]: The company address as a string, or an empty string if not found.
    """
    # The primary pattern looks for the explicit "Geschäftsanschrift:" label.
    # This is the most common format.
    primary_pattern = re.compile(r"Geschäftsanschrift:\s*([^\n]+)")
    match = primary_pattern.search(full_text)
    if match:
        return match.group(1).strip()

    # A fallback pattern for cases where the address
    # appears on the line directly following the city, under the "Sitz" section.
    fallback_pattern = re.compile(r"b\)\s*Sitz,[^\n]+\n[^\n]+\n\s*([^\n]+)")
    match = fallback_pattern.search(full_text)
    return match.group(1).strip() if match else ""

def parse_string_name(full_name: str) -> HumanName:
    """
    Parses a string containing the full name of a person to a HumanName object where the individual parts can get accessed individually.

    Args:
        full_name (str): The string containing the full name of a person, including titles and with no clear structure.

    Returns:
        HumanName: The HumanName object that was parsed from the input string.
    """
    name = HumanName(full_name)
    return name

def create_company_folder_name(name: str, city: str, shorten: bool) -> str:
    """
    Creates the name of the download folder, where the documents of the corresponding company gets saved to.
    If the name should get shortened, then the company name may get up to 15 characters long, and the city name may get up to 10 characters long.
    
    Args:
        name (str): The string name of the company.
        city (str): The string city of the company.
        shorten (bool): Boolean flag to indicate if the name should get sanitized and shortened.
    
    Returns:
        str: The generated company folder name.
    """
    
    n_len = 15
    c_len = 10
    
    if shorten:
        return crop_string_to_max_length(sanitize_string_for_folder_name(name), n_len) + "-" + crop_string_to_max_length(sanitize_string_for_folder_name(city), c_len)
    
    return name + "-" + city

def remove_diacritical_marks(s: str) -> str:
    """
    Removes all diacritical marks from a given string.
    
    Args:
        s (str): The string to get sanitized.
    
    Returns:
        str: The string without any diacritical marks.
    """
    
    # Normalize the string into NFD, which removes all of those special characters and replaces them with the base letter equivalent.
    nfkd_form = unicodedata.normalize('NFD', s)
    # Additionally filters out all remaining combining diacritics before returning the string.
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def sanitize_string_for_folder_name(s: str) -> str:
    """
    Sanitizes a given string to get a simplified version of it, without special characters or empty spaces.
    
    Args:
        s (str): The string that needs to get sanitized.
    
    Returns:
        str: The sanitized string that can be used for creating a company folder name.
    """
    
    # Sanitation map containing german special characters and their base letter replacements.
    sanitation_map = {
        'ä': 'ae',
        'ö': 'oe',
        'ü': 'ue',
        'ß': 'ss'
    }
    
    # Trim extra spaces from the start and end of the string, replace all "´" and replace all commas.
    sanitized = s.strip().replace(",", "")
    sanitized = sanitized.replace("´", "")
    sanitized = sanitized.replace(" - ", "-")
    sanitized = sanitized.replace(" & ", "&")

    # Convert to lowercase and replace all remaining spaces with dashes.
    sanitized = sanitized.lower().replace(" ", "-")

    # Replace german special characters via the sanitation map.
    for char, replacement in sanitation_map.items():
        sanitized = sanitized.replace(char, replacement)

    # Remove other diacritical marks.
    sanitized = remove_diacritical_marks(sanitized)

    return sanitized

def crop_string_to_max_length(s: str, max: int) -> str:
    """
    Function that takes a string and a maximum length value and ensures that the returned strings length does not exceed the specified threshold.
    If the string is shorter than the threshold, it gets returned as is. Otherwise the substring until the threshold index will get returned instead.

    Args:
        s (str): The string that needs to get cropped to ensure its length does not exceed the specified threshold.
        max (int): The maximum length that the returned string is allowed to have.

    Returns:
        str: The (possibly) cropped string.
    """
    
    if len(s) <= max:
        return s

    return s[0:max]