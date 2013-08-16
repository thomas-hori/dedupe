#So far for exact dupes and only symlinking, and running on curdir ONLY
#Prints matches on Windows so far

import os,time
def megalink(a,b):
    os.unlink(b)
    os.symlink(a,b)
if os.name=="nt":
    #Otherwise dangerous: IT WOULD BE UNLINKED BUT NOT SYMLINKED!!! HAHAHAHAHAAAAAAAA
    def megalink(a,b):
        print "I would link",`a`,"to",`b`,"but I can't."
try:
    from hashlib import md5 #For newer pythons
except ImportError:
    from md5 import md5 #For older pythons

import shelve #No deletes so even dumbdbm will kinda work well
revhashes=shelve.open("hashes_temp.db","n")#{} #Dict fills memory like no tomorrow
for root,dirs,files in os.walk(os.getcwd()):
    if (".git" in root) or (".hg" in root) or (".bzr" in root) or (".rcs" in root):
        #Skip VCSs
        continue
    for f in files:
        p=os.path.join(root,f)
        fd=open(p,"rb")
        b=fd.read()
        fd.close()
        hash=md5(b).digest() #Not hexdigest as it takes up 2x the space and there is no need for being ascii
        if hash in revhashes:
            for uvver in revhashes[hash]:
                fd2=open(uvver,"rb")
                b2=fd2.read()
                fd2.close()
                if b2==b:
                    megalink(uvver,p)
                    break
            else:
                revhashes[hash]+=(p,) #Tuples as collision rare - thus optimised
        else:
            revhashes[hash]=(p,) #Tuples as collision rare - thus optimised
        time.sleep(0.1) #Let the OS breath!

#unlinking the db is complicated as any one (or pair) of the following may be present:
#  hashes_temp.db  hashes_temp.db.db  hashes_temp.db.pag  hashes_temp.db.dir
#  hashes_temp.db.dat
#This is according to the control of the default dbm system on the python installation.

