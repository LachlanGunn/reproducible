Reproducible scientific computing tools for Python
==================================================

![Public Domain](doc/images/badge-licence-publicdomain.svg)
[![Build Status](https://travis-ci.org/LachlanGunn/reproducible.svg?branch=master)](https://travis-ci.org/LachlanGunn/reproducible)
[![Coverage Status](https://coveralls.io/repos/github/LachlanGunn/reproducible/badge.svg)](https://coveralls.io/github/LachlanGunn/reproducible)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/29dfd6e38473454cb2e29b388bb8b28c)](https://www.codacy.com/app/LachlanGunn/reproducible?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=LachlanGunn/reproducible&amp;utm_campaign=Badge_Grade)

___This software is highly experimental.  Expect it to break at every
    opportunity.___

The **`reproducible`** module for Python provides tools to aid
in performing reproducible scientific computations.

By supporting a more functional style of programming, we allow
parameters to be described at the top level of a computation.
This will allow us to make full use of the literate programming
capabilities provided by
[_PythonTex_](https://github.com/gpoore/pythontex)
without either a long wait every time we compile or external result
caches that must be kept in sync.

Synopsis
--------

```python
>>> def slow_add(a, b):
...     time.sleep(3)
...     return a+b

>>> %time slow_add(1, 2)
Wall time: 3 s

>>> %time slow_add(1, 2)
Wall time: 3 s

>>> @reproducible.operation
... def less_slow_add(a, b):
...     time.sleep(3)
...     return a+b

>>> %time less_slow_add(1, 2)
Wall time: 3 s

>>> %time less_slow_add(1, 2)
Wall time: 502 µs

>>> %time less_slow_add(2, 2)
Wall time: 3 s
```

Problem statement
-----------------

We would like to write a paper whose results depends upon
some computation.  This paper should be *reproducible*, so that
others can see how we achieved our results.

### A note on state

Persistent state makes reproducibility more difficult, as a user
attempting to reproduce the computation must also reproduce the
state of environment.  Conversely, if our computation depends only
on a well-defined set of input data and does not have any side-effects
that will affect the results of future runs, other scientists can
reproduce the computation by simply running the same code with the
same inputs.

This encourages the use of _functional-style_ code, even though we
may not be using a more 'pure' functional language such as ML or
Haskell.  By specifying parameters at the point of use&mdash;e.g., when
we insert a figure into a document that uses the results of the
computation&mdash;we ensure that the document remains synchronised
with the computations actually performed.

### Literate programming

We can use literate programming tools like
[_PythonTeX_](https://github.com/gpoore/pythontex) to include Python
code in our paper; this makes clear exactly what code was executed
to produce our figures and numerical values, keeping the document
in sync with the computational results as discussed above.
_PythonTeX_ lets us include code like

```LaTeX
$\sin\left(\frac{\pi}{6}\right) = \py{np.sin(np.pi/6)}$
```
But what if our computations are not so easy?
```LaTeX
$f(x) = \py{some_slow_function('/path/to/a/data/file.csv')}$
```
This will take a long time to run, and may even force us to pre-compute
the values and load them from a file; destroying the reproducibility
advantages that we gain from a functional side-effect-free style
of programming.  Caching just the output values makes document changes
inexpensive, and this is indeed done by _PythonTeX_, but we still must
perform a potentially large amount of computation each time we change
our figures.


Caching to the rescue
---------------------

We can cache the resulting figures so that changes to the document do
not require regeneration of computational results; though this allows
fast document compilation, even the smallest change to the figures
forces regeneration.  This suggests caching at a more fine-grained
level, for example by writing data-analysis code that yields
CSV or HDF5 files, which can then be read and plotted by a second
script.

Depending on the nature of the computation, even-finer-grained
caching might be useful; the result is a potentially-quite-complex
dependency graph that cannot be executed by hand in a reliable
manner.

All of these tools and interfaces make fine-grained caching difficult,
and potentially not worthwhile: given the effort required to manage
all of the intermediate results and build system scripts, it may be
better to simply accept the excess computation.

The `reproducible.operation` decorator is designed to provide
transparent caching of intermediate results, allowing us to write
functional-style code without side effects, with all parameters
specified at the point-of-use in the document, without
unnecessary computation.

Licence
-------

`reproducible` is public-domain software, with a Creative Commons CC0
dedication.  See [LICENCE.md](LICENCE.md) for details.

The Author
----------

**Lachlan Gunn**

<table>
<tr><td>Email</td><td>lachlan@twopif.net</td></tr>
<tr>
    <td>PGP</td>
    <td><code>F3E3 8891 8560 5B82 933D  6180 D288 91D2 136B 33B0</code></td>
</tr>
<tr>
    <td>Github</td>
    <td><a href="https://github.com/lachlangunn">LachlanGunn</a></td>
</tr>
<tr>
    <td>ORCID</td>
    <td><a href="https://orcid.org/0000-0003-1767-7897">0000-0003-1767-7897</a></td>
</tr>
</table>
