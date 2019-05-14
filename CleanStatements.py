# Description: This file converts the raw FOMC Statements into cleaner
#              versions of themselves. In addition to basic cleaning,
#              the file performs some of the preprocessing steps described
#              in Acosta and Meade "Hanging on every word: Semantic analysis of the
#              FOMC's postmeeting statement" (2015).
#              It also creates a term-document matrix (tdm) for each type of cleaning
#              described in the 'output' section below.
#              The original author of this file and script is Miguel Acosta www.acostamiguel.com
#              and it has been reused for this project with only minor changes.
#
#              This file significantly reuses an open source version for the cleaning.
#              It has been modified from it's originally published version which used python2.
#              The author of that original version is Miguel Acosta  www.acostamiguel.com
#
# Input:       The raw FOMC statements, downloaded from federalreserve.gov
#              by the python script pullStatements.py. These should be
#              located in the directory statements/statements.raw
#
# Output:      Two sets of cleaned FOMC statements:
#                (i) A set, located in the directory statements/statements.clean
#                    of FOMC statements that have had header, footer, and voting
#                    information removed.
#                (ii) A set, located in statements/statements.clean.np
#                    of FOMC statements that have had header, footer, and voting
#                    information removed. They have also been stemmed, words
#                    have been concatenated, and numbers/stopwords
#                    have been removed.
#              Three files for each type of preprocessing: a sparse form of the
#              tdm, a list of words and a list of documents that compose the
#              tdm.
#
#--------------------------------- IMPORTS -----------------------------------#
import os, csv, re
from os import listdir
from os.path import isfile, join
from nltk.stem.lancaster import LancasterStemmer
from textmining_withnumbers import TermDocumentMatrix as TDM

#-------------------------DEFINE GLOBAL VARIABLES-----------------------------#
# Directory where the stop words and n-grams to concatenate are
datadir      = 'data'
# Where the raw statements are
statementdir = os.path.join('statements','statements.raw')
# Where the clean statements will go (with and without preprocessing)
cleanDir     = os.path.join('statements','statements.clean')
cleanDirNP   = os.path.join('statements','statements.clean.np')
# Where the tdms should go
outputDir    = 'output'

#-----------------------------------------------------------------------------#
# getReplacementList: Returns two lists, a list of N n-grams (phrase with n
#   words) and a list with N "words" to replace the n-grams. The function reads
#   a file, list_name, where every odd entry is an n-gram, and every even entry
#   is a replacement.
#-----------------------------------------------------------------------------#
def getReplacementList (list_name):
    allWords = [line.rstrip('\n') for line in  open(list_name, 'r') ]
    oldWords = [allWords[i] for i in range(len(allWords)) if i % 2 == 0]
    newWords = [allWords[i] for i in range(len(allWords)) if i % 2 == 1]
    return [oldWords, newWords]



#-----------------------------------------------------------------------------#
# cleanStatement: This function is the meat of this code--it performs all of the
#   cleaning/preprocessing described in the header of this document. It's
#   inputs are:
#     (1) statement   : a string with the filename of a single FOMC statement
#     (2) locationold : Directory where raw statements are located (string)
#     (3) replacements: Output from getReplacementList
#     (4) locationnew : Directory where clean statements go (string)
#     (5) stoplist    : A list of words to remove (list of strings)
#     (6) charsToKeep : A regular expression of the character types to keep
#     (7) stem        : A logical for whether to stem the words
#-----------------------------------------------------------------------------#
def cleanStatement (statement, locationold, replacements, locationnew, \
                    stoplist, charsToKeep, stem):
    # Read in the statement and convert it to lower case
    original  = open(os.path.join(locationold,statement),'r').read().lower()

    clean = original
    # Remove punctuation and newlines first, to keep space between words
    for todelete in ['.', '\r\n', '\n', ',', '-', ';', ':']:
        clean = clean.replace(todelete, ' ')

    # Keep only the characters that you want to keep
    clean = re.sub(charsToKeep, '', clean)
    clean = clean.replace('  ', ' ')
    clean = clean.replace(' u s ', ' unitedstates ')

    # Remove anything before (and including) 'for immediate release'
    deleteBefore= re.search("[Ff]or\s[Ii]mmediate\s[Rr]elease", \
                            clean).start() + len ('for immediate release')
    clean = clean[deleteBefore:]

    # Looking for the end of the text
    intaking   = re.search("in\staking\sthe\sdiscount\srate\saction",\
                           clean)
    votingfor  = re.search("voting\sfor\sthe\sfomc", clean)
    if intaking == None and not votingfor == None:
        deleteAfter = votingfor.start()
    elif votingfor == None and not intaking == None:
        deleteAfter = intaking.start()
    elif votingfor == None and intaking == None:
        deleteAfter = len(clean)
    else:
        deleteAfter = min(votingfor.start(), intaking.start())
    clean = clean[:deleteAfter]

    # Replace replacement words (concatenations)
    for word in range(len(replacements[0])):
        clean = clean.replace(replacements[0][word], replacements[1][word])

    # Remove stop words
    for word in stoplist:
        clean = clean.replace(' '+word.lower() + ' ', ' ')

    # Stem words
    if stem == 1:
        stemmer = LancasterStemmer()
        stemmed = [stemmer.stem(w) for w in clean.split()]
        clean   = ''
        for w in stemmed:
            clean = clean + w + ' '

    # Write cleaned file
    new = open(os.path.join(locationnew,statement), 'w')
    new.write(clean)
    new.close

