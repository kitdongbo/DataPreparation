
class DayFeatureEx:

    def __init__(self, i_pt_id, i_fixed_dt, i_gl_rises, i_nocturnal_minimum):
        self.m_pt_id = i_pt_id
        self.m_fixed_dt = i_fixed_dt
        self.m_gl_rises = i_gl_rises
        self.m_nocturnal_minimum = i_nocturnal_minimum

    def __str__(self):
        return "PtId: " + str(self.m_pt_id) + ", Fixed_DT: " + str(self.m_fixed_dt) + ", GlRises: " + str(self.m_gl_rises) + ", NoctMin: " + str(self.m_nocturnal_minimum)

    def GetPtId(self):
        return self.m_pt_id

    def GetFixedDT(self):
        return self.m_fixed_dt

    def GetGlRises(self):
        return self.m_gl_rises

    def GetNocturnalMinimum(self):
        return self.m_nocturnal_minimum
