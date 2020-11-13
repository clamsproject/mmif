.. _instroduction:

Getting Started
===============


Overview 
---------

MultiMedia Interchange Format (MMIF) is a JSON(-LD)-based data format designed for transparency and interoperability for customized computational analysis application workflows.
This documentation focuses on Python implementation of the MMIF. To learn more about the data format specification, please visit the `MMIF wbesite <https://mmif.clams.ai>`_.
``mmif-python`` is a public, open source implementation of the MMIF data format. ``mmif-python`` supports de-/serialization of MMIF objects, as well as many navigation and manipulation helpers for MMIF objects. 

Prerequisites
-------------

* `Python <https://www.python.org>`_: ``mmif-python`` requires Python 3.6 or newer. We have no plan to support `Python 2.7 <https://pythonclock.org/>`_. 

Installation 
---------------

Package ``mmif-python`` is distributed via the official PyPI. Users are supposed to pip-install to get latest release. 

.. code-block:: bash

  pip install mmif-python

This will install a package `mmif` to local python.
The MMIF format and specification is evolving over time, and ``mmif-python`` package will be updated along with the changes in MMIF format. Note that MMIF format is not always backward-compatible. To find out more about relations between MMIF versions and ``mmif-python`` versions, and which supports which, please take time to read our decision on the subject `here <https://mmif.clams.ai/versioning/>`_. 

MMIF Serialization
---------------------------

:class:`mmif.serialize.mmif.Mmif` represents the top-level MMIF object. For subcomponents of the MMIF (view objects, annotation objects, metadata for each object) are all subclass of :class:`mmif.serialize.model.MmifObject`, including the :class:`mmif.serialize.mmif.Mmif`. To start with an existing MMIF :class:`str`, simple initiate a new ``Mmif`` object with the file. 

.. code-block:: python 

  import mmif
  from mmif import Mmif

  mmif_str = """{
  "metadata": {
    "mmif": "http://mmif.clams.ai/0.2.0"
  },
  "documents": [
    {
      "@type": "http://mmif.clams.ai/0.2.0/vocabulary/VideoDocument",
      "properties": {
        "id": "m1",
        "mime": "video/mp4",
        "location": "/var/archive/video-0012.mp4"
      }
    },
    {
      "@type": "http://mmif.clams.ai/0.2.0/vocabulary/TextDocument",
      "properties": {
        "id": "m2",
        "mime": "text/plain",
        "location": "/var/archive/video-0012-transcript.txt"
      }
    }
  ],
  "views": []}"""
  mmif_obj = Mmif(mmif_str)


Few notes; 

#. MMIF does not carry the primary source files in it. 
#. MMIF encode the specification version at the top. As not all MMIF versions are backward-compatible, a version ``mmif-python`` implementation of the MMIF might not be able to load an unsupported version of MMIF string. 

When serializing back to :class:`str`, call ``.serialize()`` (:meth:`mmif.serialize.model.MmifObject.serialize`) on the object. 

To get subcomponents, you can use various getters implemented in subclasses. For more details, the API documentation (:ref:`apidoc`) will help. 

