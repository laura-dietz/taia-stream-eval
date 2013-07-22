"""
Create randomly perturbed rankings to study the robustness of the measure with respect to variations in the ground truth.
"""

import matplotlib.pyplot as pl
import numpy as np
import random
from math import floor
from metrics import *
        
groundtruths = [(100,100),(50,50),(5,5),(20,180),(10,90),(1,9)]
perturbations = [0.1, 0.25, 0.5]

invisGt=0

        
#metrics = { 'MAP':mapEval}
metrics = {
'nDCG':ndcgEval, 'nDCG@R': ndcgREval,'Prec@R': precREval, 'AUC': aucEval, 'correctedAUC':normalizeAUC, 'MAP':mapEval}


def singleBitSwap(pert,elem):
   if np.random.rand() < pert:
       return not elem
   else:
       return elem

def bitSwap(idealData, pert, gt, gf):
    return [ singleBitSwap(pert,elem) for elem in idealData] 


def trueFalsePairSwap(idealData, pert, gt, gf):
    totalPool = gt * gf
    choices = int(pert * totalPool)
    trues = set(range(gt))
    falses = set(i+gt for i in range(gf))
    for c in range(choices):
        tIdx = random.choice(list(trues))
        fIdx = random.choice(list(falses))
        trues.add(fIdx)
        trues.remove(tIdx)
        falses.add(tIdx)
        falses.remove(fIdx)

    result = [ idx in trues for idx in range(gt+gf)]
    return result

def randomFrac(frac):
    intPart = floor(frac)
    remainder = frac - intPart
    rand = random.random()
    if(rand < remainder):
        return int(intPart) +1
    else:
        return int(intPart)

def trueSwap(idealData, pert, gt, gf):
    totalPool = gt
    choices = randomFrac(pert * totalPool)
    trues = set(range(gt))
    falses = set(i+gt for i in range(gf))
    for c in range(choices):
        tIdx = random.choice(list(trues))
        fIdx = random.choice(list(falses))
        trues.add(fIdx)
        trues.remove(tIdx)
        falses.add(tIdx)
        falses.remove(fIdx)

    result = [ idx in trues for idx in range(gt+gf)]
    return result


def simulate():
    scoresPerMetricPerPerturbation = {}

    for pert in perturbations:
        scoresPerMetric = {}
        for gt,gf in groundtruths:
           idealData = [True for i in range(gt)] + [False for i in range(gf)]
           runs = [ np.array(trueSwap(idealData, pert, gt, gf)) for run in range(1000)]  
           for metricname,metric in metrics.items():
               scores = [metric(data,gt+invisGt,gf) for data in runs]
               evalscore = np.mean(scores)
               #print gt, gf, pert, metricname, evalscore           
               scoresPerMetric.setdefault(metricname, []).append(evalscore)
        scoresPerMetricPerPerturbation[pert] = scoresPerMetric
    return scoresPerMetricPerPerturbation

def doplot(scoresPerMetricPerPerturbation):

    print scoresPerMetricPerPerturbation
    
    fig = pl.figure()    
    fig.add_subplot(4,2,1)
    pl.plot([0.1, 0.19,0.2,0.39,0.4,0.6],[0.9, 0.9, 0.75, 0.75,0.5,0.5], c='k', alpha=0.5)

    for pi, pert in enumerate(perturbations):
        scoresPerMetric = scoresPerMetricPerPerturbation[pert]
        for idx, (color,(name,scores)) in enumerate((zip('bgrykm', scoresPerMetric.items()))):
            pl.scatter(pert*np.ones_like(scores)+0.01*np.arange(len(scores)), scores,
                       c=color, label=name, alpha=0.7)            
        pl.ylim(0,1)
        pl.ylabel('score')
        pl.xlabel('perturbation')
        if pi==0: pl.legend(bbox_to_anchor=(0,0, 1,1), bbox_transform=pl.gcf().transFigure, fontsize='small')

    
    for idx, (metricname,metric) in zip([0,1,2,3,4,5],metrics.items()):
        fig.add_subplot(4,2,3+idx)
        for pert in perturbations:
            scoresPerMetric = scoresPerMetricPerPerturbation[pert]
            name = metricname
            scores = scoresPerMetric[metricname]
            color = 'bgrykm'[idx]
            pl.title(metricname)
            pl.scatter(pert*np.ones_like(scores)+0.01*np.arange(len(scores)), scores,
                               c=color, label=name, alpha=0.7)            
            pl.plot([0.1, 0.19,0.2,0.39,0.4,0.6],[0.9, 0.9, 0.75, 0.75,0.5,0.5], c='k', alpha=0.5)
            pl.ylim(0,1)


    fig.subplots_adjust(hspace=1)
    #pl.show()
    pl.savefig("metric-comparison.pdf")


results = simulate()
doplot(results)

