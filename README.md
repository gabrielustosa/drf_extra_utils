# Django Rest Extra Utils

A collection of useful tools, serializers and views to help and DRY your code.

Full documentation: 

## Overview

This is a useful tool for developers working with Django Rest Framework, as it provides a range of useful features that 
can help streamline development and improve the functionality of your API.

## Requirements

* Python (3.8, 3.9, 3.10, 3.11)
* Django (3.0, 3.1, 3.2, 3.3, 4.0, 4.1, 4.2)
* Django Rest Framework (3.10, 3.11, 3.12, 3.13, 3.14, 3.15)

## Installation

```
$ pip install drf-extra-utils
```

Add `drf_extra_utils` to your INSTALLED_APPS setting:

```
INSTALLED_APPS = (
    ...
    'drf_extra_utils'
)
```

## Testing

Install testing requirements

```
$ pip install -r requirements-test.txt
```

Run with pytest

```
$ pytest
```

Run with tox

```
$ pip install tox
$ tox
```