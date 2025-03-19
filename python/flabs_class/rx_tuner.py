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
from gnuradio import filter
from gnuradio.filter import firdes


class rx_tuner(gr.hier_block2):
    """
    docstring for block rx_tuner
    """
    def __init__(self,
                 samp_rate_in=4e6,
                 samp_rate_out=200e3,
                 center_freq=100e6,
                 tune_freq=99.1e6,
                 chan_width=150e3):
        gr.hier_block2.__init__(self,
            "RX Tuner",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),  # Input signature
            gr.io_signature(1, 1, gr.sizeof_gr_complex)) # Output signature

        ##################################################
        # Parameters
        ##################################################
        self.center_freq = center_freq
        self.chan_width = chan_width
        self.samp_rate_in = samp_rate_in
        self.samp_rate_out = samp_rate_out
        self.tune_freq = tune_freq

        self.tuner = filter.freq_xlating_fir_filter_ccc(
            (int(samp_rate_in/samp_rate_out)),
            firdes.low_pass(1, samp_rate_in, chan_width/2, chan_width/20),
            (tune_freq - center_freq),
            samp_rate_in)
        self.connect((self, 0), (self.tuner, 0))
        self.connect((self.tuner, 0), (self, 0))

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.tuner.set_center_freq((self.tune_freq - self.center_freq))

    def get_chan_width(self):
        return self.chan_width

    def set_chan_width(self, chan_width):
        self.chan_width = chan_width
        self.tuner.set_taps(firdes.low_pass(1, self.samp_rate_in, self.chan_width/2, self.chan_width/20))

    def get_samp_rate_in(self):
        return self.samp_rate_in

    def set_samp_rate_in(self, samp_rate_in):
        self.samp_rate_in = samp_rate_in
        self.tuner.set_taps(firdes.low_pass(1, self.samp_rate_in, self.chan_width/2, self.chan_width/20))

    def get_samp_rate_out(self):
        return self.samp_rate_out

    def set_samp_rate_out(self, samp_rate_out):
        self.samp_rate_out = samp_rate_out

    def get_tune_freq(self):
        return self.tune_freq

    def set_tune_freq(self, tune_freq):
        self.tune_freq = tune_freq
        self.tuner.set_center_freq((self.tune_freq - self.center_freq))