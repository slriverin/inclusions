# -*- coding: utf-8 -*-

#Commonly used libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import os, sys

#Configuration of Matplotlib grahps to use LaTeX formatting with siunitx library
from matplotlib.ticker import FormatStrFormatter
import matplotlib as mpl
from matplotlib import rc
rc('font',**{'family':'serif','serif':['DejaVu Sans']})
rc('text', usetex=True)
mpl.rcParams['errorbar.capsize'] = 3
mpl.rcParams['lines.markersize'] = 5
mpl.rcParams['text.latex.preamble']=r'\usepackage{siunitx}'

#Headers for meta and data Dataframes
fields_data = ['ID_specimen', 'slice', 'incl_nb', 'x', 'y', 'area', 
               'sqr_area', 'feret', 'min_feret', 'feret_angle', 'circ', 
               'round', 'ar', 'solid', 'incl_type', 'r', 'theta', 'division']
fields_meta = ['ID_specimen', 'slice', 'filename', 'img_width', 'img_height',
               'img_area_mm2', 'x_c', 'y_c', 'r_outer', 'n_divis_x', 'n_divis_y', 'divis_area_mm2']


#Basic I/O functions
def get_data():
    """
    Gets data from database and returns it as Pandas Dataframes.

    Parameters
    ----------
    None

    Returns
    -------
    meta : Metadata
    data : Data

    """
    
    #Looks for database and asks the user to creat it if does not exist
    try:
        meta = pd.read_hdf('db_incl.h5', 'meta', 'r')
        data = pd.read_hdf('db_incl.h5', 'data', 'r')
        
    except FileNotFoundError:
        ans = input('Database not found... create? ...: [n] ')
        meta = pd.DataFrame(columns = fields_meta)
        data = pd.DataFrame(columns = fields_data)
        if ans == 'y':
            meta.to_hdf('db_incl.h5', 'meta')
            data.to_hdf('db_incl.h5', 'data')
            
    return meta, data


def save_data(meta, data):
    """
    Overwrites the database with the metadata and data contained in the Pandas Dataframes in argument.
    This routine is used by I/O functions to update the database.
    It can also be used by the user to manually update fields in the database.
    No confirmation is asked to the user.
    
    WARNING: Use only if you know what you are doing. The changes may corrupt the database and are irreversible.
    ADVICE: Make backup copies of the database regularly.

    Parameters
    ----------
    meta: Metadata
    data: Data

    Returns
    -------
    Nothing

    """
    
    try:
        #Makes sure the data is in the right format
        meta['slice'] = meta.slice.astype(int)
        meta['n_divis_x'] = meta.n_divis_x.astype(int)
        meta['n_divis_y'] = meta.n_divis_y.astype(int)
        for col in ['img_width', 'img_height', 'img_area_mm2', 'x_c', 'y_c', 'r_outer']:
            meta[col] = meta[col].astype(float)

        
        int_cols = ['slice', 'incl_nb', 'division']
        float_cols = ['x', 'y', 'area', 'sqr_area', 'feret', 'min_feret', 
                      'feret_angle', 'circ', 'round', 'ar', 'solid', 'r', 'theta']
        
        for col in int_cols:
            data[col] = data[col].astype(int) 
        for col in float_cols:
            data[col] = data[col].astype(float) 
        
        data = data.sort_values('division', ascending=False)
        data = data.drop_duplicates(subset = ['ID_specimen', 'slice', 'incl_nb'])
        data = data.sort_values(['ID_specimen', 'slice', 'incl_nb'])\
            .reset_index(drop=True)
        
        
        meta.loc[:, fields_meta].to_hdf('db_incl.h5', 'meta')
        data.loc[:, fields_data].to_hdf('db_incl.h5', 'data')
    
    except:
        print('Error writing data. Verify datasets.')


