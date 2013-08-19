#So far for exact dupes and only symlinking, and running on curdir ONLY
#Prints matches on Windows so far

import os,time
import shelve #No deletes so even dumbdbm will kinda work well

class BaseComparer(object):
    """ABC for comparers"""
    #Should be a mutable object implementing the mapping protocol: hash to sequence
    revhashes=None 
    def fingerprint(self,buffer):
        """Remove metadata from the buffer and/or smart-fingerprint it (or do nothing) and return it, for (e.g.) MP3 data comparison.
        A hook for mixins."""
        return buffer
    def check_file(self,path,buffer):
        """Check for duplicates of a file, return path if successful, None otherwise"""
        raise NotImplementedError("should be implemented by subclass")
    def dedupe_link(self,a,b):
        """Link a to b deleting the original b, possibly bringing metadata into harmony on the way (according to subclass)"""
        if os.name=="nt":
            #DO NOT even approach the unlinking stage on Windows!
            print "I would link",`a`,"to",`b`,"but I can't."
            return
        os.unlink(b)
        try:
            os.link(a,b)
        except: #XXX except what?  IOError?  OSError?  RuntimeError?  GrueError?  YASDError?
            os.symlink(a,b)
class ExactMd5Hasher(BaseComparer):
    def __init__(self):
        self.revhashes=shelve.open("md5hasher.db","n")#{} #Dict fills memory like no tomorrow
    def check_file(self,p,b):
        try:
            import hashlib
        except ImportError:
            import md5 as hashlib
        b=self.fingerprint(b)
        hash=hashlib.md5(b).digest() #Not hexdigest as it takes up 2x the space and there is no need for being ascii
        if hash in self.revhashes:
            for uvver in self.revhashes[hash]:
                fd2=open(uvver,"rb")
                b2=fd2.read()
                fd2.close()
                if b2==b:
                    return uvver
            self.revhashes[hash]+=(p,) #Tuples as collision rare - thus optimised
        else:
            self.revhashes[hash]=(p,) #Tuples as collision rare - thus optimised
        return None
comparers=[ExactMd5Hasher()]
print "Installed comparers:"
for comparer in comparers:
    print "\t"+comparer.__class__.__name__
for root,dirs,files in os.walk(os.getcwd()):
    #XXX check if these repodirs are corect
    if (".git" in root) or (".hg" in root) or (".bzr" in root) or (".rcs" in root):
        continue
    for f in files:
        p=os.path.join(root,f)
        if os.path.islink(p):
            #Skip symlinks
            continue
        fd=open(p,"rb")
        b=fd.read()
        fd.close()
        for comparer in comparers:
            other=comparer.check_file(p,b)
            if other:
                comparer.dedupe_link(other,p)
        time.sleep(0.1) #Let the OS breath!

#unlinking the db is complicated as any one (or pair) of the following may be present:
#  hashes_temp.db  hashes_temp.db.db  hashes_temp.db.pag  hashes_temp.db.dir
#  hashes_temp.db.dat
#This is according to the control of the default dbm system on the python installation.

