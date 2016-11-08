# Testing `collection.py`

The following tutorial shows how to use the collection module of Dariah-Topics.

1. Prearrangement
----
First you need to import the collection module so your ipython notebook has access to its functions and classes.
As second step we set paths for a test corpus consisting of plain text files and one consisting of annotated text preprocessed with several NLP-Tools in form of csv files (if you have questions concerning the format go to: https://github.com/DARIAH-DE/DARIAH-DKPro-Wrapper/blob/master/doc/tutorial.adoc). 

2. Creating list of filenames (plain text and csv files)
----
The following function is used to normalize path names so non-uniform text files will be processable by the module. It is possible to add an additional argument "ext" where you can specify an extension ('csv' in this case). The CSV

3. Load the corpora
----
By using the "read\_from\_"-functions we create a generator object which provides a memory efficient way to handle bigger corpora.

4. Segmenting text
----
An important part of pre-processing in Topic modelling is segmenting the the texts in 'chunks'. The arguments of the function are for the targeted corpus and the size of the 'chunks' in words. Depending on the languange and type of text results can vary widely in quality.

5. Filtering text using POS-Tags
----
Another way to preprocess the text is by filtering by POS-Tags and using lemmata (in this case only adjectives, verbs and nouns are filterable). The annotated csv-file we provide in this example is already enriched with this kind of information. 

6. Visualization
----
Simple get-functions are implemented for visualization tasks. In this case the get_labels-function extracts the titles of the corpus files we loaded above.