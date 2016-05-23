#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DataReader import ReadDataSet
from DataWriter import WriteDataSet
from DayFeatureExpert import DayFeatureExpert

not_fixed_data_set = ReadDataSet(u"D:\GDrive\Диплом 2\DataPreparation\output1\\not_fixed_dataset.xlsx")

fixed_data_set = list()
for record in not_fixed_data_set:
    if len(record.GetGlRises()) < 3:
        continue
    fixed_record = DayFeatureExpert.ReduceGlucoseRises(record)
    print fixed_record
    fixed_data_set.append(fixed_record)
WriteDataSet(u"D:\GDrive\Диплом 2\DataPreparation\output1\\fixed_dataset.xlsx", fixed_data_set)

