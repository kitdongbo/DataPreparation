#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FeatureExtraction import FeatureExtractor
from DataGetter import DataGetter
import datetime
g_file_name = u'D:/GDrive/Диплом 2/DataPreparation/output/Patient#2/Period_from_2000-01-08__21-40.xlsx'


def TestSeparateMeasurementsForDays():
    measurements = DataGetter.GetAllMeasurements(g_file_name,
                                                 i_patient_id_column_num=1,
                                                 i_datetime_column_num=2,
                                                 i_glucose_level_column_num=3)
    time_separator = datetime.datetime.strptime("05:00:00", "%H:%M:%S").time()
    measurements_per_day = FeatureExtractor.SeparateMeasurementsForDays(measurements, time_separator)

    assert len(measurements_per_day) == 4
    return


def TestExtractDayFeature():
    measurements = DataGetter.GetAllMeasurements(g_file_name,
                                                 i_patient_id_column_num=1,
                                                 i_datetime_column_num=2,
                                                 i_glucose_level_column_num=3)
    time_separator = datetime.datetime.strptime("05:00:00", "%H:%M:%S").time()
    measurements_per_day = FeatureExtractor.SeparateMeasurementsForDays(measurements, time_separator)
    day_measurement = measurements_per_day[1]
    day_feature = FeatureExtractor.ExtractDayFeature(day_measurement)
    assert day_feature

TestSeparateMeasurementsForDays()
TestExtractDayFeature()
