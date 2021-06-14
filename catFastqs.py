import argparse
import os
import glob
import subprocess as sp 

global thisDir
thisDir=os.path.dirname(os.path.realpath(__file__))+'/'

def catSamples(lista, out):
    r1 = lista
    # -1 por el undetermined.fastq.gz
    for i in range(0,len(r1)-1,2):
        output = None
        print("cat " + r1[i] + " " + r1[i+1] + " > " + out + r1[i][0:r1[i].find("_S")] + ".fastq.gz")
        try:
            output = sp.check_output("cat " + r1[i] + " " + r1[i+1] + " > " + out + r1[i][0:r1[i].find("_S")] + ".fastq.gz",
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
catSamples(readsFiles1, outDir)