#Data entry functions for interacting with user.
def new_image():
    """
    Imports data from a newly analyzed image and updates the metadata.
    
    OR
    
    Overwrites data and metadata if the user specifies existing specimen and slice.
    
    The user is asked to properly identify the sample and slice to which the data pertain.
    The user is then asked to point the right .csv file in which the data is contained.
    The .csv file must be properly formatted and put in the root folder (see readme file)
    The user is then asked to input the dimensions of the specimen and to identify whether it is circular or not.
    If there are no errors, the data is read from the .csv file, formatted and uploaded in the database.
    At the same time, the metadata is updated in the database.

    Parameters
    ----------
    None

    Returns
    -------
    Nothing

    """
    
    #Asks the user for the specimen ID. 
    #The user is asked to choose from a list of existing specimens
    print('Which specimen ID? Enter sequential number. <0> for new specimen.')
    print('Other entry does nothing.')
    print('Seq. nb\tID_specimen')
    
    #Lists the existing specimens
    meta, data = get_data()
    specs = meta.ID_specimen.unique()
    for i in range(len(specs)):
        print('{:d}\t{:s}'.format(i+1, specs[i]))
        
    try:
        ans = input('...: [0] ')
        
        #Default answer: New specimen
        if ans == '':
            i_spec = 0
        else:
            i_spec = int(ans)
        
        if i_spec == 0:
            #New specimen
            ID_spec = input('New sample ID? ...: ')
            if ID_spec == '':
                print('Invalid name')
                return
                
        elif i_spec > len(specs):
            #Invalid entry
            print('No such sample')
            return 
            
        else:
            #Existing specimen
            ID_spec = specs[i_spec-1]
            
    except ValueError:
        #Invalid entry
        return

    try:
        #Asks for the slice number. By default, adds a new slide.
        slice_def = len(meta.loc[meta.ID_specimen==ID_spec, 'slice'])+1
        ans = input('Which slice? ...: [{:d}] '.format(slice_def))
        
        #Default answer
        if ans == '':
            slice = slice_def
        else:
            slice = int(ans)
            
    except ValueError:
        print('Must enter integer')
        return
    
    #Asks user for the filename
    print('Which filename? Enter sequential number.')
    
    #Lists .csv files from which to choose
    print('Seq. nb\tID_specimen')
    list_csv = []
    for file in os.listdir():
        if file[-3:] == 'csv':
            list_csv.append(file)
    for i in range(len(list_csv)):
        print('{:d}\t{:s}'.format(i+1, list_csv[i]))
        
    try:
        ans = input('...: [] ')
        if ans == '':
            print('No such file')
            return
        elif int(ans) > len(list_csv):
            print('No such file')
            return 
        else:
            filename = list_csv[int(ans)-1]
            
    except ValueError:
        print('No such file')
        return
            
    #Asks user for metadata
    try:
        print('If sample circular, type width = 0')
        img_width = float(input('Image width (microns) ...: '))
        if int(img_width) == 0:
            #Circular cross-section
            img_r1 = float(input('Outer radius (microns) ...: '))
            img_r2 = float(input('Inner radius (microns) ...: '))
            img_area = np.pi*(img_r1**2 - img_r2**2)/1e6
            img_height = (img_area/np.pi)**0.5*1000
            
        else:
            #Rectangular cross-section
            img_height = float(input('Image height (microns) ...: '))
            img_area = img_width*img_height/1e6
            
    except ValueError:
        print('Numerical value needed')
        return
    
    try:
        df_data = pd.read_csv(filename)         #Extracts data from .csv file
        
        #Changes row header names
        df_data = df_data.rename(columns={' ': 'incl_nb', 'X': 'x', 'Y': 'y',
                    'Area': 'area', 'Feret': 'feret', 'MinFeret': 'min_feret',
                    'FeretAngle': 'feret_angle', 'Circ.': 'circ', 'AR': 'ar',
                    'Round': 'round', 'Solidity': 'solid'}, errors='raise')
                    
        df_data = df_data.loc[df_data.incl_nb.notnull()]    #Eliminate empty rows
        df_data['sqr_area'] = df_data.area**0.5             #Add sqr(Area) data
        df_data['ID_specimen'] = ID_spec                    #Identifies specimen
        df_data['slice'] = slice                            #Identifies slice
        df_data['incl_type'] = ''                           #Leaves inclusion type unidentified
        df_data = df_data.loc[:, fields_data]               #Sets the headers properly
        
    except (KeyError, AttributeError):
        #Exits if any error in the format of the .csv file.
        print('Error reading .csv file')
        return
        
    data = data.loc[(data.ID_specimen != ID_spec)|(data.slice != slice)]    #Removes any existing data on the current specimen and slice
    data = pd.concat([data, df_data])                                       #Updates the data
    
    meta = meta.loc[(meta.ID_specimen != ID_spec)|(meta.slice != slice)]    #Removes any existing metadata on the current specimen and slice
    meta = meta.append({'ID_specimen': ID_spec, 'slice': slice, 
                        'filename': filename, 'img_width': img_width,
                        'img_height': img_height, 'img_area_mm2': img_area}, 
                       ignore_index=True)                                   #Adds a row with the newly input metadata
 
    save_data(meta, data)   #Updates the database


