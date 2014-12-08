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

Several modules expose a command line interface.

To learn more about training syntax-based models based on IBM model 1, you can run:

    python -m discourse.syntax_based.ibm1 -h

If you are not sure which module implements the functionality you are looking for, you can use the module `discotools` which is an interface to every tool in this package.
You can obtain a list of subcommands by checking the help message:

    python -m discotools -h

IBM1 example using discotools:

    python -m discotools syntax-based ibm1 -h

You can also find other types of tools, such as `preprocessing` tools:

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

# discotools

If you develop a new module and want it to be listed by `discotools` do the following:


```python
from discourse import command

# write a main function which receives parsed arguments (an instance of argparse.Namespace)
def main(args):
    """Example main, simply writes the input to the output"""
    for line in args.input:
        print >> args.output, line.strip()
    
# write a function to configure an argparse.ArgumentParser object and declare it as a command
@command('mymodule', 'mygroup')
def argparser(parser=None, func=main):
    """
    Configures and returns a parser for the tool 'mymodule' which is part of the groups of tools 'mygroup'.

    Arguments
    ---------
    parser: a clean argparse parser to be configured (the program name shouldn't be changed),
        or None in which case a parser will be created
    main: the main function to be called when the program is invoked

    Returns
    -------
    a configured parser
    """
    if parser is None:
        parser = argparse.ArgumentParser(prog='mymodule')
    
    parser.description = "Example"

    parser.add_argument('input', nargs='?', 
            type=argparse.FileType('r'), default=sys.stdin,
            help='Input stuff')
    parser.add_argument('output', nargs='?', 
            type=argparse.FileType('w'), default=sys.stdout,
            help='output stuff')
    
    if func is not None:
        parser.set_defaults(func=func)

    # note that we do not parse the command line arguments,
    # we just configure the parser
    return parser

if __name__ == '__main__':
    # having this bit will make your module expose an interface of its own (which is a good idea)
    # however, because we declared a command, we can also have this interface as part of discotools
    main(argparser().parse_args())
```

To complete, change `discotools` to import your module. Then you will be able to run

    python -m discotools mygroup mymodule -h

