import re
import pandas as pd

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