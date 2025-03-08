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
import numpy
import pmt
from gnuradio import gr
from gnuradio.flabs_class import bit_list_utils as blu

class payload_strobe(gr.basic_block):
    """
    docstring for block payload_strobe
    """
    def __init__(self,
                 payloads,
                 tx_spacing,
                 repeat_count,
                 packet_ctr_enable):
        gr.basic_block.__init__(self,
            name="payload_strobe",
            in_sig=None,
            out_sig=None)

        self.payloads = payloads
        self.tx_spacing = tx_spacing
        self.repeat_count = repeat_count
        self.packet_ctr_enable = packet_ctr_enable

        # init packet counter
        self.packet_ctr = 0

        # register the message port
        self.message_port_register_out(pmt.intern('out'))

        # start a wakeup thread
        self.finished = False
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        payload_index = 0
        # number of payloads to output
        max_payloads = len(self.payloads) * self.repeat_count

        while not self.finished:
            time.sleep(self.tx_spacing)

            # create transmission
            payload_bytes = []

            # add the 4-byte packet counter if enabled
            if self.packet_ctr_enable == 1:  # binary counter
                payload_bytes += blu.int_to_u8_list(self.packet_ctr)
            elif self.packet_ctr_enable == 2:  # ascii counter
                counter_str = f"{self.packet_ctr:0>4}"
                payload_bytes += list(counter_str.encode('utf-8'))

            # get payload bytes
            if isinstance(self.payloads[payload_index], str):
                payload_bytes += blu.ascii_str_to_byte_list(self.payloads[payload_index])
            else:
                payload_bytes += self.payloads[payload_index]

            return_msg = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(payload_bytes), payload_bytes))
            self.message_port_pub(pmt.intern('out'), return_msg)

            # update payload and packet index
            if payload_index < len(self.payloads) - 1:
                payload_index += 1
            else:
                payload_index = 0
            self.packet_ctr += 1

            # check if done
            if max_payloads and self.packet_ctr >= max_payloads:
                self.finished = True
                break

    def stop(self):
        self.finished = True
        self.thread.join()