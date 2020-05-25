.. aroundvision documentation master file, created by
   sphinx-quickstart on Thu May 21 14:43:41 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to aroundvision's documentation!
****************************************

The AROUNDVISION is a tool to visualize 360 images from an API
in different projections. Additionally, it allows the user to
select some region of interest to visualize that area in more
detail!

Configuration of Project Environment
************************************

Overview on How to Run this application
---------------------------------------
1. Create a Python virtual environment to install the packages required
2. How to install
3. Fill the configuration file
4. How to run in command line
5. Unit Test and Code Coverage - Locally

Setup Procedure
+++++++++++++++
1. **Create a Python virtual environment to install the packages required**
        - Install virtualenv::

            sudo pip install virtualenv

        - Create virtualenv::

            virtualenv -p python3 <name of virtualenv>

        - Install requirements::

            pip install -r requirements.txt

2. **How to install**
    A::

      python setup.py install

    B::

      pip install .

3. **Fill the configuration file**

Fill the config.yaml file with your configurations.

4. **How to run in command line**
   - Run the following::

      aroundvision

5. **Unit Test and Code Coverage - Locally**

In base folder you just run the following command::

   tox

This will perform some analysis and export a report.
All the tests are executed against some py versions defined
in tox.ini.

Code Documentation
******************
.. toctree::
   :maxdepth: 2
   :caption: Contents:

Aroundvision main
-----------------

.. automodule:: aroundvision.main
   :members:

Aroundvision views
------------------

1. MainWindow
~~~~~~~~~~~~~
.. automodule:: aroundvision.views.mainwindow
   :members:

2. LoadSource
~~~~~~~~~~~~~
.. automodule:: aroundvision.views.load_source
   :members:

3. About
~~~~~~~~
.. automodule:: aroundvision.views.about
   :members:

4. Video Player
~~~~~~~~~~~~~~~
.. automodule:: aroundvision.views.video_player
   :members:

5. Displayer
~~~~~~~~~~~~
.. automodule:: aroundvision.views.displayer
   :members:

6. QTimer Worker
~~~~~~~~~~~~~~~~
.. automodule:: aroundvision.views.qtimer_worker
   :members:

7. Region of Interest
~~~~~~~~~~~~~~~~~~~~~
.. automodule:: aroundvision.views.region_of_interest
   :members:

8. Region of Interest Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: aroundvision.views.roi_settings
   :members:

9. Popup
~~~~~~~~
.. automodule:: aroundvision.views.popup
   :members:

10. Loading Screen
~~~~~~~~~~~~~~~~~~
.. automodule:: aroundvision.views.loading_screen
   :members:

Aroundvision models
-------------------
.. automodule:: aroundvision.models.models
   :members:

Aroundvision controllers
------------------------
.. automodule:: aroundvision.controllers.controller
   :members:

Indices and tables
******************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
