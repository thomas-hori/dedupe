genre_to_name={#From Appendix A of ID3v2.2 Standard
    0:"Blues",
    1:"Classic Rock",
    2:"Country",
    3:"Dance",
    4:"Disco",
    5:"Funk",
    6:"Grunge",
    7:"Hip-Hop",
    8:"Jazz",
    9:"Metal",
    10:"New Age",
    11:"Oldies",
    12:"Other",
    13:"Pop",
    14:"R&B",
    15:"Rap",
    16:"Reggae",
    17:"Rock",
    18:"Techno",
    19:"Industrial",
    20:"Alternative",
    21:"Ska",
    22:"Death Metal",
    23:"Pranks",
    24:"Soundtrack",
    25:"Euro-Techno",
    26:"Ambient",
    27:"Trip-Hop",
    28:"Vocal",
    29:"Jazz+Funk",
    30:"Fusion",
    31:"Trance",
    32:"Classical",
    33:"Instrumental",
    34:"Acid",
    35:"House",
    36:"Game",
    37:"Sound Clip",
    38:"Gospel",
    39:"Noise",
    40:"AlternRock",
    41:"Bass",
    42:"Soul",
    43:"Punk",
    44:"Space",
    45:"Meditative",
    46:"Instrumental Pop",
    47:"Instrumental Rock",
    48:"Ethnic",
    49:"Gothic",
    50:"Darkwave",
    51:"Techno-Industrial",
    52:"Electronic",
    53:"Pop-Folk",
    54:"Eurodance",
    55:"Dream",
    56:"Southern Rock",
    57:"Comedy",
    58:"Cult",
    59:"Gangsta",
    60:"Top 40",
    61:"Christian Rap",
    62:"Pop/Funk",
    63:"Jungle",
    64:"Native American",
    65:"Cabaret",
    66:"New Wave",
    67:"Psychadelic",
    68:"Rave",
    69:"Showtunes",
    70:"Trailer",
    71:"Lo-Fi",
    72:"Tribal",
    73:"Acid Punk",
    74:"Acid Jazz",
    75:"Polka",
    76:"Retro",
    77:"Musical",
    78:"Rock & Roll",
    79:"Hard Rock",
    #The following genres are Winamp extensions
    80:"Folk",
    81:"Folk-Rock",
    82:"National Folk",
    83:"Swing",
    84:"Fast Fusion",
    85:"Bebob",
    86:"Latin",
    87:"Revival",
    88:"Celtic",
    89:"Bluegrass",
    90:"Avantgarde",
    91:"Gothic Rock",
    92:"Progressive Rock",
    93:"Psychedelic Rock",
    94:"Symphonic Rock",
    95:"Slow Rock",
    96:"Big Band",
    97:"Chorus",
    98:"Easy Listening",
    99:"Acoustic",
    100:"Humour",
    101:"Speech",
    102:"Chanson",
    103:"Opera",
    104:"Chamber Music",
    105:"Sonata",
    106:"Symphony",
    107:"Booty Bass",
    108:"Primus",
    109:"Porn Groove", #XXX What???
    110:"Satire",
    111:"Slow Jam",
    112:"Club",
    113:"Tango",
    114:"Samba",
    115:"Folklore",
    116:"Ballad",
    117:"Power Ballad",
    118:"Rhythmic Soul",
    119:"Freestyle",
    120:"Duet",
    121:"Punk Rock",
    122:"Drum Solo",
    123:"A capella",
    124:"Euro-House",
    125:"Dance Hall",
    #the empty field:
    255:None
}
for i in range(126,225):
    genre_to_name[i]="ID3v1 Genre %d (nonstandard)"%i

class Id3dat: #Read "struct"
    def __init__(s):
        s.last_byte_of_actual_audio=-1
        s.tags=[]
        s.id3v1=Id3v1dat()
        s.id3v2=Id3v2dat()

class Id3v1dat: #Read "struct"
    def __init__(s):
        s.title=None
        s.rest_of_title=None
        s.artist=None
        s.rest_of_artist=None
        s.album=None
        s.rest_of_album=None
        s.year=None
        s.comment=None
        s.track=0 #The "undefined" value it is going to wind up with if comment 28 bytes or lower
        s.genre=None
        s.textual_genre=None
        s.speed=0 #0=unset, 1=slow, 2= medium, 3=fast, 4=hardcore
        s.start_time=None #mmm:ss
        s.end_time=None #mmm:ss

class Id3v2dat: #Read "struct"
    version=None #i.e. id3v2.* (starts at 2...it seems they changed their mind on whether the next backwards incompatible version was a 2.x or not)
    revision=None#e.g. id3v2.2.*
    flags=None #MSb=Global Unsynchronisation Used, next=Extended header present (it was planned in the id3v2[.2] standard for this to be compression but it is NOT), next=Tag is experimental, next=Footer Present
    extended_header="" # *** IN THIS PARSER *** not including the size int
    frames=[]
    
