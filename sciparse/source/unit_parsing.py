import pint
import re
from ast import literal_eval
from sciparse import ureg

def sampling_period(data):
    """
    Extracts the sample period from a pandas DataFrame assuming that data is evenly spaced in time. Uses the difference in time between the first and second data points to determine the sampling period  and sampling frequency.

    :param data: Pandas array with Time (including units, i.e. Time (ms))
    :returns sampling_period: Sampling period as a pint quantity
    """
    # For now, assume time is the first variable in the column
    columns_names = data.columns.values
    time_column = 0
    time_string = columns_names[time_column]
    if len(data) < 2:
        raise ValueError(f'Data does not have enough points to compute a sampling period. Only has {len(data)} ponits')
    delta_time = data[time_string][1] - data[time_string][0]

    sampling_period = delta_time * title_to_quantity(time_string)
    return sampling_period

def frequency_bin_size(data):
    """
    Extracts the frequency bin (in Hz, as a pint unit) from a PSD dataset.

    :param data: Input power spectral density as a Pandas Array
    :returns bin_size: frequency bin size as a pint unit
    """
    column_names = data.columns.values
    frequency_column = 0
    frequency_string = column_names[frequency_column]
    if len(data) < 2:
        raise ValueError(f'Data does not have enough points to compute a frequency bin size. Only has {len(data)} ponits')
    delta_frequency = data[frequency_string].iloc[1] - data[frequency_string].iloc[0]

    bin_size = delta_frequency * title_to_quantity(frequency_string)
    return bin_size

def title_to_quantity(title_string, return_name=False):
    """
    Extracts unit from a column name such as Time (ms).

    :param title_string: The string to look for the unit
    :param return_name: Whether to return a tuple containing the base name and the unit.
    """
    # Search for anything in parentheses, interpret as a unit.
    # Squared units are fine.
    unit_pattern = re.compile(r'\(.*\)') # Find the thing in parentheses.
    match = unit_pattern.search(title_string)
    if match == None:
        quantity = ureg.Quantity(1)
        bare_unit_string = ''
        unit_string_parens = ''
    else:
        bare_unit_string = match.group()[1:-1] # remove parentheses
        unit_string_parens = match.group()
        quantity = 1 * ureg.parse_expression(bare_unit_string)

    if return_name:
        name = title_string.replace(unit_string_parens , '').rstrip()
        return quantity, name
    else:
        return quantity

def quantity_to_title(quantity, name=None):
    """
    Converts a quantity into a standard title
    """
    standard_mapping = {
        ureg.V: 'voltage',
        ureg.A: 'current',
        ureg.ohm: 'impedance',
        ureg.V**2: 'power',
        ureg.A**2: 'power',
        ureg.V**2/ureg.Hz: 'PSD',
        ureg.A**2/ureg.Hz: 'PSD',
        ureg.ohm**2: 'power',
        ureg.Hz: 'frequency',
        ureg.m: 'wavelength',
        ureg.s: 'time',
        ureg.degK: 'temperature',
        ureg.degC: 'temperature',
        ureg.degF: 'temperature',
        ureg.J: 'energy',
        ureg.W: 'power',
        ureg.Unit('dimensionless'): '',
    }
    if not name:
        standard_unit = to_standard_quantity(quantity).units
        title_prefix = standard_mapping[standard_unit]
    else:
        title_prefix = name

    if quantity.dimensionless:
        title = title_prefix
    else:
        title = title_prefix + ' ({:~})'.format(quantity.units)

    return title

