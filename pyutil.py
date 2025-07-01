# pyutil.py (ANGEPASST FÜR BESSERE TESTBARKEIT)

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
    tmp_name = extract_company_name(pdf_path, _test_text=_test_text)
    tmp_address = extract_company_address(pdf_path, _test_text=_test_text)
    ceos = extract_management_data(pdf_path, True, _test_text=_test_text)
    name = ""
    address = ""
    if tmp_name:
        name = tmp_name
    if tmp_address:
        address = tmp_address
    return CompanyPdfData(ceos, name, address)

def extract_management_data(pdf_path: str, fetch_ceos_only: bool = False, _test_text: Optional[str] = None) -> List[str]:
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
            return []

    geschaeftsfuehrer_block_regex = re.compile(r"b\) Vorstand, Leitungsorgan.*?5\.", re.DOTALL)
    geschaeftsfuehrer_block = geschaeftsfuehrer_block_regex.search(full_text)
    
    geschaeftsfuehrer_list = []
    if geschaeftsfuehrer_block:
        block_text = geschaeftsfuehrer_block.group(0)
        gf_pattern = re.compile(r"Geschäftsführer:\s*(.*)")
        found_geschaeftsfuehrer = gf_pattern.findall(block_text)
        for gf in found_geschaeftsfuehrer:
            geschaeftsfuehrer_list.append(gf.strip())

    if not fetch_ceos_only:
        prokura_block_regex = re.compile(r"5\.\s*Prokura:(.*?)6\.\s*a\)", re.DOTALL)
        prokura_block = prokura_block_regex.search(full_text)
        
        prokuristen_list = []
        if prokura_block:
            block_text = prokura_block.group(1).strip()
            if block_text and '---' not in block_text:
                prokura_pattern = re.compile(r"(Einzelprokura|Gesamtprokura):\s*(.*)")
                found_prokuristen = prokura_pattern.findall(block_text)
                for prok in found_prokuristen:
                    prokuristen_list.append(prok[1].strip())
        geschaeftsfuehrer_list.extend(prokuristen_list)
        
    return geschaeftsfuehrer_list
    
def extract_company_name(pdf_path: str, _test_text: Optional[str] = None) -> Optional[str]:
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
            return None

    pattern = re.compile(r"\d+\.\s*a\) Firma:[\s\n]+([^\n]*)")
    match = pattern.search(full_text)

    if match:
        return match.group(1).strip()
    
    return None

def extract_company_address(pdf_path: str, _test_text: Optional[str] = None) -> Optional[str]:
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
            return None
    
    pattern = re.compile(r"\d+\.\s*Geschäftsanschrift:[\s\n]+([^\n]*)")
    match = pattern.search(full_text)

    if match:
        return match.group(1).strip()
    
    return None