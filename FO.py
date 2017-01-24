class FieldOffice:

    def __init__(self):
        self.FOID = -1
        self.FOName = ""
        self.IconFilepath = ""
        self.FOURL = ""
        self.FOLat = ""
        self.FOLong = ""

    def __init__(self, fn, ifp, u, la, lo):
        self.FOID = -1
        self.FOName = fn
        self.IconFilepath = ifp
        self.FOURL = u
        self.FOLat = la
        self.FOLong = lo


class FOLeader:

    def __init__(self):
        self.FOProfileID = -1
        self.FullName = ""
        self.Title = ""
        self.isLead = False
