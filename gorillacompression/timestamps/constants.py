from typing import List, TypedDict

from bitarray import bitarray

# Works until 2038.
N_BITS_FOR_FIRST_TIMESTAMP = 31
DEFAULT_DELTA = 60
DEFAULT_MIN_TIMESTAMP_DELTA = 0

MAX_TIMESTAMP = 2**N_BITS_FOR_FIRST_TIMESTAMP - 1
# >>> from datetime import datetime
# >>> datetime.fromtimestamp(MAX_TIMESTAMP)
# datetime.datetime(2038, 1, 19, 4, 14, 7)

####
## TIMESTAMP_ENCODING
####
bits_for_value = [7, 9, 12, 31]
control_value = list(map(bitarray, ['10', '110', '1110', '1111']))
max_value = [1 << (bv - 1) for bv in bits_for_value]
bits_for_control_value = [len(cv) for cv in control_value]

MAX_BITS_FOR_CONTROL_VALUE = max(bits_for_control_value)
MAX_MAX_VALUE = max(max_value)

TimestampEncoding = TypedDict(
    'TimestampEncoding', {
        'bits_for_value': List[int],
        'control_value': List[bitarray],
        'max_value': List[int],
        'bits_for_control_value': List[int]
    })

TIMESTAMP_ENCODING: TimestampEncoding = {
    'bits_for_value': bits_for_value,
    'control_value': control_value,
    'max_value': max_value,
    'bits_for_control_value': bits_for_control_value
}
