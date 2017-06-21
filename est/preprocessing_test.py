from dariah_topics import preprocessing as pre
from pathlib import Path

project_path = Path(__file__).absolute().parent.parent

# TODO: Add tests
"""
# Funktion muss irgendwie mit test heißen
def test_document_list():

    # die Funktion under test aufrufen
    docs = pre.PathDocList(str(Path(project_path, 'corpus_txt')))
    doclist = docs.full_paths(as_str=True)

    # Bedingungen auf dem Ergebnis prüfen:
    assert len(doclist) == 17

    return doclist

def test_document_labels():
    doclist = test_document_list()
    docs = pre.PathDocList(str(Path(project_path, 'corpus_txt')))
    labels = docs.labels()
    assert len(list(labels)) == len(doclist)
"""
