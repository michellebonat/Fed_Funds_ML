# Description: This file converts the raw FOMC Statements into cleaner
#              versions of themselves.
#
#              This file leverages an open source version for the cleaning.
#              The content has been modified from it's originally published version and
#              adapted for python3.
#              The author of that original version is Miguel Acosta  www.acostamiguel.com
#
# Input:       The raw FOMC statements, downloaded from federalreserve.gov
#              by the python script pullStatements.py. These are
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
# Where the cleaned documents should go
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
#-----------------------------------------------------------------------------#
def cleanStatement (statement, locationold, replacements, locationnew, \
                    stoplist, charsToKeep):
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

    # Write cleaned file
    new = open(os.path.join(locationnew,statement), 'w')
    new.write(clean)
    new.close

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

if __name__ == "__main__":
    main()
