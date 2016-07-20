#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2016 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr
from gnuradio import blocks
from gnuradio import gr
from gnuradio import analog
import random
import numpy
import pmt
import string
import math

class Rx(gr.hier_block2):
    """ Generates oscillators with frequency equals to that of hopping sequence produced at the transmitter.
        It starts working when it receives an ack float signal on its input signal  """
    def __init__(
                 self,
    		 n_channels,burst_length,
    		 freq_delta, base_freq,
    		 seed,rate
		):
       gr.hier_block2.__init__(self,
	    "HoppingRx",
	    gr.io_signature(1, 1, gr.sizeof_float), # Input Signature
	    gr.io_signature(1, 1, gr.sizeof_gr_complex), # Output Signature
       )

       ##################################################
       # Hopping Sequence
       ##################################################

       lowest_frequency = base_freq - numpy.floor(n_channels/2) * freq_delta
       self.hop_sequence = [lowest_frequency + n * freq_delta for n in xrange(n_channels)]
       random.seed(seed)	
       lam = random.random()        
       random.shuffle(self.hop_sequence, lambda: lam)
       
       senstivity = 2*math.pi

       ##################################################
       # Blocks
       ##################################################
       self.hop_vec = blocks.vector_source_f((self.hop_sequence), repeat=True)
       self.repeat_blk = blocks.repeat(gr.sizeof_float*1, burst_length)
       self.vco_blk = blocks.vco_c(rate,senstivity,1.0)
       
       self.null_snk = blocks.null_sink(gr.sizeof_float*1)
       ##################################################
       # Connections
       ##################################################
       self.connect((self.hop_vec,0),(self.repeat_blk,0))
       self.connect((self.repeat_blk,0),(self.vco_blk,0))
       self.connect((self.vco_blk,0),self)
       self.connect(self,(self.null_snk,0))
       
       threshold = self              

    def begin(self,):
	Rx.unlock()			# I found this in the hier_block2.h

    def end(self,):		
        Rx.lock()			

    def work(self,input_items,output_items):
        for i in xrange(len(input_items)):
           
           if input_items[i] > 0:
              Rx.begin()
           else:
              Rx.end()    
	
