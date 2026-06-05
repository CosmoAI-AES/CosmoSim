#! /usr/bin/env python

import pandas as pd
import argparse

parser = argparse.ArgumentParser( prog='chiconvert')
parser.add_argument('infile')
parser.add_argument('outfile')
args = parser.parse_args()

df = pd.read_csv( args.infile )


cols = [ "x", "y", "sigma", "sigma2" ]
# for k in cols:
#    df[k] = df[k]* df["chi"]/100
df["einsteinR"] = df["einsteinR"]*100/ df["chi"]

df.to_csv( args.outfile, index=False)

