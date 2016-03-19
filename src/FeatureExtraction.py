from DataGetter import PatientGlucoseMeasurement
import numpy

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

        # update measurements measurements
        result = map(lambda m, new_gl: PatientGlucoseMeasurement(i_pt_id=m.GetPtId(), i_datetime=m.GetDateTime(),
                                                                 i_glucose_level=new_gl),
                     measurements, smoothed_gl)
        return result

