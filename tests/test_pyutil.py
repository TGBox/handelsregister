# Adjusted to utilize the direct injection that was added to the functions!

import pytest
import unittest
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
def sample_pdf_text2() -> str:
    """Eine Fixture, die einen weiteren realistischen, gemockten PDF-Text zurückgibt."""
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
Geschäftsführer: Mustermann, Max, Kaufmann, Dreieich

5. Prokura:
-

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

def test_extract_management_data2(sample_pdf_text2):
    """Testet, ob die Geschäftsführer auch von einem anders formatierten Dokument korrekt extrahiert werden."""
    result = pyutil.extract_management_data(full_text=sample_pdf_text2)
    assert result == ["Mustermann, Max"]

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

# --- Tests for the parsing of name strings ---

class TestNameParsing(unittest.TestCase):
    
    def test_most_common_name_formats(self):
        """Testet die gängigsten Namensformate."""
        
        # Arrange.
        names_to_test = [
            "Stefan Müller",
            "Schmidt, Maria",
            "Prof. Dr. Anna-Lena von der Heide",
            "Jan de Vries",
            "Winter, Peter Otto"
        ]
        
        # Act.
        expected_results = [
            {'firstName': 'Stefan', 'lastName': 'Müller', 'title': '', 'middle': ''},
            {'firstName': 'Maria', 'lastName': 'Schmidt', 'title': '', 'middle': ''},
            {'firstName': 'Anna-Lena', 'lastName': 'von der Heide', 'title': 'Prof. Dr.', 'middle': ''},
            {'firstName': 'Jan', 'lastName': 'de Vries', 'title': '', 'middle': ''},
            {'firstName': 'Peter', 'lastName': 'Winter', 'title': '', 'middle': 'Otto'},
        ]
        
        real_results = []
        for test_name in names_to_test:
            name = pyutil.parse_string_name(test_name)
            real_results.append({
                'firstName': name.first,
                'lastName': name.last,
                'title': name.title,
                'middle': name.middle
            })
        
        # Assert.
        self.assertEqual(expected_results, real_results)
    
    def test_more_obscure_name_formats(self):
        """Testet ungewöhnlichere Namensformate."""
        
        # Arrange.
        names_to_test = [
            "Jens Stefan Hans-Jürgen Möller-Döhling",
            "Dr. Phil Specter",
            "Mike Hunt",
            "Schlachter-Ohnewald, Sieglinde Berta Ruth",
            "Dr. Eitelbert Hupfeld",
            "Böttinger, Luitwin"
        ]
        
        # Act.
        expected_results = [
            {'firstName': 'Jens', 'lastName': 'Möller-Döhling', 'title': '', 'middle': 'Stefan Hans-Jürgen'},
            {'firstName': 'Phil', 'lastName': 'Specter', 'title': 'Dr.', 'middle': ''},
            {'firstName': 'Mike', 'lastName': 'Hunt', 'title': '', 'middle': ''},
            {'firstName': 'Sieglinde', 'lastName': 'Schlachter-Ohnewald', 'title': '', 'middle': 'Berta Ruth'},
            {'firstName': 'Eitelbert', 'lastName': 'Hupfeld', 'title': 'Dr.', 'middle': ''},
            {'firstName': 'Luitwin', 'lastName': 'Böttinger', 'title': '', 'middle': ''},
        ]
        
        real_results = []
        for test_name in names_to_test:
            name = pyutil.parse_string_name(test_name)
            real_results.append({
                'firstName': name.first,
                'lastName': name.last,
                'title': name.title,
                'middle': name.middle
            })
        
        # Assert.
        self.assertEqual(expected_results, real_results)
        
    def test_single_name(self):
        """Testet wie ein einzelner Name ohne Leerzeichen verarbeitet wird."""
        name = "Cher"
        expected = {'firstName': 'Cher', 'lastName': '', 'title': '', 'middle': ''}
        human_name = pyutil.parse_string_name(name)
        actual = {
            'firstName': human_name.first,
            'lastName': human_name.last,
            'title': human_name.title,
            'middle': human_name.middle
        }
        self.assertEqual(actual, expected)
        
    def test_empty_string(self):
        """Testet wie ein leerer String verarbeitet wird."""
        name = ""
        expected = {'firstName': '', 'lastName': '', 'title': '', 'middle': ''}
        human_name = pyutil.parse_string_name(name)
        actual = {
            'firstName': human_name.first,
            'lastName': human_name.last,
            'title': human_name.title,
            'middle': human_name.middle
        }
        self.assertEqual(actual, expected)

