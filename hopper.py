#!/usr/bin/env python
#
# Copyright 2014 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

"""
TXs a waveform (either from a file, or a sinusoid) in a frequency-hopping manner.
"""
import random
import numpy
import argparse
import pmt
import TAGS # For Optimization
from gnuradio import gr
from gnuradio import blocks
from gnuradio import uhd




class hopper(gr.hier_block2):
    """ Provides tags for frequency hopping """
    def __init__(
            self,
            n_bursts, n_channels,
            freq_delta, base_freq, dsp_tuning,
            burst_length, base_time, hop_time,
            seed,rate,
	    post_tuning=False, 
            tx_gain=0,
            verbose=False
        ):
        gr.hier_block2.__init__(self,
            "Hopping",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
        )
        n_samples_total = n_bursts * burst_length
        lowest_frequency = base_freq - numpy.floor(n_channels/2) * freq_delta
        self.hop_sequence = [lowest_frequency + n * freq_delta for n in xrange(n_channels)]
	random.seed(seed)	
	lam = random.random()        
	random.shuffle(self.hop_sequence, lambda: lam)
        # Repeat that:
        self.hop_sequence = [self.hop_sequence[x % n_channels] for x in xrange(n_bursts)]
        if verbose:
            print "Hop Frequencies  | Hop Pattern"
            print "=================|================================"
            for f in self.hop_sequence:
                print "{:6.3f} MHz      |  ".format(f/1e6),
                if n_channels < 50:
                    print " " * int((f - base_freq) / freq_delta) + "#"
                else:
                    print "\n"
            print "=================|================================"
        # There's no real point in setting the gain via tag for this application,
        # but this is an example to show you how to do it.
        gain_tag = gr.tag_t()
        gain_tag.offset = 0
        gain_tag.key = pmt.string_to_symbol('tx_command')
        gain_tag.value = pmt.to_pmt({'gain': tx_gain})
        tag_list = [gain_tag,]
        for i in xrange(len(self.hop_sequence)):
            tune_tag = gr.tag_t()
            tune_tag.offset = i * burst_length
            if i > 0 and post_tuning and not dsp_tuning: # TODO dsp_tuning should also be able to do post_tuning
                tune_tag.offset -= 1 # Move it to last sample of previous burst
            if dsp_tuning:
                tune_tag.key = pmt.string_to_symbol('tx_command')
                tune_tag.value = pmt.to_pmt({'rf_freq_policy': int(ord('N')), 'lo_freq': base_freq, 'dsp_freq_policy': int(ord('M')),'dsp_freq': base_freq - self.hop_sequence[i] })
            else:
                tune_tag.key = pmt.string_to_symbol('tx_freq')
                tune_tag.value = pmt.to_pmt(self.hop_sequence[i])
            tag_list.append(tune_tag)
            length_tag = gr.tag_t()
            length_tag.offset = i * burst_length
            length_tag.key = pmt.string_to_symbol('packet_len')
            length_tag.value = pmt.from_long(burst_length)
            tag_list.append(length_tag)	
            time_tag = gr.tag_t()
            time_tag.offset = i * burst_length
            time_tag.key = pmt.string_to_symbol("tx_time")
            time_tag.value = pmt.make_tuple(
                    pmt.from_uint64(int(base_time + i * hop_time)),
                    pmt.from_double((base_time + i * hop_time) % 1),
            )
            tag_list.append(time_tag)
        #############################################
        # Old Version
        #############################################
        tag_source = blocks.vector_source_c((1.0,) * n_samples_total, repeat= True, tags=tag_list)
        mult = blocks.multiply_cc()
        self.connect(self, mult, self)
        self.connect(tag_source, (mult, 1))

        #############################################
        # Optimized Version
        #############################################
        #tag_source = blocks.vector_source_c((1.0,) * n_samples_total, repeat= True, tags=TAGS.tags.tag_list)
        #mult = blocks.multiply_cc()
        #self.connect(self, mult, self)
        #self.connect(tag_source, (mult, 1))

class FlowGraph(gr.top_block):
    """ Flow graph that does the frequency hopping. """
    def __init__(self, options):
        gr.top_block.__init__(self,in_sig  = [numpy.complex],
				   out_sig = [numpy.complex])

        if options.input_file is not None:
            src = blocks.file_source(gr.sizeof_gr_complex, options.filename, repeat=True)
        else:
            src = in_sig  
	#blocks.vector_source_c((.5,) * int(1e6) * 2, repeat=True)
        # Setup USRP
        #self.u = uhd.usrp_sink(options.args, uhd.stream_args(underflow_policy="next_burst",cpu_format="fc32",channels=range(1),),"packet_len")
        #if(options.spec):
        #   self.u.set_subdev_spec(options.spec, 0)
        #if(options.antenna):
        #    self.u.set_antenna(options.antenna, 0)
        #self.u.set_samp_rate(options.rate)
        # Gain is set in the hopper block
        #if options.gain is None:
        #    g = self.u.get_gain_range()
        #    options.gain = float(g.start()+g.stop())/2.0
        #print "-- Setting gain to {} dB".format(options.gain)
        #r = self.u.set_center_freq(options.freq)
        #if not r:
        #    print '[ERROR] Failed to set base frequency.'
        #    raise SystemExit, 1
        hopper_block = hopper(
                options.num_bursts, options.num_channels,
                options.freq_delta, options.freq, options.dsp,
                options.samp_per_burst, 1.0, options.hop_time,
                options.post_tuning,
                options.gain,
                options.verbose,
        )
        self.connect(src, hopper_block,out_sig)

def print_hopper_stats(args):
    """ Nothing to do with Grace Hopper """
    print """
Parameter          | Value
===================+=========================
Hop Interval       | {hop_time} ms
Burst duration     | {hop_duration} ms
Lowest Frequency   | {lowest_freq:6.3f} MHz
Highest Frequency  | {highest_freq:6.3f} MHz
Frequency spacing  | {freq_delta:6.4f} MHz
Number of channels | {num_channels}
Sampling rate      | {rate} Msps
Transmit Gain      | {gain} dB
===================+=========================
    """.format(
            hop_time=args.hop_time,
            hop_duration=1000.0/args.rate*args.samp_per_burst,
            gain=args.gain,
            lowest_freq=args.freq/1e6,
            highest_freq=(args.freq + (args.num_channels-1) * args.freq_delta)/1e6,
            freq_delta=args.freq_delta/1e6,
            num_channels=args.num_channels,
            rate=args.rate/1e6,
        )

def main():
    """ Go, go, go! """
    args = setup_parser().parse_args()
    if (1.0 * args.samp_per_burst / args.rate) > args.hop_time * 1e-3:
        print "Burst duration must be smaller than hop time."
        exit(1)
    if args.verbose:
        print_hopper_stats(args)
    top_block = FlowGraph(args)
    print "Starting to hop, skip and jump... press Ctrl+C to exit."
    top_block.u.set_time_now(uhd.time_spec(0.0))
    top_block.run()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass    
    


