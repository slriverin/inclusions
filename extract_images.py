# -*- coding: utf-8 -*-

#Commonly used libraries
import pandas as pd
import numpy as np
import os

from PIL import Image
Image.MAX_IMAGE_PIXELS = 1e9

import analysis

meta, data = analysis.get_data()

for spec in data.loc[data.incl_type=='2'].ID_specimen.unique():

    im_filename = os.path.join('data', spec + '.jpg')
    im = Image.open(im_filename)

    df = data.loc[data.ID_specimen==spec]
    for index, row in df.loc[df.incl_type=='2'].iterrows():
        x = row.x
        y = row.y
        feret = row.feret
        feret_min = row.min_feret
        feret_angle = row.feret_angle
        
        width = np.max([np.abs(feret*np.cos(feret_angle*np.pi/180)), feret_min])*2
        height = np.max([np.abs(feret*np.sin(feret_angle*np.pi/180)), feret_min])*2
        
        xmin = x - width/2
        xmax = x + width/2
        ymin = y - height/2
        ymax = y + height/2
        
        im_out = im.crop((xmin, ymin, xmax, ymax))
        filename = '{:s}.{:d}.jpg'.format(row.ID_specimen, row.incl_nb)
        im_out.save('images/Inclusions/{:s}'.format(filename), 'JPEG')

    for index, row in df.loc[df.incl_type.apply(lambda x: x in ['1', '3', '4', '5', '6'])].iterrows():
        x = row.x
        y = row.y
        feret = row.feret
        feret_min = row.min_feret
        feret_angle = row.feret_angle
        
        width = np.max([np.abs(feret*np.cos(feret_angle*np.pi/180)), feret_min])*2
        height = np.max([np.abs(feret*np.sin(feret_angle*np.pi/180)), feret_min])*2
        
        xmin = x - width/2
        xmax = x + width/2
        ymin = y - height/2
        ymax = y + height/2
        
        im_out = im.crop((xmin, ymin, xmax, ymax))
        filename = '{:s}.{:d}.jpg'.format(row.ID_specimen, row.incl_nb)
        im_out.save('images/Other/{:s}'.format(filename), 'JPEG')