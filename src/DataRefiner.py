#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from DataGetter import DataGetter
from FeatureExtraction import FeatureExtractor
from FeatureExtraction import SeriesModifier as SM
import datetime
import matplotlib.dates as dates
import matplotlib.pyplot as plt
from matplotlib.widgets import Button


class DayMeasurementsIterator:
    g_ts = datetime.datetime.strptime("05:00:00", "%H:%M:%S").time()

    def __init__(self, root_path):
        self.m_files = list()
        for root, dirs, files in os.walk(root_path):
            for cur_file in files:
                if cur_file.endswith('.xlsx'):
                    src_path = os.path.join(root, cur_file)
                    self.m_files.append(src_path)
        self.m_next_file_index = 0
        self.m_cur_day_measurements = list()
        self.m_next_day_measurement_index = 0
        self.m_current = None

    def is_empty(self):
        is_measurements_empty = self.m_next_day_measurement_index == len(self.m_cur_day_measurements)
        is_files_empty = self.m_next_file_index == len(self.m_files)
        return is_measurements_empty and is_files_empty

    def _read_next_file(self):
        assert self.m_next_file_index < len(self.m_files)
        src_file = self.m_files[self.m_next_file_index]
        con_ms = DataGetter.GetAllMeasurements(src_file,
                                               i_patient_id_column_num=1,
                                               i_datetime_column_num=2,
                                               i_glucose_level_column_num=3)
        self.m_cur_day_measurements = FeatureExtractor.SeparateMeasurementsForDays(con_ms, DayMeasurementsIterator.g_ts)
        self.m_next_file_index += 1
        self.m_next_day_measurement_index = 0

    def next(self):
        if self.is_empty():
            raise EOFError("there is no more measurements")
        if self.m_next_day_measurement_index == len(self.m_cur_day_measurements):
            self._read_next_file()
        measurements = self.m_cur_day_measurements[self.m_next_day_measurement_index]
        self.m_current = SM.EraseNulls(measurements)
        self.m_next_day_measurement_index += 1
        return self.m_current

    def current(self):
        return self.m_current

root_path = u'D:/GDrive/Диплом 2/DataPreparation/output/Patient#12'
dm_iter = DayMeasurementsIterator(root_path)
day_measurements = None
day_feature = None

ax = plt.subplot(111)
plt.subplots_adjust(bottom=0.25)

axcolor = 'lightgoldenrodyellow'
acceptax = plt.axes([0.6, 0.025, 0.1, 0.04])
button_accept = Button(acceptax, 'Accept', color=axcolor, hovercolor='0.975')
rejectax = plt.axes([0.8, 0.025, 0.1, 0.04])
button_reject = Button(rejectax, 'Reject', color=axcolor, hovercolor='0.975')

labels = ['bf', 'dn', 'sp']


def update_canvas_or_close():
    if dm_iter.is_empty():
        plt.close()
    else:
        ax.cla()
        dm = dm_iter.next()
        dt = map(lambda x: x.GetDateTime(), dm)
        m = map(lambda x: x.GetGlucoseLevel(), dm)
        ax.plot(dt, m, 'b')

        df = FeatureExtractor.ExtractDayFeature(dm)
        if df:
            dfrs = df.GetRiseFeatures()
            for i, dfr in enumerate(dfrs):
                m1 = dfr.GetBeforeMax()
                m2 = dfr.GetMax()
                m3 = dfr.GetAfterMax()
                m_list = list([m1, m2, m3])
                datetimes = map(lambda x: x.GetDateTime(), m_list)
                data = map(lambda x: x.GetGlucoseLevel(), m_list)
                ax.plot(datetimes, data, 'ro')
                label = labels[i]
                for index, m in enumerate(m_list):
                    ax.annotate(label+str(index), xy=(m.GetDateTime(), m.GetGlucoseLevel()),
                                xytext=(m.GetDateTime(), m.GetGlucoseLevel()+5))
            nm = df.GetNocturnalMinimum()
            ax.plot(nm.GetDateTime(), nm.GetGlucoseLevel(), 'go')
        plt.draw()

def accept_func(event):
    print 'Accept'
    update_canvas_or_close()
button_accept.on_clicked(accept_func)


def reject_func(event):
    print 'Reject'
    update_canvas_or_close()
button_reject.on_clicked(reject_func)

plt.show()
