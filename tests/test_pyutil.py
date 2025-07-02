# Adjusted to utilize the direct injection that was added to the functions!

import pytest
from hr import pyutil

# ------------------- #
# -- MOCK-FIXTURES -- #
# ------------------- #

@pytest.fixture
def sample_pdf_text() -> str:
    """Eine Fixture, die einen realistischen, gemockten PDF-Text zurückgibt."""
    return """
Auszug aus dem Handelsregister
----------------------------------
1. a) Firma:
Testfirma GmbH

2. b) Sitz:
Musterstadt

3. Geschäftsanschrift:
Musterstraße 1, 12345 Musterstadt

4. b) Vorstand, Leitungsorgan, geschäftsführende Direktoren, persönlich haftender Gesellschafter
Geschäftsführer: Mustermann, Max
Geschäftsführer: Musterfrau, Erika

5. Prokura:
Einzelprokura: Prokurist, Peter

6. a) Rechtsform, Beginn, Satzung oder Gesellschaftsvertrag
Gesellschaft mit beschränkter Haftung
    """

@pytest.fixture
def text_without_data() -> str:
    """Eine Fixture mit Text, in dem keine der gesuchten Daten vorkommen."""
    return "Dies ist ein irrelevanter Text ohne Firmen- oder Managementdaten."

# ------------------------- #
# -- Tests for functions -- #
# ------------------------- #

# --- Tests for extract_company_name ---

def test_extract_company_name_success(sample_pdf_text):
    """Testet den Erfolgsfall, indem der Text direkt übergeben wird."""
    result = pyutil.extract_company_name("dummy.pdf", _test_text=sample_pdf_text)
    assert result == "Testfirma GmbH"

def test_extract_company_name_not_found(text_without_data):
    """Testet den 'nicht gefunden'-Fall."""
    result = pyutil.extract_company_name("dummy.pdf", _test_text=text_without_data)
    assert result is None

# --- Tests for extract_company_address ---

def test_extract_company_address_success(sample_pdf_text):
    """Testet die erfolgreiche Extraktion der Adresse."""
    result = pyutil.extract_company_address("dummy.pdf", _test_text=sample_pdf_text)
    assert result == "Musterstraße 1, 12345 Musterstadt"

# --- Tests for extract_management_data ---

def test_extract_management_data_ceos_only(sample_pdf_text):
    """Testet, ob nur die Geschäftsführer korrekt extrahiert werden."""
    result = pyutil.extract_management_data("dummy.pdf", fetch_ceos_only=True, _test_text=sample_pdf_text)
    assert result == ["Mustermann, Max", "Musterfrau, Erika"]

def test_extract_management_data_with_prokuristen(sample_pdf_text):
    """Testet, ob Geschäftsführer UND Prokuristen korrekt extrahiert werden."""
    result = pyutil.extract_management_data("dummy.pdf", fetch_ceos_only=False, _test_text=sample_pdf_text)
    assert "Mustermann, Max" in result
    assert "Musterfrau, Erika" in result
    assert "Prokurist, Peter" in result
    assert len(result) == 3

# --- Test for main function ---

def test_extract_company_data_from_pdf_integration(mocker):
    mocker.patch("hr.pyutil.extract_company_name", return_value="Testfirma GmbH")
    mocker.patch("hr.pyutil.extract_company_address", return_value="Musterstraße 1")
    mocker.patch("hr.pyutil.extract_management_data", return_value=["Max Mustermann"])

    result = pyutil.extract_company_data_from_pdf("dummy.pdf")

    assert isinstance(result, pyutil.CompanyPdfData)
    assert result.name == "Testfirma GmbH"
    assert result.address == "Musterstraße 1"
    assert result.ceos == ["Max Mustermann"]