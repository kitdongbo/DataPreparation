class ExtremaFilter:
    @staticmethod
    def _Sign(i_val):
        if i_val == 0:
            return 0
        return i_val / abs(i_val)

    @staticmethod
    def _IsExtremalValue(i_prev, i_val, i_next):
        if ExtremaFilter._Sign(i_val-i_prev) != ExtremaFilter._Sign(i_next-i_val):
            return True
        return False

    @staticmethod
    def ExtractExtremalMeasurements(measurements):
        just_glucose_level = map(lambda x: x.GetGlucoseLevel(), measurements)
        predicate_values = map(lambda x, pre_x, after_x: ExtremaFilter._IsExtremalValue(pre_x, x, after_x),
                               just_glucose_level[1:-1], just_glucose_level[2:], just_glucose_level[:-2])
        indexed_extremal_measurements = filter(lambda index_x: predicate_values[index_x[0]], enumerate(measurements[1:-1]))
        extremal_measurements = map(lambda x: x[1], indexed_extremal_measurements)
        return extremal_measurements
