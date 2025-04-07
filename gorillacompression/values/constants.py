INIT_CONSTS = {
    # IEEE 754, binary64, Big Endian
    'f64': {
        'n_bits_value': 64,
        'n_bits_number_of_leading_zeros': 5,
        'n_bits_length_of_the_meaningful_xored_value': 6,
        'pack_format': '>d',
    },
    # IEEE 754, binary32, Big Endian
    'f32': {
        'n_bits_value': 32,
        'n_bits_number_of_leading_zeros': 4,
        'n_bits_length_of_the_meaningful_xored_value': 5,
        'pack_format': '>f',
    },
    # IEEE 754, binary16, Big Endian
    'f16': {
        'n_bits_value': 16,
        'n_bits_number_of_leading_zeros': 3,
        'n_bits_length_of_the_meaningful_xored_value': 4,
        'pack_format': '>e',
    },
}

BLOCK_SIZE_ADJUSTMENT = 1
