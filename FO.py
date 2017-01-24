class FieldOffice:

    def __init__(self):
        self.FOID = -1
        self.FOName = ""
        self.IconFilepath = ""
        self.FOURL_External = ""
        self.FOURL_Internal = ""
        self.FOLat = ""
        self.FOLong = ""

    def __init__(self, fn, ifp, u_e, u_i, la, lo):
        self.FOID = -1
        self.FOName = fn
        self.IconFilepath = ifp
        self.FOURL_External = u_e
        self.FOURL_Internal = u_i
        self.FOLat = la
        self.FOLong = lo


class FOLeader:

    def __init__(self):
        self.FOProfileID = -1
        self.FullName = ""
        self.Title = ""
        self.isLead = False
