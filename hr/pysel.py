# Selenium/Python powered stand-alone module to provide convenient programmatic access the bundesAPI WebSearch.
import sys
import json
from pyutil import extract_company_address, extract_company_data_from_pdf, extract_company_name, extract_management_data
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from pathlib import Path,PurePath, PureWindowsPath
import argparse

# ! Second adaptation of selenium_handelsregister.py - WIP
# Contains the updated versions of the extraction methods that have been introduced via pyutil.py from imsMailVerify.
# Needs to get called with the keyword argument syntax. This pairs each value to a specific key, which eleminates the need for correct order of params.

def parse_cli_arguments():
    """
        Function to parse the arguments that were passed on to this python script when it was executed.
        
        Returns:
            Dictionary containing all key=value pairs.
    """
    # Creating a parser with name, description and help text.
    parser = argparse.ArgumentParser(
        prog="Selenium - Python | HandelsregisterCLI",
        description="Ein Python Skript, welches mit Selenium die Suche von Einträgen im Handelsregister automatisieren kann.",
        add_help=True,
        epilog="Achtung! Maximal 60 Anfragen pro Stunde stellen!"
    )

    # Adding help texts for our expected arguments. NOT NEEDED ANYMORE!
    #parser.add_argument("searchTerms", nargs='+', help="Eine Liste von zu verarbeitenden Strings. 1. String ist der eigentliche Suchstring. 2. String zeigt an, welche Suchoptionen gewählt werden sollen. (all, exact oder min) 3. String ist der Name der Stadt. 4. String ist die Straße (und ggf. die Hausnummer). Der 5. String repräsentiert die Postleitzahl. Der 6. String entscheidet mit einem Boolean Wert, ob auch phonetisch ähnlich klingende Worte gesucht werden sollen. (Default false)")

    # Parsing the arguments from the command line.
    parser.add_argument(
        "-d",
        "--debug",
        help="Enable debug mode and activate logging",
        action="store_true"
    )
    parser.add_argument(
        "-f",
        "--force",
        help="Force a fresh pull and skip the cache",
        action="store_true"
    )
    parser.add_argument(
        "-s",
        "--schlagwoerter",
        help="Search for the provided keywords",
        required=True,
    )
    parser.add_argument(
        "-so",
        "--schlagwortOptionen",
        help="Keyword options: all=contain all keywords; min=contain at least one keyword; exact=contain the exact company name.",
        choices=["all", "min", "exact"],
        default="all"
    )
    parser.add_argument(
        "-sa",
        "-sae",
        "--sucheAehnliche",
        help="Should phonetically similar sounding results also get returned?",
        action="store_true",
        required=False,
        default=False
    )
    parser.add_argument(
        "-sg",
        "-sge",
        "-sog",
        "--sucheGeloeschte",
        help="Should already removed results get returned as well?",
        action="store_true",
        required=False,
        default=False
    )
    parser.add_argument(
        "-n",
        "--registerNummer",
        help="Add registry number to improve search results",
        required=False
    )
    parser.add_argument(
        "-ci",
        "--city",
        help="Name of the city where the company is located.",
        required=False
    )
    parser.add_argument(
        "-st",
        "--street",
        help="Name of the street where the company is located.",
        required=False
    )
    parser.add_argument(
        "-po",
        "--postCode",
        help="Post code of the city where the company is located.",
        required=False
    )
    args = parser.parse_args()

    # Enable debugging if wanted
    if args.debug:
        import logging
        logger = logging.getLogger("mechanize")
        logger.addHandler(logging.StreamHandler(sys.stdout))
        logger.setLevel(logging.DEBUG)

    return args

