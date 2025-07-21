# Adjusted methods with added _test_text to allow for easier tests via data injection!

from dataclasses import dataclass
import re
from typing import List, Optional
import fitz
from nameparser import HumanName

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
    Extrahiert die Namen der Geschäftsführer aus dem Text, indem es den entsprechenden
    Abschnitt im Dokument isoliert und anschließend alle Personen mit Geburtsdatum findet.
    Die Funktion kann verschiedene Formatierungen von Namen, Orten und Daten verarbeiten.
    """
    
    # 1. Den Abschnitt mit den Geschäftsführer-Daten isolieren.
    #    Dieser beginnt typischerweise mit "b) Vorstand..." und endet vor dem nächsten nummerierten Abschnitt.
    section_pattern = re.compile(
        r"b\)\s*(?:Vorstand, Leitungsorgan|Geschäftsführer, Vertretungsberechtigte)[\s\S]+?(?=\n\s*\d+\.\s*)",
        re.DOTALL
    )
    management_section_match = section_pattern.search(full_text)
    
    source_text = full_text
    if management_section_match:
        source_text = management_section_match.group(0)

    # 2. Innerhalb des Textes alle Zeilen finden, die ein Geburtsdatum enthalten.
    #    Das Format "*tt.mm.jjjj" ist ein sehr zuverlässiger Anker.
    person_lines = re.findall(r"^\s*.*\*.*$", source_text, re.MULTILINE)
    
    if not person_lines:
        return []

    all_managers = []
    # Muster zum Entfernen von "Ort, *Datum"
    junk_pattern_city_first = re.compile(r',\s*[^,]+,\s*\*\d{2}\.\d{2}\.\d{4}.*$', re.IGNORECASE)
    # Muster zum Entfernen von "*Datum, Ort"
    junk_pattern_date_first = re.compile(r',\s*\*\d{2}\.\d{2}\.\d{4}.*$', re.IGNORECASE)
    # Muster zum Entfernen von Rollen-Präfixen wie "Geschäftsführer: "
    prefix_pattern = re.compile(r"^\s*(?:Geschäftsführer|Liquidator|Vorstand|Partner|\d+\.\s+Vorstand):\s*", re.IGNORECASE)

    for line in person_lines:
        cleaned_line = line.strip()
        
        # Zuerst ein mögliches Präfix (z.B. "Liquidator: ") entfernen.
        cleaned_line = prefix_pattern.sub('', cleaned_line)
        
        # Nun versuchen, die restlichen Informationen (Ort, Datum) zu entfernen.
        # Es wird zuerst das spezifischere Muster für "Name, Ort, *Datum" probiert.
        temp_line = junk_pattern_city_first.sub('', cleaned_line)
        
        # Wenn sich nichts geändert hat, das Muster für "Name, *Datum, Ort" anwenden.
        if temp_line == cleaned_line:
            temp_line = junk_pattern_date_first.sub('', cleaned_line)
        
        final_name = temp_line.strip()
        
        if final_name:
            all_managers.append(final_name)
            
    return all_managers
    
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

    # A fallback pattern for cases where the address
    # appears on the line directly following the city, under the "Sitz" section.
    fallback_pattern = re.compile(r"b\)\s*Sitz,[^\n]+\n[^\n]+\n\s*([^\n]+)")
    match = fallback_pattern.search(full_text)
    return match.group(1).strip() if match else ""

def parse_string_name(full_name: str) -> HumanName:
    """
    Parses a string containing the full name of a person to a HumanName object where the individual parts can get accessed individually.

    Args:
        full_name: The string containing the full name of a person, including titles and with no clear structure.

    Returns:
        The HumanName object that was parsed from the input string.
    """
    name = HumanName(full_name)
    return name