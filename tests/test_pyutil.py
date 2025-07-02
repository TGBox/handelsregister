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
Geschäftsführer: Mustermann, Max, Musterhausen, *01.03.1988
Geschäftsführer: Musterfrau, Erika, Musterdorf, *29.11.1945

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
    result = pyutil.extract_company_name(full_text=sample_pdf_text)
    assert result == "Testfirma GmbH"

def test_extract_company_name_not_found(text_without_data):
    """Testet den 'nicht gefunden'-Fall."""
    result = pyutil.extract_company_name(full_text=text_without_data)
    assert result is ""

# --- Tests for extract_company_address ---

def test_extract_company_address_success(sample_pdf_text):
    """Testet die erfolgreiche Extraktion der Adresse."""
    result = pyutil.extract_company_address(full_text=sample_pdf_text)
    assert result == "Musterstraße 1, 12345 Musterstadt"

# --- Tests for extract_management_data ---

def test_extract_management_data(sample_pdf_text):
    """Testet, ob nur die Geschäftsführer korrekt extrahiert werden."""
    result = pyutil.extract_management_data(full_text=sample_pdf_text)
    assert result == ["Mustermann, Max", "Musterfrau, Erika"]

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