# Introduction

Welcome to Django Rest Extra Utils, a library designed to make your life easier when working with Django REST framework.

A collection of useful tools, serializers and views to help and DRY your code.

## Overview

This a library that provides a set of tools for use with Django Rest Framework. Some key features of this library
include:

- [Annotations](/annotation/): Allows you to annotate your models with additional information that can be used in your 
  serializers and views.
- Related Object: Allows you to easily retrieve your model related objects in your responses, with support for
  filtering, permissions, and pagination.
- Serializer: Provide a set of mixins that you can use in your serializers and views to add common functionality, such
  as DynamicFields, PermissionForField, CreateOrUpdateOnly
- Models: Offers some useful models like TimeStampedModel to handling creation and modification and CreatorBase to
  setting the creator of an object model.
- Middleware: Provide a middleware to allow you to easily access the current request and current user without explicitly
  passing it as an argument.

Overall, this is a useful tool for developers working with Django Rest Framework, as it provides a range of useful
features that can help streamline development and improve the functionality of your API.


## Requirements

- Python (3.8, 3.9, 3.10, 3.11)
- Django (3.0, 3.1, 3.2, 3.3, 4.0, 4.1, 4.2)
- Django Rest Framework (3.10, 3.11, 3.12, 3.13, 3.14, 3.15)