def def_pol_coord():
    """
    Converts cartesian coordinates to polar coordinates for sample with circular cross-section.
    Excludes any data that is out of bounds (from other specimens appearing on the same picture).
    
    The user is asked to choose specimen and slides on which to update coordinates.
    First approximation to the center of the specimen is estimated by calculating the average coordinates of the features.
    First approximation of outer radius is obtained from known geometry.
    Plots all the points on a graph, with the proposed center and a circle representing radius.
    The user is asked to update the position of the center and outer radius as needed until all the out-of-bounds points are outside of the circle.
    Then, new center is calculated by the average between min and max coordinates.
    The outer radius is set as the point with max radius.
    Confirmation is asked to the user.
    Then the database is updated with the polar coordinates of the points and the points out of bounds are marked with incl_type = '7'.
    
    Parameters
    ----------
    None

    Returns
    -------
    Nothing

    """
    
    #Asks for the specimen number
    print('Which specimen ID? Enter sequential number. <0> for new specimen.')
    print('Other entry does nothing.')
    
    #Lists the specimens with circular cross-section.
    print('Seq. nb\tID_specimen')
    meta, data = get_data()
    specs = meta.loc[meta.img_width.apply(lambda x: int(x))==0].ID_specimen.unique()    #Condition img_width = 0: circular specimen
    
    for i in range(len(specs)):
        print('{:d}\t{:s}'.format(i+1, specs[i]))
    try:
        ans = input('...: [0] ')
        if ans == '':
            i_spec = 0
        else:
            i_spec = int(ans)
            
        if i_spec == 0 or i_spec > len(specs):
            print('No such sample')
            return 
        else:
            ID_spec = specs[i_spec-1]
    except ValueError:
        return

    try:
        #Asks the slice number from the existing ones.
        slice_def = len(meta.loc[meta.ID_specimen==ID_spec, 'slice'])
        ans = input('\nWhich slice? ...: [1-{:d}] '.format(slice_def))
        
        if ans == '':
            raise ValueError
        else:
            slice = int(ans)
            
    except ValueError:
        print('Must enter integer')
        return
        
    if slice > slice_def or slice == 0:
        print('No such slice')
        return
        
    #Extracts existing metadata and data for the specified specimen and slice
    ser_meta = meta.loc[(meta.ID_specimen==ID_spec)&(meta.slice==slice)].iloc[0]
    df = data.loc[(data.ID_specimen==ID_spec)&(data.slice==slice), data.columns]
    
    if math.isnan(ser_meta.x_c) or math.isnan(ser_meta.y_c) or math.isnan(ser_meta.r_outer):
        print('No center defined. Default values will be inferred from data.')
        x_c = df.x.mean()   #Average x coordinate
        y_c = df.y.mean()   #Average y coordinate
        r_outer = 6500      #Known default dimension
        
    else:
        #Data exists
        x_c = ser_meta.x_c
        y_c = ser_meta.y_c
        r_outer = ser_meta.r_outer
    
    
    ok = False
    while ok == False:      #Loops until the user is satisfied.
        
        #Plots the features, with the center and outer radius
        fig = plt.figure(dpi=200)
        ax = fig.gca()
        ax.plot(df.x, df.y, 'k.', label = 'Features')   
        TH=np.linspace(0, 2*np.pi, 100)
        ax.plot(x_c + r_outer*np.cos(TH), y_c + r_outer*np.sin(TH), 'b-', label = 'Max radius')
        ax.plot(x_c, y_c, 'g*', label = 'Center')
        ax.legend()
        fig.show()
        
        print('\nPoints outside of blue circle will be excluded. Center and max diameter will be recalculated... OK?')
        print('<1>: Yes')
        print('<2>: No, adjust values manually')
        ans = input('Any other entry: no change and exit...: ')
        if ans == '1':  
            #User accepts changes
            ok = True
            
        elif ans == '2':
            #User updates the coordinates of the center and the outer radius.
            try:
                print('Center of circle...:')
                ans = input('X ...: [{:.1f}] '.format(x_c))
                if ans == '':
                    pass
                else:
                    x_c = float(ans)
                    
                ans = input('Y ...: [{:.1f}] '.format(y_c))
                if ans == '':
                    pass
                else:
                    y_c = float(ans)
                    
                ans = input('Exclusion radius ...: [{:.1f}] '.format(r_outer))
                if ans == '':
                    pass
                else:
                    r_outer = float(ans)
            except:
                print('Error in entering values')
                return
                
        else:
            #Other entry, exits the loop and the routine
            return
        
    #Calculates the polar coordinates
    df.loc[:, 'r'] = ((df.x - x_c)**2 + (df.y - y_c)**2)**0.5
    df.loc[:, 'theta'] = df.apply(lambda row: ret_th(row.x, row.y, x_c, y_c), axis=1)
    
    #Calculates the real position of the center of the sample
    x_c = (df.loc[df.r < r_outer].x.max() + df.loc[df.r < r_outer].x.min())/2
    y_c = (df.loc[df.r < r_outer].y.max() + df.loc[df.r < r_outer].y.min())/2
    
    #Updates the polar coordinates and the outer radius
    df.loc[:, 'r'] = ((df.x - x_c)**2 + (df.y - y_c)**2)**0.5
    df.loc[:, 'theta'] = df.apply(lambda row: ret_th(row.x, row.y, x_c, y_c), axis=1)
    r_outer = df.loc[df.r < r_outer].r.max()
    
    #Plots the final results to get confirmation from user.
    fig = plt.figure(dpi=200)
    ax = fig.gca()
    ax.plot(df.loc[df.r < r_outer].x, df.loc[df.r < r_outer].y, 'k.', label = 'Features')
    ax.plot(df.loc[df.r > r_outer].x, df.loc[df.r > r_outer].y, 'r.', label = 'Out of bounds')
    TH=np.linspace(0, 2*np.pi, 100)
    ax.plot(x_c + r_outer*np.cos(TH), y_c + r_outer*np.sin(TH), 'b-', label = 'Outside radius')
    ax.plot(x_c, y_c, 'g*', label = 'Center')
    ax.legend()
    fig.show()
    
    print('\nSpecimens limit accurately represented? Outside radius for info only, not used for area calculation.')
    print('<1>: Yes')
    ans = input('Any other entry: no change and exit...: ')
    if ans == '1':
        #Changes accepted, updates database
        df.loc[df.r > r_outer, 'incl_type'] = '7'       #Out of bounds features
        data.update(df)
        meta.loc[(meta.ID_specimen==ID_spec)&(meta.slice==slice), 'x_c'] = x_c
        meta.loc[(meta.ID_specimen==ID_spec)&(meta.slice==slice), 'y_c'] = y_c
        meta.loc[(meta.ID_specimen==ID_spec)&(meta.slice==slice), 'r_outer'] = r_outer
        save_data(meta, data)

       
