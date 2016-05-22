#!/usr/bin/env python
# -*- coding: utf-8 -*-

import openpyxl
from datetime import datetime, timedelta
from DayFeatureEx import DayFeatureEx
from DayFeatureExpert import DayFeatureExpert


def ReadDataSet(f_path):
    wb = openpyxl.load_workbook(f_path)
    ws = wb.active

    day_features = list()

    header = ws.rows[0]
    for row in ws.rows[1:]:
        pt_id = None
        fixed_dt = None
        bm_t = dict()
        m_t = dict()
        bm_gl = dict()
        m_gl = dict()
        noct_min_gl = None
        noct_min_t = None

        # parse record
        debug_row_index = None
        for index, cell in enumerate(row):
            col_name = header[index].value
            if col_name == u"№":
                debug_row_index = cell.value
            elif col_name == "PtId":
                pt_id = cell.value
            elif col_name == "DT_Fix":
                fixed_dt = datetime.strptime(cell.value, '%Y-%m-%d %H:%M:%S')
            elif col_name == "NoctMin_T":
                if cell.value == "NA":
                    continue
                noct_min_t = timedelta(seconds=int(round(float(cell.value))))
            elif col_name == "NoctMin_Gl":
                if cell.value == "NA":
                    continue
                noct_min_gl = float(cell.value)
            elif col_name.find("BMax_T") != -1:
                if cell.value == "NA":
                    continue
                key = int(col_name.split("BMax_T")[1])
                bm_t[key] = timedelta(seconds=int(round(float(cell.value))))
            elif col_name.find("Max_T") != -1:
                if cell.value == "NA":
                    continue
                key = int(col_name.split("Max_T")[1])
                m_t[key] = timedelta(seconds=int(round(float(cell.value))))
            elif col_name.find("BMax_Gl") != -1:
                if cell.value == "NA":
                    continue
                key = int(col_name.split("BMax_Gl")[1])
                bm_gl[key] = float(cell.value)
            elif col_name.find("Max_Gl") != -1:
                if cell.value == "NA":
                    continue
                key = int(col_name.split("Max_Gl")[1])
                m_gl[key] = float(cell.value)

        # checking parsed data
        if not (pt_id and fixed_dt and bm_t and m_t and bm_gl and m_gl and noct_min_gl and noct_min_t):
            print str(debug_row_index) + ": corrupted row"
            continue

        if not (len(bm_t) == len(m_t) == len(bm_gl) == len(m_gl)):
            print str(debug_row_index) + ": not full rises data"
            continue

        is_ok = True
        for key in range(1, len(bm_t) + 1):
            if not (key in m_t.keys() and key in bm_gl.keys() and key in m_gl.keys()):
                is_ok = False
                break
        if not is_ok:
            print str(debug_row_index) + ": corrupted rises data"
            continue

        glucose_rises = list()
        for key in range(1, len(bm_t) + 1):
            glucose_rises.append(((bm_t[key], bm_gl[key]), (m_t[key], m_gl[key])))

        noct_minimum = (noct_min_t, noct_min_gl)
        dfe = DayFeatureEx(pt_id, fixed_dt, glucose_rises, noct_minimum)

        is_valid, why_invalid_msg = DayFeatureExpert.IsFeatureValid(dfe)
        if not is_valid:
            print str(debug_row_index) + ": " + why_invalid_msg
            continue

        day_features.append(dfe)

    return day_features
