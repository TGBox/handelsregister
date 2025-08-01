# Fork der Handelsregister BundesAPI

> Siehe originales [GitHub Projekt](https://github.com/bundesAPI/handelsregister.git).

Das Handelsregister stellt ein öffentliches Verzeichnis dar, das im Rahmen des Registerrechts Eintragungen über</br>die angemeldeten Kaufleute in einem bestimmten geografischen Raum führt.
Eintragungspflichtig sind die im HGB,</br>AktG und GmbHG abschließend aufgezählten Tatsachen oder Rechtsverhältnisse.</br>Eintragungsfähig sind weitere Tatsachen, wenn Sinn und Zweck des Handelsregisters die Eintragung erfordern</br>und für ihre Eintragung ein erhebliches Interesse des Rechtsverkehrs besteht.

Die Einsichtnahme in das Handelsregister sowie in die dort eingereichten Dokumente ist daher</br>gemäß § 9 Abs. 1 HGB jeder und jedem zu Informationszwecken gestattet, wobei es unzulässig ist,</br>mehr als **60 Abrufe pro Stunde** zu tätigen (vgl. [Nutzungsordnung](https://www.handelsregister.de/rp_web/information.xhtml)).</br>Die Recherche nach einzelnen Firmen, die Einsicht in die Unternehmensträgerdaten</br>und die Nutzung der Handelsregisterbekanntmachungen ist kostenfrei möglich.

**Achtung:** Das Registerportal ist regelmäßig das Ziel automatisierter Massenabfragen.</br>Den Ausführungen der [FAQs](https://www.handelsregister.de/rp_web/information.xhtml) zufolge erreiche die Frequenz dieser Abfragen sehr häufig eine Höhe,</br>bei der die Straftatbestände der Rechtsnormen §§303a, b StGB vorliege.</br>Mehr als **60 Abrufe pro Stunde** widersprechen der Nutzungsordnung.

## Handelsregister

### Datenstruktur

**_URL:_** [Handelsregister Webportal](https://www.handelsregister.de/rp_web/erweitertesuche.xhtml)

Das gemeinsame Registerportal der Länder ermöglicht jeder und jedem die Recherche nach einzelnen Firmen zu Informationszwecken.</br>Einträge lassen sich dabei über verschiedene Parameter im Body eines POST-request filtern:

**Parameter:** _schlagwoerter_ (Optional)

Schlagwörter (z.B. Test). Zulässige Platzhalterzeichen sind für die Suche nach genauen Firmennamen</br>(siehe Parameter _schlagwortOptionen_) \* und ? - wobei das Sternchen für beliebig viele (auch kein) Zeichen steht,</br>das Fragezeichen hingegen für genau ein Zeichen.

**Parameter:** _schlagwortOptionen_ (Optional)

- 1
- 2
- 3

Schlagwortoptionen: 1=alle Schlagwörter enthalten; 2=mindestens ein Schlagwort enthalten; 3=den genauen Firmennamen enthalten.

**Parameter:** _suchOptionenAehnlich_ (Optional)

- true

true=ähnlich lautende Schlagwörter enthalten.</br>Unter der Ähnlichkeitssuche ist die sogenannte phonetische Suche zu verstehen.</br>Hierbei handelt es sich um ein Verfahren, welches Zeichenketten und ähnlich ausgesprochene Worte als identisch erkennt.</br>Grundlage für die Vergleichsoperation ist hier die insbesondere im Bereich der öffentlichen Verwaltung angewandte sogenannte Kölner Phonetik.

**Parameter:** _suchOptionenGeloescht_ (Optional)

- true

true=auch gelöschte Formen finden.

**Parameter:** _suchOptionenNurZNneuenRechts_ (Optional)

- true

true=nur nach Zweigniederlassungen neuen Rechts suchen.

**Parameter:** _btnSuche_ (Optional)

- Suchen

Button "Suchen"

**Parameter:** _suchTyp_ (Optional)

- n
- e

Suchtyp: n=normal; e=extended.</br>Die normale Suche erlaubt eine Suche über den gesamten Registerdatenbestand der Länder anhand einer überschaubaren Anzahl von Suchkriterien.</br>Die erweiterte Suche bietet neben den Auswahlkriterien der normalen Suche die selektive Suche in den Datenbeständen ausgewählter Länder,</br>die Suche nach Rechtsformen und die Suche nach Adressen an.

**Parameter:** _ergebnisseProSeite_ (Optional)

- 10
- 25
- 50
- 100

Ergebnisse pro Seite.

**Parameter:** _niederlassung_ (Optional)

Niederlassung / Sitz.</br>Zulässige Platzhalterzeichen sind \* und ? - wobei das Sternchen für beliebig viele (auch kein) Zeichen steht,</br>das Fragezeichen hingegen für genau ein Zeichen.

**Parameter:** _bundeslandBW_ (Optional)

- on

Einträge aus Baden-Württemberg

**Parameter:** _bundeslandBY_ (Optional)

- on

Einträge aus Bayern

**Parameter:** _bundeslandBE_ (Optional)

- on

Einträge aus Berlin

**Parameter:** _bundeslandBR_ (Optional)

- on

Einträge aus Bradenburg

**Parameter:** _bundeslandHB_ (Optional)

- on

Einträge aus Bremen

**Parameter:** _bundeslandHH_ (Optional)

- on

Einträge aus Hamburg

**Parameter:** _bundeslandHE_ (Optional)

- on

Einträge aus Hessen

**Parameter:** _bundeslandMV_ (Optional)

- on

Einträge aus Mecklenburg-Vorpommern

**Parameter:** _bundeslandNI_ (Optional)

- on

Einträge aus Niedersachsen

**Parameter:** _bundeslandNW_ (Optional)

- on

Einträge aus Nordrhein-Westfalen

**Parameter:** _bundeslandRP_ (Optional)

- on

Einträge aus Rheinland-Pfalz

**Parameter:** _bundeslandSL_ (Optional)

- on

Einträge aus Saarland

**Parameter:** _bundeslandSN_ (Optional)

- on

Einträge aus Sachsen

**Parameter:** _bundeslandST_ (Optional)

- on

Einträge aus Sachsen-Anhalt

**Parameter:** _bundeslandSH_ (Optional)

- on

Einträge aus Schleswig-Holstein

**Parameter:** _bundeslandTH_ (Optional)

- on

Einträge aus Thüringen

**Parameter:** _registerArt_ (Optional)

- alle
- HRA
- HRB
- GnR
- PR
- VR

Registerart (Angaben nur zur Hauptniederlassung): alle; HRA; HRB; GnR; PR; VR.

**Parameter:** _registerNummer_ (Optional)

Registernummer (Angaben nur zur Hauptniederlassung).

**Parameter:** _registerGericht_ (Optional)

Registergericht (Angaben nur zur Hauptniederlassung). Beispielsweise D3201 für Ansbach

**Parameter:** _rechtsform_ (Optional)

- 1
- 2
- 3
- 4
- 5
- 6
- 7
- 8
- 9
- 10
- 12
- 13
- 14
- 15
- 16
- 17
- 18
- 19
- 40
- 46
- 48
- 49
- 51
- 52
- 53
- 54
- 55

Rechtsform (Angaben nur zur Hauptniederlassung).</br>1=Aktiengesellschaft; 2=eingetragene Genossenschaft; 3=eingetragener Verein;</br>4=Einzelkauffrau; 5=Einzelkaufmann; 6=Europäische Aktiengesellschaft (SE);</br>7=Europäische wirtschaftliche Interessenvereinigung; 8=Gesellschaft mit beschränkter Haftung; 9=HRA Juristische Person;</br>10=Kommanditgesellschaft; 12=Offene Handelsgesellschaft; 13=Partnerschaft; 14=Rechtsform ausländischen Rechts GnR;</br>15=Rechtsform ausländischen Rechts HRA; 16=Rechtsform ausländischen Rechts HRb; 17=Rechtsform ausländischen Rechts PR;</br>18=Seerechtliche Gesellschaft; 19=Versicherungsverein auf Gegenseitigkeit; 40=Anstalt öffentlichen Rechts;</br>46=Bergrechtliche Gesellschaft; 48=Körperschaft öffentlichen Rechts; 49= Europäische Genossenschaft (SCE);</br>51=Stiftung privaten Rechts; 52=Stiftung öffentlichen Rechts; 53=HRA sonstige Rechtsformen;</br>54=Sonstige juristische Person; 55=Einzelkaufmann/Einzelkauffrau

**Parameter:** _postleitzahl_ (Optional)

Postleitzahl (Angaben nur zur Hauptniederlassung). Beispielsweise 90537 für Feucht.</br>Zulässige Platzhalterzeichen sind \* und ? - wobei das Sternchen für beliebig viele (auch kein) Zeichen steht,</br>das Fragezeichen hingegen für genau ein Zeichen.

**Parameter:** _ort_ (Optional)

Ort (Angaben nur zur Hauptniederlassung). Beispielsweise Feucht.</br>Zulässige Platzhalterzeichen sind \* und ? - wobei das Sternchen für beliebig viele (auch kein) Zeichen steht,</br>das Fragezeichen hingegen für genau ein Zeichen.

**Parameter:** _strasse_ (Optional)

Straße (Angaben nur zur Hauptniederlassung). Beispielsweise Teststraße 2.</br>Zulässige Platzhalterzeichen sind \* und ? - wobei das Sternchen für beliebig viele (auch kein) Zeichen steht,</br>das Fragezeichen hingegen für genau ein Zeichen.

---

### Installation with poetry

Example installation and execution with [poetry](https://python-poetry.org/):

```bash
git clone https://github.com/TGBox/handelsregister.git
cd handelsregister
poetry install
poetry run python pysil.py -s "deutsche bahn" -so all
```

Run tests:

```bash
poetry run python -m pytest
```

### Command-line Interface

> Das CLI ist momentan noch _WIP_.

```bash
usage: handelsregister.py [-h] [-d] [-f] -s SCHLAGWOERTER [-so {all,min,exact}]

A handelsregister CLI

options:
  -h, --help            show this help message and exit
  -d, --debug           Enable debug mode and activate logging
  -f, --force           Force a fresh pull and skip the cache
  -s SCHLAGWOERTER, --schlagwoerter SCHLAGWOERTER
                        Search for the provided keywords
  -so {all,min,exact}, --schlagwortOptionen {all,min,exact}
                        Keyword options: all=contain all keywords; min=contain at least one
                        keyword; exact=contain the exact company name.
```
