import re
import pandas as pd
import numpy as np
from sciparse import string_to_dict, dict_to_string
from datetime import datetime as dt

def parse_default(
        filename, data=None, metadata=None, read_write='r'):
    """
    Default parser for data. Assumes there is a single line of metadata at the top line in the form of a dictionary and the remainder is tabular and can be imported as a pandas DataFrame

    :param filename: Name of the file to be written
    :param data: Data to write to file
    :param metadata: Metadata to write to file
    :param read_write: "r" or "w". Read or write.
    """

    if read_write == 'r':
        with open(filename) as fh:
            string_metadata = fh.readline().rstrip('\n')
            metadata = string_to_dict(string_metadata)
            data = pd.read_csv(fh)

        return data, metadata
    elif read_write == 'w':
        with open(filename, 'w') as fh:
            metadata_line = dict_to_string(metadata) + '\n'
            fh.write(metadata_line)
            if isinstance(data, pd.DataFrame):
                data.to_csv(fh, mode='a', index=False)
            elif data is None:
                pass
            else:
                raise ValueError(f'This method only implemented for type of pd.DataFrame, you attempted to pass in type {type(data)}.')

def parse_xrd(filename):
    """
    Loads XRD data from a given filename

    :param filename: The filename to open
    :returns (data, metadata): set of data and metadata from XRD file

    """
    with open(filename) as file_handle:
        count = 0
        reg_pattern = re.compile(r'\w+=\S*\w+')
        metadata = {}
        while True:
            line = file_handle.readline()
            if line == '[Data]\n' or not line:
                break
            line = line.rstrip('\n')

            if reg_pattern.match(line):
                split_string = line.split('=')
                name = split_string[0].lower()
                val = split_string[1].lower()
                interesting_names = [
                    'drivename', 'startposition', 'date',
                     'time', 'increment', 'scantype','start',
                     'steps']
                if name in interesting_names:
                    if name == 'drivename':
                        current_drive = val
                    elif name == 'startposition':
                        metadata[current_drive] = float(val)
                    else:
                        try:
                            metadata[name] = int(val)
                        except:
                            try:
                                metadata[name] = float(val)
                            except:
                                metadata[name] = val
        data = pd.read_csv(file_handle)
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        data = data.rename(columns=lambda x: x.strip()) # Strip whitespace
        data = data.rename(columns={'Angle': 'Angle (deg)', 'Det1Disc1':
                                    'Counts'})
        return data, metadata

def parse_lcr(filename):
    metadata = parse_lcr_header(filename)
    data_start_line = find_lcr_dataline(filename)

    with open(filename, 'r') as dataFile:
        lines = dataFile.readlines()
        header_line = lines[data_start_line-1]
        header_line = header_line.replace("\n", "")
        data_types = header_line.split("\t")
        data_types = [x for x in data_types if x != ""]
        data = pd.DataFrame({})
        for dtype in data_types:
            data[dtype] = np.array([])

        lines = lines[data_start_line:-4]
        if len(lines) != metadata['n_samples']:
            raise ValueError("number lines not equal to data lines. Issue with parsing.")

        for line in lines:
            line = line.replace("\n", "")
            line_data = line.split("\t")
            line_data = [float(x) for x in line_data if x != '']
            new_data_row = pd.DataFrame({})
            for i, dtype in enumerate(data_types):
                new_data_row[dtype] = [line_data[i]]
            data = data.append(new_data_row)
    return data, metadata

def parse_lcr_header(filename):
    metadata = {}
    currentID = ''
    with open(filename, 'r') as dataFile:
        lines = dataFile.readlines()
        for line in lines:
            line = line.replace(":", " ")
            line = line.replace("\n", "")
            line = line.replace("\t", "")
            lineData = line.split(" ")
            if lineData[0] == 'ID':
                currentID = lineData[-1]
            if lineData[0] == 'MODE':
                if currentID == 'A':
                    mode = lineData[-1]
            elif lineData[0] == 'START':
                start_voltage = float(lineData[-1])
            elif lineData[0] == 'STOP':
                stop_voltage = float(lineData[-1])
            elif lineData[0] == 'STEP':
                step_voltage = float(lineData[-1])
            elif lineData[0] == 'DATE':
                recorded_date = dt.strptime(lineData[-1], "%m/%d/%Y")
            elif lineData[0] == 'TIME':
                timeData = lineData[-3] + " " + lineData[-2] + " " + lineData[-1]
                recorded_time = dt.strptime(timeData, "%H %M %S")
            elif lineData[0] == 'PNTS':
                n_samples = int(lineData[-1])
    metadata = {
        'start_voltage': start_voltage,
        'stop_voltage': stop_voltage,
        'step_voltage': step_voltage,
        'date': recorded_date,
        'time': recorded_time,
        'n_samples': n_samples,
        'mode': mode,
    }
    return metadata

def find_lcr_dataline(filename):
    with open(filename, 'r') as dataFile:
        lines = dataFile.readlines()
        currentLine = 0
        dataLines = []
        for line in lines:
            lineData = line.split(" ")
            if lineData[0] == "DATA:": # begin reading data
                data_start_line = currentLine + 3
                return data_start_line
            currentLine += 1
