# Readme: Inclusions repository

## General information

The programs in this repository aims at easing data collection and statistical analysis of inclusion data from salami slicing. The image below summarizes the workflow in data analysis from salami slicing, and shows what parts are covered by the present repository, and what is left to develop.

![Workflow](workflow.png)

### Before using the program

Before using the program, the user first has to generate data. The recommended procedure is to mount a metallographic sample and polish it to 0.05 µm in colloidal silica. Then, the surface of the sample should be mapped at a magnification of 100X or more, depending on the size of inclusions. The image should be stitched so that only one file is generated. This can be done with the Keyence microscrope software, or other software. Next, using ImageJ, the user has to increase the contrast in order to isolate the inclusions from the other features. Finally the user can make the image binary and apply a threshold, and then extract a list of particles that can be saved in a .csv file. The requirements of the data file are shown [below](#inclusion-data-files).

### Importing data in the program

The data is centralized in a HDF5 database, in the file `db_incl.h5`. The database is created automatically when importing the data. The data is imported from the .csv files, and those files are not reused after importation. The program will ask the user about metadata from the imported image file (sample identification, slice, sample area...), and then the inclusion data will be stored in the `data` table, and the metadata in the `meta` table. For more details see [below](#h5-database). The importation toolbox offers to the user to select out-of-range zones. Any feature mapped by ImageJ and contained in this area will be wxcluded from the analysis. It is also possible to use polar coordinates in case the cross-section of a sample is round.

### Filtering out the artifacts

Typically, when applying thresholding, artifacts such as scratches, dust and stains can get counted as inclusions. The best way to avoid this is to firstly use sound polishing procedure avoiding scratches and to wash the sample properly with hand soap and dry quickly just before the observation, so that the number of stains and dust particles is kept to a minimum. Since it is not possible to systematically avoir all those, the program comes with an utility to quickly filter out those artifacts. The program shows magnified views of the features to the user in rapid succession, and the user classifies them to the best of his/her know knowledge, so that the artifacts are removed from the analysis.

Attemps had been made to use the classified data to train an artificial neural networks (ANN). This seems to be promising, although work remains to be done. The accuracy of the ANN has not been tested yet, and more data will need to be fed to the model. There always will be uncertainty because even a human user cannot discern dust from inclusion in some cases. More data will need to be fed to the model.

Another application of ANN could be to differentiate types of inclusions automatically, which would allow separate the distributions proper to each inclusion.

### Analysis workflows

The workflows below are being or will be developed for data analysis, and are at different stages of maturity:

* Basic analysis: the program currently has the capacity to generate automatically size statistics for inclusions, as well as kernel density plots showing the repartition of inclusions in function of size.
* Block maxima analysis: Capabilities to separate an image file in blocks have been implemented in cartesian and polar coordinates, but analysis capabilities still need to be developed.
* Peak over threshold: Exponential probability plots can be drawn, but the rest of the analysis needs to be programmed.
* Pitting analysis: An interesting application of this program is the comparison of the same sample before and after pitting. This could allow identification and counting of pits.

## Getting started: Example
In the following, we will download the repository, create a database, import data from an image, post-treat the data and perform basic statistical analyses. Before so, first make sure that Python and Git are installed on your computer.

To download the repository on your computer, there are several ways. With Git installed on your computer, you should have extra options when you right-click in the Windows file explorer. So first choose a convenient folder on your computer (for better performance the folder should be on your computer and not on a remote drive, because we will treat large files.) In my case, I chose the folder `Documents/Python Scripts`. 

Right click in the file explorer, and select `Git GUI Here`. Click on `Clone Existing Repository`. Then in source location, enter: [https://github.com/slriverin/inclusions](https://github.com/slriverin/inclusions). In Target directory, enter the name of a new directory, for example `inclusions`, then click `Clone`. The program may ask you for your Github credentials. Once this is done, the repository will be downloaded (or "cloned") in the indicated folder. You can take a look to see that the Python file is there, and that the example data (one .csv and one .jpg files) are present in the `data` folder.

![Github menu](menu.png)
![Github window](gitwindow.png)

Once this is done, open a IPython console (usually I type 'Anaconda Powershell Prompt' in the windows search window), then I use `cd` and `ls` commands to navigate to my folder. You should see something like below. Then, I type `cd inclusions` and I `ipython` to open the Python console. Now you are ready to begin!!

![Ipython console](console.png)

Then, as you do at the beginning of every Python session, import the libraries you are going to use:

```
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
```

Then, run the the program, which will put in memory all the necessary commands: `run analysis.py`. Maybe you will see warnings from Tensorflow, don't mind about that.

Then, type `meta, data = get_data()`. This command is used to load the data in the database (HDFS file format) into two Pandas tables, `meta` and `data`. However, since you just downloaded the repository, the data does not exist yet, you have to create it. It should be written `Database not found... creata? ...: [n] `. The `[n]` in brackets means that the default answer is no. So if you enter anything but 'y', the program won't create the database. Type `y`.

Now, empty databases are loaded in the variables `meta` and `data`. You can see their content by typing them in the prompt.

Now you want to import the data from the example provided in the repository. Type `new_image()`. Then, follow the instructions. Normally, the program shows you the list of existing samples, but none of them exist, so you create one by typing '0'. You can choose any ID you like for this example. Choose slice 1 as proposed (this is the first slice of your hypothetical sample). Then, the program looks in the `data` folder for you, so you just have to type the number corresponding to the data file you want to import. Choose '1' for the file `example.csv`.

To fill the metadata, I suggest you open the image in ImageJ. ImageJ tells you the dimensions of the image: 6711x17831 µm (red circle below). Be careful though. In this case, the image produced by the Keyence has a definition of 1 µm per pixel. If this is not the case, you have to calibrate the image in ImageJ before exporting the data, and keep the same calibration to enter the proper dimensions. So enter the width (6711) and the height (17831) as requested, and congratulations, you just imported your first image! The program saved it directly in the database (db_incl.h5). If you want to look at the data, you have to reimport it, by typing `meta, data = get_data()`. The database is updated, but the variables in the Python environment are not upated automatically so you have to reimport them.

![Image with dimensions](dims.png)

If you type `meta` you should see the metadata for the image you just imported. You can see that the image has an area of 119.66 mm^2. You can also type `data`, so you see that the table has 1504 rows and 18 columns. Image analysis with ImageJ has recorded 1504 particles. However, you can see that the first feature has a very large feret diameter (19 mm). In fact, ImageJ records all dark features, so the bakelite outside of the polished sample is recorded as a gigantic feature, same for the digits in the scale bar. It is important to exclude those features before performing any analysis.

The first step is to exclude areas where you know there isn't anything interesting. Type `exclude()`. Then, answer the questions to identify which sample you are working on. Then, let's say we want to exclude the top part of the picture, where the scale is and a lot of bakelite. You have to enter the coordinates of a bounding box so that the program will eliminate it. You can use ImageJ to identify the coordinates, as below. You exclude a zone that spans the whole width (so xmin=0 and xmax=6711) and that goes from 0 to approximately 1560 in the y direction. Make sure that the "invert y measurements" box is unchecked in ImageJ/Analyze/Set Measurements, so that the zero in y is at the top. Once you entered the bounding box coordinates, the program will show you the area to be removed and ask you to confirm. You have to close the window before confirming.

![Area to be excluded](exclude.png)

We still need to exclude the left, right and bottom parts before continuing the analysis. You can do it the same way as the one above. It is OK if some useful area is removed. However, be careful that the excluded areas don't overlap each other, because the program does not verify if it is the case, and the area of each is substracted from the surface area in the `meta` table. If you exclude twice the same area, the area is substracted twice. This could be improved in future versions. A graphical user interface would also facilitate this step.

Once you are done, you can type `print_stats`. This will show stats per sample (if there are more than one slice), and also some stats about inclusion density. You can also explore the statistical functions. For example, type:

```
fig = dens_vs_size()
fig.show()
```

You should see something like this, which is a kernel density plot of the distribution of feret diameters of inclusions.

![KD of feret diameter](figtest.png)

Finally, you can give a shot at classifying features. Type `ID_incl()`. Enter the informations about the sample and choose Mode 1. The program will show you inclusions in decreasing order of size. Note that it will not show a feature larger than 500 µm, because it takes long time to load. In the case of this sample, it shows the whole bakelite as a single continuous feature. You have an idea about that with the Feret diameter which corresponds to the diagonal of the full picture.  It didn't exclude this feature from the analysis because its center of gravity was not in one of the excluded zones. So in the classification, type '7' as out of bounds. This feature will not be included in the analysis. Then, the program will show pictures of inclusions, which you observe, close the picture and classify. The program will ask you to classify features until you are bored. Usually, I classify maybe the 50 or 100 larger ones and I consider that the rest are not artifacts. You can stop before if your sample is very clean and you don't see a lot of artifacts. Of course, it will take some time for your eye to train.

Below you see an example of a picture that is clearly an inclusion. In that case, you would type '2' for inclusion. Note also that it is mentioned: "This image is 99.71 percent inclusion". This is the evaluation of the ANN, that is 99.71 percent sure it is an inclusion. It seems great, but it doesn't always work, and this inclusion was in the training dataset, so it already "knows" about it. The ANN should be tested against new data so we can know about its efficienty.

![Example of classification](classify.png)


## Data description
The data is stored in tabular format. The following describes the fields in the tables used in this program

### H5 database
The database is made of two tables:
* `meta` contains all the metadata from the image file. Each row of the table corresponds to a separate image file.
* `data` lists all the data concerning each individual feature observed on all the images. The features from all the images are grouped in the same table, with fields identifying to which image they belong.

The program takes care of formatting the data and metadata properly before storing them in the database, thus reducing risks of errors. Nevertheless, it is possible for the user to modify data manually if need be (WARNING: there is no UNDO when you make a change to a database, so make sure you know what you are doing). The field headers are case sensitive when manipulated in pandas.

The `meta` table consists of the following fields. Each combination of `ID_specimen` and `slice` is unique.

Field |Data type |Description
---|---|---
ID_specimen |String |Unique identifier for the metallographic specimen
slice |Integer |Sequential number used to identify successive slices of the same specimen, if repolished between 2 observations.
filename |String |Path to the image file used to obtain the data. Must be complete so the program is able to find the picture.
img_width |Float |Width of the image file (µm)
img_height |Float |Height of the image fileé 
img_area_mm2 |Float |Area of image (mm^2). Initially calculated with the dimensions, but any excluded area is substracted.
x_c, y_c |Float |Coordinates (µm) of the center of the specimen (used for circular specimens)
r_outer |Float |Radius of the specimen (µm), for circular specimens
n_divis_x |Integer |Number of divisions in x, or in theta if the sample is circular. Used for block maxima workflow.
n_divis_y |Integer |Number of divisions in y. Not used for polar coordinates
divis_area_mm2 |Float |Area of the divisions (mm2)

The `data` table contains the following fields. Each combination of `ID_specimen`, `slice` and `incl_nb` is unique.

Field |Data type |Description
---|---|---
ID_specimen |String |Unique identifier for the metallographic specimen
slice |Integer |Sequential number used to identify successive slices of the same specimen, if repolished between 2 observations.
incl_nb |Integer |Index of feature/inclusion
x, y |Float |Coordinates of feature (µm)
area |Float |Area of feature (µm^2)
feret |Float |Feret diameter (µm^2)
min_feret|Float|Minimum distance between 2 points on the boundary
feret_angle|Float|Angle of 0 to 180° between feret diameter and a horizontal line (°)
circ|Float|Circularity. A value of 1.0 for a perfect circle, and close to zero if very elongated
round|Float|Roundness. Inverse of aspect ratio
ar|Float|Aspect ratio. Ratio of max to min axes of an ellipse fitted to the contour of the feature
solid|Float|Indicator of convexity. Ratio of area over convex area.
incl_type |Categorical |Classification of the type of feature (inclusion, porosity, dust, scratch, ...)
r |Float |Radial coordinate of feature, if sample circular (µm)
theta |Float |Azimuthal coordinate of feature, if sample is circular (°)
division |Integer |To which division (block) belongs the feature (for block maxima workflow)

### Data logger

There is no UNDO operations in a database, however a datalogger was added to this repository. Every change made to the database is automatically timestamped and logged with a text description in `db_incl.log`. If any unwanted change was to occur, it is possible to see exactly what change has been made and revert it back manually. Eventually, another option would be to playback the log file and rebuilt the database from the original data. This is not implemented yet.

### Inclusion data files

The following applies to .csv files to be imported in the database. It is important to have the right column headers (case sensitive). See [ImageJ user guide](https://imagej.nih.gov/ij/docs/guide/146-30.html#toc-Subsection-30.2) for more info on shape descriptors.

Column header | Data type   | Description
--- | --- | ---
(blank) |Integer  |Index of feature/inclusion
X, Y  |Float  |Coordinates of feature (µm)
Area  |Float  |Area of feature (µm^2)
Feret |Float  |Feret diameter (longest distance between 2 points on the boundary) (µm)
MinFeret|Float|Minimum distance between 2 points on the boundary
FeretAngle|Float|Angle of 0 to 180° between feret diameter and a horizontal line (°)
Circ.|Float|Circularity. A value of 1.0 for a perfect circle, and close to zero if very elongated
AR|Float|Aspect ratio. Ratio of max to min axes of an ellipse fitted to the contour of the feature
Round|Float|Roundness. Inverse of aspect ratio
Solidity|Float|Indicator of convexity. Ratio of area over convex area.
