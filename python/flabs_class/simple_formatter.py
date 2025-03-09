#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MIT License
#
# Copyright (c) 2024 Paul Clark
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import numpy
from gnuradio import gr
import pmt
from gnuradio.flabs_class import bit_list_utils as blu


class simple_formatter(gr.basic_block):
    """
    docstring for block simple_formatter
    """
    def __init__(self,
                 preamble_bit_count,
                 sync_word,
                 encode_zero,
                 encode_one,
                 pad_byte_count,
                 length_field):
        gr.basic_block.__init__(self,
            name="simple_formatter",
            in_sig=None,
            out_sig=None)

        self.preamble_bit_count = preamble_bit_count
        self.sync_word = sync_word
        self.encode_zero = encode_zero
        self.encode_one = encode_one
        self.pad_byte_count = pad_byte_count
        self.length_field = length_field

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
        payload_bytes = list(pmt.u8vector_elements(msg))

        # create transmission
        tx_bits = []

        # add pre-padding
        tx_bits += [0, ] * (8 * self.pad_byte_count)

        # add preamble, starting with 0 bit (0101... vs 1010...)
        preamble_bit_high = False
        for _ in range(self.preamble_bit_count):
            tx_bits.append(1 if preamble_bit_high else 0)
            preamble_bit_high = not preamble_bit_high

        # add sync word
        for nibble in self.sync_word:
            if nibble == '0':
                tx_bits += (0, 0, 0, 0)
            elif nibble == '1':
                tx_bits += (0, 0, 0, 1)
            elif nibble == '2':
                tx_bits += (0, 0, 1, 0)
            elif nibble == '3':
                tx_bits += (0, 0, 1, 1)
            elif nibble == '4':
                tx_bits += (0, 1, 0, 0)
            elif nibble == '5':
                tx_bits += (0, 1, 0, 1)
            elif nibble == '6':
                tx_bits += (0, 1, 1, 0)
            elif nibble == '7':
                tx_bits += (0, 1, 1, 1)
            elif nibble == '8':
                tx_bits += (1, 0, 0, 0)
            elif nibble == '9':
                tx_bits += (1, 0, 0, 1)
            elif nibble.upper() == 'A':
                tx_bits += (1, 0, 1, 0)
            elif nibble.upper() == 'B':
                tx_bits += (1, 0, 1, 1)
            elif nibble.upper() == 'C':
                tx_bits += (1, 1, 0, 0)
            elif nibble.upper() == 'D':
                tx_bits += (1, 1, 0, 1)
            elif nibble.upper() == 'E':
                tx_bits += (1, 1, 1, 0)
            elif nibble.upper() == 'F':
                tx_bits += (1, 1, 1, 1)
            else:
                raise ValueError(f"Invalid sync word character: {nibble}")

        # convert payload to bits
        payload_bits = blu.byte_list_to_bit_list(payload_bytes)

        # add length field if enabled
        if self.length_field:
            # compute encoded payload length
            payload_length = len(payload_bytes) * len(self.encode_zero)
            payload_length_bytes = blu.int_to_u8_list(payload_length)
            length_header_bytes = []
            length_header_bytes += 2 * payload_length_bytes[2:]
            tx_bits += blu.byte_list_to_bit_list(length_header_bytes)

        # encode the payload bits
        encoded_payload_bits = []
        for bit in payload_bits:
            if bit == 0:
                encoded_payload_bits += self.encode_zero
            if bit == 1:
                encoded_payload_bits += self.encode_one

        # build the rest of the bit list
        tx_bits += encoded_payload_bits + [0, ] * (8 * self.pad_byte_count)
        tx_bytes = blu.bit_list_to_byte_list(tx_bits)

        return_msg = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(tx_bytes), tx_bytes))
        self.message_port_pub(pmt.intern('out'), return_msg)
