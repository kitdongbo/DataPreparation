from DayFeatureEx import DayFeatureEx

class DayFeatureExpert:
    g_hypoglycemia = 70

    @staticmethod
    def IsHypoglycemia(dfe):
        return dfe.GetNocturnalMinimum() < DayFeatureExpert.g_hypoglycemia

    @staticmethod
    def IsFeatureValid(dfe):
        if not (dfe.GetPtId() and dfe.GetFixedDT() and dfe.GetGlRises() and dfe.GetNocturnalMinimum()):
            return False, "One of field is empty"

        is_monotonous_measurements = True
        is_valid_raises = True
        for index, gl_raise in enumerate(dfe.GetGlRises()):
            if index > 0:
                if not dfe.GetGlRises()[index-1][1][0] < gl_raise[0][0]:
                    is_monotonous_measurements = False
                    break
            if not gl_raise[0][0] < gl_raise[1][0]:
                is_monotonous_measurements = False
                break
            if not gl_raise[0][1] < gl_raise[1][1]:
                is_valid_raises = False
                break
        if not dfe.GetGlRises()[-1][1][0] < dfe.GetNocturnalMinimum()[0]:
            is_monotonous_measurements = False

        if not is_monotonous_measurements:
            return False, "Glucose rises is not monotonous"
        if not is_valid_raises:
            return False, "Invalid glucose raise"

        return True, ""
