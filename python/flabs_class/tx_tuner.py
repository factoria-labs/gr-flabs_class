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
from gnuradio import analog
from gnuradio import blocks

class tx_tuner(gr.hier_block2):
    """
    docstring for block tx_tuner
    """
    def __init__(self, samp_rate, center_freq, tune_freq):
        gr.hier_block2.__init__(self,
            "tx_tuner",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),  # Input signature
            gr.io_signature(1, 1, gr.sizeof_gr_complex)) # Output signature

        ##################################################
        # Parameters
        ##################################################
        self.center_freq = center_freq
        self.samp_rate = samp_rate
        self.tune_freq = tune_freq

        # complex sinusoid for upconversion
        self.complex_sine = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, (tune_freq - center_freq), 1, 0, 0)

        # multiply
        self.mult = blocks.multiply_vcc(1)
        self.connect((self, 0), (self.mult, 0))
        self.connect((self.complex_sine, 0), (self.mult, 1))

        # connect multiply to block output
        self.connect((self.mult, 0), (self, 0))


    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.complex_sine.set_frequency((self.tune_freq - self.center_freq))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.complex_sine.set_sampling_freq(self.samp_rate)

    def get_tune_freq(self):
        return self.tune_freq

    def set_tune_freq(self, tune_freq):
        self.tune_freq = tune_freq
        self.complex_sine.set_frequency((self.tune_freq - self.center_freq))