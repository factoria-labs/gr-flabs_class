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
from gnuradio import analog
from gnuradio import digital

class ook_demod(gr.hier_block2):
    """
    docstring for block ook_demod
    """
    def __init__(self, sps, threshold, agc):
        gr.hier_block2.__init__(self,
            "ook_demod",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),  # Input signature
            gr.io_signature(2, 2, (gr.sizeof_char, gr.sizeof_float))) # Output signature

        ##################################################
        # Parameters
        ##################################################
        self.sps = sps
        self.threshold = threshold
        self.agc = agc

        # do the AGC or...
        if self.agc:
            self.agc = analog.feedforward_agc_cc((int(sps) * 8), 1.0)
            self.connect((self, 0), (self.agc, 0))
            # raw demodulation
            self.raw_demod = blocks.complex_to_mag(1)
            self.connect((self.agc, 0), (self.raw_demod, 0))
        # just do immediately into the raw demod
        else:
            self.raw_demod = blocks.complex_to_mag(1)
            self.connect((self, 0), (self.raw_demod, 0))

        # threshold detection
        self.threshold_shift = blocks.add_const_ff(-1 * self.threshold)
        self.connect((self.raw_demod, 0), (self.threshold_shift, 0))
        self.threshold_slice = digital.binary_slicer_fb()
        self.connect((self.threshold_shift, 0), (self.threshold_slice, 0))

        # convert to a waveform transitioning from -0.5 to +0.5, as needed by symbol_sync
        self.convert_to_float = blocks.uchar_to_float()
        self.connect((self.threshold_slice, 0), (self.convert_to_float, 0))
        self.half_shift = blocks.add_const_ff(-0.5)
        self.connect((self.convert_to_float, 0), (self.half_shift, 0))

        # clock sync
        self.clk_sync = digital.symbol_sync_ff(
            digital.TED_MUELLER_AND_MULLER,
            #digital.TED_EARLY_LATE,
            sps,
            0.045,
            1.0,
            1.0,
            1.5,
            1,
            digital.constellation_bpsk().base(),
            digital.IR_MMSE_8TAP,
            128,
            [])
        self.connect((self.half_shift, 0), (self.clk_sync, 0))

        # slice for output
        self.final_slice = digital.binary_slicer_fb()
        self.connect((self.clk_sync, 0), (self.final_slice, 0))
        self.connect((self.final_slice, 0), (self, 0))

        # also connect the optional raw demod port
        self.connect((self.raw_demod, 0), (self, 1))

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.clk_sync.set_sps(self.sps)

    def get_threshold(self):
        return self.threshold

    def set_threshold(self, threshold):
        self.threshold = threshold
        self.threshold_shift.set_k(-1 * self.threshold)
