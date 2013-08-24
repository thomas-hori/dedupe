#I wrote this some time ago, and now rework it for use here.
#I don't *think* that any identifiable portions are copiedfrom another location.
#--Thomas

def _cmp(a,b):
    if a > b:
        return 1
    elif a < b:
        return -1
    else:
        return 0

def cmp(a,b):
    try:
        return a.__cmp__(b)
    except AttributeError:
        return _cmp(a,b)

class CmpAble:
    """Danger of recursion unless __gt__+__lt__ or __cmp__ overriden. Otherwise rich and poor comparison in fullness."""
    def __lt__(self, other):
        """Override along with __gt__, or override __cmp__"""
        return cmp(self,other)<0

    def __le__(self, other):
        return cmp(self,other)<1

    def __eq__(self, other):
        return cmp(self,other)==0

    def __ne__(self, other):
        return cmp(self,other)!=0

    def __gt__(self, other):
        """Override along with __lt__, or override __cmp__"""
        return cmp(self,other)>0

    def __ge__(self, other):
        return cmp(self,other)>-1

    def __cmp__(self, other):
        """Override this, or __gt__ along with __lt__"""
        return _cmp(self,other)
