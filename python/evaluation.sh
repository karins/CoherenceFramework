# You need to configure this file
# the paths I show here are relative to my own workspace
# take it as an illustration of how you should do it

# which test set are you using?
testset=newstest2014

# which language pairs
pairs=( de-en )

# which version of each model are you using?
# for each $path you give me, I expect to find '$path/eval/$testset.$pair/rankings'
grid=pilot/grid/giga.d2.s2
graph=extra/graph
alouis=pilot/alouis/giga.d2.c0.001.u.i
ibm1=pilot/ibm1/giga.d2.m5.u

# how many rounds of bootstrap resampling
rounds=100

# where do you want your results?
experiment=sigtest/pilot

# don't change anything from here, unless you know what you are doing ;)
mkdir -p $experiment
for pair in ${pairs[@]};
do
    echo $pair
    mkdir -p $experiment/$pair
    
    python -m discotools scripts sigtest \
        --rounds $rounds \
        --tablefmt latex \
        --refsys $testset.$pair.ref \
        --ranker EntityGrid $grid/eval/$testset.$pair/rankings \
        --ranker GraphSimilarity $graph/eval/$testset.$pair/rankings \
        --ranker ALouis $alouis/eval/$testset.$pair/rankings \
        --ranker IBM1 $ibm1/eval/$testset.$pair/rankings \
        $experiment/$pair/$testset.$pair &
done
wait

echo "done"
