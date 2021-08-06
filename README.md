# Gorilla Time Series Compression

This is an implementation (with some adaptations) of the compression algorithm described in **section 4.1** (Time series compression) of [[1]](#1) (read the paper [here](./doc/p1816-teller.pdf)).

Gorilla compression is lossless.

This library can be used in three ways:
- Timestamps only compression.
- Values only compression (useful for regular time series compression).
- Timestamp-Value pairs compression (useful for irregular time series compression).

In all three cases, the result of the encoding process is a dict with everything necessary for decoding (see [Usage](#usage) for examples). If you want to use this library for compressed message exchanges, you can serialize the result of the encoding process as you like (JSON, protobuf, etc.)

This implementation is based on **section 4.1** of [[1]](#1) and on the Facebook's open source implementation [[2]](#2) (which have some differences).

## Differences from the original paper

- Timestamps or values can be encoded separately.
- The header (with an aligned timestamp) at the beginning (64 bits) of the message is not encoded.
- The float format can be specified (f64, f32, f16) to optimize the size of certain fields.

## Installation

To install the latest release:
```
$ pip install gorillacompression
```

You can also build a local package and install it:
```
$ make build
$ pip install dist/*.whl
```

## <a id="usage"></a> Usage

Import `gorillacompression` module.

```python
>>> import gorillacompression as gc
```

Data to encode.

```python
>>> timestamps = [1628164645, 1628164649, 1628164656, 1628164669]
>>> values = [18.95, 18.91, 17.01, 14.05]
>>> pairs = list(zip(timestamps, values))
>>> pairs
[(1628164645, 18.95), (1628164649, 18.91), (1628164656, 17.01), (1628164669, 14.05)]
```

In the three scenarios of compression (timestamps, values, pairs), you can use:

- `encode_all` to encode all elements or `encode_next` to encode element by element.
- `decode_all` to decode everything.

`encode_next` returns `True` if the element has been encoded correctly, `False` if the element has not been encoded accompanied by a warning explaining the reason.

### Timestamps only compression

The expected input timestamp is a POSIX timestamp less than 2147483647 ('January 19, 2038 04:14:07'). The delta between two successive timestamps must be greater than or equal to 0.

You can use `encode_all` to encode all timestamps:
```python
>>> content = gc.TimestampsEncoder.encode_all(timestamps)
>>> content
{'encoded': b'\xc2\x17\xa4K\x08\xa1Q@', 'nb_timestamps': 4}
>>> gc.TimestampsDecoder.decode_all(content)
[1628164645, 1628164649, 1628164656, 1628164669]
```

Or you can use `encode_next` to encode one by one:
```python
>>> ts_encoder = gc.TimestampsEncoder()
>>> for ts in timestamps:
...     ts_encoder.encode_next(ts)
>>> content = ts_encoder.get_encoded()
>>> content
{'encoded': b'\xc2\x17\xa4K\x08\xa1Q@', 'nb_timestamps': 4}
>>> gc.TimestampsDecoder.decode_all(content)
[1628164645, 1628164649, 1628164656, 1628164669]
```

### Values only compression

You can use `encode_all` to encode all values:
```python
>>> content = gc.ValuesEncoder.encode_all(values)
>>> content
{'encoded': b'@2\xf333333\xe7f\xf1\xbco\x1b\xc6\xee\xc7\xeaz\x9e\xa7\xa9\xeb\xaf^\x8d\x8bb\xd8\xb6,\x80', 'nb_values': 4, 'float_format': 'f64'}
>>> gc.ValuesDecoder.decode_all(content)
[18.95, 18.91, 17.01, 14.05]
```

Or you can use `encode_next` to encode one by one:
```python
>>> values_encoder = gc.ValuesEncoder()
>>> for v in values:
...     values_encoder.encode_next(v)
>>> content = values_encoder.get_encoded()
>>> content
{'encoded': b'@2\xf333333\xe7f\xf1\xbco\x1b\xc6\xee\xc7\xeaz\x9e\xa7\xa9\xeb\xaf^\x8d\x8bb\xd8\xb6,\x80', 'nb_values': 4, 'float_format': 'f64'}
>>> gc.ValuesDecoder.decode_all(content)
[18.95, 18.91, 17.01, 14.05]
```

### Timestamp-Value pairs compression

You can use `encode_all` to encode all pairs:
```python
>>> content = gc.PairsEncoder.encode_all(pairs)
>>> content
{'encoded': b'\xc2\x17\xa4J\x80e\xe6ffffg\x08\xe7f\xf1\xbco\x1b\xc6\xd0\xb7c\xf5=OS\xd4\xf5\xa2\xeb\xd7\xa3b\xd8\xb6-\x8b ', 'nb_pairs': 4, 'float_format': 'f64'}
>>> gc.PairsDecoder.decode_all(content)
[(1628164645, 18.95), (1628164649, 18.91), (1628164656, 17.01), (1628164669, 14.05)]
```

Or you can use `encode_next` to encode one by one:
```python
>>> pairs_encoder = gc.PairsEncoder()
>>> for (ts, v) in pairs:
...     pairs_encoder.encode_next(ts, v)
>>> content = pairs_encoder.get_encoded()
>>> content
{'encoded': b'\xc2\x17\xa4J\x80e\xe6ffffg\x08\xe7f\xf1\xbco\x1b\xc6\xd0\xb7c\xf5=OS\xd4\xf5\xa2\xeb\xd7\xa3b\xd8\xb6-\x8b ', 'nb_pairs': 4, 'float_format': 'f64'}
>>> gc.PairsDecoder.decode_all(content)
[(1628164645, 18.95), (1628164649, 18.91), (1628164656, 17.01), (1628164669, 14.05)]
```

## Gorilla compression algorithm explanation

Below is a brief explanation of the implemented method. (Refer to [[1]](#1) **section 4.1** (read the paper [here](./doc/p1816-teller.pdf)) for the original explanation)

### Timestamps compression

- The first timestamp is encoded in a fixed number of bits.
- The following timestamps are encoded as follows:
```
  (a) Calculate the delta of delta
          D = (t_n − t_(n−1)) − (t_(n−1) − t_(n−2))
  (b) If D is zero, then store a single ‘0’ bit
  (c) If D is between [-63, 64], store ‘10’ followed by the value (7 bits)
  (d) If D is between [-255, 256], store ‘110’ followed by the value (9 bits)
  (e) if D is between [-2047, 2048], store ‘1110’ followed by the value (12 bits)
  (f) Otherwise store ‘1111’ followed by D using 32 bits
```

### Values compression

```
Notation

    n bits:
    +---- n ----+
    |           |
    +---- n' ---+

    n bytes:
    +==== n ====+
    |           |
    +==== n' ===+

    `~` in place of `n` means a variable number of bytes or bits.

    When it makes sense, n refers to the default value, and n' to the variable containing the value.
```

This explanation corresponds to the case of float format `f64`, for the other formats (`f32`, `f16`), the size of some fields is different (refer to the code for more details).

1. The first value is stored with no compression.
```
    +======================= 8 =======================+
    |  First value (IEEE 754, binary64, Big Endian)   |
    +======================= 8 =======================+
```
2. If XOR with the previous is zero (same value), store
single ‘0’ bit.
```
    +-- 1 --+
    |   0   |
    +-- 1 --+
```
3. When XOR is non-zero, calculate the number of leading and trailing zeros in the XOR, store bit ‘1’ followed by either a) or b):
  * (a) (Control bit ‘0’) If the block of meaningful bits falls within the block of previous meaningful bits*, i.e., there are at least as many leading zeros and as many trailing zeros as with the previous value, use that information for the block position and just store the meaningful XORed value\*.
```
    +--- 2 ---+--- length of the meaningful XORed value ---+
    |   10    |         [meaningful XORed value]           |
    +--- 2 ---+--- length of the meaningful XORed value ---+
```
  * (b) (Control bit ‘1’) Store the length of the number of leading zeros in the next 5 bits, then store the length of the meaningful XORed value in the next 6 bits. Finally store the meaningful bits of the XORed value.
```
    +--- 2 ---+------------- 5 -------------+------------------- 6 ------------------+--- length of the meaningful XORed value ---+
    |   11    |   number of leading zeros   |   length of the meaningful XORed value |         [meaningful XORed value]           |
    +--- 2 ---+------------- 5 -------------+------------------- 6 ------------------+--- length of the meaningful XORed value ---+
```
4. After the compression of the last value, if the length of the bitarray is not a multiple of 8, the few remaining bits are padded with zero.
```
    +---- n ----+
    |   0...0   |
    +---- n ----+

    n < 8
```

(*) The terms "meaningful bits" and "meaningful XORed value" used in the original paper may be confusing.
  - In case (b), "meaningful XORed value" is a value with absolutely no leading and trailing zero.
  - In case (a), "meaningful XORed value" is the XORed value striped off same amount of leading and trailing zeroes as previous value delta. The meaningful bits in this case may still contain some leading and trailing zeroes.

### Timestamp-Value pairs compression

The encoding of a pair is the encoding of the timestmap followed by the encoding of the value.

## Contribute

Please, open issues. PR are very welcome!

```
$ git clone https://github.com/ghilesmeddour/gorilla-time-series-compression.git
$ cd gorilla-time-series-compression
```

```
make format
make dead-code-check
make test
make type-check
make coverage
make build
```

### TODOs

- [ ] Add more unit tests (`f32` and `f16` float formats are currently not tested).
- [ ] Add profiling, benchmarks, etc.
- [ ] Improve doc, docstring, etc.

## Other implementations

- <a id="2">[2]</a> Facebook's open source implementation (C++): [Beringei](https://github.com/facebookarchive/beringei), see especially [TimeSeriesStream.cpp](https://github.com/facebookarchive/beringei/blob/92784ec6e22572f28500c76b669276007635c875/beringei/lib/TimeSeriesStream.cpp)
- [gorilla-tsc (Java)](https://github.com/burmanm/gorilla-tsc)
- [BlueEyes (.Net)](https://github.com/joshclark/BlueEyes) and a [fork](https://github.com/olivergrimes/BlueEyes)
- [py-tsz (Python)](https://github.com/kurakihx/py-tsz)

## References

<a id="1">[1]</a>
Pelkonen, T., Franklin, S., Teller, J., Cavallaro, P., Huang, Q., Meza, J., & Veeraraghavan, K. (2015).
Gorilla: A fast, scalable, in-memory time series database. Proceedings of the VLDB Endowment, 8(12), 1816-1827.
