from struct import pack
from typing import Iterable

from bitarray import bitarray
from bitarray import util

from . import constants as C
from .result import ValuesGorillaContent


class ValuesEncoder:
    """Gorilla Values Encoder.

    Parameters
    ----------
    bit_array : bitarray.bitarray, default None
        Object that contains everything that is encoded,
        it can be shared with a ValuesEncoder object.
    float_format : {{'f64', 'f32', 'f16'}}, default 'f64'
        This parameter determines the number of bits that
        will be used to encode the different informations
        (first value, number of leading zeros, length of
        the meaningful xored value). See `C.INIT_CONSTS`.
    """
    def __init__(self, bit_array=None, float_format='f64'):
        if float_format not in C.INIT_CONSTS.keys():
            raise ValueError(
                'Unexpected `float_format` value ({}). Sould be one of f64, f32, f16.'
                .format(float_format))

        self.float_format = float_format
        self.n_bits_value = C.INIT_CONSTS[float_format]['n_bits_value']
        self.n_bits_number_of_leading_zeros = C.INIT_CONSTS[float_format][
            'n_bits_number_of_leading_zeros']
        self.n_bits_length_of_the_meaningful_xored_value = C.INIT_CONSTS[
            float_format]['n_bits_length_of_the_meaningful_xored_value']
        self.pack_format = C.INIT_CONSTS[float_format]['pack_format']

        # TODO: use this and previous.
        self.max_n_leading_zeros = (
            1 << self.n_bits_number_of_leading_zeros) - 1

        if bit_array is None:
            self.bit_array = bitarray(endian='big')
        else:
            self.bit_array = bit_array

        self.current_value_bits = bitarray(endian='big')
        self.previous_value_bits = bitarray(endian='big')

        self.previous_n_leading_zeros = None
        self.previous_n_trailing_zeros = None

        self.nb_values = 0

    def encode_next(self, value: float) -> bool:
        """
        Encodes a value, returns True if the encoding was done,
        False otherwise.

        Parameters
        ----------
        value : float
            Float value to encode.

        Returns
        -------
        bool
            `True` if the element has been encoded correctly, `False` if not.
        """
        self.nb_values += 1

        self.current_value_bits = bitarray(endian='big')
        self.current_value_bits.frombytes(pack(self.pack_format, value))

        # The very first value.
        # The very first value is stored with no compression.
        if self.nb_values == 1:
            self.bit_array += self.current_value_bits
            self.previous_value_bits = self.current_value_bits
            return True

        xored_value = self.previous_value_bits ^ self.current_value_bits

        # Same value as the previous one.
        if (~xored_value).all():
            # Control bit for same value.
            self.bit_array.append(0)
            return True
        else:
            # Control bit for different value.
            self.bit_array.append(1)

        n_leading_zeros = xored_value.index(1)
        n_trailing_zeros = len(xored_value) - util.rindex(xored_value, 1) - 1

        if n_leading_zeros > self.max_n_leading_zeros:
            n_leading_zeros = self.max_n_leading_zeros

        # The block of meaningful bits falls within the block of previous
        # meaningful bits, so we can use previous block information.
        if self.previous_n_leading_zeros is not None \
            and self.previous_n_trailing_zeros is not None \
            and n_leading_zeros >= self.previous_n_leading_zeros \
            and n_trailing_zeros >= self.previous_n_trailing_zeros:
            # Control bit for using previous block information.
            self.bit_array.append(0)
        # The block of meaningful bits doesn't fall within the block of previous
        # meaningful bits, so we can't use previous block information.
        else:
            # Control bit for not using previous block information.
            self.bit_array.append(1)

            # Encode number of leading zeros.
            self.bit_array += util.int2ba(
                n_leading_zeros, length=self.n_bits_number_of_leading_zeros)

            # Encode length of the meaningful XORed value.
            length_of_the_meaningful_xored_value = self.n_bits_value - n_leading_zeros - n_trailing_zeros
            self.bit_array += util.int2ba(
                length_of_the_meaningful_xored_value - C.BLOCK_SIZE_ADJUSTMENT,
                length=self.n_bits_length_of_the_meaningful_xored_value)

            self.previous_n_leading_zeros = n_leading_zeros
            self.previous_n_trailing_zeros = n_trailing_zeros

        # Encode meaningful bits of the XORed value.
        meaningful_xored_value = xored_value[self.previous_n_leading_zeros:self
                                             .n_bits_value -
                                             self.previous_n_trailing_zeros]

        self.bit_array += meaningful_xored_value
        self.previous_value_bits = self.current_value_bits

        return True

    def get_encoded(self) -> ValuesGorillaContent:
        result: ValuesGorillaContent = {
            'encoded': self.bit_array.tobytes(),
            'nb_values': self.nb_values,
            'float_format': self.float_format
        }

        return result

    @staticmethod
    def encode_all(values: Iterable[float]) -> ValuesGorillaContent:
        vals_encoder = ValuesEncoder()
        for v in values:
            vals_encoder.encode_next(v)
        return vals_encoder.get_encoded()