#-----------------------------------------------------------------------------#
# createtdm: Creates a term-document matrix (tdm), using the code in
#   textmining_withnumbers, and stores the output in 'data.'
#   indir is a string indicating the directory from which to create
#   a term-document matrix, outdir is a string denoting where to store the
#   output, and fname is the suffix appended to the output file names.
#   Output files are a sparse form of the tdm, a list of words and a list
#   of documents that compose the tdm.
#-----------------------------------------------------------------------------#
# Commenting this section as it's producing the error L152: TypeError: '>' not supported between instances of 'str' and 'int'
# def createtdm (indir, outdir, fname):
#     statementList = [ f for f in listdir(indir) \
#                        if isfile(join(indir,f)) ]
#     # Initialize and fill term-document matrix
#     tdm = TDM()
#     [tdm.add_doc(open(join(indir,f), 'r').read()) for f in statementList]
#
#     # Store the output as a sparse matrix: first column is the row index
#     # (for words), second is column (for documents), and third is the word count
#     # Note that these are 0-indexed.
#     with open(join(outdir,'tdm.sparse' + fname + '.csv'), 'w') as f:
#         n = -1 # First row in tdm.rows are the word names.
#         for row in tdm.rows( cutoff = 1): # cutoff is the number of documents
#                                           # in which a term must appear to be
#                                           # included.
#             [f.write(str(n) + ',' + str(t) + ',' + str(row[t]) + '\n')
#              for t in range(len(row)) if row[t] > 0 and n > -1]
#             n = n+1
#
#     # Store the document names
#     with open(join(outdir,'tdm.docs' + fname + '.csv'), 'w') as f:
#         [f.write(filename + '\n') for filename in statementList]
#
#     # Store the word names
#     with open(join(outdir,'tdm.words' + fname + '.csv'), 'w') as f:
#         n = 0
#         for row in tdm.rows( cutoff = 1):
#             [f.write(r + '\n') for r in row if n == 0 ]
#             n = n+1

#-----------------------------------------------------------------------------#
# The Main function generates the stop list, and word replacement lists, then
#   loops through every file in the statements/statements.raw directory and
#   performs two types of cleaning: one that is less extensive (saved in
#   statements/statements.clean) and one that includes more preprocessing steps
#   (saved in statements/statements.clean.np). 'NP' denotes 'no preprocessing.
#   Finally, it creates the term-document matrix for each type of cleaning.
#-----------------------------------------------------------------------------#

def main():
    stoplist       = [line.rstrip('\n') for line in \
                      open(os.path.join(datadir,"stoplist_mcdonald_comb.txt")
                           , 'r') ]
    stoplistNP     = [line.rstrip('\n') for line in \
                      open(os.path.join(datadir,"emptystop.txt"), 'r') ]

    replacements   = getReplacementList(os.path.join(datadir,"wordlist.txt"))
    replacementsNP = getReplacementList(os.path.join(datadir,"wordlist.np.txt"))

    statementList  = [ f for f in listdir(statementdir) \
                       if isfile(join(statementdir,f)) ]

    for statement in statementList:
        # First, the case with heavier preprocessing (keep only letters)
        cleanStatement(statement, statementdir, replacements, \
                       cleanDir, stoplist, '[^A-Za-z ]+',1)
        # Second, the no-preprocessing case (keep letters and numbers)
        cleanStatement(statement, statementdir, replacementsNP, \
                       cleanDirNP, stoplistNP, '[^A-Za-z0-9 ]+',0)

    # Commenting this tdm section output as I commented the code above to generate it
    # Create term-document matrix
    # createtdm(cleanDir  , outputDir, '')
    # createtdm(cleanDirNP, outputDir, '.np')


if __name__ == "__main__":
    main()
