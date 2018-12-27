.. highlight:: shell

.. _Contributing:

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

First, please read the pylighthouse :ref:`Code of Conduct`. This project
will not take any contribution coming from those who do not abide by
the code of conduct. This means that while a person is currently under
disciplinary action via avenues set forth in that document, this project will
ignore and not incorporate any contributions they might give at that time,
including pull requests, bug reports, feature requests, or any other
contribution. We here at pylighthouse are committed to caring about
the well-being of every one in our community, and we are prepared to act to
protect that well-being if needed.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/djhaskin987/pylighthouse/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

pylighthouse could always use more documentation, whether as part of the
official pylighthouse docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/djhaskin987/pylighthouse/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `pylighthouse` for local development.

1. Fork the `pylighthouse` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/pylighthouse.git

3. Install your local copy into a virtualenv. This is how you set up your fork
   for local development::

    $ cd pylighthouse/
    $ virtualenv ve
    $ . ve/bin/activate
    $ pip install -r requirements_dev.txt

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the
   tests, including testing other Python versions with tox::

    $ . ve/bin/activate
    $ flake8 pylighthouse tests
    $ python setup.py test or py.test
    $ tox

   flake8 and tox should be installed if you are in the pipenv shell. If not,
   just pip install them into your virtualenv like this::

    $ pip install --user flake8
    $ pip install --user tox

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

When you go to make the PR, please use the following checklist to test
whether or not it is likely to be accepted:

2. **Do you have tests in your PR, and do they pass?** Tests are in
   two places in pylighthouse: the ``tests/`` directory, where more
   or less normal unit tests reside. You must have at least a few
   simple unit tests as a "spot-check" of your feature if the PR is to be
   merged. The tests need not be elaborate; simple tests are better than no
   tests.
3. **Is your PR backwards compatible?** The biggest feature pylighthouse
   provides is backwards compatibility. If pylighthouse breaks a build, it
   is a bug. A PR is herein defined to be "backwards incompatible"
   if 1) it significantly changes the content of any previously merged unit or
   script test and 2) if it breaks any of them.
4. **Did you add documentation around the feature in your PR?**
   Generally this means adding something to the `usage <usage>`
   document.
5. **Did you add an entry to the Changelog?** This project keeps a
   curated :ref:`changelog <pylighthouse Changelog>`.

There are some exceptions to the above rules. If your patch is less than
two lines' difference from the previous version, your PR may be a "typo" PR,
which may qualify to get around some of the above rules. Just ask the team
on your GitHub issue.

Tips
----

To run a subset of tests::

    $ py.test tests.test_pylighthouse

Deploying
---------

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in HISTORY.rst).
Then run this::

    $ bumpversion patch # possible: major / minor / patch
    $ git push
    $ git push --tags

Travis will then deploy to PyPI if tests pass.
