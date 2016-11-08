
# Testing `collection.py`

The following tutorial shows how to use the collection module of Dariah-Topics.

1. Prearrangement
----
First you need to import the collection module so your ipython notebook has access to its functions and classes.
As second step we set paths for a test corpus consisting of plain text files and one consisting of annotated text preprocessed with several NLP-Tools in form of csv files (if you have questions concerning the format go to: https://github.com/DARIAH-DE/DARIAH-DKPro-Wrapper/blob/master/doc/tutorial.adoc). 


```python
import collection
```


```python
path_txt = "corpus_txt"
path_csv = "corpus_csv"
```

2. Creating list of filenames (plain text and csv files)
----
The following function is used to normalize path names so non-uniform text files will be processable by the module. It is possible to add an additional argument "ext" where you can specify an extension ('csv' in this case). The CSV


```python
doclist_txt = collection.create_document_list(path_txt)
doclist_txt[:5]
```




    ['corpus_txt\\Doyle_AScandalinBohemia.txt',
     'corpus_txt\\Doyle_AStudyinScarlet.txt',
     'corpus_txt\\Doyle_TheHoundoftheBaskervilles.txt',
     'corpus_txt\\Doyle_TheSignoftheFour.txt',
     'corpus_txt\\Howard_GodsoftheNorth.txt']




```python
doclist_csv = collection.create_document_list(path_csv, 'csv')
doclist_csv[:5]
```




    ['corpus_csv\\Doyle_AStudyinScarlet.txt.csv',
     'corpus_csv\\Doyle_TheHoundoftheBaskervilles.txt.csv',
     'corpus_csv\\Doyle_TheSignoftheFour.txt.csv',
     'corpus_csv\\Howard_GodsoftheNorth.txt.csv',
     'corpus_csv\\Howard_SchadowsinZamboula.txt.csv']



3. Load the corpora
----
By using the "read\_from\_"-functions we create a generator object which provides a memory efficient way to handle bigger corpora.


```python
corpus_txt = collection.read_from_txt(doclist_txt)
```


```python
corpus_csv = collection.read_from_csv(doclist_csv)
```

4. Segmenting text
----
An important part of pre-processing in Topic modelling is segmenting the the texts in 'chunks'. The arguments of the function are for the targeted corpus and the size of the 'chunks' in words. Depending on the languange and type of text results can vary widely in quality.


```python
segments = collection.segmenter(corpus_txt, 1000)
next(segments)
```




    "A SCANDAL IN BOHEMIA\n\nA. CONAN DOYLE\n\n\nI\n\nTo Sherlock Holmes she is always _the_ woman. I have seldom heard him\nmention her under any other name. In his eyes she eclipses and\npredominates the whole of her sex. It was not that he felt any emotion\nakin to love for Irene Adler. All emotions, and that one particularly,\nwere abhorrent to his cold, precise but admirably balanced mind. He was,\nI take it, the most perfect reasoning and observing machine that the\nworld has seen; but as a lover, he would have placed himself in a false\nposition. He never spoke of the softer passions, save with a gibe and a\nsneer. They were admirable things for the observer--excellent for\ndrawing the veil from men's motives and actions. But for the trained\nreasoner to admit such intrusions into his own delicate and finely\nadjusted temperament was to introduce a distracting factor which might\nthrow a doubt upon all his mental results. Grit in a sensitive\ninstrument, or a crack in one of his own high-power lenses, w"



5. Filtering text using POS-Tags
----
Another way to preprocess the text is by filtering by POS-Tags and using lemmata (in this case only adjectives, verbs and nouns are filterable). The annotated csv-file we provide in this example is already enriched with this kind of information. 


```python
lemmas = collection.filter_POS_tags(corpus_csv)
next(lemmas)[:10]
```




    107     infrequent
    147           fine
    149          thick
    175          broad
    225          solid
    291          least
    330    unfortunate
    344     accidental
    390     successful
    392        elderly
    Name: Lemma, dtype: object



6. Visualization
----
Simple get-functions are implemented for visualization tasks. In this case the get_labels-function extracts the titles of the corpus files we loaded above.


```python
labels = collection.get_labels(doclist_txt)
list(labels)
```




    ['Doyle_AScandalinBohemia.txt',
     'Doyle_AStudyinScarlet.txt',
     'Doyle_TheHoundoftheBaskervilles.txt',
     'Doyle_TheSignoftheFour.txt',
     'Howard_GodsoftheNorth.txt',
     'Howard_SchadowsinZamboula.txt',
     'Howard_ShadowsintheMoonlight.txt',
     'Howard_TheDevilinIron.txt',
     'Kipling_TheEndofthePassage.txt',
     'Kipling_TheJungleBook.txt',
     'Kipling_ThyServantaDog.txt',
     'Lovecraft_AttheMountainofMadness.txt',
     'Lovecraft_TheShunnedHouse.txt',
     'Poe_EurekaAProsePoem.txt',
     'Poe_TheCaskofAmontillado.txt',
     'Poe_TheMasqueoftheRedDeath.txt',
     'Poe_ThePurloinedLetter.txt']


