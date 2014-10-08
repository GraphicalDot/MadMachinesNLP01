PyPi - Registration 
===================

Procedure: 
 - read http://wiki.python.org/moin/Distutils/Tutorial
 - write this setup.py
 - create new account at http://pypi.python.org
 - reply on confirmation mail
 - python setup.py register
 - http://pypi.python.org/pypi/text-sentence/
 - python setup.py sdist
 - python setup.py sdist upload
 - check there: http://pypi.python.org/pypi/text-sentence/0.10


How to post new release:
 - increase version nr. 
 - python setup.py sdist upload 
    - creates source distribution in dist directory -
      tarball and uploads it
 
TODO: 
    ++ install test_sentence.txt too
    ++ run tests and fix problems
    ++ ain't, oš' 
        http://stackoverflow.com/questions/2039140/python-re-how-do-i-match-an-alpha-character
    - samples
    - html preprocessor
    - move samples from html preprocessor
    - refactor??
    - where is documentation?
        - sphinx and rest
        - master thesis final ... reference on Croatian
        - documentation upload to pypi - make it with sphinx, zip and upload

    - write todo-s from dnevnik.txt
    - isn't it? -> isn + ' + t

    - enable running tests like this::

        python -m"text_sentence"


