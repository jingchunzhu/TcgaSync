import os
import sys,string
from glob import glob
from urlparse import urlparse

basedir = "/data/TCGA"

handle = open(sys.argv[1])

urls = {}
dirs = {}

for path in handle:
    u = urlparse(path.strip())
    urls[ path.strip() ] = u
    dirname = os.path.dirname(u.path)
    if dirname not in dirs:
        dirs[ dirname ] = []
    dirs[dirname].append( os.path.basename(u.path) )
handle.close()

for dirname in dirs:
    #match local to web
    if os.path.exists(basedir + dirname):
        for f in glob( basedir + dirname + "/*" ):
            # do not match Level_1 and ucsc_md5 files with web
            if os.path.basename( f ) not in dirs[dirname]:
                if os.path.isdir(f) :
                    found=0
                    for d in dirs:
                        if string.find(basedir+d, f)==0:
                            found =1
                            break
                    if not found:
                        print "extra_dir: ", f, dirname, dirs[dirname]
                elif string.find(f,"Level_1")==-1 and string.find(f,"ucsc_md5")==-1:
                    print "extra_file: ", f
    else:
        print "missing_dir: ", dirname

    #match web to local
    for name in dirs[dirname]:
        path =  basedir + dirname + "/" + name
        # do not match Level_1, image file web local
        #if string.find(path,"Level_1")!=-1 or string.find(path,"diagnostic_images")!=-1 or string.find(path,"diagnostic_images")!=-1:
        #    continue
        if not os.path.exists( path ):
            print "missing_file: ", dirname + "/" + name
