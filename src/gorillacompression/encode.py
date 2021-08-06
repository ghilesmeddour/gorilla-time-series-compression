from typing import Iterable, Tuple
from bitarray import bitarray

from . import TimestampsEncoder
from . import ValuesEncoder
from .result import PairsGorillaContent


class PairsEncoder:
    """Gorilla Pairs (Timestamp-Value) Encoder.

    Parameters
    ----------
    float_format : {{'f64', 'f32', 'f16'}}, default 'f64'
        Value float format. This parameter determines the number
        of bits that will be used to encode the different informations
        (first value, number of leading zeros, length of the meaningful
        xored value).
        See `gorillacompression.values.contants.INIT_CONSTS`.
    """
    def __init__(self, float_format='f64'):
        self.bit_array = bitarray(endian='big')

        self.nb_pairs = 0
        self.float_format = float_format

        self.timestamps_encoder = TimestampsEncoder(bit_array=self.bit_array)
        self.values_encoder = ValuesEncoder(bit_array=self.bit_array,
                                            float_format=self.float_format)

    def encode_next(self, timestamp: int, value: float) -> bool:
        """
        Encodes a pair (timestamp, value), returns True if the encoding was done,
        False otherwise.

        Parameters
        ----------
        timestamp : int
            POSIX timestamp less than 2147483647 ('January 19, 2038 04:14:07').
        value : float
            Float value to encode.

        Returns
        -------
        bool
            `True` if the element has been encoded correctly, `False` if not.
        """
        if not self.timestamps_encoder.encode_next(timestamp):
            return False
        self.values_encoder.encode_next(value)
        self.nb_pairs += 1
        return True

    def get_encoded(self) -> PairsGorillaContent:
        result: PairsGorillaContent = {
            'encoded': self.bit_array.tobytes(),
            'nb_pairs': self.nb_pairs,
            'float_format': self.float_format,
        }

        return result

    @staticmethod
    def encode_all(pairs: Iterable[Tuple[int, float]]) -> PairsGorillaContent:
        pairs_encoder = PairsEncoder()
        for ts, v in pairs:
            pairs_encoder.encode_next(ts, v)
        return pairs_encoder.get_encoded()
