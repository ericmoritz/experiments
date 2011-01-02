#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This code is based on mongokit.helpers, therefore, the following
# License information is requried to be included. The only modification
# I made was strip the mongokit dependancies. 

# Copyright (c) 2009-2010, Nicolas Clairon
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the University of California, Berkeley nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import datetime
import logging
log = logging.getLogger(__name__)

def totimestamp(value):
    """
    convert a datetime into a float since epoch
    """
    import calendar
    return int(calendar.timegm(value.timetuple()) * 1000 + value.microsecond / 1000)

def fromtimestamp(epoch_date):
    """
    convert a float since epoch to a datetime object
    """
    seconds = float(epoch_date) / 1000.0
    return datetime.datetime.utcfromtimestamp(seconds)

from copy import deepcopy


class DotedDict(dict):
    """
    Dot notation dictionnary access
    """
    def __init__(self, doc=None, warning=False):
        self._dot_notation_warning = warning
        if doc is None: doc = {}
        super(DotedDict, self).__init__(doc)
        self.__dotify_dict(self)
    def __dotify_dict(self, doc):
        for k,v in doc.iteritems():
            if isinstance(v, dict):
                doc[k] = DotedDict(v)
                self.__dotify_dict(v)
    def __setattr__(self, key, value):
        if key in self:
            self[key] = value
        else:
           if self._dot_notation_warning and not key.startswith('_') and\
             key not in ['db', 'collection', 'versioning_collection', 'connection', 'fs']:
               log.warning("dot notation: %s was not found in structure. Add it as attribute instead" % key)
           dict.__setattr__(self, key, value) 
    def __getattr__(self, key):
        if key in self:
            return self[key]
    def __deepcopy__(self, memo={}):
        obj = dict(self)
        return deepcopy(obj, memo)

class EvalException(Exception):pass

class DotExpandedDict(dict): 
    """ 
    A special dictionary constructor that takes a dictionary in which the keys 
    may contain dots to specify inner dictionaries. It's confusing, but this 
    example should make sense. 

    >>> d = DotExpandedDict({'person.1.firstname': ['Simon'], \ 
          'person.1.lastname': ['Willison'], \ 
          'person.2.firstname': ['Adrian'], \ 
          'person.2.lastname': ['Holovaty']}) 
    >>> d 
    {'person': {'1': {'lastname': ['Willison'], 'firstname': ['Simon']}, '2': {'lastname': ['Holovaty'], 'firstname': ['Adrian']}}} 
    >>> d['person'] 
    {'1': {'lastname': ['Willison'], 'firstname': ['Simon']}, '2': {'lastname': ['Holovaty'], 'firstname': ['Adrian']}} 
    >>> d['person']['1'] 
    {'lastname': ['Willison'], 'firstname': ['Simon']} 

    # Gotcha: Results are unpredictable if the dots are "uneven": 
    >>> DotExpandedDict({'c.1': 2, 'c.2': 3, 'c': 1}) 
    {'c': 1} 
    """ 
    # code taken from Django source code http://code.djangoproject.com/
    def __init__(self, key_to_list_mapping): 
        for k, v in key_to_list_mapping.items():
            parent = None
            current = self
            bits = k.split('.')
            for bit in bits[:-1]:
                current = current.setdefault(bit, {})


            # Now assign value to current position
            try:
                current[bits[-1]] = v
            except TypeError: # Special-case if current isn't a dict.
                current = {bits[-1]: v}

def flatten_lists(dct):
    for name, value in dct.iteritems():
        # If the value is an iterable,
        # yield each item with the 
        # param's name
        if hasattr(value, "__iter__"):
            for item in value:
                yield (name, item)
        # If the value is not iterable,
        # just yield the name and value
        else:
            yield (name, value)
