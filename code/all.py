#import subprocess
from string import *

evalDir = "~/kba-evaluation/taia-stream-eval/data/c/"
judgmentLevel = 2

env = {'judgmentLevel':judgmentLevel,
       'evalDir':evalDir}


import os
os.system('python weights-over-time.py -d {evalDir}  --judgmentLevel {judgmentLevel}' % env)
os.system('python total-stats.py -d {evalDir}  --judgmentLevel {judgmentLevel} --weighted' % env)

#python total-stats.py -d $evalDir --judgmentLevel 2 --weighted