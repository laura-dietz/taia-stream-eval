#!/bin/bash

PYTHONPATH=`dirname $0`
datadir=`pwd`
#judgmentLevel=1 # for central + relevant
#judgmentLevel=2 # for central only
judgmentLevel="$1"



## ====== COLLAPSE JUDGMENTS =======

echo "you need to modify the python scripts collapse-truth-judgment.py and truthutil.py to reflect your paths!"

## Collapse the official judgments by resolving inter-annotator agreement
## (only need to do this once)

python collapse-truth-judgment.py


## ====== MEASURE SLICE PERFORMANCE =====

## Measure slice performance for all runs and all of (week, day, all)
## Notice:the call to measure-slice takes a long time for big run files.
## you may want to consider running it on grid engine or hadoop.


for f in `ls $datadir/*gz`; do
    # $f is the name of the run-file

    for intervalType in day week all; do
        python measure-slice.py -f $f --intervalType $intervalType --judgmentLevel $judgmentLevel
        # you may also create output for trec_eval using the following line
        # python measure-slice.py -f $f --intervalType $intervalType --judgmentLevel $judgmentLevel --trec_eval
    done;
done;

## this stage generates files "$f.eval-day.tsv", "$f.eval-week.tsv"  ,"$f.eval-all.tsv"
## only those files (and the collapsed truth file) are required for the following scripts
## they can be executed in any order - there is no further dependency



## ===== UNIFORM AGGREGATION ====

## uniform weighting over time (day,week,all in one plot per measure)
python $PYTHONPATH/perf-over-time.py -d $datadir/ --judgmentLevel $judgmentLevel --subplot

## uniform weighting over time, one plot per team, intervalType, and metric
python $PYTHONPATH/perf-over-time.py -d $datadir/ --judgmentLevel $judgmentLevel --plot-teams

## compute overall performance with uniform aggregation, one table per metric
## also outputs tables on performance per entity
python $PYTHONPATH/total-stats.py -d $datadir/ --judgmentLevel $judgmentLevel

## ===== BURST-AWARE AGGREGATION =====

## compute overall performance with burst-aware weighting, one table per metric
## also outputs tables on performance per entity
python $PYTHONPATH/total-stats.py -d $datadir/ --judgmentLevel $judgmentLevel --weighted


## for reference, plot burst-weights over time
python $PYTHONPATH/weights-over-time.py -d $datadir/ --judgmentLevel $judgmentLevel


## comparison for two teams on a single entity, side-by-side with and without burst-aware weighting
## you can also omit the --entity option to produce comparisons for all entities.
python $PYTHONPATH/sidebyside-singleentity.py -d  $datadir/ --judgmentLevel $judgmentLevel --team1 udel_fang --run1 UDInfoKBA_WIKI1 --team2 uiucGSLIS --run2 gslis_adaptive --entity Mario_Garnero

## this computes side-by-side plots for all runs in the directory
## evaluates entities Mario_Garnero and James_McCarthy
allteamruns=`ls input*all.tsv | sed -e 's/input\.//g' -e 's/.gz-eval-all.tsv//g'`
for teamrun1 in $allteamruns; do
    for teamrun2 in $allteamruns; do
        if [[ $teamrun1 < $teamrun2 ]]; then
            run1=`echo $teamrun1|  sed -e 's/.*-//g'`
            team1=`echo $teamrun1| sed -e 's/-.*$//g'`
            run2=`echo $teamrun2|  sed -e 's/.*-//g'`
            team2=`echo $teamrun2| sed -e 's/-.*$//g'`

            echo "$team1 $run1 vs $team2 $run2"
            python $PYTHONPATH/sidebyside-singleentity.py -d  $datadir/ --judgmentLevel $judgmentLevel --team1 $team1 --run1 $run1 --team2 $team2 --run2 $run2 --entity Mario_Garnero
            python $PYTHONPATH/sidebyside-singleentity.py -d  $datadir/ --judgmentLevel $judgmentLevel --team1 $team1 --run1 $run1 --team2 $team2 --run2 $run2 --entity James_McCartney
        fi
    done
done