class TestFolderNameFunctions(unittest.TestCase):

    def test_crop_string_to_max_length(self):
        print("\n--- Testing crop_string_to_max_length ---")
        self.assertEqual(pyutil.crop_string_to_max_length("kurz", 10), "kurz", "Sollte den String unverändert lassen, wenn er kürzer ist.")
        self.assertEqual(pyutil.crop_string_to_max_length("genauzehn", 10), "genauzehn", "Sollte den String unverändert lassen, wenn er genau die maximale Länge hat.")
        self.assertEqual(pyutil.crop_string_to_max_length("dieserstringistvielzulang", 10), "dieserstri", "Sollte den String auf die maximale Länge kürzen.")
        self.assertEqual(pyutil.crop_string_to_max_length("", 10), "", "Sollte einen leeren String korrekt behandeln.")
        self.assertEqual(pyutil.crop_string_to_max_length("test", 0), "", "Sollte einen leeren String zurückgeben, wenn max_len 0 ist.")

    def test_remove_diacritical_marks(self):
        print("\n--- Testing remove_diacritical_marks ---")
        self.assertEqual(pyutil.remove_diacritical_marks("François"), "Francois", "Sollte französische Diakritika entfernen.")
        self.assertEqual(pyutil.remove_diacritical_marks("crème brûlée"), "creme brulee", "Sollte mehrere Diakritika entfernen.")
        self.assertEqual(pyutil.remove_diacritical_marks("año"), "ano", "Sollte spanische Diakritika entfernen.")
        self.assertEqual(pyutil.remove_diacritical_marks("normaler text"), "normaler text", "Sollte Text ohne Diakritika unverändert lassen.")
        self.assertEqual(pyutil.remove_diacritical_marks(""), "", "Sollte einen leeren String korrekt behandeln.")

    def test_sanitize_string_for_folder_name(self):
        print("\n--- Testing sanitize_string_for_folder_name ---")
        self.assertEqual(pyutil.sanitize_string_for_folder_name("  Test Firma  "), "test-firma", "Sollte Leerzeichen am Anfang/Ende entfernen und in der Mitte ersetzen.")
        self.assertEqual(pyutil.sanitize_string_for_folder_name("Müller & Söhne, Groß-Gerau"), "mueller&soehne-gross-gerau", "Sollte deutsche Umlaute, Kommas und Leerzeichen korrekt behandeln.")
        self.assertEqual(pyutil.sanitize_string_for_folder_name("ABC Company"), "abc-company", "Sollte in Kleinbuchstaben umwandeln.")
        self.assertEqual(pyutil.sanitize_string_for_folder_name("François Immo-AG"), "francois-immo-ag", "Sollte eine Kombination aus verschiedenen Zeichen korrekt bereinigen.")
        self.assertEqual(pyutil.sanitize_string_for_folder_name(""), "", "Sollte einen leeren String korrekt behandeln.")
        self.assertEqual(pyutil.sanitize_string_for_folder_name("Gregor´s Laden"), "gregors-laden", "Sollte den seltenen Randfall korrekt behandeln, falls ein falsches Anführungszeichen entdeckt wurde.")


    def test_create_company_folder_name(self):
        print("\n--- Testing create_company_folder_name  ---")
        
        # Test case 1: `shorten=False`
        self.assertEqual(pyutil.create_company_folder_name("Müller AG", "Berlin", False), "Müller AG-Berlin", "Sollte bei shorten=False einfach verketten.")

        # Test case 2: `shorten=True`, but strings are shorter than their limits.
        self.assertEqual(pyutil.create_company_folder_name("Kurz AG", "Ulm", True), "kurz-ag-ulm", "Sollte bei kurzen Namen nur bereinigen, nicht kürzen.")

        # Test case 3: `shorten=True`, name is too long, city is too short.
        long_name = "Eine sehr lange Firma mit einem langen Namen"
        self.assertEqual(pyutil.create_company_folder_name(long_name, "Ulm", True), "eine-sehr-lange-ulm", "Sollte nur den Namen auf 15 Zeichen kürzen.")

        # Test case 4: `shorten=True`, name is too short, city is too long.
        long_city = "Friedrichshafen am Bodensee"
        self.assertEqual(pyutil.create_company_folder_name("Kurz AG", long_city, True), "kurz-ag-friedrichs", "Sollte nur die Stadt auf 10 Zeichen kürzen.")

        # Test case 5: `shorten=True`, both names are too long and complex.
        name = "Müller & Söhne, Groß-Gerau" # sanitized: "mueller-&-soehne-gross-gerau"
        city = "Friedrichshafen am Bodensee" # sanitized: "friedrichshafen-am-bodensee"
        expected = "mueller&soehne--friedrichs" # shortened to 15 and 10
        self.assertEqual(pyutil.create_company_folder_name(name, city, True), expected, "Sollte komplexe Namen korrekt bereinigen und auf die festen Längen (15/10) kürzen.")
        
        # Test case 6: empty strings
        self.assertEqual(pyutil.create_company_folder_name("", "", True), "-", "Sollte leere Strings zu einem Bindestrich verbinden.")
    
    def test_create_company_folder_name_typescript_parity(self):
        print("\n--- Testing create_company_folder_name - Checking for parity on Typescript function ---")
        
        # Test case 1: `shorten=False`
        self.assertEqual(pyutil.create_company_folder_name("immersight GmbH", "Ulm", False), "immersight GmbH-Ulm", "Sollte bei shorten=False einfach verketten.")
        self.assertEqual(pyutil.create_company_folder_name("Sonntag und Partner", "Märkßheim", False), "Sonntag und Partner-Märkßheim", "Sollte bei shorten=False einfach verketten.")
        self.assertEqual(pyutil.create_company_folder_name("@Home-Wröck", "Berlin (Mitte)", False), "@Home-Wröck-Berlin (Mitte)", "Sollte bei shorten=False einfach verketten.")
        self.assertEqual(pyutil.create_company_folder_name("123.de - Blitzschnelle Hilfe wenn man einen langen Firmennamen braucht", "Potsdam", False), "123.de - Blitzschnelle Hilfe wenn man einen langen Firmennamen braucht-Potsdam", "Sollte bei shorten=False einfach verketten.")
        self.assertEqual(pyutil.create_company_folder_name("Gregor´s - Gas, Wasser & Scheiße Betrieb", "Köln", False), "Gregor´s - Gas, Wasser & Scheiße Betrieb-Köln", "Sollte bei shorten=False einfach verketten.")

        # Test case 2: `shorten=True`.
        self.assertEqual(pyutil.create_company_folder_name("immersight GmbH", "Ulm", True), "immersight-gmbh-ulm", "Sollte bei shorten=True verketten und bereinigen.")
        self.assertEqual(pyutil.create_company_folder_name("Sonntag und Partner", "Märkßheim", True), "sonntag-und-par-maerksshei", "Sollte bei shorten=True verketten und bereinigen.")
        self.assertEqual(pyutil.create_company_folder_name("@Home-Wröck", "Berlin (Mitte)", True), "@home-wroeck-berlin-(mi", "Sollte bei shorten=True verketten und bereinigen.")
        self.assertEqual(pyutil.create_company_folder_name("123.de - Blitzschnelle Hilfe wenn man einen langen Firmennamen braucht", "Potsdam", True), "123.de-blitzsch-potsdam", "Sollte bei shorten=True verketten und bereinigen.")
        self.assertEqual(pyutil.create_company_folder_name("Gregor´s - Gas, Wasser & Scheiße Betrieb", "Köln", True), "gregors-gas-was-koeln", "Sollte bei shorten=True verketten und bereinigen.")