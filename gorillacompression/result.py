from typing import TypedDict


class PairsGorillaContent(TypedDict):
    encoded: bytes
    nb_pairs: int
    # 'f64', 'f32', 'f16'
    float_format: str