def ID_incl():
    """
    Assists user in visually identifying inclusions.
    
    Only modes 1 and 2 are programmed so far.
    The user chooses specimen and slice on which to identify inclusions.
    The routine chooses the largest unidentified inclusion in terms of area (mode 1) or feret diameter (mode 2).
    The routine gives the coordinates of the inclusion to the user.
    The user looks in the original image file and identifies the type of inclusion, or skips to the next inclusion.
    Each time the users identifies an inclusion, the database is updated.
    In the database, the field <incl_type> is updated each time.
    The routine continues as long as the users does not quit.
    
    Inclusion types (field <incl_type>)
    ---------------
        '1':    Spherical inclusion or void
        '2':    Irregular inclusion
        '3':    Lack of fusion
        '4':    Scratch
        '5':    Dust
        '6':    Unknown or other artifact
        '7':    Out of bounds
        '':     Empty field: not identified yet

    Parameters
    ----------
    None

    Returns
    -------
    Nothing

    """
    
    #Asks for the mode. Default value: Mode 1.
    print('What mode? <1>: Largest ones (Area); <2>: Largest ones (Feret); <3>: Specific inclusion; <4>: By location, <5>: Review entries.')
    
    try:
        ans = input('[1]...: ')
        if ans == '':
            ans = 1
        
        mode = int(ans)
        
    except ValueError:
        return
    
    if mode == 1 or mode == 2:
        #In mode 1 or mode 2, chooses the appropriate column on which to sort the database
        if mode == 1:
            colsort = 'area'
        elif mode ==2:
            colsort = 'feret'
        
        #Asks specimen number
        print('Which specimen ID? Enter sequential number. <0> for all specimens. ')
        print('Seq. nb\tID_specimen\tNb. of slices')
        meta, data = get_data()
        specs = meta.ID_specimen.unique()
        for i in range(len(specs)):
            print('{:d}\t\t{:s}\t\t{:d}'.format(i+1, specs[i], data.loc[data.ID_specimen==specs[i]].slice.max()))
            
        try:
            i_spec = int(input('...: '))
                
            if i_spec == 0:
                #All specimens
                ID_spec = -1
            elif i_spec > len(specs):
                print('No such sample')
                return 
            else:
                ID_spec = specs[i_spec-1]
        except ValueError:
            return
    
        try:
            #Asks for slice
            ans = input('Which slice? <0> for all slices...: ')
            slice = int(ans)
                
        except ValueError:
            print('Must enter integer')
            return
            
        #Creates df, the reduced dataset
        if ID_spec == -1:   #All specimens
            df = data
        elif slice == 0:    #All slices
            df = data.loc[data.ID_specimen == ID_spec]
        else:               #Specific specimen and slice
            df = data.loc[(data.ID_specimen == ID_spec) & (data.slice == slice)]
        
        df = df.loc[df.incl_type == '']     #Keeps only indidentified inclusions
        
        cont = True
        while cont == True:     #Loops until user quits
            df = df.sort_values(by=colsort, ascending = False)  #Sort by appropriate size indicator (per mode)
            index_incl = df.index[0]
            
            #Displays data on the feature to identify
            print('For defect... :')
            print(df.head(1))
            
            #Asks user input
            print('Please identify inclusion type')
            print('<>: Next, leave unidentified')
            print('<1>: Inclusion (spherical) or spherical void')
            print('<2>: Inclusion (irregular)')
            print('<3>: Lack of fusion')
            print('<4>: Scratch')
            print('<5>: Dust')
            print('<6>: Unknown or other artifact')
            print('<7>: Out of bounds')
            print('<x> or other entry: Quit')
            ans=input('...: ')
            
            if ans in ['1', '2', '3', '4', '5', '6', '7']:
                #User made a choice, update database
                data.loc[index_incl, 'incl_type'] = ans
                save_data(meta, data)
                df = df.iloc[1:]    #Removes the top row so we can analyse the next one
                
            elif ans == '':
                #Leave unidentified, continue
                df = df.iloc[1:]
                
            else:
                #Quit
                cont=False
                return


