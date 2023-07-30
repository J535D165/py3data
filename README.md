# py3data

[![PyPI](https://img.shields.io/pypi/v/py3data)](https://pypi.org/project/py3data/) [![DOI](https://zenodo.org/badge/557541347.svg)](https://zenodo.org/badge/latestdoi/557541347)

py3data is a Python library for [re3data](https://re3data.org/) registry.
Re3data is a global registry of research data repositories that covers
research data repositories from different academic disciplines. It includes
repositories that enable permanent storage of and access to data sets to
researchers, funding bodies, publishers, and scholarly institutions. Re3data
offers an open and free [REST API](https://www.re3data.org/api/doc). py3data
is a lightweight and thin Python interface to the beta version of this API.

The following features of re3data are currently supported by py3data:

- [x] Get single repositories
- [x] Filter and query repositories


## Key features

- **Pipe operations** - py3data can handle multiple operations in a sequence. This allows the developer to write understandable queries. For examples, see [code snippets](#code-snippets).
- **JSON support** - Re3data [doesn't offer a JSON implementation of the REST API](https://www.re3data.org/api/doc). py3data parses the XML REST API and offers it in Python dict-like objects.
- **Schema fixes** - The re3data Schema is slightly hard to parse in Python directly. Re3data makes is very easy to parse the API and solves the issues.
- **Permissive license** - Re3data data is CC0 licensed :raised_hands:. py3data is published under the MIT license.

## Installation

py3data requires Python 3.8 or later.

```sh
pip install py3data
```

## Getting started

```python
from py3data import Repositories
```

### Get single repository

Get a single Repository

```python
Repositories()["r3d100011986"]
```

The result is a `Repository` object, which is very similar to a dictionary. Find the available fields with `.keys()`.

For example, get the open access status:

```python
Repositories()["r3d100011986"]["subjects"]
```

```python
[{'subjectScheme': 'DFG', 'subjectName': '2 Life Sciences'},
 {'subjectScheme': 'DFG', 'subjectName': '202 Plant Sciences'},
 {'subjectScheme': 'DFG',
  'subjectName': '20202 Plant Ecology and Ecosystem Analysis'},
 {'subjectScheme': 'DFG',
  'subjectName': '20203 Inter-organismic Interactions of Plants'},
 {'subjectScheme': 'DFG', 'subjectName': '203 Zoology'},
 {'subjectScheme': 'DFG',
  'subjectName': '20303 Animal Ecology, Biodiversity and Ecosystem Research'},
 {'subjectScheme': 'DFG', 'subjectName': '21 Biology'},
 {'subjectScheme': 'DFG', 'subjectName': '3 Natural Sciences'},
 {'subjectScheme': 'DFG',
  'subjectName': '313 Atmospheric Science and Oceanography'},
 {'subjectScheme': 'DFG', 'subjectName': '318 Water Research'},
 {'subjectScheme': 'DFG',
  'subjectName': '31801 Hydrogeology, Hydrology, Limnology, Urban Water Management, Water Chemistry, Integrated Water Resources Management'},
 {'subjectScheme': 'DFG',
  'subjectName': '34 Geosciences (including Geography)'}]
```

### Get lists of repositories

It is possible to get lists of results from re3data. However keep in mind that
lists consist of `Repository` objects with very few metadata (`id`, `name`,
`doi`, `link`).

Get all repositories:

```python
Repositories().get()
```

For lists of repositories, you can also `count` the number of records found
instead of returning the results. This also works for search queries and
filters.

```python
Repositories().count()
# 3137
```

#### Filter and query records

Re3data makes use of filters and queries. Filters can be used to slice the
structured metadata of re3data and queries can be used to search for specific
terms or phrases. Both filters and queries can be used in one request.

An overview of all the filters can be found under ["Beta" in the REST API
documentation](https://www.re3data.org/api/doc). It can be hard to find the
correct values sometimes. In that case, look for values in other single
Repository requests, the [Metadata Schema](https://www.re3data.org/schema), or the website.

```python
(
  Repositories()
    .filter(countries="CAN")
    .filter(subjects=["2 Life Sciences", "3 Natural Sciences"])
    .filter(pidSystems="DOI")
    .query("University")
    .get()
)
```

which is identical to:

```python
(
  Repositories()
    .filter(
      countries="CAN",
      subjects=["2 Life Sciences", "3 Natural Sciences"],
      pidSystems="DOI",
    )
    .query("University")
    .get()
)
```

## Code snippets

A list of examples for the re3data.org dataset.

### Get repositories running Dataverse software

```python
(
  Repositories()
    .filter(software="Dataverse")
    .get()
)
```

### Get repositories with word "climate" and DOI identifiers

```python
(
  Repositories()
    .filter(pidSystems="DOI")
    .query("climate")
    .get()
)
```

## License

[MIT](/LICENSE)

## Contact

> This library is a community contribution. The authors of this Python library aren't affliated to re3data.

Feel free to reach out with questions, remarks, and suggestions. The
[issue tracker](/issues) is a good starting point. You can also email me at
[jonathandebruinos@gmail.com](mailto:jonathandebruinos@gmail.com).
