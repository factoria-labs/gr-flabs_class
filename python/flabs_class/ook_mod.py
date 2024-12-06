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


from gnuradio import gr
from gnuradio import blocks

class ook_mod(gr.hier_block2):
    """
    docstring for block ook_mod
    """
    def __init__(self, sps, packed):
        gr.hier_block2.__init__(self,
            "ook_mod",
            gr.io_signature(1, 1, gr.sizeof_char),  # Input signature
            gr.io_signature(1, 1, gr.sizeof_gr_complex)) # Output signature

        ##################################################
        # Parameters
        ##################################################
        self.sps = sps
        self.packed = packed

        # first unpack the bytes (if they are packed) and repeat for symbol timing
        if packed:
            self.unpacker = blocks.packed_to_unpacked_bb(1, gr.GR_MSB_FIRST)
            self.connect((self, 0), (self.unpacker, 0))
            self.repeater = blocks.repeat(gr.sizeof_char * 1, sps)
            self.connect((self.unpacker, 0), (self.repeater, 0))
        # else just skip the unpack step
        else:
            self.repeater = blocks.repeat(gr.sizeof_char * 1, sps)
            self.connect((self, 0), (self.repeater, 0))

        # convert bitstream to float
        self.byte_to_float = blocks.uchar_to_float()
        self.connect((self.repeater, 0), (self.byte_to_float, 0))

        # convert stream of floats to stream of complex
        self.float_complex = blocks.float_to_complex(1)
        self.connect((self.byte_to_float, 0), (self.float_complex, 0))

        # send to block output
        self.connect((self.float_complex, 0), (self, 0))


    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.repeater.set_interpolation(self.sps)