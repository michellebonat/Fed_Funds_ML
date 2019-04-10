# Description:
# This file downloads the FOMC statements from the Fed website,
# www.federalreserve.gov, and stores them as individual files
# in the directory 'statements'.

# The file has been modified from it's originally published version which used python2.
# The author of that original version is Miguel Acosta  www.acostamiguel.com
# -----
# Input:
# A file in the directory 'data', called 'dates.sort.txt',
# that contains FOMC meeting dates in the format YYYYMMDD, one date
# per line. Currently, this file only contains dates through
# 2015. If you run this and want more statements, you will need
# to add the dates manually from the FOMC website, and possibly
# edit the FOMCstatementURL function.
# -----
# Output:
# Files titles 'statements.fomc.YYYYMMDD', each of which contains
# an FOMC statement.
# -----

#--------------------------------- IMPORTS -----------------------------------#
from   bs4    import BeautifulSoup
from   urllib.request import urlopen
from   time   import sleep
import re,csv,os

#-------------------------DEFINE GLOBAL VARIABLES-----------------------------#
# Directory in which to place statements (careful in changing this--other
# scripts in this package rely on it).
outdir = os.path.join('statements','statements.raw')

#-----------------------------------------------------------------------------#
# FOMCstatementsURL: A function that returns the appropriate URL of the
#   FOMC statements. Given a date string in the format YYYYMMDD, it returns a
#   string with the appropriate URL. I collected the URLs manually.
#-----------------------------------------------------------------------------#

def FOMCstatementURL(date):
    year = date[0:4]
    dateInt = int(date)

    if dateInt == 20081216:
        urlout = 'http://www.federalreserve.gov/newsevents/' + \
                 'press/monetary/' + date + 'b.htm'
    elif dateInt >= 19990501 and dateInt < 20020331:
        urlout = 'http://www.federalreserve.gov/boarddocs/' + \
                 'press/general/' + year + '/' + date + '/'
    elif dateInt >= 20020501 and dateInt < 20030000:
        urlout = 'http://www.federalreserve.gov/boarddocs/press/' + \
                 'monetary/' + year + '/' + date + '/'
    elif dateInt >= 20030000 and dateInt < 20060000:
        urlout = 'http://www.federalreserve.gov/boarddocs/press/' + \
                 'monetary/' + year + '/' + date + '/default.htm'
    elif dateInt >= 20050000:
        urlout = 'http://www.federalreserve.gov/newsevents/press/' + \
                 'monetary/' + date + 'a.htm'

    return urlout

#-----------------------------------------------------------------------------#
# getDate: A function that uses the BeautifulSoup library to scrape the
#   text of the FOMC statement from the Fed website, which the function
#   returns as a string. Note that there is little effort to clean the text---
#   that is reserved for another step.
#-----------------------------------------------------------------------------#

def getStatement(mtgDate):
    print('Pulling: ' + mtgDate)
    html      = urlopen(FOMCstatementURL(mtgDate)).read()
    soup      = BeautifulSoup(html)
    allText   = soup.get_text(" ")
    startLoc  = re.search("[Ff]or\s[Ii]mmediate\s[Rr]elease", \
                          allText).start()
    statementText = allText[startLoc:]
    endLoc    = re.search("[0-9]{4}\s[Mm]onetary\s[Pp]olicy", \
                          statementText).start()
    statementText = statementText[:endLoc]
    statementText = statementText.encode('ascii', 'ignore').decode('ascii')
    return statementText


#-----------------------------------------------------------------------------#
# The Main function reads the file data/data.sort.txt, forms a list of the
#   meeting dates contained therein, and loops over them, at each iteration
#   calling the function getStatement to get the FOMC statement from
#   that date. It then prints out the results to individual files.
#-----------------------------------------------------------------------------#

def main():

    releaseDates = [line.rstrip() for line in
                    open(os.path.join('data','dates.sort.txt'), 'r')]

    for releaseDate in releaseDates:
        data = getStatement(releaseDate)
        # Give the Fed servers a break
        sleep(2)
        # The URL for 20070628 is stored at 20070618 page.
        if releaseDate.find("20070618")>-1:
           releaseDate = "20070628"
        filename="statement.fomc." + releaseDate +".txt"
        f = open(os.path.join(outdir,filename), 'w')
        f.write(data)
        f.close


if __name__ == "__main__":
    main()