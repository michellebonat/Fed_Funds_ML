# This is taken from the textmining package, which is described
# at http://www.christianpeccei.com/textmining/, and extended to
# not discard numeric characters by Miguel Acosta.
import re, csv, os

def simple_tokenize(document):
    """
    Clean up a document and split into a list of words.

    Converts document (a string) to lowercase and strips out everything which
    is not a lowercase letter.

    """
    document = document.lower()
    document = re.sub('[^a-z0-9]', ' ', document)
    return document.strip().split()


class TermDocumentMatrix(object):

    """
    Class to efficiently create a term-document matrix.

    The only initialization parameter is a tokenizer function, which should
    take in a single string representing a document and return a list of
    strings representing the tokens in the document. If the tokenizer
    parameter is omitted it defaults to using textmining.simple_tokenize

    Use the add_doc method to add a document (document is a string). Use the
    write_csv method to output the current term-document matrix to a csv
    file. You can use the rows method to return the rows of the matrix if
    you wish to access the individual elements without writing directly to a
    file.

    """

    def __init__(self, tokenizer=simple_tokenize):
        """Initialize with tokenizer to split documents into words."""
        # Set tokenizer to use for tokenizing new documents
        self.tokenize = tokenizer
        # The term document matrix is a sparse matrix represented as a
        # list of dictionaries. Each dictionary contains the word
        # counts for a document.
        self.sparse = []
        # Keep track of the number of documents containing the word.
        self.doc_count = {}

    def add_doc(self, document):
        """Add document to the term-document matrix."""
        # Split document up into list of strings
        words = self.tokenize(document)
        # Count word frequencies in this document
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        # Add word counts as new row to sparse matrix
        self.sparse.append(word_counts)
        # Add to total document count for each word
        for word in word_counts:
            self.doc_count[word] = self.doc_count.get(word, 0) + 1

    def rows(self, cutoff=2):
        """Helper function that returns rows of term-document matrix."""
        # Get master list of words that meet or exceed the cutoff frequency
        words = [word for word in self.doc_count \
          if self.doc_count[word] >= cutoff]
        # Return header
        yield words
        # Loop over rows
        for row in self.sparse:
            # Get word counts for all words in master list. If a word does
            # not appear in this document it gets a count of 0.
            data = [row.get(word, 0) for word in words]
            yield data

    def write_csv(self, filename, cutoff=2):
        """
        Write term-document matrix to a CSV file.

        filename is the name of the output file (e.g. 'mymatrix.csv').
        cutoff is an integer that specifies only words which appear in
        'cutoff' or more documents should be written out as columns in
        the matrix.

        """
        f = csv.writer(open(filename, 'wb'))
        for row in self.rows(cutoff=cutoff):
            f.writerow(row)