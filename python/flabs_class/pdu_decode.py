#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 Paul Clark.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import pmt
import array
import numpy
from gnuradio import gr


def int_to_padded_bits(int_val, num_bits):
    """
    returns a bit list of the specified length, corresponding to
    the integer value passed; the input integer must be greater than
    or equal to zero and less than 2**(len)
    """
    # make sure the input value is an int
    val = int(int_val)
    if val.bit_length() > num_bits:
        print("WARNING: int_to_padded_bits() passed too few bits ({}) to render integer: {}".format(num_bits, val))
        return [0]
    # build minimum bit count equivalent
    bits = [int(digit) for digit in bin(val)[2:]]
    # now pad the front end with zeros as needed
    pad_count = num_bits - len(bits)
    bits = pad_count * [0, ] + bits
    return bits


def byte_list_to_bits(byte_list):
    """
    returns a list of bits corresponding to an input list of bytes
    """
    bit_list = []
    for byte in byte_list:
        bit_list += int_to_padded_bits(byte, 8)
    return bit_list

def bits_to_int(bit_list, invert = False, reverse = False):
    """
    returns the integer value of the binary value represented by
    the bit list; by default, the function assumes MSB, in which
    the item at index 0 is the most significant bit. You can choose
    an LSB conversion by setting reverse to True. You can also
    invert the bits before the conversion
    """
    # invert bits if necessary
    bit_list2 = []
    if invert:
        for bit in bit_list:
            if bit == 0:
                bit_list2.append(1)
            else:
                bit_list2.append(0)
    else:
        bit_list2 = bit_list[:]

    # reverse bits if necessary
    if reverse:
        bit_list3 = reversed(bit_list2)
    else:
        bit_list3 = bit_list2[:]

    value = 0
    for bit in bit_list3:
        if isinstance(bit, int):
            value = (value << 1) | bit
        else:
            # if we don't have an integer, then we ended up with a
            # logic error at some point
            value = -1
            break
    return int(value)

def bit_list_to_byte_list(bits):
    """
    converts list of input bits to a list of bytes
    """
    # handle "partial byte" scenario
    if len(bits) % 8 != 0:
        print("WARNING: non-mod8 length in bits->bytes conversion, zero-padding...")
        padded_bits = bits + [0, ] * (8 - len(bits) % 8)
    else:
        padded_bits = bits

    byte_list = []
    for i in range(0, len(padded_bits), 8):
        bits_in_byte = padded_bits[i:i+8]
        byte = bits_to_int(bits_in_byte)
        byte_list.append(byte)
    return byte_list

def general_decoder(encoded_bits, one_seq, zero_seq):
    """
    Performs generalized decoding of an input list of
    integer 1s and 0s; if de-sync occurs, the decoded
    output will terminate at that point
    """
    # reused values
    one_len = len(one_seq)
    zero_len = len(zero_seq)

    decoded_bits = []
    index = 0
    while True:
        if encoded_bits[index:index + one_len] == list(one_seq):
            decoded_bits.append(1)
            index += one_len
        elif encoded_bits[index:index + zero_len] == list(zero_seq):
            decoded_bits.append(0)
            index += zero_len
        else:
            break

    return decoded_bits


class pdu_decode(gr.basic_block):
    """
    docstring for block pdu_decode
    """
    def __init__(self, zero_seq, one_seq):
        gr.basic_block.__init__(self,
            name="pdu_decode",
            in_sig=None,
            out_sig=None)
        # store the sequences
        self.zero_seq = zero_seq
        self.one_seq = one_seq

        # register the message ports
        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)
        self.message_port_register_out(pmt.intern('out'))

    # runs each time a msg pdu arrives at the block input
    # it converts the input PDU bytes to half as many output PDU bytes
    def handle_msg(self, msg_pmt):
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
            print("ERROR: Invalid data type: Expected u8vector.")
            return

        encoded_data = list(pmt.u8vector_elements(msg))

        # convert bytes to a single list of bits
        bit_list = byte_list_to_bits(encoded_data)

        decoded_bits = general_decoder(
            encoded_bits=bit_list,
            zero_seq=self.zero_seq,
            one_seq=self.one_seq
        )
        decoded_bytes = bit_list_to_byte_list(decoded_bits)

        # send out the decoded PDU
        self.message_port_pub(
            pmt.intern('out'),
            pmt.cons(
                pmt.PMT_NIL,
                pmt.init_u8vector(len(decoded_bytes), decoded_bytes)
            )
        )
