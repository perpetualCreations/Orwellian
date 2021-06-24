Python 3 Flask QR-Code Timesheet Tracker
========================================
:Latest Version - |version|:

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Indices and tables
------------------
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* `Back to Projects </index.html##projects>`_

Install
-------
ORWELLIAN is distributed as a source archive, and is not locked to Debian and Debian-based operating systems.
Manually download and extract project contents.

.. parsed-literal::

   wget https://github.com/perpetualCreations/arbiter/releases/download/orwellian-|release|.zip
   unzip orwellian-|release|.zip

.. |release| replace:: |version|

Outline
-------
ORWELLIAN is a Flask application for timesheet tracking. Personnel are assigned QR codes generated from their inputed names.

The backend server (of which this documentation describes the installation process for) must be installed on any Linux machine.

To clock in or out, personnel must present their QR code to a client machine with a browser instance open to the ORWELLIAN web interface.
The client machine transmits the image to the backend server, which processes the personnel. Unless a match is found, no log is made.

The backend processing system is smart enough to identify whether an entry notates a login/logout event, by referring to the last event made by the user.
When a user has no history, their first entry will always be a login event.

ORWELLIAN stores user and log information in a single SQLite database, hosted locally.
Other applications may interface with this database file.

Configuration
-------------
Under the main application directory is the main.cfg configuration file.

Inline comments document each field. Please refer to them for advisories and preliminary information.

Run
---
Use the included shell script to start the server. Press CTRL+C to stop the server.
