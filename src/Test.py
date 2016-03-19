#!/usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib.dates as dates
import matplotlib.pyplot as plt
import numpy as np

from DataGetter import DataGetter
from FeatureExtraction import ExtremaFilter

src_path = u'D:/GDrive/Диплом 2/DataPreparation/output/Patient#2/Period_from_2000-01-08__21-40.xlsx'

measurements = DataGetter.GetAllMeasurements(src_path,
                                             i_patient_id_column_num=1,
                                             i_datetime_column_num=2,
                                             i_glucose_level_column_num=3)

extremal_measurements = ExtremaFilter.ExtractExtremalMeasurements(measurements)

datetime = np.array(map(lambda x: x.GetDateTime(), measurements))
gl_level = np.array(map(lambda x: x.GetGlucoseLevel(), measurements))

ex_date_time = np.array(map(lambda x: x.GetDateTime(), extremal_measurements))
ex_gl_level = np.array(map(lambda x: x.GetGlucoseLevel(), extremal_measurements))

print '\n'.join(map(str, extremal_measurements))

fig = plt.figure()
ax = fig.add_subplot(111)
ax.xaxis.set_major_locator(dates.DayLocator())
dmyhm = dates.DateFormatter('%d.%m.%Y %H:%M')
ax.xaxis.set_major_formatter(dmyhm)
plt.xticks(rotation='vertical')
plt.plot(datetime, gl_level, c='b')
plt.plot(ex_date_time, ex_gl_level, 'ro')
plt.show()