def divide():
    meta, data = get_data()
    
    print('Choose specimen... enter sequential number')
    print('Average dimensions, millimeters')
    print('\nRectangular specimens')
    print('\tSpec.\tWidth\tHeight\tArea\tDivisions\tArea per division')
    df = meta.loc[meta.img_width > 1, meta.columns].groupby('ID_specimen').agg('mean')  #Selects only rectangular specimens
    
    i = 1
    dict_index = {}
    
    #Lists the samples with existing divisions
    for index, row in df.iterrows():
        if row.n_divis_x*row.n_divis_y == 0:
            area_per_div = 0
        else:
            area_per_div = row.img_area_mm2/(row.n_divis_x*row.n_divis_y)
        print('{:d}\t{:s}\t{:.2f}\t{:.2f}\t{:.2f}\t({:.0f}, {:.0f})\t\t{:.2f}'.format(i, index, row.img_width/1000, row.img_height/1000, row.img_area_mm2, 
                row.n_divis_x, row.n_divis_y, area_per_div))
        dict_index[i] = index
        i += 1
        
                
    print('\nCircular specimens')
    print('\tSpec.\tRadius\t\tArea\tDivisions\tArea per division')     
    df = meta.loc[meta.img_width.apply(lambda x: int(x)==0), meta.columns].groupby('ID_specimen').agg('mean')  #Selects circular specimens
    
    for index, row in df.iterrows():
        if row.n_divis_x == 0:
            area_per_div = 0
        else:
            area_per_div = row.img_area_mm2/row.n_divis_x
        print('{:d}\t{:s}\t{:.2f}\t\t{:.2f}\t{:.0f}\t\t{:.2f}'.format(i, index, row.img_height/1000, row.img_area_mm2, 
                row.n_divis_x, area_per_div))
        dict_index[i] = index
        i += 1
        
    #User chooses specimen
    try:
        spec = dict_index[int(input('\n... : '))]
    except ValueError:
        print('Please enter integer value')
        return
    except KeyError:
        print('No such specimen')
        return
        
    if meta.loc[meta.ID_specimen == spec, 'img_width'].mean() > 1:
        #Rectangular sample
        def get_div_rect(x, y, div_width, div_height, n_divis_x):
            #Returns coordinates of the division: 0, 1, 2 ...
            div_coord_x = int(x//div_width)
            div_coord_y = int(y//div_height)
            return div_coord_x + 1 + div_coord_y*n_divis_x


        n_divis_x = int(input('Divisions in x ... : '))
        n_divis_y = int(input('Divisions in y ... : '))
        if n_divis_x < 1 or n_divis_y < 1:
            raise ValueError
        
        df = meta.loc[meta.ID_specimen == spec, meta.columns]
        df.loc[:, 'n_divis_x'] = n_divis_x
        df.loc[:, 'n_divis_y'] = n_divis_y
        df.loc[:, 'divis_area_mm2'] = df.img_area_mm2/(df.n_divis_x*df.n_divis_y)
        
        df2 = data.loc[data.ID_specimen == spec, data.columns]
        df2 = df2.merge(df2.groupby(['ID_specimen', 'slice'])[['x', 'y']].transform('min').rename(columns={'x': 'x_min', 'y': 'y_min'}), 
                        left_index=True, right_index=True)
        df2 = df2.merge(df2.groupby(['ID_specimen', 'slice'])[['x', 'y']].transform('max').rename(columns={'x': 'x_max', 'y': 'y_max'}), 
                        left_index=True, right_index=True)
        df2 = df2.merge(df.loc[:, ['ID_specimen', 'slice', 'n_divis_x', 'n_divis_y', 'img_width', 'img_height']], on=['ID_specimen', 'slice'])
        df2.loc[:, 'div_width'] = (df2.x_max-df2.x_min)/n_divis_x*1.01
        df2.loc[:, 'div_height'] = (df2.y_max-df2.y_min)/n_divis_y*1.01
        
        df2.division = df2.apply(lambda row: get_div_rect(row.x-row.x_min, row.y-row.y_min, row.div_width, row.div_height, row.n_divis_x), axis=1)
        

        meta.update(df)
        data.update(df2)
        
        save_data(meta, data)
        
        
    
    
#Analysis tools
def print_stats():
    """
    Displays stats per specimen and slice.
    
    Displayed information per specimen:
        -Number of slices
        -Total area
        
    Dislpayed information per slice:
        -Analysed area
        -Total number of features (excluding artifacts and out-of-bounds)
        -Number of features per mm^2
        -Filename of original data

    Parameters
    ----------
    None

    Returns
    -------
    Nothing

    """
    meta, data = get_data()
    print('List of specimens studied')
    print('Spec.\tNb. of slices\tTotal area (mm^2)')
    for index, row in meta.groupby('ID_specimen')\
        .agg({'slice': 'nunique', 'img_area_mm2': 'sum'}).iterrows():
            print('{:s}\t{:d}\t\t{:.1f}'.format(index, int(row.slice), 
                                              row.img_area_mm2))
    print('\nStats per image file')
    df1 = data.loc[data.incl_type.apply(lambda x: x not in ['4', '5', '6', '7'])]\
        .groupby(['ID_specimen', 'slice'])\
        .agg({'incl_nb': 'count', 'feret': 'max'})

    df2 = meta.merge(df1, on=['ID_specimen', 'slice'])
    df2=df2.sort_values(['ID_specimen', 'slice'])
    
    print('Spec.\tSlice\tArea (mm^2)\tNb. incl.\tIncl. per mm^2\tFilename')
    for index, row in df2.iterrows():
        print('{:s}\t{:d}\t{:.2f}\t\t{:d}\t\t{:.2f}\t\t{:s}'.format(
            row.ID_specimen, row.slice, row.img_area_mm2, row.incl_nb, 
            row.incl_nb/row.img_area_mm2, row.filename))

def plot_prob(df, plot=False):
    df = df.loc[:, ['feret']].sort_values('feret').reset_index(drop=True)
    df['i'] = df.index+1
    df['P'] = df.i/(len(df)+1)
    df['q'] = -np.log(1-df.P)
    
    if plot==True:
        plt.plot(df.feret, df.q, 'k.')
        plt.xlabel('Feret (um)')
        plt.ylabel('-ln(1-F)')
    
    return df

def plot_prob_sqrsurf(df, plot=False):
    df = df.loc[:, ['area']].sort_values('area').reset_index(drop=True)
    df['i'] = df.index+1
    df['P'] = df.i/(len(df)+1)
    df['q'] = -np.log(1-df.P)
    
    if plot==True:
        plt.plot(df.area**0.5, df.q, 'k.')
        plt.xlabel(r'$\sqrt{A}$ (\si{\micro\metre}')
        plt.ylabel('-ln(1-F)')
    
    return df

def plot_feret(rem_artifacts = True):
    meta, data = get_data()
    if rem_artifacts == True:
        df = data.loc[data.incl_type.apply(lambda x: x not in ['4', '5', '6', '7'])]
    else:
        df = data
    
    df.loc[:, 'ID_specimen'] = df.ID_specimen.apply(lambda x: x.replace('_', ' '))
    fig = plt.figure(dpi=200)
    ax = fig.gca()
    for ech in df.ID_specimen.unique():
        df1 = plot_prob(df.loc[df.ID_specimen == ech])
        ax.plot(df1.feret, df1.q, marker='.', label=ech)
    ax.set_xlabel('Feret diameter (\si{\micro\metre})')
    ax.set_ylabel('Exponential quantiles, $-\ln(1-F)$')
    ax.legend()
    return fig

def plot_sqra(rem_artifacts = True):
    meta, data = get_data()
    if rem_artifacts == True:
        df = data.loc[data.incl_type.apply(lambda x: x not in ['4', '5', '6', '7'])]
    else:
        df = data

    df.loc[:, 'ID_specimen'] = df.ID_specimen.apply(lambda x: x.replace('_', ' '))
    fig = plt.figure(dpi=200)
    ax = fig.gca()
    for ech in df.ID_specimen.unique():
        df1 = plot_prob_sqrsurf(df.loc[df.ID_specimen==ech])
        ax.plot(df1.area**0.5, df1.q, marker='.', label=ech)
    ax.set_xlabel('Equivalent diameter, $\sqrt{A}$ (\si{\micro\metre})')
    ax.set_ylabel('Exponential quantiles, $-\ln(1-F)$')
    ax.legend()
    return fig

def plot_morph(rem_artifacts = True, x = 'feret', y = 'sqr_area', xlabel = 'Feret diameter (\si{\micro\metre})', ylabel ='Equivalent diameter, $\sqrt{A}$ (\si{\micro\metre})'):
    meta, data = get_data()
    
    fig = plt.figure(dpi=200)
    ax = fig.gca()
    
    ax.plot(data.loc[data.incl_type == ''][x], data.loc[data.incl_type==''][y], color='gray', marker = '.', linestyle = 'none', label = 'Unidentified')
    ax.plot(data.loc[data.incl_type == '1'][x], data.loc[data.incl_type=='1'][y], color='black', marker = 'x', linestyle = 'none', label = 'Spherical incl./void')
    ax.plot(data.loc[data.incl_type == '2'][x], data.loc[data.incl_type=='2'][y], color= 'blue', marker = 'o', linestyle = 'none', label = 'Irregular incl.')
    ax.plot(data.loc[data.incl_type == '3'][x], data.loc[data.incl_type=='3'][y], color = 'red', marker = '^' , linestyle = 'none', label = 'Lack of fusion')
    
    if rem_artifacts == False:
        ax.plot(data.loc[data.incl_type == '4'][x], data.loc[data.incl_type=='4'][y], 'ro', label = 'Scratch')
        ax.plot(data.loc[data.incl_type == '5'][x], data.loc[data.incl_type=='5'][y], 'r^', label = 'Dust')
        ax.plot(data.loc[data.incl_type == '6'][x], data.loc[data.incl_type=='6'][y], 'rx', label = 'Other artifact')
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    return fig
    

def plot_dist():
    bins = 10**np.linspace(0, 3, 31)
    x = 10**(np.linspace(0, 3, 31)[:-1]+0.05)
    meta['area_mm2'] = meta.proc_img_width_um*meta.proc_img_height_um/1e6
    A_BD, A_PD = meta.groupby('dir')['area_mm2'].agg('sum')
    y_BD1 = plt.hist(BD1.Feret, bins=bins)[0]/(A_BD/2)
    y_BD2 = plt.hist(BD2.Feret, bins=bins)[0]/(A_BD/2)
    y_PD1 = plt.hist(PD1.Feret, bins=bins)[0]/(A_PD/2)
    y_PD2 = plt.hist(PD2.Feret, bins=bins)[0]/(A_PD/2)
    
    fig = plt.figure(dpi=200)
    ax = fig.gca()
    ax.semilogx(x, y_BD1, label = 'BD, slice 1', marker='.')
    ax.semilogx(x, y_BD2, label = 'BD, slice 2', marker='.')
    ax.semilogx(x, y_PD1, label = 'PD, slice 1', marker='.')
    ax.semilogx(x, y_PD2, label = 'PD, slice 2', marker='.')
    ax.set_xlabel('Feret diameter, (\si{\micro\metre})')
    ax.set_ylabel('Density, \si{\per\milli\metre\squared}')
    ax.legend()
    return fig

def MLE_sig_exp(Y, k):
    """
    Returns Maximum Likelihood Estimate (MLE) of the exponential distribution
    fitted on the data Y. The regression is done using the k highest values
    with the peak-over-threshold method. The threshold is set to the lowest
    value in Y. [Ref. Reiss and Thomas chap. 5]

    Parameters
    ----------
    Y : Vector of values on which to perform regression. Need not to be ordered.
    k : Size of the sample. Scalar or vector.

    Returns
    -------
    sigma_k : MLE estimate of distribution parameter. Returns scalar or vector
              depending of k.

    """
    
    #If k is array, finds each separate element by recursivity
    if type(k) == np.ndarray:
        sigma_k = k*0.
        for i in range(len(k)):
            sigma_k[i] = MLE_sig_exp(Y, k[i])
        return sigma_k
    
    Y = np.sort(Y)[::-1]    #Sorts in descending order
    Y = Y[:k]               #Keeps the k highest
    u = Y[-1]               #Threshold
    
    sigma_k = 0
    for i in range(len(Y)):
        sigma_k += Y[i] - u
    sigma_k = sigma_k / k
    
    return sigma_k
    
    
#Utilities    
def ret_th(x, y, x_c, y_c):
    """
    Returns the azimut of polar coordinates, given cartesian coordinates relative to the origin.

    Parameters
    ----------
    x, y:       Coordinates of the point of interest
    x_c, y_c:   Coordinates of the origin   

    Returns
    -------
    theta :     Azimutal coordinate (theta) of the point (x, y). 0 < theta < 2*pi
    """
    
    #Obtains coordinates relative to the origin
    xprime = x - x_c
    yprime = y - y_c
    
    #Obtains the arctan, between -pi and pi
    theta = np.arctan(yprime/xprime)
    
    #Adjusts theta to fit in the right quadrant
    if (xprime < 0):
        theta = np.pi+theta
    elif yprime < 0:
        theta = 2*np.pi+theta
        
    return theta
    
    
def extract_data_Matteo(excel_sheet, csv_output):
    if excel_sheet[0:3] == 'CB2':
        skip = 10
    else:
        skip = 8
        
    df = pd.read_excel('MA_Analysis_BM_v3.0.xlsx', excel_sheet, skiprows=skip)
    if df.columns[0] == ' ':
        df = df.loc[:, [' ', 'Area', 'X', 'Y', 'Circ.', 'Feret', 'FeretAngle', 'MinFeret', 'AR', 'Round', 'Solidity']]
    else:
        df = df.loc[:, ['ID', 'Area', 'X', 'Y', 'Circ.', 'Feret', 'FeretAngle', 'MinFeret', 'AR', 'Round', 'Solidity']]    
    df.to_csv(csv_output, index=False)