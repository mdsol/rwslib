rwscmd
======

rwscmd is a command-line tool providing convenient access to Rave WebServices, via rwslib.


Installation
------------

python setup.py install


Usage
-----

```
Usage: rwscmd [OPTIONS] URL COMMAND [ARGS]...

Options:
  -u, --username TEXT           Rave login 
  -p, --password TEXT           Rave password
  --virtual_dir TEXT            RWS virtual directory, defaults to
                                RaveWebServices                              
  --raw / --list                Display raw xml response from RWS or human-
                                readable list, defaults to list                              
  -v, --verbose / -s, --silent 
  -o, --output FILENAME         Write output to file 
  --help                        Show this message and exit.

Commands:
  autofill  Request enterable data for a subject,...
  data      List EDC data for [STUDY] [ENV] [SUBJECT]
  direct    Make direct call to RWS, bypassing rwslib
  metadata  List metadata for [PROJECT] [VERSION]
  post      Post ODM clinical data
  version   Display RWS version
``` 
  
Examples
--------

    $ rwscmd innovate version
        Username: anewbigging
        Password:
        1.15.0
        
    $ export RWSCMD_USERNAME=anewbigging
    $ export RWSCMD_PASSWORD=*********
    
    $ rwscmd innovate version
        1.15.0
    
    $ rwscmd innovate data
        ATN01(Prod)
        Medidata(Prod)
        Mediflex(Prod)
        Mediflex(Dev)
        
    $ rwscmd innovate data Mediflex Prod
        0004-bbc-003
        001 aaa
        001 ADS


