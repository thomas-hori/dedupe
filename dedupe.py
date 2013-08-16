#So far for exact dupes and only symlinking, and running on C:\ or /home ONLY
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
try:
    import anydbm #No deletes so dumbdbm will kinda work, preferably gdbm or bsddb though
except ImportError:
    import dbm as anydbm #Newer and older pythons
revhashes=dbm.open("hashes_temp","n")#{} #Dict fills memory like no tomorrow
for root,dirs,files in os.walk({"nt":"C:\\","posix":"/home"}[os.name]):
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
        time.sleep(0.01) #Let the OS breath!