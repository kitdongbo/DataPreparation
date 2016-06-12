
class DayFeatureEx:

    def __init__(self, i_pt_id, i_fixed_dt, i_gl_rises, i_last_before_bed, i_nocturnal_minimum, i_gl_rise_speeds, i_ill_years, i_age, i_gender, i_height, i_weight, i_ins_mod, i_bmi):
        self.m_pt_id = i_pt_id
        self.m_fixed_dt = i_fixed_dt

        self.m_gl_rises = i_gl_rises
        self.m_last_before_bed = i_last_before_bed
        self.m_nocturnal_minimum = i_nocturnal_minimum
        self.m_gl_rise_speeds = i_gl_rise_speeds

        self.m_ill_years = i_ill_years
        self.m_age = i_age
        self.m_gender = i_gender
        self.m_height = i_height
        self.m_weight = i_weight
        self.m_ins_mod = i_ins_mod
        self.m_bmi = i_bmi

    def __str__(self):
        return "PtId: " + str(self.m_pt_id) + \
               "\nFixed_DT: " + str(self.m_fixed_dt) + \
               "\nGlRises: " + str(self.m_gl_rises) + \
               "\nTheLastBeforeBed: " + str(self.m_last_before_bed) + \
               "\nRiseSpeeds: " + str(self.m_gl_rise_speeds) + \
               "\nNoctMin: " + str(self.m_nocturnal_minimum) + \
               "\nIll_years: " + str(self.m_ill_years) + \
               "\nAge: " + str(self.m_age) + \
               "\nGender: " + str(self.m_gender) + \
               "\nHeight: " + str(self.m_height) + \
               "\nWeight: " + str(self.m_weight) + \
               "\nIns_mod: " + str(self.m_ins_mod) + \
               "\nBMI: " + str(self.m_bmi)

    # Primary key
    def GetPtId(self):
        return self.m_pt_id

    def GetFixedDT(self):
        return self.m_fixed_dt

    # Glycemic parameters
    def GetGlRises(self):
        return self.m_gl_rises

    def GetNocturnalMinimum(self):
        return self.m_nocturnal_minimum

    def GetRoseSpeeds(self):
        return self.m_gl_rise_speeds

    # Demographic parameters
    def GetIllYears(self):
        return self.m_ill_years

    def GetAge(self):
        return self.m_age

    def GetGender(self):
        return self.m_gender

    def GetInsMod(self):
        return self.m_ins_mod

    def GetHeight(self):
        return self.m_height

    def GetWeight(self):
        return self.m_weight

    def GetBMI(self):
        return self.m_bmi