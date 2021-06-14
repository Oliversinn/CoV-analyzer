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


