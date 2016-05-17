#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2016 Matt Hostetter.
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

import numpy as np 

# Configuration
M = 4 # QPSK
fc = 0e3 # Hz
fs = 500e3 # samples/second
fsym = 50e3 # symbols/second
sps = int(fs/fsym) # samples/symbol
ebno_db = 30
filename = "/home/matt/IQ/psk_burst.fc32"

print "Generating PSK Burst..."
print "  M      = %d" % (M)
print "  fc     = %d Hz" % (fc)
print "  fs     = %d sps" % (fs)
print "  fsym   = %d sym/s" % (fsym)
print "  sps    = %d" % (sps)
print "  Eb/N0  = %1.1f dB" % (ebno_db)

# Symbol 0 = 0/M*360 deg
# Symbol 1 = 1/M*360 deg
# Symbol 2 = 2/M*360 deg
# etc ...

# symbols = np.concatenate((np.zeros(16), np.random.randint(0,M,64)))
symbols = np.concatenate((np.array([0,2]*8), np.random.randint(0,M,64)))
symbols = symbols.astype(float)

# Number of samples in the burst
N_syms = len(symbols)
N_samps = sps*N_syms

print "\n%d symbols" % (N_syms)
print symbols

# Calculate phase values for each samples (changes per symbol)
phase = np.zeros(N_samps)
for ii in range(0,N_syms):
    phase[ii*sps:(ii+1)*sps] = (symbols[ii]/M*2*np.pi)*np.ones(sps)

# Calculate complex IQ samples
samps = np.exp(1j*(2*np.pi*fc/fs*np.arange(0,N_samps) + phase))

# Add noise (zeros for now) samples before and after the burst
samps = np.concatenate((np.zeros(int(fs*20e-3)), samps, np.zeros(int(fs*20e-3))))

print "len(samps)", (len(samps))
print "samps"
print samps

# Calculate noise standard deviation for a given Eb/N0
ebno = 10.0**(ebno_db/10)
eb = np.sum(np.abs(samps))/(np.log2(M)*N_syms)
no = eb/ebno
sigma2 = no/2
sigma = np.sqrt(sigma2)

# Add noise
samps += np.random.normal(0, sigma, len(samps))

# Format interleaved IQ float array
floats = np.zeros(2*len(samps), dtype=np.float32)
floats[0:len(floats):2] = samps.real
floats[1:len(floats):2] = samps.imag

# Write to file
fid = open(filename, "w")
floats.tofile(fid)