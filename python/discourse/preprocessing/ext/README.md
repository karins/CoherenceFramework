1. download browncoherence

2. compile it with `make`

2. copy `ExtractGrid.cc` into `src`

3. edit the `Makefile`

    everything: TestSent TestGrid ExtractGrid Train TrainOnThreads Insert TrainMixture TrainDiscMixture TrainWSJDiscMixture Featurize TrainFromFeatures Average DiscriminateRand Discriminate DiscriminateDiscRand RankDisentangle TestDisentangle ChatStyleTranscript Print

4. compile

    make ExtractGrid
