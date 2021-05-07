# Readme: Inclusions repository

## General information

The programs in this repository aims at easing data collection and statistical analysis of inclusion data from salami slicing. The image below summarizes the workflow in data analysis from salami slicing, and shows what parts are covered by the present repository, and what is left to develop.

![Workflow](workflow.png)

### Before using

Before using the program, the user first has to generate data. The recommended procedure is to mount a metallographic sample and polish it to 0.05 µm in colloidal silica. Then, the surface of the sample should be mapped at a magnification of 100X or more, depending on the size of inclusions. The image should be stitched so that only one file is generated. This can be done with the Keyence microscrope software, or other software. Next, using ImageJ, the user has to increase the contrast in order to isolate the inclusions from the other features. Finally the user can make the image binary and apply a threshold, and then extract a list of particles that can be saved in a .csv file. The requirements of the data file are shown [below](#inclusion-data-files).

### Importing data in the program

The data is centralized in a HDF5 database, in the file `db_incl.h5`. The database is created automatically when importing the data. The data is imported from the .csv files, and those files are not reused after importation. The program will ask the user about metadata from the imported image file (sample identification, slice, sample area...), and then the inclusion data will be stored in the `data` table, and the metadata in the `meta` table. For more details see [below](#h5-database). The importation toolbox offers to the user to select out-of-range zones. Any feature mapped by ImageJ and contained in this area will be wxcluded from the analysis. It is also possible to use polar coordinates in case the cross-section of a sample is round.

### Filtering out the artifacts

Typically, when applying thresholding, artifacts such as scratches, dust and stains can get counted as inclusions. The best way to avoid this is to firstly use sound polishing procedure avoiding scratches and to wash the sample properly with hand soap and dry quickly just before the observation, so that the number of stains and dust particles is kept to a minimum. Since it is not possible to systematically avoir all those, the program comes with an utility to quickly filter out those artifacts. The program shows magnified views of the features to the user in rapid succession, and the user classifies them to the best of his/her know knowledge, so that the artifacts are removed from the analysis.


## Data description

### Inclusion data files

### H5 database
