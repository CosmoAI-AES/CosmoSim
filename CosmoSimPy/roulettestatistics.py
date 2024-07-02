#!/usr/bin/env python3
# (C) 2024: Hans Georg Schaathun <georg@schaathun.net>

import pandas as pd
import argparse

from RouletteAmplitudes import RouletteAmplitudes 




if __name__ == "__main__":
    parser = argparse.ArgumentParser(
          prog = 'Roulette Statistics',
          description = 'Roulette Statistics',
          epilog = '')

    parser.add_argument("-o",'--outfile',required=False)
    parser.add_argument('fn')
    args = parser.parse_args()

    dataset = pd.read_csv( args.fn )
    cols = dataset.columns
    ramp = RouletteAmplitudes( cols )

    with open(args.outfile,"w") as out:
        out.write( "\\begin{tabular}{|rr|rr|rr|}\n" )
        out.write( "\\hline\n" )
        out.write( " $m$ & $s$ & $\\bar\\alpha_m^s$ & $\\mathsf{stdev}(\\alpha_m^s)$" )
        out.write( "     & $\\bar\\beta_m^s$ & $\\mathsf{stdev}(\\beta_m^s)$ \\\\\n" )
        out.write( "\\hline\n" )
        out.write( "\\hline\n" )
        for m in range(ramp.getNterms()+1):
            for s in range((m+1)%2,m+2,2):
                 avg = dataset[f"alpha[{m}][{s}]"].mean()
                 sd = dataset[f"alpha[{m}][{s}]"].std()
                 out.write( f"  ${m}$ & ${s}$ & ")
                 out.write( f"${avg}$ & ${sd}$ & ")
                 avg = dataset[f"beta[{m}][{s}]"].mean()
                 sd = dataset[f"beta[{m}][{s}]"].std()
                 out.write( f"${avg}$ & ${sd}$ \\\\\n ")
 
        out.write( "\\hline\n" )
        out.close()

