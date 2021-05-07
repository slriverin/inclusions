# Readme: Inclusions repository

## General information

The programs in this repository aims at easing data collection and statistical analysis of inclusion data from salami slicing. The image below summarizes the workflow in data analysis from salami slicing, and shows what parts are covered by the present repository, and what is left to develop.

![Workflow](workflow.png)

Before using the program, the user first has to generate data. The recommended procedure is to mount a metallographic sample and polish it to 0.05 µm in colloidal silica. Then, the surface of the sample should be mapped at a magnification of 100X or more, depending on the size of inclusions. The image should be stitched so that only one file is generated. This can be done with the Keyence microscrope software, or other software. Next, using ImageJ, the user has to increase the contrast in order to isolate the inclusions from the other features. Finally the user can make the image binary and apply a threshold, and then extract a list of particles that can be saved in a .csv file. The requirements of the data file are shown [below](#inclusion-data-files).

## Data description

### Inclusion data files
