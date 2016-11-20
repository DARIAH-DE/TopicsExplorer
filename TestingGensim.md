
# Testing `collection.py`
The following tutorial shows how to use the `collection` module of DARIAH-Topics.

## 1. Prearrangement
First you need to import the collection module so your IPython notebook has access to its functions and classes. As second step we set paths for a test corpus consisting of plain text files and one consisting of annotated text preprocessed with several NLP-Tools in form of CSV files (if you have questions concerning the format, click [here](https://github.com/DARIAH-DE/DARIAH-DKPro-Wrapper/blob/master/doc/tutorial.adoc)).


```python
import collection
```


```python
path_txt = "corpus_txt"
path_csv = "corpus_csv"
```

## 2. Creating list of filenames (plain text and csv files)
The following function is used to normalize path names so non-uniform text files will be processable by the module. It is possible to add an additional argument `ext` where you can specify an extension.



```python
doclist_txt = collection.create_document_list(path_txt)
doclist_txt[:5]
```

    20-Nov-2016 17:52:27 INFO collection: Creating document list from TXT files ...
    20-Nov-2016 17:52:27 DEBUG collection: 17 entries in document list.





    ['corpus_txt/Doyle_AScandalinBohemia.txt',
     'corpus_txt/Doyle_AStudyinScarlet.txt',
     'corpus_txt/Doyle_TheHoundoftheBaskervilles.txt',
     'corpus_txt/Doyle_TheSignoftheFour.txt',
     'corpus_txt/Howard_GodsoftheNorth.txt']




```python
doclist_csv = collection.create_document_list(path_csv, 'csv')
doclist_csv[:5]
```

    20-Nov-2016 17:52:29 INFO collection: Creating document list from CSV files ...
    20-Nov-2016 17:52:29 DEBUG collection: 16 entries in document list.





    ['corpus_csv/Doyle_AStudyinScarlet.txt.csv',
     'corpus_csv/Doyle_TheHoundoftheBaskervilles.txt.csv',
     'corpus_csv/Doyle_TheSignoftheFour.txt.csv',
     'corpus_csv/Howard_GodsoftheNorth.txt.csv',
     'corpus_csv/Howard_SchadowsinZamboula.txt.csv']



## 3. Getting document labels


```python
labels = collection.get_labels(doclist_txt)
list(labels)[:5]
```

    20-Nov-2016 17:52:32 INFO collection: Creating document labels ...
    20-Nov-2016 17:52:32 DEBUG collection: Document labels available.





    ['Doyle_AScandalinBohemia.txt',
     'Doyle_AStudyinScarlet.txt',
     'Doyle_TheHoundoftheBaskervilles.txt',
     'Doyle_TheSignoftheFour.txt',
     'Howard_GodsoftheNorth.txt']



## 3. Load the corpora
By using the `read_from()`-functions we create a generator object which provides a memory efficient way to handle bigger corpora.


```python
corpus_txt = collection.read_from_txt(doclist_txt)
```


```python
corpus_csv = collection.read_from_csv(doclist_csv)
```

## 4. Segmenting text
An important part of pre-processing in Topic Modeling is segmenting the the texts in 'chunks'. The arguments of the function are for the targeted corpus and the size of the 'chunks' in words. Depending on the languange and type of text results can vary widely in quality.


```python
segments = collection.segmenter(corpus_txt, 1000)
next(segments)
```

    20-Nov-2016 17:52:40 DEBUG collection: Accessing TXT document ...
    20-Nov-2016 17:52:40 INFO collection: Segmenting document ...
    20-Nov-2016 17:52:40 DEBUG collection: Segment has a length of 1000 characters.





    "A SCANDAL IN BOHEMIA\n\nA. CONAN DOYLE\n\n\nI\n\nTo Sherlock Holmes she is always _the_ woman. I have seldom heard him\nmention her under any other name. In his eyes she eclipses and\npredominates the whole of her sex. It was not that he felt any emotion\nakin to love for Irene Adler. All emotions, and that one particularly,\nwere abhorrent to his cold, precise but admirably balanced mind. He was,\nI take it, the most perfect reasoning and observing machine that the\nworld has seen; but as a lover, he would have placed himself in a false\nposition. He never spoke of the softer passions, save with a gibe and a\nsneer. They were admirable things for the observer--excellent for\ndrawing the veil from men's motives and actions. But for the trained\nreasoner to admit such intrusions into his own delicate and finely\nadjusted temperament was to introduce a distracting factor which might\nthrow a doubt upon all his mental results. Grit in a sensitive\ninstrument, or a crack in one of his own high-power lenses, w"



## 5. Filtering text using POS-Tags
Another way to preprocess the text is by filtering by POS-Tags and using lemmas (in this case only adjectives, verbs and nouns are filterable). The annotated CSV-file we provide in this example is already enriched with this kind of information.



```python
lemmas = collection.filter_POS_tags(corpus_csv)
next(lemmas)[:5]
```

    20-Nov-2016 17:52:48 INFO collection: Accessing CSV documents ...
    20-Nov-2016 17:52:48 INFO collection: Accessing ['ADJ', 'V', 'NN'] lemmas ...





    37    typographical
    56          textual
    59           square
    72              old
    75             such
    Name: Lemma, dtype: object



# 6. Creating a counter to use `find_stopwords()` and `find_hapax()`.


```python
counter = collection.calculate_term_frequency(corpus_txt)
```

    20-Nov-2016 17:52:51 INFO collection: Calculating term frequency ...
    20-Nov-2016 17:52:51 DEBUG collection: Accessing TXT document ...
    20-Nov-2016 17:52:51 DEBUG collection: Term frequency calculated.
    20-Nov-2016 17:52:51 DEBUG collection: Accessing TXT document ...
    20-Nov-2016 17:52:51 DEBUG collection: Term frequency calculated.
    20-Nov-2016 17:52:51 DEBUG collection: Accessing TXT document ...
    20-Nov-2016 17:52:51 DEBUG collection: Term frequency calculated.
    20-Nov-2016 17:52:51 DEBUG collection: Accessing TXT document ...
    20-Nov-2016 17:52:51 DEBUG collection: Term frequency calculated.
    20-Nov-2016 17:52:51 DEBUG collection: Accessing TXT document ...
    20-Nov-2016 17:52:51 DEBUG collection: Term frequency calculated.
    20-Nov-2016 17:52:51 DEBUG collection: Accessing TXT document ...
    20-Nov-2016 17:52:51 DEBUG collection: Term frequency calculated.
    20-Nov-2016 17:52:51 DEBUG collection: Accessing TXT document ...
    20-Nov-2016 17:52:51 DEBUG collection: Term frequency calculated.
    20-Nov-2016 17:52:51 DEBUG collection: Accessing TXT document ...
    20-Nov-2016 17:52:51 DEBUG collection: Term frequency calculated.
    20-Nov-2016 17:52:51 DEBUG collection: Accessing TXT document ...
    20-Nov-2016 17:52:51 DEBUG collection: Term frequency calculated.
    20-Nov-2016 17:52:51 DEBUG collection: Accessing TXT document ...
    20-Nov-2016 17:52:52 DEBUG collection: Term frequency calculated.
    20-Nov-2016 17:52:52 DEBUG collection: Accessing TXT document ...
    20-Nov-2016 17:52:52 DEBUG collection: Term frequency calculated.
    20-Nov-2016 17:52:52 DEBUG collection: Accessing TXT document ...
    20-Nov-2016 17:52:52 DEBUG collection: Term frequency calculated.
    20-Nov-2016 17:52:52 DEBUG collection: Accessing TXT document ...
    20-Nov-2016 17:52:52 DEBUG collection: Term frequency calculated.
    20-Nov-2016 17:52:52 DEBUG collection: Accessing TXT document ...
    20-Nov-2016 17:52:52 DEBUG collection: Term frequency calculated.
    20-Nov-2016 17:52:52 DEBUG collection: Accessing TXT document ...
    20-Nov-2016 17:52:52 DEBUG collection: Term frequency calculated.
    20-Nov-2016 17:52:52 DEBUG collection: Accessing TXT document ...
    20-Nov-2016 17:52:52 DEBUG collection: Term frequency calculated.



```python
#
# Kopie des ursprünglichen Counters um im Testvorgang den Counter zurückzusetzen
# Auf diese Weise muss der Counter nicht jedes Mal erneut erstellt werden,
# sondern kann hier zurückgesetzt werden
#

countercopy = counter.copy()
```

## 7. Find stopwords


```python
stopwords = collection.find_stopwords(countercopy, 50)
stopwords[:5]
```

    20-Nov-2016 17:52:57 INFO collection: Finding stopwords ...
    20-Nov-2016 17:52:57 DEBUG collection: 50 stopwords found.





<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>word</th>
      <th>freq</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>the</td>
      <td>21357</td>
    </tr>
    <tr>
      <th>1</th>
      <td>of</td>
      <td>11614</td>
    </tr>
    <tr>
      <th>2</th>
      <td>and</td>
      <td>11040</td>
    </tr>
    <tr>
      <th>3</th>
      <td>to</td>
      <td>8516</td>
    </tr>
    <tr>
      <th>4</th>
      <td>a</td>
      <td>7652</td>
    </tr>
  </tbody>
</table>
</div>



## 8. Find hapax legomena


```python
hapax = collection.find_hapax(countercopy)
hapax[:5]
```

    20-Nov-2016 17:53:03 INFO collection: Find hapax legomena ...
    20-Nov-2016 17:53:04 DEBUG collection: 26096 hapax legomena found.





<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>word</th>
      <th>freq</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>jewelled</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Beach.</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>scaling</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3</th>
      <td>muffle</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>"Fear</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



## 9. Remove stopwords


```python
dict_without_stopwords = collection.remove_filtered_words(countercopy, stopwords)
```

    20-Nov-2016 17:53:13 INFO collection: Removing stopwords ...
    20-Nov-2016 17:53:13 DEBUG collection: 50 words removed.



```python
print("Länge des counters: ", len(counter))
print("Länge des dicts nachdem Stopwords entfernt wurden: ", len(dict_without_stopwords))
print("25 MFWs von counter:\n", counter.most_common(25), "\n")
print("25 MFWs nachdem stopwords entfernt wurden:\n", dict_without_stopwords.most_common(25))
print("Anzahl der Wörter, die genau ein Mal vorkommen: ",len([count for count in dict_without_stopwords.values() if count == 1]))
```

    Länge des counters:  43989
    Länge des dicts nachdem Stopwords entfernt wurden:  43939
    25 MFWs von counter:
     [('the', 21357), ('of', 11614), ('and', 11040), ('to', 8516), ('a', 7652), ('in', 5585), ('I', 5393), ('that', 4479), ('was', 4211), ('he', 3610), ('his', 3503), ('had', 2816), ('is', 2768), ('with', 2767), ('as', 2733), ('it', 2457), ('for', 2282), ('at', 2272), ('have', 2171), ('which', 2063), ('we', 1963), ('you', 1905), ('not', 1902), ('my', 1833), ('be', 1738)] 
    
    25 MFWs nachdem stopwords entfernt wurden:
     [('up', 871), ('into', 860), ('so', 849), ('will', 841), ('there', 819), ('their', 802), ('It', 789), ('when', 725), ('very', 694), ('more', 680), ('some', 666), ('she', 652), ('if', 631), ('has', 628), ('who', 623), ('about', 622), ('down', 613), ('what', 608), ('We', 601), ('than', 585), ('any', 584), ('us', 565), ('your', 561), ('over', 540), ('like', 528)]
    Anzahl der Wörter, die genau ein Mal vorkommen:  26096


## 9. Remove hapax legomena


```python
dict_without_hapax = collection.remove_filtered_words(countercopy, hapax)
```

    20-Nov-2016 17:53:20 INFO collection: Removing stopwords ...
    20-Nov-2016 17:53:20 DEBUG collection: 26096 words removed.



```python
print("Länge des counters: ", len(counter))
print("Länge des dicts nachdem Hapax entfernt wurden: ",len(dict_without_hapax))
print("Anzahl der Wörter, die öfter als ein Mal vorkommen: ", len([count for count in dict_without_hapax.values() if count > 1]))
print("Anzahl der Wörter, die genau ein Mal vorkommen: ",len([count for count in dict_without_hapax.values() if count == 1]))
```

    Länge des counters:  43989
    Länge des dicts nachdem Hapax entfernt wurden:  17843
    Anzahl der Wörter, die öfter als ein Mal vorkommen:  17843
    Anzahl der Wörter, die genau ein Mal vorkommen:  0


## 9. Visualization
Simple get-functions are implemented for visualization tasks. In this case the get_labels-function extracts the titles of the corpus files we loaded above.



```python
lda_model = 'out_easy/corpus.lda'
corpus = 'out_easy/corpus.mm'
dictionary = 'out_easy/corpus.dict'
doc_labels = 'out_easy/corpus_doclabels.txt'
interactive  = False

vis = collection.Visualization(lda_model, corpus, dictionary, doc_labels, interactive)
```

    20-Nov-2016 17:53:27 INFO collection: Accessing corpus ...
    20-Nov-2016 17:53:27 INFO gensim.corpora.indexedcorpus: loaded corpus index from out_easy/corpus.mm.index
    20-Nov-2016 17:53:27 INFO gensim.matutils: initializing corpus reader from out_easy/corpus.mm
    20-Nov-2016 17:53:27 INFO gensim.matutils: accepted corpus with 17 documents, 514 features, 4585 non-zero entries
    20-Nov-2016 17:53:27 DEBUG collection: Corpus available.
    20-Nov-2016 17:53:27 INFO collection: Accessing model ...
    20-Nov-2016 17:53:27 INFO gensim.utils: loading LdaModel object from out_easy/corpus.lda
    20-Nov-2016 17:53:27 INFO gensim.utils: loading id2word recursively from out_easy/corpus.lda.id2word.* with mmap=None
    20-Nov-2016 17:53:27 INFO gensim.utils: setting ignored attribute state to None
    20-Nov-2016 17:53:27 INFO gensim.utils: setting ignored attribute dispatcher to None
    20-Nov-2016 17:53:27 INFO gensim.utils: loading LdaModel object from out_easy/corpus.lda.state
    20-Nov-2016 17:53:27 DEBUG collection: Model available.
    20-Nov-2016 17:53:27 DEBUG collection: :param: interactive == False.
    20-Nov-2016 17:53:27 INFO collection: Accessing doc_labels ...
    20-Nov-2016 17:53:27 DEBUG collection: doc_labels accessed.
    20-Nov-2016 17:53:27 DEBUG collection: 29 doc_labels available.
    20-Nov-2016 17:53:27 DEBUG collection: Corpus, model and doc_labels available.


It is not possible to run `save_heatmap()` before `make_heatmap()`.


```python
vis.save_heatmap("./visualizations/heatmap")
```

    20-Nov-2016 17:53:31 INFO collection: Saving heatmap figure...
    20-Nov-2016 17:53:31 ERROR collection: Run make_heatmap() before save_heatmp()



    ---------------------------------------------------------------------------

    AttributeError                            Traceback (most recent call last)

    <ipython-input-20-27d29aa95e9c> in <module>()
    ----> 1 vis.save_heatmap("./visualizations/heatmap")
    

    /Users/severin/Desktop/Topics/collection.py in save_heatmap(self, path, filename, ext, dpi)
        367         log.info("Saving heatmap figure...")
        368         try:
    --> 369             self.heatmap_vis.savefig(os.path.join(path, filename + '.' + ext), dpi=dpi)
        370             log.debug("Heatmap figure available at %s/%s.%s", path, filename, ext)
        371         except AttributeError:


    AttributeError: 'Visualization' object has no attribute 'heatmap_vis'



```python
vis.make_heatmap()
```

    20-Nov-2016 17:53:35 INFO collection: Accessing topic distribution ...
    20-Nov-2016 17:53:35 DEBUG collection: Topic distribution available.
    20-Nov-2016 17:53:35 INFO collection: Accessing topic probability ...
    20-Nov-2016 17:53:35 DEBUG collection: Topic probability available.
    20-Nov-2016 17:53:35 INFO collection: Accessing plot labels ...
    20-Nov-2016 17:53:35 DEBUG collection: 10 plot labels available.
    20-Nov-2016 17:53:35 INFO collection: Creating heatmap figure ...
    20-Nov-2016 17:53:35 DEBUG collection: Heatmap figure available.



```python
vis.save_heatmap("./visualizations/heatmap")
```

    20-Nov-2016 17:53:37 INFO collection: Saving heatmap figure...
    20-Nov-2016 17:53:37 DEBUG collection: Heatmap figure available at ./visualizations/heatmap/heatmap.png



```python
vis = collection.Visualization(lda_model, corpus, dictionary, doc_labels, interactive=True)
```

    20-Nov-2016 17:53:38 INFO collection: Accessing corpus ...
    20-Nov-2016 17:53:38 INFO gensim.corpora.indexedcorpus: loaded corpus index from out_easy/corpus.mm.index
    20-Nov-2016 17:53:38 INFO gensim.matutils: initializing corpus reader from out_easy/corpus.mm
    20-Nov-2016 17:53:38 INFO gensim.matutils: accepted corpus with 17 documents, 514 features, 4585 non-zero entries
    20-Nov-2016 17:53:38 DEBUG collection: Corpus available.
    20-Nov-2016 17:53:38 INFO collection: Accessing model ...
    20-Nov-2016 17:53:38 INFO gensim.utils: loading LdaModel object from out_easy/corpus.lda
    20-Nov-2016 17:53:38 INFO gensim.utils: loading id2word recursively from out_easy/corpus.lda.id2word.* with mmap=None
    20-Nov-2016 17:53:38 INFO gensim.utils: setting ignored attribute state to None
    20-Nov-2016 17:53:38 INFO gensim.utils: setting ignored attribute dispatcher to None
    20-Nov-2016 17:53:38 INFO gensim.utils: loading LdaModel object from out_easy/corpus.lda.state
    20-Nov-2016 17:53:38 DEBUG collection: Model available.
    20-Nov-2016 17:53:38 DEBUG collection: :param: interactive == True.
    20-Nov-2016 17:53:38 INFO collection: Accessing dictionary ...
    20-Nov-2016 17:53:38 INFO gensim.utils: loading Dictionary object from out_easy/corpus.dict
    20-Nov-2016 17:53:38 DEBUG collection: Dictionary available.
    20-Nov-2016 17:53:38 DEBUG collection: Corpus, model and dictionary available.


It is not possible to run `save_heatmap()` before `make_heatmap()`.


```python
vis.save_interactive("./visualizations/interactive")
```

    20-Nov-2016 17:53:43 INFO collection: Saving interactive visualization ...
    20-Nov-2016 17:53:43 ERROR collection: Run make_interactive() before save_interactive()



    ---------------------------------------------------------------------------

    AttributeError                            Traceback (most recent call last)

    <ipython-input-24-c43724cc858f> in <module>()
    ----> 1 vis.save_interactive("./visualizations/interactive")
    

    /Users/severin/Desktop/Topics/collection.py in save_interactive(self, path, filename)
        407         try:
        408             log.info("Saving interactive visualization ...")
    --> 409             pyLDAvis.save_html(self.interactive_vis, os.path.join(path, 'corpus_interactive.html'))
        410             pyLDAvis.save_json(self.interactive_vis, os.path.join(path, 'corpus_interactive.json'))
        411             pyLDAvis.prepared_data_to_html(self.interactive_vis)


    AttributeError: 'Visualization' object has no attribute 'interactive_vis'



```python
vis.make_interactive()
```

    20-Nov-2016 17:53:47 INFO collection: Accessing model, corpus and dictionary ...
    20-Nov-2016 17:53:47 DEBUG gensim.models.ldamodel: performing inference on a chunk of 17 documents
    20-Nov-2016 17:53:47 DEBUG gensim.models.ldamodel: 6/17 documents converged within 50 iterations
    20-Nov-2016 17:53:48 DEBUG collection: Interactive visualization available.



```python
vis.save_interactive("./visualizations/interactive")
```

    20-Nov-2016 17:53:50 INFO collection: Saving interactive visualization ...
    20-Nov-2016 17:53:50 DEBUG collection: Interactive visualization available at ./visualizations/interactive/corpus_interactive.html and ./visualizations/interactive/corpus_interactive.json


![success](http://cdn2.hubspot.net/hub/128506/file-446943132-jpg/images/computer_woman_success.jpg)
