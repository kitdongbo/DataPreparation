from datetime import timedelta


class RiseFeature:
    def __init__(self, i_max, i_before_max):
        self.m_max = i_max
        self.m_before_max = i_before_max

    def _IsNotEmpty(self):
        if not self.m_max or not self.m_before_max:
            return False
        return True

    def _IsMonotonous(self):
        bt = self.m_before_max.GetDateTime()
        mt = self.m_max.GetDateTime()
        if bt < mt:
            return True
        return False

    def _IsRising(self):
        bg = self.m_before_max.GetGlucoseLevel()
        mg = self.m_max.GetGlucoseLevel()
        if bg < mg:
            return True
        return False

    def GetMax(self):
        return self.m_max

    def GetBeforeMax(self):
        return self.m_before_max

    def GetRiseSpeed(self):
        dt = self.m_max.GetDateTime() - self.m_before_max.GetDateTime()
        dg = self.m_max.GetGlucoseLevel() - self.m_before_max.GetGlucoseLevel()
        return dg / dt.hour()

    def IsValid(self):
        if not self._IsNotEmpty():
            return False
        if not self._IsMonotonous():
            return False
        if not self._IsRising():
            return False
        return True


class DayFeature:
    def __init__(self, i_rise_features, i_nocturnal_minimum, i_hypo_val=70):
        self.m_rise_features = i_rise_features
        self.m_nocturnal_minimum = i_nocturnal_minimum
        self.m_hypo_val = i_hypo_val

    def _IsNotEmpty(self):
        if not self.m_nocturnal_minimum:
            return False
        if not self.m_rise_features:
            return False
        if len(self.m_rise_features) == 0:
            return False
        return True

    def _IsMonotonous(self):
        for i, rf in enumerate(self.m_rise_features[:-1]):
            prev = self.m_rise_features[i]
            next = self.m_rise_features[i+1]
            if prev.GetMax().GetDateTime() >= next.GetBeforeMax().GetDateTime():
                return False
        last = self.m_rise_features[-1]
        if last.GetMax().GetDateTime() >= self.m_nocturnal_minimum.GetDateTime():
            return False
        return True

    def _IsInOneDay(self):
        start_time = self.m_rise_features[0].GetBeforeMax().GetDateTime()
        end_time = self.m_nocturnal_minimum.GetDateTime()
        if end_time - start_time <= timedelta(days=1):
            return True
        return False

    def GetRiseFeatures(self):
        return self.m_rise_features

    def GetNocturnalMinimum(self):
        return self.m_nocturnal_minimum

    def IsHypoglucemia(self):
        return self.GetNocturnalMinimum() < self.m_hypo_val

    def SetRiseFeatures(self, i_rise_features):
        self.m_rise_features = i_rise_features

    def SetNocturnalMinimum(self, i_nocturnal_minimum):
        self.m_nocturnal_minimum = i_nocturnal_minimum

    def IsValid(self):
        if not self._IsNotEmpty():
            return False
        for rf in self.m_rise_features:
            if not rf.IsValid():
                return False
        if not self._IsMonotonous():
            return False
        if not self._IsInOneDay():
            return False
        return True
