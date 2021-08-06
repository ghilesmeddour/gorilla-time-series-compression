from typing import TypedDict


class ValuesGorillaContent(TypedDict):
    encoded: bytes
    nb_values: int
    # 'f64', 'f32', 'f16'
    float_format: str
