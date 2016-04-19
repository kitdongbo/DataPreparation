from DataGetter import PatientGlucoseMeasurement
import numpy
import datetime
import itertools


class ExtremaFilter:
    @staticmethod
    def _Sign(i_val):
        if i_val == 0:
            return 0
        return i_val / abs(i_val) # how about (i_val>0)-(i_val<0) ?

    @staticmethod
    def _IsExtremalValue(i_prev, i_val, i_next):
        if ExtremaFilter._Sign(i_val-i_prev) != ExtremaFilter._Sign(i_next-i_val):
            return True
        return False

    @staticmethod
    def _WhichExtremalValue(i_prev, i_val, i_next):
        # "None" --- not an extrema
        # "Max" --- maximum
        # "Min" --- minimum
        prev_sign = ExtremaFilter._Sign(i_val - i_prev)
        next_sign = ExtremaFilter._Sign(i_next - i_val)
        if prev_sign == next_sign:
            return "None"
        if prev_sign > next_sign:
            return "Max"
        if prev_sign < next_sign:
            return "Min"

    @staticmethod
    def FindExtremalMeasurements(measurements):
        # indexes, types
        # type in {"Max", Min}
        just_glucose_level = map(lambda x: x.GetGlucoseLevel(), measurements)
        extrema_views = map(lambda x, pre_x, after_x: ExtremaFilter._WhichExtremalValue(pre_x, x, after_x),
                            just_glucose_level[1:-1], just_glucose_level[2:], just_glucose_level[:-2])
        extrema_indexes_types = filter(lambda i_x: i_x[1] != "None", enumerate(extrema_views))
        extremal_indexes = map(lambda i_t: i_t[0]+1, extrema_indexes_types)
        extrema_types = map(lambda i_t: i_t[1], extrema_indexes_types)
        return extremal_indexes, extrema_types


class SeriesModifier:
    @staticmethod
    def Smooth(measurements, window_len=10, window='hanning'):
        # get just glucose values
        x = numpy.array(map(lambda m: m.GetGlucoseLevel(), measurements))

        # code of smoothing from https://mail.scipy.org/pipermail/scipy-dev/2006-January/005182.html
        if x.ndim != 1:
            raise ValueError("smooth only accepts 1 dimension arrays.")

        if x.size < window_len:
            raise ValueError("Input vector needs to be bigger than window size.")

        if window not in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
            raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")

        s = numpy.r_[2*x[0]-x[window_len:1:-1], x, 2*x[-1]-x[-1:-window_len:-1]]

        if window == 'flat':
            w = numpy.ones(window_len, 'd')
        else:
            w = eval('numpy.'+window+'(window_len)')

        y = numpy.convolve(w/w.sum(), s, mode='same')
        smoothed_gl = y[window_len-1:-window_len+1]

        # update measurements
        result = map(lambda m, new_gl: PatientGlucoseMeasurement(i_pt_id=m.GetPtId(), i_datetime=m.GetDateTime(),
                                                                 i_glucose_level=new_gl),
                     measurements, smoothed_gl)
        return result


