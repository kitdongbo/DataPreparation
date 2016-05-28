
class DayFeatureEx:

    def __init__(self, i_pt_id, i_fixed_dt, i_gl_rises, i_nocturnal_minimum, i_ill_months, i_age, i_gender, i_height, i_weight, i_ins_mod):
        self.m_pt_id = i_pt_id
        self.m_fixed_dt = i_fixed_dt
        self.m_gl_rises = i_gl_rises
        self.m_nocturnal_minimum = i_nocturnal_minimum
        self.m_ill_months = i_ill_months
        self.m_age = i_age
        self.m_gender = i_gender
        self.m_height = i_height
        self.m_weight = i_weight
        self.m_ins_mod = i_ins_mod

    def __str__(self):
        return "PtId: " + str(self.m_pt_id) + \
               "\nFixed_DT: " + str(self.m_fixed_dt) + \
               "\nGlRises: " + str(self.m_gl_rises) + \
               "\nNoctMin: " + str(self.m_nocturnal_minimum) + \
               "\nIll_months: " + str(self.m_ill_months) + \
               "\nAge: " + str(self.m_age) + \
               "\nGender: " + str(self.m_gender) + \
               "\nHeight: " + str(self.m_height) + \
               "\nWeight: " + str(self.m_weight) + \
               "\nIns_mod: " + str(self.m_ins_mod)

    def GetPtId(self):
        return self.m_pt_id

    def GetFixedDT(self):
        return self.m_fixed_dt

    def GetGlRises(self):
        return self.m_gl_rises

    def GetNocturnalMinimum(self):
        return self.m_nocturnal_minimum

    def GetIllMonths(self):
        return self.m_ill_months

    def GetAge(self):
        return self.m_age

    def GetGender(self):
        return self.m_gender

    def GetHeight(self):
        return self.m_height

    def GetWeight(self):
        return self.m_weight

    def GetInsMod(self):
        return self.m_ins_mod