import codes

import csv
import json
import sys
import datetime
import re
import os
import pathlib

import xlrd


''' Convert export from SolisCloud to json files '''

''' Exporting:'''
''' Goto Report > Inverter Report > Export, download file.xls and run ./cloud2json file.xls '''


# Dir to save output json files. Default is ./www/json, e.g. to add any historical or missed local data.
OUT_DIR = './www/json'
#OUT_DIR = './export'
# Set to True to overwrite output files
REPLACE_FILES = False
# Skip 7 row header
SKIP_ROWS = 8


FIELDS = {
    #idx: "JSON key": "Column title"
    0: { 'None': "Number" },
    1: { 'INVERTER_TIME': "Time" },
    2: { 'CURRENT_STATE': "Working State" },
    3: { 'WARNING_INFO_DATA': "Alarm Code" },
    4: { 'U_PV': "DC Voltage PvPV1(V)" },   # TODO: list U_PV ;[0,0,0,0]
    5: { 'I_PV': "DC Current PvPV1(A)" },   # TODO: list I_PV ;[0,0,0,0]
    6: { 'DC_TOTALPOWER': "DC Power PvPV1(W)" },
    7: { 'U_MPPT': "DC Voltage PvMPPT1(V)" },
    8: { 'I_MPPT': "DC Current PvMPPT1(A)" },
    # UNUSED 9: { '': "DC Power PvMPPT1(W)" },
    10: { 'U_AC': "AC Voltage L1(V)" },
    11: { 'U_AC_L2': "AC Voltage L2(V)" },  # TODO: list U_AC; [L1, L2, L3, ...]
    12: { 'U_AC_L3': "AC Voltage L3(V)" },
    13: { 'I_AC': "AC Current L1(A)" },     # TODO: list I_AC; [L1, L2, L3, ...]
    14: { 'I_AC_L2': "AC Current L2(A)" },
    15: { 'I_AC_L3': "AC Current L3(A)" },
    16: { 'FAC': "AC Frequency(Hz)" },
    17: { 'APPARENT_POWER': "Total Inverter Power(W)" },
    18: { 'E_TODAY': "Today Yield(kWh)" },
    19: { 'E_TOTAL': "Total Yield(kWh)" },
    20: { 'INVERTER_TEMP': "IGBT  Temperature(℃)" },
}


FILE = sys.argv[1]


def to_number(value):
    return(int(value.replace(',', '')))


def get_time(value):
    ''' Convert date time '''   
    ''' Return timestamp and filedate '''
    try:
        dt_obj = datetime.datetime.strptime(value, '%d/%m/%Y %H:%M:%S (%Z%z)')
        ts = int(dt_obj.strftime("%s"))
        fdate = dt_obj.strftime("%Y%m%d_%H%M%S")
        fpattern = dt_obj.strftime("%Y%m%d_%H")
        return [ts, fdate, fpattern]
    except Exception:
        pass
    return None


def get_state(value):
    try:
        for idx, state in enumerate(codes.status()):
            if value in state:
                return idx
    except Exception:
        pass
    return None


def get_error(value):
    try:
        if value  == ' ':
            return 0
        for idx, error in enumerate(codes.errors().items()):
            if value in error:
                return error[0]
    except Exception:
        pass
    return None


def write_json(fpattern, fn, fmt_json_row):
    for p in pathlib.Path(OUT_DIR, '/').glob(f'{fpattern}*'):
        if pathlib.Path.is_file(p) and not REPLACE_FILES:
            print(f'File "{p}" already exists, skipping ... ')
            return
    print(f'Writing "{fn}" ...')
    with open(f'{OUT_DIR}/{fn}', 'w', encoding='utf-8', errors='ignore') as f_json:
        json.dump(fmt_json_row, f_json)


def xls2json():
    ''' Convert input .xls file and save to JSON (xlrd) '''
    book = xlrd.open_workbook(FILE)
    sheet = book.sheet_by_index(0)
    for row_idx in range(SKIP_ROWS, sheet.nrows):
        row_values = sheet.row_values(row_idx)
        #print(f'DEBUG: Row {row_idx}: {row_values}"')
        fmt_json_row = {
            'NOTIFICATION': {
                'INVERTER1': {}
            }
        }
        ts = None
        fdate = None
        fpattern = None
        if row_values[1]:
            ts, fdate, fpattern = get_time(row_values[1])
            fmt_json_row['NOTIFICATION']['INVERTER1']['INVERTER_TIME'] = ts
        if row_values[2]:        
            fmt_json_row['NOTIFICATION']['INVERTER1']['CURRENT_STATE'] = get_state(row_values[2])
        if row_values[3]:
            fmt_json_row['NOTIFICATION']['INVERTER1']['WARNING_INFO_DATA'] = get_error(row_values[3])
        for i in range(4,sheet.ncols):
            if FIELDS.get(i):
                key = next(iter(FIELDS[i].keys()))
                value = None
                if key == 'E_TOTAL':
                    value = format(row_values[i], ".0f")
                elif key == 'APPARENT_POWER':
                    value = format(row_values[i], ".0f")
                elif key == 'FAC':
                    value = format(row_values[i]*100, ".0f")
                elif isinstance(row_values[i], float):                    
                    value = format(row_values[i]*10, ".0f")
                else:
                    #value = int(row_values[i])
                    value = row_values[i]
                #print('DEBUG: float', key, ":", row_values[i], '->', value)
                fmt_json_row['NOTIFICATION']['INVERTER1'][key] = value
        if fpattern and fdate:
            write_json(fpattern, f'{fdate}-solis.json', fmt_json_row)
        else:
            print(f'ERROR: {row_values}')


def csv2json():
    ''' Convert input .csv file and save to JSON (needs converting) '''
    csvfile = open(FILE, 'r')
    # fieldnames =[next(iter(x.values())) for x in FIELDS.values()]
    # reader = csv.DictReader(csvfile, fieldnames, delimiter=';')
    reader = csv.reader(csvfile, delimiter=';')
    r = 0
    for row in reader:
        if r > SKIP_ROWS:
            fmt_json_row = {
                'NOTIFICATION': {
                    'INVERTER1': {}
                }
            }
            ts = None
            fdate = None
            fpattern = None
            if row[1]:
                ts, fdate,fpattern = get_time([row[1]])
                fmt_json_row['NOTIFICATION']['INVERTER1']['INVERTER_TIME'] = to_number(ts)
            if row[2]:
                fmt_json_row['NOTIFICATION']['INVERTER1']['CURRENT_STATE'] = get_state([row[2]])
            if row[3]:
                fmt_json_row['NOTIFICATION']['INVERTER1']['WARNING_INFO_DATA'] = get_error([row[3]])
            i = 0
            for i in range(4, len(row)):
                if FIELDS.get(i):
                    value = None
                    if re.match(r'\d+', row[i]):
                        value = int(str(row[i]).replace('.', ''))
                    else:
                        value = row[i]
                    fmt_json_row['NOTIFICATION']['INVERTER1'][next(iter(FIELDS[i].keys()))] = value
                i = 1+i
            #print('DEBUG:', fn, fmt_json_row)
            if fpattern and fdate:
                write_json(fpattern, f'{fdate}-solis.json', fmt_json_row)
            else:
                print(f'ERROR: {row}')
        r = r+1


def main():                    
    if os.path.splitext(FILE)[1] == '.xls':
        xls2json()
    if os.path.splitext(FILE)[1] == '.csv':
        csv2json()


if __name__ == "__main__":
    main()
