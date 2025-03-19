from gnuradio.flabs_class import bit_list_utils as blu
from typing import Tuple

def str_to_encoded_bytes(
        input_str: str,
        one_seq=None,
        zero_seq=None,
        pad_val: int = 0) -> list[int]:

    # default is Manchester
    if zero_seq is None:
        zero_seq = [1, 0]
    if one_seq is None:
        one_seq = [0, 1]

    str_bytes = blu.ascii_str_to_byte_list(input_str)
    str_bits = blu.byte_list_to_bit_list(str_bytes)
    encoded_str_bits = []
    for b in str_bits:
        if b:
            encoded_str_bits += one_seq
        else:
            encoded_str_bits += zero_seq

    # add payload and ending padding
    out_bits = []
    out_bits += encoded_str_bits

    # ensure n mod 8 length for byte conversion
    if len(out_bits) % 8:
        out_bits += [pad_val] * (8 - len(out_bits) % 8)
    return out_bits


def str_to_encoded_tx(
        input_str: str,
        preamble: list[int],
        sync_seq: Tuple[int, ...] = (0x2d, 0xd4),
        one_seq: Tuple[int, ...] = (0, 1),
        zero_seq: Tuple[int, ...] = (1, 0),
        num_pad_bits: int = 16,
        pad_val: int = 0) -> list[int]:
    """
    Converts an input string to an encoded list of bytes; this
    general-purpose encoder can be used for both Manchester, PWM or
    any other scheme.
    :param input_str:
    :param preamble: [0, 1, 0, 1, 0, 1, 0, 1] for 8-bit alternating
    :param sync_seq: [0, 0, 1, 0, 1, 1, 0, 1] for 0x2d
    :param one_seq: [0, 1] for standard Manchester
    :param zero_seq: [1, 0] for standard Manchester
    :param num_pad_bits: minimum number of bits to pad at beginning and end (default 16)
    :param pad_val: value for pad bits (default: 0)
    :return:
    """

    # build the output bit list
    out_bits = []
    out_bits += num_pad_bits * [pad_val, ]
    out_bits += preamble
    out_bits += sync_seq

    # encode the string
    str_bytes = blu.ascii_str_to_byte_list(input_str)
    str_bits = blu.byte_list_to_bit_list(str_bytes)
    encoded_str_bits: list[int] = []
    for b in str_bits:
        if b:
            encoded_str_bits += one_seq
        else:
            encoded_str_bits += zero_seq

    # add payload and ending padding
    out_bits += encoded_str_bits
    out_bits += num_pad_bits * [pad_val, ]

    # ensure n mod 8 length for byte conversion
    if len(out_bits) % 8:
        out_bits += [pad_val] * (8 - len(out_bits) % 8)

    return out_bits


def main():
    in_str = "Hello SDR"

    in_bytes = blu.ascii_str_to_byte_list(in_str)
    in_bits = blu.byte_list_to_bit_list(in_bytes)
    print(blu.byte_list_to_hex_str(in_bytes))
    print(blu.bit_list_to_bit_str(in_bits))

    one = [0, 1]
    zero = [1, 0]

    bits = str_to_encoded_bytes(
        input_str=in_str,
        one_seq=one,
        zero_seq=zero)
    print(bits)
    print(len(bits))

if __name__ == "__main__":
    main()