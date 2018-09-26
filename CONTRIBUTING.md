Contributing to rwslib
======================

Thank you for considering contributing to rwslib.

Developer Setup
---------------
1. Clone the repository
   ```
   git clone https://github.com/mdsol/rwslib
   ```
2. Create a Virtual Env for the Local instance
    ```bash
    $ python -m venv venv
    $ source venv/bin/activate
    ```
3. Install the development dependencies
    ```bash
    $ pip install -r requirements-dev.txt
    ```
4. Enjoy !!!

Pull Requests
-------------

The best way to contribute to rwslib is to fork the develop branch of the rwslib repo in github and then raise a pull
request back to the develop branch. Our workflow is:

1. Branch from and merge to develop
2. When ready for new pypi release change the version number and merge develop -> master

We do this because docs are auto-created from a merge to master but also because it allows us to control the rwslib
version in pypi, the python packaging index.

Tests
-----

We use unittest for tests in rwslib, aiming for a high degree of coverage. Any code contributions should have associated
tests. 

We test python version compatibility with [tox](https://pypi.python.org/pypi/tox) against py27, py34, py35

Documentation
-------------

We document with Sphinx. Updates/additions to documentation are welcome. Please consider adding docs for any new 
request types you wish to add to the core of the library.

Merges to master have a hook that publishes updated docs to readthedocs. See http://rwslib.readthedocs.org/en/latest/

Acknowledgement
---------------

Contributions to rwslib are recognized in the AUTHORS.rst file. We welcome contributions large and small!