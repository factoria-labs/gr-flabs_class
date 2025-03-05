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
import threading
import time
from gnuradio.flabs_class import bit_list_utils as blu

import numpy
import pmt
from gnuradio import gr

class baseband_gen(gr.basic_block):
    """
    docstring for block baseband_gen
    """
    def __init__(self,
                 preamble_bit_count,
                 sync_word,
                 payloads,
                 encode_zero,
                 encode_one,
                 checksum_enable,
                 checksum_offset,
                 pad_byte_count,
                 tx_spacing):
        gr.basic_block.__init__(self,
            name="baseband_gen",
            in_sig=None,
            out_sig=None)

        # snapshot args
        self.preamble_bit_count = preamble_bit_count
        self.sync_word = sync_word
        self.payloads = payloads
        self.encode_zero = encode_zero
        self.encode_one = encode_one
        self.checksum_enable = checksum_enable
        self.checksum_offset = checksum_offset
        self.pad_byte_count = pad_byte_count
        self.tx_spacing = tx_spacing

        # register the message port
        self.message_port_register_out(pmt.intern('out'))

        # start a wakeup thread (need?)
        self.finished = False
        self.thread = threading.Thread(target=self.run)
        self.thread.start()


    def run(self):
        payload_index = 0

        while not self.finished:
            time.sleep(self.tx_spacing)

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

            # get payload bytes
            if isinstance(self.payloads[payload_index], str):
                payload_bytes = blu.ascii_str_to_byte_list(self.payloads[payload_index])
            else:
                payload_bytes = self.payloads[payload_index]
            # append checksum if enabled
            if self.checksum_enable:
                arithmetic_checksum = (sum(payload_bytes) + self.checksum_offset) % 256
                payload_bytes.append(arithmetic_checksum)

            # convert payload to bits
            payload_bits = blu.byte_list_to_bit_list(payload_bytes)

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

            if payload_index < len(self.payloads) - 1:
                payload_index += 1
            else:
                payload_index = 0

    def stop(self):
        self.finished = True
        self.thread.join()