# Requirements

* numpy
* scipy
* nltk

# Optional

* install `progressbar` from Google code for improved feedback

```bash
wget https://python-progressbar.googlecode.com/files/progressbar-2.3.tar.gz
tar -xzvf progressbar-2.3.tar.gz
cd progressbar-2.3
sudo python setup.py install --record files.txt
```

* I often use tabulate to dump markdown tables with some helpful information, you can easily install it with `pip`

    sudo pip install tabulate


# Install

I recommend using `virtualenv`


1. Create an environment

        virtualenv ~/worspace/envs/discourse

2. Activate the environment

        source ~/workspace/envs/discourse/bin/activate

3. Install dependencies

        pip install numpy
        pip install scipy
        pip install nltk

4. Install extras, such as progressbar

5. Git clone the code, navigate to the python directory and run

        python setup.py install


## Check

Install `yolk`

    pip install yolk

This is what I get running `yolk -l`

    Python          - 2.7.3        - active development (/usr/lib/python2.7/lib-dynload)
    argparse        - 1.2.1        - active development (/usr/lib/python2.7)
    discourse       - 0.0.0        - active 
    nltk            - 3.0.0        - active
    numpy           - 1.9.1        - active 
    pip 1.5.4 has no metadata
    progressbar     - 2.3          - active 
    scipy           - 0.14.0       - active 
    setuptools 2.2 has no metadata
    tabulate        - 0.7.3        - active 
    wsgiref         - 0.1.2        - active development (/usr/lib/python2.7)
    yolk            - 0.4.3        - active 

# Usage

The module `discotools` can be used as an interface to tools in this package.
You can obtain a list of subcommands by checking the help message:

    python -m discotools -h

For example, you can find `preprocessing` tools using:

    python -m discotools preprocessing -h

One such tool can be used to fix the SGML markup of WMT files:

    python -m discotools preprocessing fixwmt -h


## Syntax-based coherence

### IBM model 1


```bash

# get a help message
python -m discourse.syntax_based.ibm1 -h

# running with Potet data
python -m discourse.syntax_based.ibm1 -m 30 -b < discourse/syntax_based/data/potet/patterns.doctext > discourse/syntax_based/data/potet/patterns.ibm1

```

