# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 22:39:48 2013

@author: dietz
"""

from metrics import *
import numpy as np
import sys

metrics = {
'nDCG@R': ndcgREval,'Prec@R': precREval, 'correctedAUC':normalizeAUC, 'MAP':mapEval
}


input = ','.join(sys.argv[1:])

arr = [True if str.lower()=='true' else False for str in input.split(',')]
gt = sum(1 if str.lower()=='true' else 0 for str in input.split(','))
gf = len(arr) - gt


for metricname, metric in metrics.items():
    print metricname,metric(np.array(arr), gt, gt)


#print 0.0, metric(np.array([False]), 0,1)
#print 0.0, metric(np.array([]), 1,0)
#print 1.0, metric(np.array([True,True,False,False]), 2, 2)
#print 1./2, metric(np.array([False,True,True,False]), 2, 2)
#print 1./2, metric(np.array([True,False,False,True]), 2, 2)
#print 2./3, metric(np.array([True,False,False,True,False]), 2, 3)
#print 1./2, metric(np.array([True,True,True,True]), 4, 0)
#print 2./3, metric(np.array([True,True,False,True]), 2, 0)