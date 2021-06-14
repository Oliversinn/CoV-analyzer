# Oliver Mazariegos

import argparse
import subprocess as sp
import os
import sys
from multiprocessing import Pool, Queue
import multiprocessing as mp
import glob
import re
import math

# Global variables
global thisDir, configs, allWork, threads

thisDir = os.path.dirname(os.path.realpath(__file__))+'/'
configs = open(thisDir+'config.txt').read().split('\n')

def showWorkDone(done, allWork):
    workDone = round((done/allWork)*100,2)
    sys.stdout.write('\r'+str(workDone)+'%\n')
    sys.stdout.flush()

# Input arguments
par=argparse.ArgumentParser(description='This script do all processing of SARS-CoV-2 sequencing data')
par.add_argument('--readsFiles_r1','-r1',dest='readsFiles1',type=str,help='regular expression for choosing files with R1 reads',required=True)
par.add_argument('--readsFiles_r2','-r2',dest='readsFiles2',type=str,help='regular expression for choosing files with R2 reads (optional)',required=False)
par.add_argument('--readsFiles_N','-rN',dest='readsFilesN',type=str,help='regular expression for choosing files with native R1 reads (including Undetermined) to evaluate effectivity of trimming reads  (alternative). If you do not have trimmed reads, do not use this parameter',required=False)
par.add_argument('--patientsTable','-pat',dest='patientsTable',type=str,help='table with information about each patient: ngs_num patient_id barcode1 barcode2',required=False)
par.add_argument('--primersCoords','-primer',dest='primersCoords',type=str,help='table with information about amplicon coordinates without column headers: amplicon_number | chromosome | start | end. (Is not required)',required=False,default=configs[9])
par.add_argument('--fixMisencodedQuals','-fix',dest='fixMisEncoded',action='store_true',help='this parameter is needed if GATK shows error of quality encoding')
par.add_argument('--outDir','-out',dest='outDir',type=str,help='directory for output',required=True)
par.add_argument('--threads','-th',dest='threads',type=int,help='number of threads',default=2)
par.add_argument('--tool-threads','-tt',dest='toolThreads',type=int,help='number of threads for each tool. Number of --threads multiplied by the number of --tool-threads must not exceed number of CPU cores',default=1)
par.add_argument('--run-name','-run',dest='runName',type=str,help='Name of run. This name will be added into the name of the final output file. Default: hCoV-2',required=False,default='hCoV-2')
par.add_argument('--without-joinment','-notjoin',dest='notToJoin',action='store_true',help='use this parameter if you only want to process patients reads separately without joining them (useful if you have an opportunity to separate processing onto several machines)')
par.add_argument('--only-join','-onlyjoin',dest='onlyJoin',action='store_true',help='use this parameter if you only want to join already processed patients reads')
par.add_argument('--language','-lang',dest='lang',type=str,help='Language of report and text on figures (spanish or english). Default: english',default='english')
args=par.parse_args()

langs=['russian','english']
if args.lang not in langs:
    print('#'*10,'\nWARNING! Chosen language is not accepted. Use default english...')
if args.notToJoin and args.onlyJoin:
    print("ERROR: only one of parameters can be used, -notjoin or -onlyjoin. But you have tried to use both")
    exit(0)
readsFiles1=sorted(glob.glob(args.readsFiles1))
if len(readsFiles1)==0:
    print('ERROR: no files for reads R1 were selected!'); exit(0)
reference='./reference/NC_045512.2.fasta'
if args.readsFiles2:
    readsFiles2=sorted(glob.glob(args.readsFiles2))
    if len(readsFiles2)==0:
        print('ERROR: no files for reads R2 were selected!'); exit(0)
else:
    readsFiles2=[False]*len(readsFiles1)
if args.readsFilesN:
    readsFilesN=sorted(glob.glob(args.readsFilesN))
    if len(readsFilesN)==0:
        print('ERROR: no files for native reads were selected!'); exit(0)
if args.patientsTable:
    patientsTable=args.patientsTable
    if not os.path.exists(patientsTable):
        print('ERROR: patients table file does not exist!'); exit(0)
    else:
        patientsTable=os.path.abspath(patientsTable)
if args.primersCoords and not os.path.exists(args.primersCoords):
    print('ERROR: primers coords table file does not exist!'); exit(0)
elif not args.primersCoords:
    args.primersCoords=thisDir+'primers_coords_default.csv'
outDir=args.outDir
if outDir[-1]!='/': outDir+='/'
# Create output directory
if not os.path.isdir(outDir):
    os.mkdir(outDir)
t=int(args.threads)
if not args.onlyJoin:
    rect=int(mp.cpu_count()/args.toolThreads)
    if t>rect:
        print('WARNING: number of threads ('+str(t)+') is too high! Recomended number of threads is '+str(rect))
        print('Continue anyway? (y/n)')
        text=input()
        if text!='Y' and text!='y':
            exit(0)
    threads=str(args.toolThreads)
    output=sp.check_output('df '+outDir,shell=True,stderr=sp.STDOUT).decode('utf-8')
    available=int(output.split('\n')[1].split()[3])
    neededFreeSpace=0
    for r1,r2 in zip(readsFiles1,readsFiles2):
        neededFreeSpace+=os.path.getsize(r1)+os.path.getsize(r2)
    neededFreeSpace=int(neededFreeSpace*4/1024)
    if available<neededFreeSpace:
        print('WARNING: there is not enough free space for analysis. You need about '+str(neededFreeSpace)+' Kb. But available free space is '+str(available)+' Kb')
        print('Continue anyway? (y/n)')
        text=input()
        if text!='Y' and text!='y':
            exit(0)
    # Check that file with reference genome sequence exists
    if not os.path.exists(reference):
        print('#'*10,'\nERROR: File with reference sequence was not found!\n'
                  'It should be:',reference+'\n'+'#'*10)
        exit(0)


