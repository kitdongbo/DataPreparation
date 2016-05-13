from DataGetter import PatientGlucoseMeasurement
import datetime
from Features import DayFeature, RiseFeature

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
    def FindExtremalMeasurements(measurements, types=('Max', 'Min')):
        just_glucose_level = map(lambda x: x.GetGlucoseLevel(), measurements)
        extrema_views = map(lambda pre_x, x, after_x: ExtremaFilter._WhichExtremalValue(pre_x, x, after_x),
                            just_glucose_level[:-2],
                            just_glucose_level[1:-1],
                            just_glucose_level[2:])
        result = map(lambda res_i_x: measurements[1:-1][res_i_x[0]], filter(lambda i_x: i_x[1] in types, enumerate(extrema_views)))
        return result


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

    @staticmethod
    def EraseNulls(measurements):
        m_without_null = [x for x in measurements if x.GetGlucoseLevel() > 5]
        return m_without_null


class FeatureExtractor:

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

        list_of_continuous_day_features = []
        for continuous_day_measurements in list_of_continuous_day_measurements:
            continuous_day_features = []
            for day_measurements in continuous_day_measurements:
                day_features = FeatureExtractor.ExtractDayFeature(day_measurements)
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
    def _IsOkToBeNextMaxMeasurement(i_ms, i_m, i_min_delta):
        if not i_ms:
            return True
        for m in i_ms:
            this_delta = m.GetDateTime() - i_m.GetDateTime()
            if abs(this_delta) < i_min_delta:
                return False
        return True

    @staticmethod
    def _GetMinFromTimeRange(measurements, datetime_from, datetime_to):
        min_measurement = None
        for measurement in measurements:
            this_datetime = measurement.GetDateTime()
            if this_datetime < datetime_from or datetime_to < this_datetime:
                continue
            if not min_measurement or min_measurement.GetGlucoseLevel() > measurement.GetGlucoseLevel():
                min_measurement = measurement
        return min_measurement

    @staticmethod
    def _IsMonotonous(measurements):
        if len(measurements) < 2:
            return True
        for i in range(0, len(measurements) - 1):
            dt_past = measurements[i].GetDateTime()
            dt_next = measurements[i+1].GetDateTime()
            if dt_next < dt_past:
                return False
        return True

    @staticmethod
    def _IsFullDay(monotonous_measurements):
        if not monotonous_measurements:
            return False
        first_measurement_dt = monotonous_measurements[0].GetDateTime()
        last_measurement_dt = monotonous_measurements[-1].GetDateTime()
        time_delta = last_measurement_dt - first_measurement_dt
        if (time_delta < datetime.timedelta(hours=25)) and (time_delta > datetime.timedelta(hours=23)):
            return True
        return False

    @staticmethod
    def ExtractDayFeature(day_measurements):
        # day_measurements: array of measurements
        # return: DayFeature
        if not FeatureExtractor._IsMonotonous(day_measurements) or not FeatureExtractor._IsFullDay(day_measurements):
            return None

        max_measurements = ExtremaFilter.FindExtremalMeasurements(day_measurements, types=('Max'))
        max_measurements.sort(key=lambda m: m.GetGlucoseLevel(), reverse=True)
        needed_max_count = 3
        min_distance_between_max = datetime.timedelta(hours=5)
        fixed_max_measurements = []
        for measurement in max_measurements:
            if FeatureExtractor._IsOkToBeNextMaxMeasurement(fixed_max_measurements, measurement, min_distance_between_max):
                fixed_max_measurements.append(measurement)
                if len(fixed_max_measurements) == needed_max_count:
                    break
            else:
                continue
        if len(fixed_max_measurements) != needed_max_count:
            return None

        fixed_max_measurements.sort(key=lambda m: m.GetDateTime())

        rise_features = []
        time_area_around_max = datetime.timedelta(hours=3)
        for mm in fixed_max_measurements:
            dt_max = mm.GetDateTime()
            min_before = FeatureExtractor._GetMinFromTimeRange(day_measurements, dt_max - time_area_around_max, dt_max)
            min_after = FeatureExtractor._GetMinFromTimeRange(day_measurements, dt_max, dt_max + time_area_around_max)
            if not min_before or not min_after:
                return None
            rise_feature = RiseFeature(mm, min_before, min_after)
            rise_features.append(rise_feature)

        night_end = day_measurements[-1].GetDateTime() # ~05:00
        night_start = night_end - datetime.timedelta(hours=5)
        nocturnal_minima_measurement = FeatureExtractor._GetMinFromTimeRange(day_measurements, night_start, night_end)
        if not nocturnal_minima_measurement:
            return None

        day_feature = DayFeature(rise_features, i_nocturnal_minimum=nocturnal_minima_measurement)
        return day_feature