def read_id3(file):
    datman=Id3dat()
    #ID3v1
    file.seek(-128,2)
    if file.read(3)=="TAG":
        datman.last_byte_of_actual_audio=-129
        datman.tags.append("ID3v1[.1]")
        datman.id3v1.title=file.read(30)
        datman.id3v1.artist=file.read(30)
        datman.id3v1.album=file.read(30)
        datman.id3v1.year=file.read(4)
        datman.id3v1.comment=file.read(28)
        marker_byte=file.read(1)
        if marker_byte=="\0":
            datman.id3v1.track=ord(file.read(1))
        else:
            datman.id3v1.comment+=marker_byte+file.read(1)
        datman.id3v1.genre=ord(file.read(1))
        datman.id3v1.textual_genre=genre_to_name[datman.id3v1.genre] #Will be overritten
    file.seek(-355,2)
    if file.read(4)=="TAG+":
        datman.last_byte_of_actual_audio=-356
        datman.tags.append("ID3v1 TAG+ Extension")
        datman.id3v1.rest_of_title=file.read(60)
        datman.id3v1.rest_of_artist=file.read(60)
        datman.id3v1.rest_of_album=file.read(60)
        datman.id3v1.speed=ord(file.read(1))
        datman.id3v1.textual_genre=file.read(30)
        datman.id3v1.start_time=file.read(6)
        datman.id3v1.end_time=file.read(6)
    #ID3v2
    file.seek(0,0)
    while 1:
        seekage=0
        if file.read(3)!="ID3":
            break
        datman.id3v2.version=ord(file.read(1))
        datman.id3v2.revision=ord(file.read(1))
        datman.id3v2.flags=ord(file.read(1))
        size=ord(file.read(1)) <<21 #Yes, that's a 21.  Not a 24.
        size+=ord(file.read(1))<<14 #Yes, that's a 14.  Not a 16.
        size+=ord(file.read(1))<<7  #Yes, that's a 7.  Not an 8.
        size+=ord(file.read(1))
        framelist_size=size
        if datman.id3v2.flags&0x01000000:
            sizel=map(ord,list(file.read(4)))
            #In ID3v2.3 it is a regular Long BUT never even remotely exceeds 127
            #In ID3v2.4 and the forseeable future the size value is a Synchsafe Long
            size=ord(file.read(1)) <<21 #Yes, that's a 21.  Not a 24.
            size+=ord(file.read(1))<<14 #Yes, that's a 14.  Not a 16.
            size+=ord(file.read(1))<<7  #Yes, that's a 7.  Not an 8.
            size+=ord(file.read(1))
            if datman.id3v2.version<4:
                #In ID3v2.3 the size value excludes itself
                datman.id3v2.extended_header=file.read(size)
                framelist_size-=(size+4)
            else:
                #ID3v2.4 changed the entire extheader format, it now include itself
                datman.id3v2.extended_header=file.read(size-4)
                framelist_size-=size
        while framelist_size:
            if datman.id3v2.version==2:
                id=file.read(3)
                if id=="\0\0\0":break
                #No, there is no fourth byte
                size=ord(file.read(1))<<16 #Yes, that's actually a 16 this time
                size+=ord(file.read(1))<<8 #Yes, that's actually an 8 this time
                size+=ord(file.read(1))
                framelist_size-=6
                flags=0
            elif datman.id3v2.version==3:
                id=file.read(4)
                if id=="\0\0\0\0":break
                size=ord(file.read(1))<<24 #Yes, that's actually a 24 this time
                size+=ord(file.read(1))<<16#Yes, that's actually a 16 this time
                size+=ord(file.read(1))<<8 #Yes, that's actually an 8 this time
                size+=ord(file.read(1))
                flags=ord(file.read(1))<<8 #Yes, that's actually an 8 this time
                flags+=ord(file.read(1))
                framelist_size-=10
            elif datman.id3v2.version>=4: #A bit optimistic but hey
                id=file.read(4)
                if id=="\0\0\0\0":break
                size=ord(file.read(1)) <<21 #Yes, that's a 21.  Not a 24.
                size+=ord(file.read(1))<<14 #Yes, that's a 14.  Not a 16.
                size+=ord(file.read(1))<<7  #Yes, that's a 7.  Not an 8.
                size+=ord(file.read(1))
                flags=ord(file.read(1))<<8 #Yes, that's actually an 8 this time
                flags+=ord(file.read(1))
                framelist_size-=10
            dat=file.read(size)
            if id=="SEEK":
                seekage =ord(file.read(1))<<24#Yes, that's actually a 24 this time
                seekage+=ord(file.read(1))<<16#Yes, that's actually a 16 this time
                seekage+=ord(file.read(1))<<8 #Yes, that's actually an 8 this time
                seekage+=ord(file.read(1))
            if id[0]!="T" or id[:3]=="TXX":
                datman.id3v2.frames.append((id,flags,dat))
            else:
                #Encoding byte: 0=latin1,1=utf16bom,2=utf16be,3=utf8
                datman.id3v2.frames.append((id,flags,ord(dat[0]),dat[1:]))
            framelist_size-=size
        if seekage:
            file.seek(framelist_size+seekage,1)
        else:
            break
    return datman
if __name__=="__main__":
    f=open("SUNDANCE.mp3","rb")
    import os
    os.environ["PYTHONINSPECT"]="1"
    result=read_id3(f)
    print "The return value is in 'result'"