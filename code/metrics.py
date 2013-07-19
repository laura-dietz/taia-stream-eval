import numpy as np
from numpy import sum

def aucEval_slow(data, gt, gf):
    _gt = np.count_nonzero(data)
    _gf = len(data) - _gt
    allPairs = _gt * _gf

    accum = 0
    correct = 0
    for i in data:
        if i:
            correct += 1
        else:
            accum += correct

    if allPairs == 0 or len(data)==0:
        return 0.5
        
    return 1. * accum / allPairs
    
def aucEval(data, gt, gf):
    _gt = np.count_nonzero(data)
    _gf = len(data) - _gt
    allPairs = _gt * _gf

    accum = np.cumsum(data)
    accum = sum(accum[np.logical_not(data)])
    if allPairs == 0 or len(data)==0:
        return 0.5
        
    return 1. * accum / allPairs

def normalizeAUC(data, gt, gf):
    classicAUC = aucEval(data, gt, gf)
    scaledAUC = (classicAUC - 0.5) * 2
    return scaledAUC

def extendedAucEval(data, gt, gf):
    _gt = np.count_nonzero(data)
    _gf = len(data) - _gt
    allPairs = gt * _gf  #virtually add ground truth docs that were not part of the ranking

    accum = np.cumsum(data)
    accum = sum(accum[np.logical_not(data)])
    if allPairs == 0 or len(data)==0:
        return 0.5
        
    return 1. * accum / allPairs

def normalizeExtendedAUC(data, gt, gf):
    classicAUC = extendedAucEval(data, gt, gf)
    scaledAUC = (classicAUC - 0.5) * 2
    return scaledAUC

def precREval(data, gt, gf):
    if(gt == 0): print 'gt=0 in precREval'
    return 1.0 * sum(data[0:gt])/gt    
           
def mapEval(data, gt, gf):
     relevant = np.count_nonzero(data)
     if relevant == 0: 
         #print 'mapEval: No relevant documents'
         return 0.0
     d = np.array(data, dtype='f8')
     prec = np.cumsum(d) / (np.arange(len(d)) + 1)
     score = 1.0 * np.sum(prec[data]) / gt
     #print 'mapscore = ',score, 'relevant', relevant,  'prec',prec,
     return score
        
def dcg(data):
    d = np.array(data, dtype='f8')
    return sum(d / np.log(np.arange(len(d))+2))
    
def generate_ideal(gt, gf):    
    ideal = np.zeros(gt+gf)
    ideal[:gt] = True
    return ideal
    
def ndcgEval(data, gt, gf):
    ideal = generate_ideal(gt, gf)
    dcgScore = dcg(data)
    norm = dcg(ideal[:len(data)])
    if(norm == 0): print('norm=0 in ndcgEval')
    return dcgScore / norm
        
def ndcgREval(data, gt, gf):
    ideal = generate_ideal(gt,gf)
    dcgScore = dcg(data[:(gt)])
    norm = dcg(ideal[:(gt)][:len(data)])
    if(norm == 0): print('norm=0 in ndcgREval')
    return dcgScore / norm
        
def ndcg2REval(data, gt, gf):
    ideal = generate_ideal(gt,gf)
    dcgScore = dcg(data[:(2*gt)])
    norm = dcg(ideal[:(2*gt)][:len(data)])
    if(norm == 0): print('norm=0 in ndcg2REval')
    return dcgScore / norm
        
def ndcgPlusREval(data, gt, gf):
    ideal = generate_ideal(gt,gf)
    dcgScore = dcg(data[:(gt+1)])
    norm = dcg(ideal[:(gt+1)][:len(data)])
    if(norm == 0): print('norm=0 in ndcgPlusREval')
    return dcgScore / norm

 
