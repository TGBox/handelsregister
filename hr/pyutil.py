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
    Extrahiert die Namen der Geschäftsführer (Geschäftsführer, Partner usw.) aus dem Text.
    Die Funktion verarbeitet mehrere Formate, einschließlich einzelner Einträge mit Geburtsdaten 
    und mehrerer Einträge in einer einzigen Zeile ohne Geburtsdaten.

    Args:
        full_text: Der Textinhalt des Handelsregisterauszugs.

    Returns:
        Eine Liste mit den Namen des Führungspersonals.
    """
    all_managers = []
    
    # Dieser Regex findet alle Zeilen, die mit Schlüsselwörtern wie "Geschäftsführer" 
    # beginnen und erfasst den Rest der Zeile, der den/die Namen enthält.
    line_pattern = re.compile(
        r"^\s*(?:Geschäftsführer|Partner|Einzelvertretungsberechtigt):\s*(.*)", 
        re.MULTILINE
    )
    
    content_lines = line_pattern.findall(full_text)
    
    for line in content_lines:
        line = line.strip()

        # Ignoriert leere Zeilen oder Platzhalter wie "-"
        if not line or line == '-':
            continue

        # Fall 1: Die Zeile enthält ein Geburtsdatum (*tt.mm.jjjj), was auf eine Person hinweist.
        if '*' in line:
            # Entfernt den Ort und das Geburtsdatum, um den Namen zu isolieren.
            # Der reguläre Ausdruck geht davon aus, dass der Name am Anfang steht.
            name_part = re.sub(r',\s*[^,]+,\s*\*\d{2}\.\d{2}\.\d{4}.*$', '', line).strip()
            all_managers.append(name_part)
        # Fall 2: Die Zeile enthält kein Geburtsdatum; wahrscheinlich eine kommagetrennte Liste.
        else:
            # Teilt die Zeile nach Kommas auf. Erwartetes Format: "Nachname1, Vorname1, Nachname2, Vorname2..."
            parts = [p.strip() for p in line.split(',') if p.strip()]
            
            # Prüft auf "Nachname, Vorname"-Paare (gerade Anzahl von Teilen).
            if len(parts) > 1 and len(parts) % 2 == 0:
                for i in range(0, len(parts), 2):
                    full_name = f"{parts[i]}, {parts[i+1]}"
                    all_managers.append(full_name)
            elif len(parts) > 0:
                # Wenn nicht in Paaren (z.B. ein einzelner Name), wird die ganze Zeile hinzugefügt.
                all_managers.append(line)

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