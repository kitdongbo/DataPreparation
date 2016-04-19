#!/usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib.dates as dates
import matplotlib.pyplot as plt
import numpy as np
import datetime

from DataGetter import DataGetter
from FeatureExtraction import ExtremaFilter
from FeatureExtraction import SeriesModifier
from FeatureExtraction import FeatureExtractor

src_path = u'D:/GDrive/Диплом 2/DataPreparation/output/Patient#2/Period_from_2000-01-08__21-40.xlsx'

measurements = DataGetter.GetAllMeasurements(src_path,
                                             i_patient_id_column_num=1,
                                             i_datetime_column_num=2,
                                             i_glucose_level_column_num=3)

smooth_measurements = SeriesModifier.Smooth(measurements)
extremal_indexes, bla = ExtremaFilter.FindExtremalMeasurements(smooth_measurements)

time_separator = datetime.datetime.strptime("05:00:00", "%H:%M:%S").time()
measurements_per_day = FeatureExtractor.SeparateMeasurementsForDays(measurements, time_separator)
day_measurement = measurements_per_day[1]

# 2nd - day
gl_level_day = np.array(map(lambda x: x.GetGlucoseLevel(), day_measurement))
datetime_day = np.array(map(lambda x: x.GetDateTime(), day_measurement))
# original
gl_level = np.array(map(lambda x: x.GetGlucoseLevel(), measurements))
datetime = np.array(map(lambda x: x.GetDateTime(), measurements))

# smoothed
sm_gl_level = np.array(map(lambda x: x.GetGlucoseLevel(), smooth_measurements))

# extrema
ex_date_time = np.array(map(lambda x: measurements[x].GetDateTime(), extremal_indexes))
ex_gl_level = np.array(map(lambda x: measurements[x].GetGlucoseLevel(), extremal_indexes))

# plot settings
fig = plt.figure()
ax = fig.add_subplot(111)
ax.xaxis.set_major_locator(dates.HourLocator())
dmyhm = dates.DateFormatter('%d.%m.%Y %H:%M')
ax.xaxis.set_major_formatter(dmyhm)
plt.xticks(rotation='vertical')
# plot data
plt.plot(datetime, gl_level, c='b')
# plt.plot(datetime, sm_gl_level, c='g')
plt.plot(ex_date_time, ex_gl_level, 'ro')
plt.plot(datetime_day, gl_level_day, 'g-')
plt.show()
