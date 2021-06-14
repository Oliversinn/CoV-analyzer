import argparse
import os
import sys
import glob
import subprocess as sp 

global thisDir
thisDir=os.path.dirname(os.path.realpath(__file__))+'/'

def intervealSamples(lista, out):
    r1 = lista
    print(r1)
    r2 = []
    for i in range(0,len(r1)):
        posicion = r1[i].find('_R1_0')
        r2.append(r1[i][:posicion+2]+'2'+r1[i][posicion+3:])
        output = None
        try:
            print(r2[i])
            output = sp.check_output("paste <(zcat " + r1[i] + " | paste - - - -) "
                            "<(zcat " + r2[i] + " | paste - - - -) "
                            "| tr '\\t' '\\n' | gzip > " +  out+ r1[i][0:r1[i].find("_L001")] + ".fastq.gz",
                                    shell=True,stderr=sp.STDOUT,executable="/bin/bash")
        except sp.CalledProcessError as e:
            output = e.output
        print(output)
         

# Section of input arguments
par=argparse.ArgumentParser(description='This script concatenates Fastqs')
par.add_argument('--readsFiles_r1','-r1',dest='readsFiles1',type=str,help='regular expression for choosing files with R1 reads',required=True)
par.add_argument('--readsFiles_r2','-r2',dest='readsFiles2',type=str,help='regular expression for choosing files with R2 reads (optional)',required=False)
par.add_argument('--outDir','-out',dest='outDir',type=str,help='directory for output',required=True)
args=par.parse_args()

readsFiles1=sorted(glob.glob(args.readsFiles1))
if len(readsFiles1)==0:
    print('ERROR: no files for reads R1 were selected!'); exit(0)
if args.readsFiles2:
    readsFiles2=sorted(glob.glob(args.readsFiles2))
    if len(readsFiles2)==0:
        print('ERROR: no files for reads R2 were selected!'); exit(0)
else:
    readsFiles2=[False]*len(readsFiles1)
outDir=args.outDir
if outDir[-1]!='/': outDir+='/'
# Create output directory
if not os.path.isdir(outDir):
    os.mkdir(outDir)
intervealSamples(readsFiles1, outDir)