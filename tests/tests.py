import sys
import unittest
import random

import numpy as np

import gorillacompression as gc


class TestTimestampsEncoding(unittest.TestCase):

    def test_simple(self):
        timestamps = [10, 20, 40, 40, 40, 90, 500, 147483647]
        ts_encoder = gc.TimestampsEncoder()

        for ts in timestamps:
            ts_encoder.encode_next(ts)

        content = ts_encoder.get_encoded()

        self.assertEqual(gc.TimestampsEncoder.encode_all(timestamps), content)
        self.assertEqual(gc.TimestampsDecoder.decode_all(content), timestamps)

    def test_random(self):
        random.seed(0)
        sizes = [random.randint(0, 1000) for _ in range(10)]

        for size in sizes:
            timestamps = [
                random.randint(0, gc.timestamps.constants.MAX_TIMESTAMP)
                for _ in range(size)
            ]
            timestamps = sorted(timestamps)

            ts_encoder = gc.TimestampsEncoder()

            for ts in timestamps:
                ts_encoder.encode_next(ts)

            content = ts_encoder.get_encoded()

            self.assertEqual(gc.TimestampsEncoder.encode_all(timestamps),
                             content)
            self.assertEqual(gc.TimestampsDecoder.decode_all(content),
                             timestamps)


class TestValuesEncoding(unittest.TestCase):

    def test_simple(self):
        values = [15.995, 0.35, 15.36, 0.0005, 0.0005, 0.0005, 0.0005, 152.3]

        vals_encoder = gc.ValuesEncoder()

        for v in values:
            vals_encoder.encode_next(v)

        content = vals_encoder.get_encoded()

        self.assertEqual(gc.ValuesEncoder.encode_all(values), content)
        self.assertEqual(gc.ValuesDecoder.decode_all(content), values)

    def test_random(self):
        random.seed(0)
        sizes = [random.randint(0, 1000) for _ in range(10)]

        for size in sizes:
            values = [random.random() for _ in range(size)]

            values_encoder = gc.ValuesEncoder()

            for v in values:
                values_encoder.encode_next(v)

            content = values_encoder.get_encoded()

            self.assertEqual(gc.ValuesEncoder.encode_all(values), content)
            self.assertEqual(gc.ValuesDecoder.decode_all(content), values)

    def test_block_size_64_bits(self):
        values = [
            -0.39263690585168304, -0.39263690585168304, -0.39263690585168304,
            0.450762617155903, 0.450762617155903, 0.450762617155903,
            -0.284155454538896
        ]

        values_encoder = gc.ValuesEncoder()

        for v in values:
            values_encoder.encode_next(v)

        content = values_encoder.get_encoded()

        self.assertEqual(gc.ValuesEncoder.encode_all(values), content)
        self.assertEqual(gc.ValuesDecoder.decode_all(content), values)


class TestPairsEncoding(unittest.TestCase):

    def test_simple(self):
        values = [15.995, 0.35, 15.36, 0.0005, 0.0005, 0.0005, 0.0005, 152.3]
        timestamps = [10, 20, 40, 40, 40, 90, 500, 147483647]

        pairs = list(zip(timestamps, values))

        pairs_encoder = gc.PairsEncoder()

        for ts, v in pairs:
            pairs_encoder.encode_next(ts, v)

        content = pairs_encoder.get_encoded()

        self.assertEqual(gc.PairsEncoder.encode_all(pairs), content)
        self.assertEqual(gc.PairsDecoder.decode_all(content), pairs)

    def test_random(self):
        random.seed(0)
        sizes = [random.randint(0, 1000) for _ in range(10)]

        for size in sizes:
            values = [random.random() for _ in range(size)]
            timestamps = [
                random.randint(0, gc.timestamps.constants.MAX_TIMESTAMP)
                for _ in range(size)
            ]
            timestamps = sorted(timestamps)

            pairs = list(zip(timestamps, values))

            pairs_encoder = gc.PairsEncoder()

            for ts, v in pairs:
                pairs_encoder.encode_next(ts, v)

            content = pairs_encoder.get_encoded()

            self.assertEqual(gc.PairsEncoder.encode_all(pairs), content)
            self.assertEqual(gc.PairsDecoder.decode_all(content), pairs)

    def test_random_different_float_formats(self):
        random.seed(1)
        sizes = [random.randint(0, 1000) for _ in range(10)]

        for ff in ['f64', 'f32', 'f16']:
            for size in sizes:
                values = [random.random() for _ in range(size)]
                timestamps = [
                    random.randint(0, gc.timestamps.constants.MAX_TIMESTAMP)
                    for _ in range(size)
                ]
                timestamps = sorted(timestamps)

                pairs = list(zip(timestamps, values))

                pairs_encoder = gc.PairsEncoder(float_format=ff)

                for ts, v in pairs:
                    pairs_encoder.encode_next(ts, v)

                content = pairs_encoder.get_encoded()

                # TODO: choose a different error precision depending 
                # on the float format and value for a more accurate test
                precision_error = 0.001

                self.assertEqual(
                    gc.PairsEncoder.encode_all(pairs, float_format=ff),
                    content)

                self.assertTrue((np.absolute(
                    np.array(gc.PairsDecoder.decode_all(content)) -
                    np.array(pairs)) < precision_error).all())
