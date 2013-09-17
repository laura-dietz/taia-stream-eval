import kbaconfig


epochsPerWeek = kbaconfig.epochsPerWeek
epochsPerDay = kbaconfig.epochsPerDay


## evalTR = 1325376000  # this is the old eval time range, Jan 1st
#evalTR = 1326334731 # this is the new eval time range, J1
#evalTRend = 1338508800

evalTR = kbaconfig.evalTR
evalTRend = kbaconfig.evalTRend


def epochsToDate(d):
    return (d - evalTR) / epochsPerDay


weekStarts = range(evalTR, evalTRend, epochsPerWeek)
dayStarts = range(evalTR, evalTRend, epochsPerDay)
allStarts = [evalTR]


def intervalRange(epochsPerInterval):
    starts = xrange(evalTR, evalTRend, epochsPerInterval)
    intervalList = [(start, start + epochsPerInterval) for start in starts]
    return intervalList


def correctWeighting(values, posData, totalposvalues, numberOfIntervals):
    return correctedWeightingMultiMix(values, posData, totalposvalues, numberOfIntervals)


def correctedWeightingGeoMean(values, posData, totalposvalues, numberOfIntervals):
    correctedWeighting = values ** (posData / totalposvalues * numberOfIntervals)
    return correctedWeighting


def correctedWeightingMultiMix(values, posData, totalposvalues, numberOfIntervals):
    correctedWeighting = posData / totalposvalues * numberOfIntervals * values
    return correctedWeighting


def correctedWeightingUnif(values, posData, totalposvalues, numberOfIntervals):
    return values


def renameMetric(metric):
    if metric == 'Prec@R':
        return 'R-prec'
    elif metric == 'correctedAUC':
        return 'ROC-AUC'
    elif metric == 'nDCG@R':
        return 'NDCG@R'
    else:
        return metric