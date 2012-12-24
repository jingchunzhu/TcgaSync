import sys
import os
import httplib
import json, string
from urlparse import urljoin, urlparse
from bs4 import BeautifulSoup
from StringIO import StringIO
import base64

def scanHTML( opener, url , fout, FHdate=""):
    outlinks = []
    try:
        doc = opener.urlopen(url).read()
        soup = BeautifulSoup(doc)
        for href in soup.findAll('a'):
            link = urljoin( url, href['href'] )
            # ignore Level_1 data
            # ignore images
            if string.find(link,"Level_1")!=-1:
                continue
            if string.find(link,"diagnostic_images")!=-1:
                continue
            if string.find(link,"tissue_images")!=-1:
                continue
            if FHdate!="" and not link.endswith("/") and string.find(link,FHdate)==-1:
                continue
            if FHdate!="" and not link.endswith("/") and string.find(link,"Level_")==-1:
                continue
            if link.endswith(".gz") or link.endswith(".gz.md5"):
                fout.write(link+'\n')
            outlinks.append( link )
    except IOError as e:
        sys.stderr.write( "Error:" + str(e) + "\n" )

    return outlinks


def scanBase( opener, baseURL, fout,FHdate=""):
    scanHash = { baseURL : False }
    found = True
    while found:
        found = False
        for url in scanHash.keys():        
            if not scanHash[ url ] and url.endswith('/'):
                newSet = scanHTML( opener, url , fout, FHdate)
                scanHash[ url ] = True
                for a in newSet:
                    a = a.split('?')[0]
                    doScan = True
                    if not a.startswith( baseURL ):
                        doScan = False
                    if scanHash.has_key(a) and scanHash[a]:
                        doScan = False    
                    if a[:-1] + ".tar.gz" in newSet:
                        doScan = False
                    if a.endswith("userCreatedArchives/"):
                        doScan = False
                    if a.endswith("lost+found/"):
                        doScan = False
                    if doScan :
                        scanHash[a] = False
                        found = True
    return scanHash.keys()
    

class OpenHTTP:
    def __init__(self, user=None, passwd=None):
        self.handle = None
        self.server = None
        self.user = user
        self.passwd = passwd
    
    def urlopen(self, path):
        u = urlparse(path)
        if self.handle is None or u.netloc != self.server:
            self.handle = httplib.HTTPSConnection(u.netloc)        
        self.handle.putrequest('GET', u.path)
        if self.user is not None:
             auth = 'Basic ' + (base64.encodestring(self.user + ':' + self.passwd)).strip()
             self.handle.putheader('Authorization', auth )
        self.handle.endheaders()     
        return self.handle.getresponse()


if __name__ == "__main__":
    if ( len( sys.argv ) not in [4,6] ):
        sys.exit()

    opener = None
    baseURL = sys.argv[1]
    fout =open(sys.argv[3],'w')
    FHdate=""
    
    if sys.argv[2]=="open":
        opener = OpenHTTP()
        
    if sys.argv[2]=="secure":
        opener = OpenHTTP(sys.argv[4], sys.argv[5])

        url = "https://tcga-data-secure.nci.nih.gov/tcgafiles/tcga4yeo/other/gdacs/gdacbroad/LATEST_RUN"
        doc = string.split(opener.urlopen(url).read(),"\n")
        FHdate=doc[1]
        if len(FHdate)!=10:
            sys.stderr.write( "Error: parsing FH last run filed\n" )
            sys.exit()
        fout.write(url+'\n')

    URLlist = scanBase( opener, baseURL, fout, FHdate)