class FeatureExtractor:
    class RiseFeature:
        def __init__(self, i_max, i_before_max, i_after_max):
            self.m_max = i_max
            self.m_before_max = i_before_max
            self.m_after_max = i_after_max

        def GetMax(self):
            return self.m_max

        def GetBeforeMax(self):
            return self.m_before_max

        def GetAfterMax(self):
            return self.m_after_max

        def GetRiseSpeed(self):
            dt = self.m_max.GetDateTime() - self.m_before_max.GetDateTime()
            dg = self.m_max.GetGlucoseLevel() - self.m_before_max.GetGlucoseLevel()
            return dg / dt.hour()

        def GetFallSpeed(self):
            dt = self.m_after_max.GetDateTime() - self.m_max.GetDateTime()
            dg = self.m_max.GetGlucoseLevel() - self.m_after_max.GetGlucoseLevel()
            return dg / dt.hour()

    class DayFeature:
        def __init__(self, i_rise_features, i_nocturnal_minimum, i_hypo_val=70):
            self.m_rise_features = i_rise_features
            self.m_nocturnal_minimum = i_nocturnal_minimum
            self.m_hypo_val = i_hypo_val

        def GetRiseFeatures(self):
            return self.m_rise_features

        def GetNocturnalMinimum(self):
            return self.m_nocturnal_minimum

        def IsHypoglucemia(self):
            return self.GetNocturnalMinimum() < self.m_hypo_val


    @staticmethod
    def ExtractFeatures(all_patient_measurements):
        # patient_all_measurements: array(array(continuous_measurements))
        # return: array(array(day_features))

        time_separator = datetime.datetime.strptime("05:00:00", "%H:%M:%S").time()
        list_of_continuous_day_measurements = [] # array(array(measurements_while_day))
        for continuous_measurement in all_patient_measurements:
            day_measurements = FeatureExtractor.SeparateMeasurementsForDays(continuous_measurement, time_separator)
            if day_measurements:
                list_of_continuous_day_measurements.append(day_measurements)

        consumption_schedule = FeatureExtractor.CalculatePatientSchedule(list_of_continuous_day_measurements)

        list_of_continuous_day_features = []
        for continuous_day_measurements in list_of_continuous_day_measurements:
            continuous_day_features = []
            for day_measurements in continuous_day_measurements:
                day_features = FeatureExtractor.ExtractDayFeature(consumption_schedule, day_measurements)
                if day_features:
                    continuous_day_features.append(day_features)
            if continuous_day_features:
                list_of_continuous_day_features.append(continuous_day_features)
        return list_of_continuous_day_features

    @staticmethod
    def SeparateMeasurementsForDays(continuous_measurement, time_separator):
        # continuous_measurement: array of measurements
        # time_separator: datetime.time that separate measurements for days
        # return: array(full_day_measurement)

        measurements_for_days = []
        if not continuous_measurement:
            return measurements_for_days

        one_day_measurements = []
        date_time_to = datetime.datetime.combine(continuous_measurement[0].GetDateTime().date(), time_separator) + datetime.timedelta(days=1)
        for measurement in continuous_measurement:
            if measurement.GetDateTime() <= date_time_to:
                one_day_measurements.append(measurement)
            else:
                measurements_for_days.append(one_day_measurements)
                one_day_measurements = [measurement]
                date_time_to += datetime.timedelta(days=1)
        if one_day_measurements:
            measurements_for_days.append(one_day_measurements)

        # may be needed filter out not full front and back days measurements
        # may be needed check if middle days measurements are full
        return measurements_for_days

    @staticmethod
    def CalculatePatientSchedule(list_of_continuous_day_measurements):
        # list_of_continuous_day_measurements: array(array(continuous_measurements))
        # return: dictionary(time_name, time_value)

        usual_food_consumption_time = {
            'night-bf': datetime.datetime.strptime("05:00:00", "%H:%M:%S").time(),
            'bf-dn': datetime.datetime.strptime("13:00:00", "%H:%M:%S").time(),
            'dn-sp': datetime.datetime.strptime("20:00:00", "%H:%M:%S").time(),
            'sp-night': datetime.datetime.strptime("23:59:00", "%H:%M:%S").time()
        }

        return usual_food_consumption_time

    @staticmethod
    def _ProjectTimeListOnTimeList(time_list, time_separators):
        # time_list: array(time)
        # time_separators: array(time)
        # return: array(index)

        result_indexes = []
        if (time_list is None) or (time_separators is None):
            return result_indexes
        if (len(time_list) == 0) or (len(time_separators) == 0):
            return result_indexes

        separator_index = 0
        for index, value in enumerate(time_list):
            while time_separators[separator_index] < value:
                result_indexes.append(index)
                separator_index+=1
                if separator_index >= len(time_separators):
                    break
        while separator_index < len(time_separators):
            result_indexes.append(len(time_list)-1)
            separator_index += 1
        return result_indexes

    @staticmethod
    def _ExtractRiseFeature(measurements):
        indexes, types = ExtremaFilter.FindExtremalMeasurements(measurements)

        max_index = None
        for count, index in enumerate(indexes):
            if types[count] == 'Min':
                continue
            measurement = measurements[index]
            if (not max_index) or (measurements[max_index].GetGlucoseLevel() < measurement.GetGlucoseLevel()):
                max_index = index

        if not max_index:
            return None

        left_min_index = None
        right_min_index = None
        for count, index in enumerate(indexes):
            if types[count] == 'Max':
                continue
            measurement = measurements[index]
            if index < max_index:
                if not left_min_index or left_min_index > measurement.GetGlucoseLevel():
                    left_min_index = index
            else:
                if not right_min_index or right_min_index > measurement.GetGlucoseLevel():
                    right_min_index = index

        if not left_min_index or not right_min_index:
            return None

        feature = FeatureExtractor.RiseFeature(measurements[max_index],
                                               measurements[left_min_index],
                                               measurements[right_min_index])
        return feature

    @staticmethod
    def ExtractDayFeature(patient_context, day_measurements):
        # patient_context: dictionary(time_name, time_value)
        # day_measurements: array of measurements
        # return: DayFeature

        time_separators = list([patient_context['bf-dn'], patient_context['dn-sp'], patient_context['sp-night']])
        time_iterator = itertools.cycle(time_separators)
        current_time = time_iterator.next()
        time_indexes = []
        for i in range(0, len(day_measurements) - 1):
            pre_measurement_datetime = day_measurements[i].GetDateTime()
            post_measurement_datetime = day_measurements[i + 1].GetDateTime()
            possible_datetime1 = datetime.datetime.combine(pre_measurement_datetime.date(), current_time)
            possible_datetime2 = datetime.datetime.combine(post_measurement_datetime.date(), current_time)
            if ((pre_measurement_datetime <= possible_datetime1 ) and (possible_datetime1 < post_measurement_datetime)) or ((pre_measurement_datetime <= possible_datetime2) and (possible_datetime2 < post_measurement_datetime)):
                time_indexes.append(i)
                current_time = time_iterator.next()

        if (time_indexes is None) or (len(time_indexes) != len(time_separators)):
            return None

        rise_features = []
        index_from = 0
        for index_to in time_indexes:
            rise_feature = FeatureExtractor._ExtractRiseFeature(day_measurements[index_from:index_to])
            if rise_feature:
                rise_features.append(rise_feature)
                index_from = index_to
            else:
                return None

        nocturnal_minimum = min(map(lambda x: x.GetGlucoseValue(), day_measurements[index_from:]))

        day_features = FeatureExtractor.DayFeature(rise_features, i_nocturnal_minimum=nocturnal_minimum)
        return day_features
