#So far for exact dupes and only symlinking, and running on curdir ONLY
#Prints matches on Windows so far
#Requires, at the moment, any Python 2.3-2.7 inclusive.

import os,time
import shelve #No deletes so even dumbdbm will kinda work well
from rich import CmpAble,cmp

def askyn(x):
    while 1: #read "a:" or ":a"
        y=raw_input(x).strip()
        if y.lower() not in ("y","n","yes","no"):
            continue #read "goto a"
        else:
            return y.lower()[0]=="y"

class BaseComparer(CmpAble,object):
    """ABC for comparers"""
    #Should be a mutable object implementing the mapping protocol: hash to sequence
    revhashes=None 
    trustworthiness=0 #Int, 0-10
    def __cmp__(self,b):
        return cmp(self.trustworthiness,b.trustworthiness)
    def fprint_quick(self,buffer):
        """Remove metadata from the buffer and/or smart-fingerprint it (or do nothing) and return it, for (e.g.) MP3 data comparison.  For the hash stage.
        A hook for mixins, default passes through to fprint_thorough."""
        return self.fprint_thorough(buffer)
    def fprint_thorough(self,buffer):
        """Remove metadata from the buffer and/or smart-fingerprint it (or do nothing) and return it, for (e.g.) MP3 data comparison.  For the actual compare stage.
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
        if (self.trustworthiness==10) or askyn("Link %s to %s [Y/N]? "%(a,b)):
            #if os.name=="nt":
            #    #DO NOT even approach the unlinking stage on Windows!
            #    print "I would link",`a`,"to",`b`,"but I can't."
            #    return
            os.unlink(b)
            try:
                os.link(a,b)
            except: #XXX except what?  IOError?  OSError?  RuntimeError?  GrueError?  YASDError?
                os.symlink(a,b)
    def is_elegible(self,path):
        return 1
class ExactMd5Hasher(BaseComparer):
    trustworthiness=10 #Very trustworthy
    hashtable_fn="md5hashr.db"
    def __init__(self):
        self.revhashes=shelve.open(self.hashtable_fn,"n")#{} #Dict fills memory like no tomorrow
    def check_file(self,p,b):
        try:
            import hashlib
        except ImportError:
            import md5 as hashlib
        b=self.fprint_quick(b)
        hash=hashlib.md5(b).digest() #Not hexdigest as it takes up 2x the space and there is no need for being ascii
        if hash in self.revhashes:
            for uvver in self.revhashes[hash]:
                fd2=open(uvver,"rb")
                b2=fd2.read()
                fd2.close()
                if self.fprint_thorough(b2)==self.fprint_thorough(b):
                    return uvver
            self.revhashes[hash]+=(p,) #Tuples as collision rare - thus optimised
        else:
            self.revhashes[hash]=(p,) #Tuples as collision rare - thus optimised
        return None
    def __del__(self):#The destroyer, called when all refs are deleted
        self.revhashes.close()
class Id3StripComparer(ExactMd5Hasher):
    trustworthiness=9 #Until metadata can be resolved
    hashtable_fn="id3stpmd.db"
    def fprint_thorough(self,buffer):
        try:
            from StringIO import StringIO as BytesIO
        except ImportError:
            from io import BytesIO
        file=BytesIO(buffer);
        import read_id3
        res=read_id3.read_id3(file)
        #Strip beginning id3v2 and also id3v1
        if len(res.id3v1.tags)==0:
            pass
        elif len(res.id3v1.tags)==1:
            buffer=buffer[:-128]
        elif (len(res.id3v1.tags)==2) and ("ID3v1 TAG+ Extension" in res.id3v1.tags):
            buffer=buffer[:-355]
        if res.id3v2s:
            if res.id3v2s[0].start_offset==0:
                buffer=buffer[res.id3v2s[0].end_offset:]
        #Don't ask.  Feel free to add more Lame versions.
        if "LAME3.98.2" in buffer:
            #teeth.gnash()
            buffer=buffer[:buffer.index("LAME3.98.2")]
        return buffer
    def is_elegible(self,path):
        return path.endswith(".mp3")

comparers=[ExactMd5Hasher(),Id3StripComparer()]
comparers.sort()
comparers.reverse()
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
        #print p
        for comparer in comparers:
            if comparer.is_elegible(p):
                other=comparer.check_file(p,b)
                if other:
                    comparer.dedupe_link(other,p)
                    break
        time.sleep(0.1) #Let the OS breath!
del comparers,comparer
#unlinking the db is complicated as e.g any one (or pair) of the following may be present
#(for name "name.db"):
#  name.db  name.db.db  name.db.pag  name.db.dir  name.db.dat
#This is according to the control of the default dbm system on the python installation.

