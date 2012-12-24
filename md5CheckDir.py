#!/usr/bin/env python

import sys
import re
from glob import glob
import os
import hashlib
import subprocess

def fileDigest( file ):
    if not os.path.exists( file + ".ucsc_md5" ):
        p = subprocess.Popen( "md5sum %s > %s.ucsc_md5" % (file, file), shell=True )
	p.wait()	
    handle = open( file + ".ucsc_md5" )
    line = handle.readline()
    handle.close()
    return line.split(' ')[0]	

def fileCheck( file ):
    p = subprocess.Popen( "file %s" % (file), shell=True, stdout=subprocess.PIPE )
    out = p.communicate()[0]
    if out.count("HTML"):
        return False
    return True

def scanDir( base ):
    for file in glob( os.path.join( base, "*" ) ):
        if os.path.isdir( file ):
	    scanDir( file )
	else:
	    if file.endswith(".md5"):
	        handle = open( file )
		line = handle.readline().rstrip()
		tmp = re.split(r'\s+', line)
		omd5 = tmp[0]
		nFile = file.replace( ".md5", "" )
		if tmp[1] != os.path.basename(nFile):
		    print "BAD_MD5:", file, tmp
		else:
		    if os.path.exists( nFile ):
		        if fileCheck(nFile):
			    nmd5 = fileDigest( nFile )
			    if omd5 != nmd5:
			        print "CORRUPT:", nFile
			    #else:
			    #	print "OK:", nFile
			else:
			    print "HTML_FILE:", nFile
		    else:
		        print file
		        print "MISSING:", nFile

if __name__ == "__main__":
	for path in sys.argv[1:]:
		scanDir( path )
