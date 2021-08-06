from typing import Iterable, Union
import warnings

from bitarray import bitarray
from bitarray import util

from . import constants as C
from .result import TimestampsGorillaContent


class TimestampsEncoder:
    """Gorilla Timestamps Encoder.

    Parameters
    ----------
    bit_array : bitarray.bitarray, default None
        Object that contains everything that is encoded,
        it can be shared with a ValuesEncoder object.
    min_timestamp_delta : int, default 0
        The minimum acceptable timestamp delta. Encoding
        is not done if the calculated delta is lower.
    """
    def __init__(self,
                 bit_array: Union[bitarray, None] = None,
                 min_timestamp_delta: int = C.DEFAULT_MIN_TIMESTAMP_DELTA):
        if bit_array is None:
            self.bit_array = bitarray(endian='big')
        else:
            self.bit_array = bit_array

        self.min_timestamp_delta = min_timestamp_delta
        self.previous_timestamp = 0
        self.previous_delta = C.DEFAULT_DELTA
        self.nb_timestamps = 0

    def encode_next(self, timestamp: int) -> bool:
        """
        Encodes a timestamp, returns True if the encoding was done,
        False otherwise.

        The encoding is not done if the calculated delta is inferior
        to the minimum delta.

        (a) Calculate the delta of delta
                D = (t_n − t_(n−1)) − (t_(n−1) − t_(n−2))
        (b) If D is zero, then store a single ‘0’ bit
        (c) If D is between [-63, 64], store ‘10’ followed by the value (7 bits)
        (d) If D is between [-255, 256], store ‘110’ followed by the value (9 bits)
        (e) if D is between [-2047, 2048], store ‘1110’ followed by the value (12 bits)
        (f) Otherwise store ‘1111’ followed by D using 32 bits

        Parameters
        ----------
        timestamp : int
            POSIX timestamp less than 2147483647 ('January 19, 2038 04:14:07').

        Returns
        -------
        bool
            `True` if the element has been encoded correctly, `False` if not.
        """
        if self.__encode_next(timestamp):
            self.nb_timestamps += 1
            return True
        else:
            return False

    def __encode_next(self, timestamp: int) -> bool:
        if not (0 <= timestamp <= C.MAX_TIMESTAMP):
            warnings.warn(
                f'The timestamp {timestamp} cannot be encoded, should be between 0 and {C.MAX_TIMESTAMP}.'
            )
            return False

        delta = timestamp - self.previous_timestamp

        if delta < self.min_timestamp_delta and self.previous_timestamp != 0:
            warnings.warn(
                f'`delta` ({delta}) is less than the acceptable minimum (< {self.min_timestamp_delta}).'
            )
            return False

        # The very first timestamp.
        if self.nb_timestamps == 0:
            # Store the first timestamp as is.
            self.bit_array += util.int2ba(timestamp,
                                          length=C.N_BITS_FOR_FIRST_TIMESTAMP,
                                          endian='big')
            self.previous_timestamp = timestamp
            return True

        # (a) Calculate the delta of delta
        # D = (t_n − t_(n−1)) − (t_(n−1) − t_(n−2))
        delta_of_delta = delta - self.previous_delta

        # (b) If D is zero, then store a single ‘0’ bit
        if delta_of_delta == 0:
            self.previous_timestamp = timestamp
            self.bit_array.append(0)
            return True

        if delta_of_delta > 0:
            # There are no zeros (handled above).
            # Shift by one to fit in x number of bits.
            delta_of_delta -= 1

        abs_delta_of_delta = abs(delta_of_delta)

        if abs_delta_of_delta >= C.MAX_MAX_VALUE:
            warnings.warn(
                f'`abs_delta_of_delta` ({abs_delta_of_delta}) is too big to be encoded (> {C.MAX_MAX_VALUE}).'
            )
            return False

        for (bits_for_value, control_value,
             max_value) in zip(C.TIMESTAMP_ENCODING['bits_for_value'],
                               C.TIMESTAMP_ENCODING['control_value'],
                               C.TIMESTAMP_ENCODING['max_value']):
            if abs_delta_of_delta < max_value:
                self.bit_array.extend(control_value)
                # Make this value between [0, max_value]
                encoded_value = delta_of_delta + max_value

                self.bit_array += util.int2ba(encoded_value,
                                              length=bits_for_value,
                                              endian='big')
                break

        self.previous_timestamp = timestamp
        self.previous_delta = delta

        return True

    def get_encoded(self) -> TimestampsGorillaContent:
        result: TimestampsGorillaContent = {
            'encoded': self.bit_array.tobytes(),
            'nb_timestamps': self.nb_timestamps
        }

        return result

    @staticmethod
    def encode_all(timestamps: Iterable[int]) -> TimestampsGorillaContent:
        ts_encoder = TimestampsEncoder()
        for ts in timestamps:
            ts_encoder.encode_next(ts)
        return ts_encoder.get_encoded()
