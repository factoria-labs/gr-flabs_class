# This file contains a list of functions useful for manipulating strings and
# lists of bits and bytes

# returns a list of bytes corresponding to the input ASCII string
def ascii_str_to_byte_list(ascii_str):
    byte_list = []
    for c in ascii_str:
        byte_list.append(ord(c))
    return byte_list


# returns a bit list of the specified length, corresponding to
# the uint value passed; the input integer must be greater than
# or equal to zero and less than 2**(len)
def uint_to_bit_list_pad(uint_val, num_bits):
    # make sure the input value is an int that's not too large
    val = int(uint_val)
    if val.bit_length() > num_bits:
        print("WARNING: uint_to_pad_bit_list() passed too few")
        print("         bits({}) to render integer: {}".format(num_bits, val))
        return num_bits * [2]

    # build minimum bit count equivalent
    bit_list = [int(digit) for digit in bin(val)[2:]]

    # now pad the front end with zeros as needed
    pad_count = num_bits - len(bit_list)
    bit_list = pad_count*[0] + bit_list
    return bit_list


# returns a list of bits corresponding to an input list of bytes
def byte_list_to_bit_list(byte_list):
    bit_list = []
    for byte in byte_list:
        bit_list += uint_to_bit_list_pad(byte, 8)
    return bit_list


# returns the unsigned integer value of the binary data represented
# by the bit_list;
def bit_list_to_uint(bit_list):
    # build integer left shifting each bit into final value
    value = 0
    for bit in bit_list:
        if bit in (0, 1):
            value = (value << 1) | bit
        else:
            raise ValueError(f"Invalid bit value in bit_list_to_uint: {bit}")
    return int(value)


# convert a list of 0s and 1s to a list of packed bytes (0-255)
def bit_list_to_byte_list(bits):
    # pad the end of the list with zeros to make it mod 8
    if len(bits) % 8 != 0:
        bits += [0, ] * (8 - len(bits) % 8)
    # go through in 8-bit chunks, building a list of bytes
    byte_list = []
    for i in range(0, len(bits), 8):
        bits_in_byte = bits[i:i+8]
        byte = bit_list_to_uint(bits_in_byte)
        byte_list.append(byte)
    return byte_list


# convert an integer into a list of four bytes with rollover
def int_to_u8_list(int_val):
    if int_val < 0:
        raise ValueError("integer_to_u8_list() only accepts positive integers")
    return [int_val >> 24 & 0xFF, int_val >> 16 & 0xFF, int_val >> 8 & 0xFF, int_val & 0xFF]
