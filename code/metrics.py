"""
Implementation of ranking metrics.
"""
import numpy as np
from numpy import sum

def aucEval(data, gt, gf):
    """
     Area under the Receiver-Operator curve.

     This is a fast implementation that follows the trajectory of the ROC curve and needs only a single pass through the data.
     Start in lower-right corner, for a pos document go up, for neg document go right.

     This implementation assumes that the ranking is complete.
    """
    _gt = np.count_nonzero(data)
    _gf = len(data) - _gt
    allPairs = _gt * _gf

    accum = np.cumsum(data)
    accum = sum(accum[np.logical_not(data)])
    if allPairs == 0 or len(data)==0:
        return 0.5
        
    return 1. * accum / allPairs

def normalizeAUC(data, gt, gf):
    """
    Rescale aucEval to [-1, +1] to better match the perturbation level
    """
    classicAUC = aucEval(data, gt, gf)
    scaledAUC = (classicAUC - 0.5) * 2
    return scaledAUC

def extendedAucEval(data, gt, gf):
    """
    Hack AUC to gracefully handle the case where not all positive documents are contained in the ranking
    """
    _gt = np.count_nonzero(data)
    _gf = len(data) - _gt
    allPairs = gt * _gf  #virtually add ground truth docs that were not part of the ranking

    accum = np.cumsum(data)
    accum = sum(accum[np.logical_not(data)])
    if allPairs == 0 or len(data)==0:
        return 0.5
        
    return 1. * accum / allPairs

def normalizeExtendedAUC(data, gt, gf):
    """
    Rescale extendedAucEval to [-1, +1] to better match the perturbation level
    """
    classicAUC = extendedAucEval(data, gt, gf)
    scaledAUC = (classicAUC - 0.5) * 2
    return scaledAUC

def precREval(data, gt, gf):
    """
    Compute R-Precision (Precision at a rank that represents the number of relevant documents).
    """
    if(gt == 0): print 'gt=0 in precREval'
    return 1.0 * sum(data[0:gt])/gt    
           
def mapEval(data, gt, gf):
    """
    Compute Mean average precision following this algorithm:
    - for every rank p that yields a positive document:
    --- compute precision at p
    - take the average of all computed precisions
    """
    relevant = np.count_nonzero(data)
    if relevant == 0:
        # no relevant documents, produce 0.0
        return 0.0
    d = np.array(data, dtype='f8')
    prec = np.cumsum(d) / (np.arange(len(d)) + 1)
    score = 1.0 * np.sum(prec[data]) / gt
    return score
        
def dcg(data):
    """
    Compute Discounted Cumulative Gain which is computed by
    - for every rank p that yields a positive document:
    --- 1/log(p+2)
    - sum over all values
    """
    d = np.array(data, dtype='f8')
    return sum(d / np.log(np.arange(len(d))+2))
    
def generate_ideal(gt, gf):
    """
    generate the ideal ranking for nDCG
    """
    ideal = np.zeros(gt+gf)
    ideal[:gt] = True
    return ideal
    
def ndcgEval(data, gt, gf):
    """
    Normalized Discounted Cumulative Gain:
     DCG / DCG(ideal ranking)
    """
    ideal = generate_ideal(gt, gf)
    dcgScore = dcg(data)
    norm = dcg(ideal[:len(data)])
    if(norm == 0): print('norm=0 in ndcgEval')
    return dcgScore / norm
        
def ndcgREval(data, gt, gf):
    """
    Compute NDCG@R, where R is the number of relevant documents
    """
    ideal = generate_ideal(gt,gf)
    dcgScore = dcg(data[:(gt)])
    norm = dcg(ideal[:(gt)][:len(data)])
    if(norm == 0): print('norm=0 in ndcgREval')
    return dcgScore / norm
