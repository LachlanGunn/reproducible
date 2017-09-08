Reproducible scientific computing tools for Python
==================================================

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

Problem Statement
-----------------

We would like to write a paper whose results depends upon
some computation.  This paper should be *reproducible*, so that
others can see how we achieved our results.


### Literate Programming

We can use literate programming tools like
[_PythonTex_](https://github.com/gpoore/pythontex) to include Python
code in our paper; this makes clear exactly what code was executed
to produce our figures and numerical values.  This lets us include
code like

```LaTeX
$\sin\left(\frac{\pi}{6}\right) = \py{np.sin(np.pi/6)}$
```
But what if our computations are not so easy?
```LaTeX
$f(x) = \py{some_slow_function('/path/to/a/data/file.csv')}$
```
This will take a long time to run, and may even force us to pre-compute
the values and load them from a file; if we have to recompute
everything after every change to our computation, then changes
become expensive and so deeper changes to the paper become impractical.

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
