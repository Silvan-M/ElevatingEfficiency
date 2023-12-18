.. Elevating Efficiency documentation master file, created by
   sphinx-quickstart on Sat Dec 16 14:51:22 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: ../img/Elevating-Efficiency-Logo.svg
   :alt: Elevating Efficiency Logo

Elevating Efficiency
====================

Our project is about the efficiency of elevators. We want to find out how the efficiency of elevators can be improved by using different policies. We will simulate the movement of elevators and passengers in a building and compare the results of different policies.

This project was created as part of the course "Complex Social Systems: Modelling Agents, Learning and Games" at ETH Zurich.

To download our project, please visit our `GitHub repository <https://github.com/Silvan-M/ElevatingEfficiency>`_.

.. image:: ../img/Elevator-Showcase.gif
   :alt: Elevator Showcase

Installation
------------------------------------------------

One can install the package by running the following command in the terminal (depending on the python installation, you might need to use pip3 instead of pip):

.. code-block:: bash

   pip install -r requirements.txt

Usage
------------------------------------------------

To run the simulation first set the parameters in the main.py file. 
Important parameters are:
- ``distribution``: The distribution of the passengers arrival times. Here you can choose one the scenarios Shopping Mall, Residential Building or Rooftop Bar.
- ``policy``: The policy that is used to control the elevators. Here you can choose from one of the 4 letter policies e.g. ``FCFSPolicy``.
- ``policy_arguments``: The arguments that are passed to the policy, only use for ``PWDPPolicy``, leave blank for others.
- ``hours, minutes, seconds``: The duration of the simulation.

Then run the following command in the terminal from the project directory (depending on the python installation, you might need to use python3 instead of python):

.. code-block:: bash

   python main.py

Plotting
------------------------------------------------

To plot simulations, call the corresponding functions in the ``simulation_plotter.py`` file.

Then run the following command in the terminal from the project directory (depending on the python installation, you might need to use python3 instead of python):

.. code-block:: bash

   python simulation_plotter.py


Documentation
=============

Modules and Packages
--------------------
Here is a list of all modules and packages of the project.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`