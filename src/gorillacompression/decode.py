from typing import Iterable, List, Tuple
from bitarray import bitarray

from . import TimestampsDecoder
from . import ValuesDecoder
from .result import PairsGorillaContent


class PairsDecoder:
    def __init__(self, bit_array, float_format):
        self.bit_array = bit_array

        self.timestamps_decoder = TimestampsDecoder(bit_array=self.bit_array)
        self.values_decoder = ValuesDecoder(bit_array=self.bit_array,
                                            float_format=float_format)

    def decode_next(self) -> Tuple[int, float]:
        timestamp = self.timestamps_decoder.decode_next()
        value = self.values_decoder.decode_next()
        return (timestamp, value)

    @staticmethod
    def decode_all(
            content: PairsGorillaContent) -> Iterable[Tuple[int, float]]:
        bit_array = bitarray(endian='big')
        bit_array.frombytes(content['encoded'])

        pairs_decoder = PairsDecoder(bit_array, content['float_format'])

        return [
            pairs_decoder.decode_next() for _ in range(content['nb_pairs'])
        ]
