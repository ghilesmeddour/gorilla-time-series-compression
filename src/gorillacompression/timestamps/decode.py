from typing import List
from bitarray import bitarray
from bitarray import util

from . import constants as C
from .result import TimestampsGorillaContent


class TimestampsDecoder:
    """
    Gorilla Timestamps Decoder.
    """
    def __init__(self, bit_array):
        self.bit_array = bit_array
        self.is_first_value_read = False
        self.previous_timestamp = None
        self.previous_delta = C.DEFAULT_DELTA

    def __read_bits_and_move_forward(self, n) -> bitarray:
        read_bits = self.bit_array[:n]
        del self.bit_array[:n]
        return read_bits

    def decode_next(self) -> int:
        # The very first timestamp.
        if not self.is_first_value_read:
            timestamp = util.ba2int(
                self.__read_bits_and_move_forward(
                    C.N_BITS_FOR_FIRST_TIMESTAMP))
            self.previous_timestamp = timestamp
            self.is_first_value_read = True
            return self.previous_timestamp

        # Find i of the first '0' occurence.
        zero_pos = self.bit_array.find(False, 0, C.MAX_BITS_FOR_CONTROL_VALUE)

        # Delta of delta is zero.
        if zero_pos == 0:
            _ = self.__read_bits_and_move_forward(1)
        # Delta of delta is non zero.
        else:
            # '0' not found.
            if zero_pos == -1:
                i = C.MAX_BITS_FOR_CONTROL_VALUE - 1
            else:
                i = zero_pos - 1

            # Move forward on the bit array.
            _ = self.__read_bits_and_move_forward(
                C.TIMESTAMP_ENCODING['bits_for_control_value'][i])

            n_bits_to_read = C.TIMESTAMP_ENCODING['bits_for_value'][i]
            value = self.__read_bits_and_move_forward(n_bits_to_read)

            decoded_value = util.ba2int(value)

            # [0,255] becomes [-128,127]
            decoded_value -= C.TIMESTAMP_ENCODING['max_value'][i]

            # [-128,127] becomes [-128,128] without the zero in the middle
            if decoded_value >= 0:
                decoded_value += 1

            self.previous_delta += decoded_value

        self.previous_timestamp += self.previous_delta
        return self.previous_timestamp

    @staticmethod
    def decode_all(content: TimestampsGorillaContent) -> List[int]:
        bit_array = bitarray(endian='big')
        bit_array.frombytes(content['encoded'])

        ts_decoder = TimestampsDecoder(bit_array)

        return [
            ts_decoder.decode_next() for _ in range(content['nb_timestamps'])
        ]
