# Ergebnisse vom Arbeitstreffen am 29.9.16

##﻿Allgemein:


Alle Funktionen die etwas Inhaltliches machen, sollen auf Iterables (statt Listen) arbeiten, getrennt von Dateioperationen ✓

Einzeldateischreiben vermeiden, Speicherfunktionen können default-werte (für Dateinamen) haben. Dateien/Folder sollen dynamisch benannt werden 

Split- und Join-Operationen vermeiden

Nicht von Leerzeichen als Trenner ausgehen, sondern mit /n trennen.

Generatoren zwischen den Funktionen hin und herreichen ✓

Prints durch Logging ersetzen,  (verschiedene Loglevels, z.b. Log-Error) → Severin ✓

TimeStamps für alle Funktionen (mit Logging) → Severin? ✓

Statt glob.glob – Liste von Dateinamen, die die Reihenfolge im Ordner behält ✓

Globale Variablen - Kommandozeilenparameter (Arg.path)


#Cophi-Toolbox-Funktionen


#### makeRemoveLists(mycounter : Counter) -> set -> Sina

- Counter schneller als Series?, Counter als Series ausgeben?

- Funktion aufteilen in:

	removeStopwords()

	remove Hapax ()

#### splitFiles(): -> Philip ✓

- eigene Funktion für Segmentierung

#### readDKPRoWrapperFiles 

- Csv in Dataframe


#### getPOSTags(): -> Philip 

- Filterung der POS-Tags 

- auf Gruppierung verzichten. CPOS-Feld beim Einlesen der CSV und mit Pandas Methoden zur Filterung nutzen. (Dann kann Funktion vor der Segmentierung aufgerufen werden).

- Aus verbleibender Tabelle eine Tokenliste machen und dann Modell übergeben



#Topic - Funktionen


#### makeCorpusFile(inDir : str,  outFileName : str) -> None


#### readFromCorpusFile(corpusfile : str, outfolder : str)


- Umbennen


#### makeCounter(path : str) -> Counter -> Sina

	
- Keine eigene Funktion f-> Konstruktor von Counter nehmen


#### gensimVisualisierungen → Sina


Gensim-Funktion mit Übergabeparameter und Default-Werten (braucht jemand Corpus ohne LDA-Model zu fitten)

- Dictionary
- Corpus

unabhängig vom Model

- Convience-Funktion, zusätzlich anbieten, die alle Gensim-Funktionen anbietet.