def fetch_and_download_from_bundes_api(s, so, sa, sg, ci, st, po):
    """Function to fetch and download a specific data request/response from the handelsregister bundesAPI.
    Currently only decorative for checking on the way that the input gets passed along.

    Args:
        s (str): the search term (i.e. name of the company)
        so (str): search options - "all", "exact" or "min"
        sa (bool): if phonetically similar sounding results should get returned, too.
        sg (bool): if already deleted entries should get returned, too.
        ci (str): the name of the city
        st (str): the name of the street (and possibly the house number)
        po (str): the post code of the city
    """
    # Save each entry into its own download folder.
    dl_path = Path.joinpath(Path.cwd(),"download", s)
    print("DOWNLOADPATH = ", dl_path)
    if not Path.is_dir(dl_path): # Creating the folder; but only if it does not exist yet.
        Path.mkdir(dl_path)

    # Chrome Options.
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless')  # Browser im Hintergrund ohne UI ausführen
    chrome_options.add_argument('--disable-gpu') # Manchmal nötig
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--log-level=3') # Surpresses low level warnings.
    # Chrome options setup to ensure that we can download and that we know where the file will get downloaded to.
    chrome_options.add_experimental_option('prefs', {
        'download.default_directory': str(dl_path),  
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True,
        "profile.default_content_settings.popups": 0,
        "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "profile.default_content_settings.mimetype_overrides": {
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
    })

    try:
        # Webdriver-manager loads the appropriate driver or uses a cached one.
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("WebDriver erfolgreich mit webdriver-manager initialisiert.")
    except Exception as e:
        print(f"Fehler beim Initialisieren des WebDrivers mit webdriver-manager: {e}")
        exit()

    try:
        # Trying to get the elements via their IDs.
        driver.get("https://www.handelsregister.de/rp_web/welcome.xhtml")
        target_class_selector = "a.ui-commandlink.ui-widget.dokumentList"
        advanced_search = "naviForm:erweiterteSucheLink"
        search_terms = "form:schlagwoerter"
        
        search_options_all = "form:schlagwortOptionen:0"
        search_options_exact = "form:schlagwortOptionen:1"
        search_options_min = "form:schlagwortOptionen:2"
        
        search_options = search_options_all  # Default value to avoid unbound error
        if so == "all":
            search_options = search_options_all
        elif so == "exact":
            search_options = search_options_exact
        elif so == "min":
            search_options = search_options_min
        
        post_code = "form:postleitzahl"
        city = "form:ort"
        street = "form:strasse"
        submitBtn = "form:btnSuche"
        
    ######## Interaction with the elements inside of the webpage search form. #########
    # Change to the advanced search form.    
        wait = WebDriverWait(driver, 10)
        try:
            search_link = wait.until(EC.element_to_be_clickable((By.ID, advanced_search)))
            search_link.click()
        except TimeoutException:
            print("Es wurde nicht rechtzeitig ein Button für die Erweiterte Suche gefunden.")
            search_link = ""
            
        print(f"Wechsel zur erweiterten Suche und Eintragen der Parameter...")
        # Changed to the page containing the search form.
    # Click on textbox and enter search term.
        wait = WebDriverWait(driver, 10)
        try:
            text_box = wait.until(EC.element_to_be_clickable((By.ID, search_terms)))
            text_box.send_keys(s)
        except TimeoutException:
            print("Es wurde nicht rechtzeitig eine Textbox für die Eingabe von Suchbegriffen gefunden.")
            text_box = ""
        
    # Find radio button label that corresponds to the selected option and click it.
        wait = WebDriverWait(driver, 10)
        try:
            radioBtnLabel = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"label[for='{search_options}']"))
            )
            radioBtnLabel.click()
            time.sleep(2)
        except TimeoutException:
            print("Es wurde nicht rechtzeitig ein klickbarer Radiobutton für die Eingabe von Suchoptionen gefunden.")
            radioBtnLabel = ""

    # Find the checkbox for similar sounding search results getting fetched as well.
        wait = WebDriverWait(driver, 10)
        try:
            checkbox_input = driver.find_element(By.ID, "form:aenlichLautendeSchlagwoerterBoolChkbox_input")
            if checkbox_input.is_selected():
                checkbox_container = wait.until(EC.element_to_be_clickable((By.ID, "form:aenlichLautendeSchlagwoerterBoolChkbox")))
                if (sa == False):
                    checkbox_container.click()  # deselect already selected if we do not want to search for similar!
            else:
                checkbox_container = wait.until(EC.element_to_be_clickable((By.ID, "form:aenlichLautendeSchlagwoerterBoolChkbox")))
                if (sa == True):
                    checkbox_container.click() # select deselected if we want to search for similar!
            time.sleep(2)
        except TimeoutException:
            print("Es wurde nicht rechtzeitig eine klickbare Checkbox für die Auswahl zur Suche von ähnlich klingenden Einträgen gefunden.")
            checkbox_container = ""
            


    # Find text input for the post code and enter it.
        wait = WebDriverWait(driver, 10)
        try:
            plz = wait.until(EC.element_to_be_clickable((By.ID, post_code)))
            if po:
                plz.send_keys(po)
        except TimeoutException:
            print("Es wurde nicht rechtzeitig eine Textbox für die Postleitzahleneingabe gefunden.")
            plz = ""
            
    # Find text input for the city name and enter it.
        wait = WebDriverWait(driver, 10)
        try:
            ort = wait.until(EC.element_to_be_clickable((By.ID, city)))
            if ci:
                ort.send_keys(ci)
        except TimeoutException:
            print("Es wurde nicht rechtzeitig eine Textbox für die Ortseingabe gefunden.")
            ort = ""
            
    # Find text input for the street name and 
        wait = WebDriverWait(driver, 10)
        try:
            strt = wait.until(EC.element_to_be_clickable((By.ID, street)))
            if st:
                strt.send_keys(st)
        except TimeoutException:
            print("Es wurde nicht rechtzeitig eine Textbox für die Straßennameneingabe gefunden.")
            strt = ""
        

        wait = WebDriverWait(driver, 10)
        try:
            # Wir warten nur noch darauf, dass das Element im DOM existiert (nicht zwingend klickbar ist)
            subBtn = wait.until(EC.presence_of_element_located((By.ID, submitBtn)))
            # Führe den Klick mit JavaScript aus
            driver.execute_script("arguments[0].click();", subBtn)
            print("Suche-Button wurde via JavaScript geklickt.")
            # Gib der Seite einen Moment Zeit, um die Ergebnisse zu laden
            wait = WebDriverWait(driver, 10) 
        except TimeoutException:
            print("Es wurde nicht rechtzeitig ein Submitbutton gefunden.")
            subBtn = ""
        
        # Es ist wichtig, auf die Sichtbarkeit/Klickbarkeit der Elemente zu warten,
        # besonders bei dynamischen Webseiten.
        wait = WebDriverWait(driver, 20) # Maximal 20 Sekunden warten
        
        try:
            links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, target_class_selector)))
        except TimeoutException:
            print("Keine Links mit der Klasse gefunden oder nicht rechtzeitig geladen.")
            links = []

        print(f"Anzahl gefundener Links: {len(links)}")

        link_id = None  # Ensure link_id is always defined
        for i, link_element in enumerate(links):
            try:
                link_text = link_element.text
                link_id = link_element.get_attribute("id")
                print(f"Link {i+1}: Text='{link_text}', ID='{link_id}'")

                # We don't need the document overview, the newest publications or the corporate sponsors. We only really need the current status.
                if (link_text != "DK") and (link_text != "VÖ") and (link_text != "UT") and (link_text != "SI") and (link_text != "CD") and (link_text != "HD"):
                    print(f"Versuche Link mit Text '{link_text}' und ID '{link_id}' zu klicken...")

                    # Stelle sicher, dass das Element klickbar ist
                    if link_id is not None:
                        wait.until(EC.element_to_be_clickable((By.ID, link_id)))
                        link_element.click()
                        print("Link geklickt!")
                    else:
                        print("Warnung: link_id ist None, überspringe Klick.")

                    time.sleep(1)
                    break
                    
            except Exception as e:
                print(f"Fehler beim Verarbeiten oder Klicken von Link {link_id if link_id is not None else ' unbekannt'}: {e}")

    except Exception as e:
        print(f"Ein genereller Fehler ist aufgetreten: {e}")

    finally:
        # ! Wenn die Zeile unter dieser nicht auskommentiert ist, dann muss der Browser manuell geschlossen werden.
        #input("Drücke Enter, um den Browser zu schließen...") # Zum Debuggen
        
        if 'driver' in locals():
            driver.quit()
        if Path("temp_page.html").exists():
            Path("temp_page.html").unlink()
            
        downloaded_files = list(Path(dl_path).iterdir())
        if not downloaded_files:
            print(f"Fehler: Download fehlgeschlagen. Keine Datei im Verzeichnis '{dl_path}' gefunden.")
            return # Beendet die Funktion hier, da es nichts zu verarbeiten gibt

        # --- Nur wenn Dateien da sind, geht es hier weiter ---
        print("Daten wurden heruntergeladen. Extrahieren der Geschäftsführer und Prokuristen wird gestartet...")
        pdfFileName = downloaded_files[0]
        pdfFilePath = PurePath.joinpath(dl_path, pdfFileName)
        print("Es wird versucht die Daten von " + str(pdfFilePath) + " zu laden...")
        companyData = extract_company_data_from_pdf(str(pdfFilePath))
        managers = companyData.ceos
        companyName = companyData.name
        companyAddress = companyData.address

        #todo: Hier muss dann noch die tatsächliche Interaktion mit den Daten eingebaut werden. Aktuell werden sie zu Testzwecken nur auf der Konsole ausgegeben.
        # Iteration over the resulting values to print them to console.
        if managers:  # Only take lists that are non-empty.
            print("Gefundene Personen in dieser Liste:")
            for person in managers:
                print(f"  - {person}")
        else:
            print("Keine Geschäftsführer konnten extrahiert werden!")
                    
        if companyName:            
            print("Name der Firma: " + companyName)
        else:
            print("Kein Name konnte extrahiert werden!")
            
        if companyAddress:
            print("Addresse der Firma: " + companyAddress)
        else:
            print("Kein Addresse konnte extrahiert werden!")
            
        
if __name__ == "__main__":
    print("PySel wird ausgeführt...")
    print("Wurde gecalled mit folgenden Parametern:")
    args = parse_cli_arguments()
    print(args)
    # Temporarily commented out to verify the correct data propagation without risking to cross the api threshold.
    fetch_and_download_from_bundes_api(
        args.schlagwoerter,
        args.schlagwortOptionen,
        args.sucheAehnliche,
        args.sucheGeloeschte,
        args.city,
        args.street,
        args.postCode
    )