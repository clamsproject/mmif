.. _consumer-tutorial:

MMIF consumer
=================================

A MMIF consumer discuss in this document is a web application that is designed for CLAMS appliance integration. The CLAMS appliance provides a turn-key installation of CLAMS-Galaxy instance. Please refer to the `appliance documentation <https://appliance.clams.ai/>`_ to learn more about the appliance. 

MMIF consumer can be implemented with any language. However a MMIF consumer must meet these requirements to be compatible with the CLAMS appliance. 

#. The code must be hosted on a public git repository (e.g. Github, Gitlab, ...)
#. Must listen to ``5000`` port.
#. Must expose ``/display`` route .
#. ``/display`` router should response to ``GET`` requests.
#. In the ``GET`` request, a public URL of the input MMIF file is passed via ``file`` URL parameter.
#. On the codebase root, there must be a ``Dockerfile`` that can build a `docker <https://www.docker.com/>`_ image that runs the web app. 

We provide an example consumer at https://github.com/clamsproject/mmif-visualizer. 