def to_standard_quantity(quantity):
    """
    :param quantity: Pint quantity in non-standard form (i.e. mV)
    """
    unit = quantity.units
    if quantity.dimensionless:
        base_unit = ureg.Quantity(1)

    unit_str_list = re.split(r' / | \* ', str(unit))
    quantity_list = [ureg.parse_expression(unit_str) \
            for unit_str in unit_str_list]

    if len(quantity_list) == 1 and not quantity.dimensionless:
        target_quantity = quantity_list[0]
        contains_power = '**' in str(target_quantity)
        if contains_power: # We have a power to deal with
            unit_power = int(str(unit)[-1])
            unit_base_str = str(unit)[:-5]
            return_tuple = ureg.parse_unit_name(str(unit_base_str))
            (prefix, base_unit, _) = return_tuple[0]
            base_unit = ureg.Quantity(1, base_unit)**unit_power
        else:
            return_tuple = ureg.parse_unit_name(str(unit))
            (prefix, base_unit, _) = return_tuple[0]

    elif len(quantity_list) > 1 and not quantity.dimensionless:
        standard_quantity_list = \
            [to_standard_quantity(q) for q in quantity_list]
        multiplication_locations = \
            [x.span()[0] for x in re.finditer(r' \* ', str(quantity))]
        division_locations = \
            [x.span()[0] for x in re.finditer(r' / ', str(quantity))]
        operator_locations = multiplication_locations + division_locations
        operator_locations.sort()
        base_unit = standard_quantity_list[0]
        for q in standard_quantity_list[1:]:
            next_index = operator_locations.pop(0)
            if next_index in multiplication_locations:
                base_unit *= q
            elif next_index in division_locations:
                base_unit /= q


    new_quantity = quantity.magnitude * ureg.Quantity(1, unit).to(base_unit)
    return new_quantity

def is_scalar(quantity):
    data_is_scalar =  isinstance(quantity, (int, float))
    if isinstance(quantity, pint.Quantity):
        data_is_scalar = isinstance(quantity.magnitude, (int, float))
    return data_is_scalar

def dict_to_string(metadata):
    """
    Converts a dictionary, potentially containing pint units, into a human- and machine-readable string

    :param metadata: Dictionary of metadata to be saved
    """
    dict_to_write = {}
    for k, v in metadata.items():
        if isinstance(v, pint.Quantity):
            name_string = quantity_to_title(v, name=k)
            value = v.magnitude
        else:
            name_string = str(k)
            value = v
        dict_to_write[name_string] = value
    return str(dict_to_write)

def string_to_dict(metadata_string):
    """
    Converts a human-readable string into a dictionary, with pint units as applicable.

    :param metadata_string: The string to be converted into a set of metadata
    """
    input_dict = literal_eval(metadata_string)
    return_dict = {}
    for k, v in input_dict.items():
        quantity, name = title_to_quantity(k, return_name=True)
        if quantity.dimensionless == False:
            return_dict[name] = quantity * v
        else:
            return_dict[k] = v

    return return_dict

def cname_from_unit(data, unit):
    """
    Extracts the column name from a pandas array where the column name has a label indicating the desired unit.

    :param data: Pandas Dataframe containing the column you want to extract
    :param unit: pint unit you would like to match the column to (i.e. ureg.mV)
    """
    column_names = data.columns.values
    desired_unit_std = to_standard_quantity(1*unit).units

    column_quantities = [(i, title_to_quantity(c)) for i, c in enumerate(column_names)]
    column_units_std = [(i, to_standard_quantity(q).units) for (i, q) in column_quantities if q]
    column_matches = [(i, u == desired_unit_std) for i, u in column_units_std]
    column_indices = [i for i, b in column_matches if b == True]
    if len(column_matches) == 0:
        raise ValueError(f'ERROR: Could not find unit {unit} in data. Available column names are {column_names}')
    else:
        index = column_indices[0]
        name = column_names[index]
        return name

def column_from_unit(data, unit):
    """
    Extracts the pandas column corresponding to a particular unit quantities. If there are multiple columns, it gives back the first one. Assumes columns names are of the form "Quantity Name (unit)", i.e. Voltage (mV) or Photocurrent (nA).

    :param data: Pandas dataframe to extract column from
    :param unit: Pint unit of the desired column. Data will be returned in terms of this unit
    """
    column_name = cname_from_unit(data, unit)
    column_unit = title_to_quantity(column_name).to(unit)
    return column_unit * data[column_name].values
