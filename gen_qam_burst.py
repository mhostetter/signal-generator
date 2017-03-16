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
M = 64 # QAM
fc = 0e3 # Hz
fs = 500e3 # samples/second
fsym = 50e3 # symbols/second
sps = int(fs/fsym) # samples/symbol
ebno_db = 1000
filename = "qam_burst.fc32"

print "Generating QAM Burst..."
print "  M      = %d" % (M)
print "  fc     = %d Hz" % (fc)
print "  fs     = %d sps" % (fs)
print "  fsym   = %d sym/s" % (fsym)
print "  sps    = %d" % (sps)
print "  Eb/N0  = %1.1f dB" % (ebno_db)

# Example: 16-QAM 
#   0  1 | 2  3
#        |
#   4  5 | 6  7
# -------|--------
#   8  9 | 10 11
#        |
#  12 13 | 14 15

sqrt_M = int(np.sqrt(M))

# symbols = np.concatenate((np.zeros(16), np.random.randint(0,M,64)))
symbols = np.concatenate((np.array([sqrt_M-1,sqrt_M*(sqrt_M-1)]*8), np.random.randint(0,M,256)))
symbols = symbols.astype(float)

symbol_lut = np.zeros(M, dtype=np.complex64)
for ii in range(0,sqrt_M):
	for jj in range(0,sqrt_M):
		symbol_lut[ii*sqrt_M+jj] = (np.sqrt(2.0)/(sqrt_M-1)*(-sqrt_M/2+jj+0.5)) + 1j*(np.sqrt(2.0)/(sqrt_M-1)*(sqrt_M/2-ii-0.5))

print "symbol_lut"
print symbol_lut

# Number of samples in the burst
N_syms = len(symbols)
N_samps = sps*N_syms

print "\n%d symbols" % (N_syms)
print symbols

# Calculate complex values for each sample (changes per symbol)
samps = np.zeros(N_samps, dtype=np.complex64)
for ii in range(0,N_syms):
    samps[ii*sps:(ii+1)*sps] = symbol_lut[symbols[ii]]*np.ones(sps)

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
samps += (np.random.normal(0, sigma, len(samps)) + 1j*np.random.normal(0, sigma, len(samps)))

# Format interleaved IQ float array
floats = np.zeros(2*len(samps), dtype=np.float32)
floats[0:len(floats):2] = samps.real
floats[1:len(floats):2] = samps.imag

# Write to file
fid = open(filename, "w")
floats.tofile(fid)