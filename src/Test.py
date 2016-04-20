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
rise_features = []
for day_measurement in measurements_per_day:
    day_feature = FeatureExtractor.ExtractDayFeature(day_measurement)
    if day_feature:
        rise_features.extend(day_feature.GetRiseFeatures())

gl_b_level = np.array(map(lambda x: x.GetBeforeMax().GetGlucoseLevel(), rise_features))
dt_b = np.array(map(lambda x: x.GetBeforeMax().GetDateTime(), rise_features))

gl_a_level = np.array(map(lambda x: x.GetAfterMax().GetGlucoseLevel(), rise_features))
dt_a = np.array(map(lambda x: x.GetAfterMax().GetDateTime(), rise_features))

gl_m_level = np.array(map(lambda x: x.GetMax().GetGlucoseLevel(), rise_features))
dt_m = np.array(map(lambda x: x.GetMax().GetDateTime(), rise_features))

# original
gl_level = np.array(map(lambda x: x.GetGlucoseLevel(), measurements))
datetime = np.array(map(lambda x: x.GetDateTime(), measurements))

# plot settings
fig = plt.figure()
ax = fig.add_subplot(111)
ax.xaxis.set_major_locator(dates.HourLocator())
dmyhm = dates.DateFormatter('%d.%m.%Y %H:%M')
ax.xaxis.set_major_formatter(dmyhm)
plt.xticks(rotation='vertical')
# plot data
plt.plot(datetime, gl_level, c='b')

plt.plot(dt_b, gl_b_level, 'go')
plt.plot(dt_m, gl_m_level, 'yo')
plt.plot(dt_a, gl_a_level, 'ro')
plt.show()
