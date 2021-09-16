from struct import unpack
from typing import List

from bitarray import bitarray
from bitarray import util

from . import constants as C
from .result import ValuesGorillaContent


class ValuesDecoder:
    def __init__(self, bit_array, float_format):
        self.bit_array = bit_array

        self.n_bits_value = C.INIT_CONSTS[float_format]['n_bits_value']
        self.n_bits_number_of_leading_zeros = C.INIT_CONSTS[float_format][
            'n_bits_number_of_leading_zeros']
        self.n_bits_length_of_the_meaningful_xored_value = C.INIT_CONSTS[
            float_format]['n_bits_length_of_the_meaningful_xored_value']
        self.pack_format = C.INIT_CONSTS[float_format]['pack_format']

        self.is_first_value_read = False
        self.n_leading_zeros = None
        self.n_trailing_zeros = None
        self.length_of_the_meaningful_xored_value = None
        self.previous_value_bits = None
        self.previous_value = None

    def __read_bits_and_move_forward(self, n) -> bitarray:
        read_bits = self.bit_array[:n]
        del self.bit_array[:n]
        return read_bits

    def decode_next(self) -> float:
        # The very first value.
        if not self.is_first_value_read:
            self.previous_value_bits = self.__read_bits_and_move_forward(
                self.n_bits_value)
            self.is_first_value_read = True
            self.previous_value = unpack(self.pack_format,
                                         self.previous_value_bits.tobytes())[0]
            return self.previous_value

        if self.__read_bits_and_move_forward(1) == bitarray('0'):
            return self.previous_value
        else:
            if self.__read_bits_and_move_forward(1) == bitarray('1'):
                self.n_leading_zeros = util.ba2int(
                    self.__read_bits_and_move_forward(
                        self.n_bits_number_of_leading_zeros))
                self.length_of_the_meaningful_xored_value = util.ba2int(
                    self.__read_bits_and_move_forward(
                        self.n_bits_length_of_the_meaningful_xored_value)
                ) + C.BLOCK_SIZE_ADJUSTMENT
                self.n_trailing_zeros = self.n_bits_value - self.n_leading_zeros - self.length_of_the_meaningful_xored_value

            meaningful_bits_of_the_xored_value = self.__read_bits_and_move_forward(
                self.length_of_the_meaningful_xored_value)
            xored_value = util.zeros(
                self.n_leading_zeros
            ) + meaningful_bits_of_the_xored_value + util.zeros(
                self.n_trailing_zeros)

            value_bits = xored_value ^ self.previous_value_bits
            self.previous_value_bits = value_bits

            value = unpack(self.pack_format, value_bits.tobytes())[0]

            self.previous_value = value
            return self.previous_value

    @staticmethod
    def decode_all(content: ValuesGorillaContent) -> List[float]:
        bit_array = bitarray(endian='big')
        bit_array.frombytes(content['encoded'])

        vals_decoder = ValuesDecoder(bit_array, content['float_format'])

        return [
            vals_decoder.decode_next() for _ in range(content['nb_values'])
        ]
