# -*- coding: utf-8 -*-
"""
For automated test of metrics with respectg other evaluation package (galago's trec_eval)
"""

from metrics import *
import numpy as np
import sys

metrics = {
'nDCG@R': ndcgREval,'Prec@R': precREval, 'correctedAUC':normalizeAUC, 'MAP':mapEval
}


commandinput = ','.join(sys.argv[1:])

arr = [True if split.lower()=='true' else False for split in commandinput.split(',')]
gt = sum(1 if split.lower()=='true' else 0 for split in commandinput.split(','))
gf = len(arr) - gt


for metricname, metric in metrics.items():
    print metricname,metric(np.array(arr), gt, gt)
