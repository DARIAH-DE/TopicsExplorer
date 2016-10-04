# Funktionenliste


## convert_corpfile


#### makeCorpusFile(inDir : str,  outFileName : str) -> None


Der Input ist ein Pfad zum Korpus-Ordner.
Der Inhalt aller Dokumente in diesem Ordner wird in eine einzelne Textdatei (name.txt) geschrieben.
Die Textdatei enthält am Ende den Inhalt eines jeden Dokuments in einer Zeile.
Die Letzte Zeile der Textdatei ist eine Liste der Dateinamen (muss für den weiteren Gebrauch beachtet ODER anders gelöst werden).


#### readFromCorpusFile(corpusfile : str, outfolder : str) -> None


Der Input ist der Dateiname eines Korpus-Datei (corpus.mm? - das mit makeCorpusFile erstellt wurde). Alle Zeilen und die Dateinamen aus der letzten Zeile werden ausgelesen.
Es wird ein Ordner erstellt (der durch die Variable outfolder benannt wird), in dem für jeden Dateinamen aus der letzten Zeile der Korpus-Datei ein Dokument erstellt. Der jeweilige Inhalt wird in die dazugehörigen Dokumente geschrieben.
Die letzte Zeile der Textdatei (name.txt) wird - außer zum Erstellen der Dateinamen - ignoriert.


#### ANWENDUNG:


* Aus der Korpus-Datei (corpus.mm?) lassen sich später Dokumente mit der MyCorpus class (siehe lda2-Skript) einzeln in den doc2bow Prozess streamen (schont Arbeitsspeicher).
* Die Entfernung von Stopwörtern und Hapax Legomena gestaltet sich sehr schnell und einfach (siehe remove_sw_hl).


## remove_sw_hl


#### makeCounter(path : str) -> Counter


Der Input ist der Pfad zur Korpusdatei (corpus.mm? - siehe makeCorpusfile in convert_corpfile).
Erstellt einen Counter (siehe collections.Counter) mit den Worthäufigkeiten in der Korpusdatei.


(nur nebenbei - verstehe gerade den Funktionsnamen nicht?)
#### makeRemoveLists(mycounter : Counter) -> set, set


Der Input ist der Counter, der mit makeCounter erstellt wurde.
Erstellt ein Set mit den Hapax Legomena des Korpus.
Erstellt Set mit den Stopwörtern (VORLÄUFIG Stopwort =  ein Wort, das über 1% des Korpus ausmacht).


#### removestuff (inpath : str, outpath : str) -> None


Funktion wird auf jeden Fall neu benannt.
Variable inpath ist der Pfad zur Korpus-Datei.
Mit der Variable outpath wird der Name für die output Datei gewählt.
Ruft die Funtionen makeCounter und makeRemoveLists auf.
Schreibt neue Datei (outpath) als Korpus-Datei, nachdem HL und Stopwörter entfernt wurden.


## lda2

Anmerkung generell:

* Time Stamps behalten?


Übergabeparameter (außer preprocessing):


SIEHE lda.model


#### stopwords


Tetxtdatei mit ein Stopwort pro Zeile (\n getrennt).

ANMERKUNG:
* Sollen Stopwortlisten verwendet werden oder sollen die Stopwörter "statistisch" Korpus-baisert herausgenommen werden? (siehe remove_sw_hl)
* Funktion nicht verwenden, wenn Dateien mit dem DKPro-Wrapper getaggt wurden.


#### preprocessing


Übergabeparameter:


* path = Pfad zum Korpus
* columns = Spaltennamen aus DKPro .csv-Dateien
* pos_tags = Liste von POS-Tags entsprechend der Bezeichnung in der POS Spalte in DKPro .csv-Dateien
* doc_size(in words) = default : 1000 für Segmentierung
* doc_split = Value 0 oder 1; 0 = nicht splitten, 1 = splitten


Liest einen Ordner mit DKPro .csv-Dateien ein. Filtert Dokumente nach POS Tags. Schreibt einen Ordner mit Dokumenten, in denen nur die gewählten POS Tags übrig sind.


ANMERKUNG:


* POS-Tags ODER Stopwords
* Key Error bei POS abfangen (wenn eine Datei nicht alle  POS_Tags enthält)
* Override? Unterscheiden zwischen .csv oder .txt
* Kapselung von POS und anderem preprocessing Schritten?


#### makeMakeDocLabels(path)


Erzeugt eine Liste mit Dateinamen die als Label später verwendet werden


ANMERKUNG:

* glob verwenden? Unterordner-Verwaltung?


#### MyCorpus(object) class


Streamt aus der Korpus-Datei um Arbeitsspeicher zu schonen.


#### Allgemeine ANMERKUNGEN


* print-Statements behalten?
* show topic print statement?
* output formatierung? bsp: no_of_topics im Dateinamen
* Kapselung der weiteren Funktionen
* Input Handling


## heatmap


ANMERKUNGEN:

* Auflösung von heatmap?
* Plot-Größe dynamisch machen?
* Hinweis darauf, dass die Heatmap sich nicht gut für große Dateimengen eignet?
* Save Funktion kapseln?


#### doc_topic_matrix


Dokumente gegen Topics. Die Werte beschreiben die Verteilung der Topics im jeweiligen Dokument.


ANMERKUNG:

* Input Handling?


## interactive


ANMERKUNGEN:


* Time Stamps behalten?
* Output Formate?
* Save Funktion kapseln?
* Input Handling (sys.argv) Beispiel für andere Funktionen?

