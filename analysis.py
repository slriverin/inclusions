# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import math
from matplotlib import rc

from scipy.optimize import curve_fit, fsolve
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
from matplotlib.ticker import FormatStrFormatter
#%config InlineBackend.figure_formats = {'png', 'eps', 'retina'}
#%matplotlib inline
#plt.ion()
rc('font',**{'family':'serif','serif':['DejaVu Sans']})
rc('text', usetex=True)
mpl.rcParams['errorbar.capsize']=3
mpl.rcParams['lines.markersize'] = 5
mpl.rcParams['text.latex.preamble']=r'\usepackage{siunitx}'
import os, sys

fields_data = ['ID_specimen', 'slice', 'incl_nb', 'x', 'y', 'area', 
               'sqr_area', 'feret', 'min_feret', 'feret_angle', 'circ', 
               'round', 'ar', 'solid', 'incl_type', 'r', 'theta', 'division']
fields_meta = ['ID_specimen', 'slice', 'filename', 'img_width', 'img_height',
               'img_area_mm2', 'x_c', 'y_c', 'r_outer', 'n_divis_x', 'n_divis_y', 'divis_area_mm2']


#Basic I/O functions
def get_data():
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
    try:
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
            
        data = data.sort_values(['ID_specimen', 'slice', 'incl_nb'])\
            .reset_index(drop=True)
        
        meta.loc[:, fields_meta].to_hdf('db_incl.h5', 'meta')
        data.loc[:, fields_data].to_hdf('db_incl.h5', 'data')
    
    except:
        print('Error writing data. Verify datasets.')


#Data entry functions
def new_image():
    print('Which specimen ID? Enter sequential number. <0> for new specimen.')
    print('Other entry does nothing.')
    print('Seq. nb\tID_specimen')
    meta, data = get_data()
    specs = meta.ID_specimen.unique()
    for i in range(len(specs)):
        print('{:d}\t{:s}'.format(i+1, specs[i]))
    try:
        ans = input('...: [0] ')
        if ans == '':
            i_spec = 0
        else:
            i_spec = int(ans)
            
        if i_spec == 0:
            ID_spec = input('New sample ID? ...: ')
            if ID_spec == '':
                print('Invalid name')
                return
        elif i_spec > len(specs):
            print('No such sample')
            return 
        else:
            ID_spec = specs[i_spec-1]
    except ValueError:
        return

    try:
        
        slice_def = len(meta.loc[meta.ID_specimen==ID_spec, 'slice'])+1
        ans = input('Which slice? ...: [{:d}] '.format(slice_def))
        
        if ans == '':
            slice = slice_def
        else:
            slice = int(ans)
            
    except ValueError:
        print('Must enter integer')
        return
    
    print('Which filename? Enter sequential number.')
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
            
    try:
        print('If sample circular, type width = 0')
        img_width = float(input('Image width (microns) ...: '))
        if int(img_width) == 0:
            img_r1 = float(input('Outer radius (microns) ...: '))
            img_r2 = float(input('Inner radius (microns) ...: '))
            img_area = np.pi*(img_r1**2 - img_r2**2)/1e6
            img_height = (img_area/np.pi)**0.5*1000
        else:
            img_height = float(input('Image height (microns) ...: '))
            img_area = img_width*img_height/1e6
    except ValueError:
        print('Numerical value needed')
        return
    
    try:
        df_data = pd.read_csv(filename)
        df_data = df_data.rename(columns={' ': 'incl_nb', 'X': 'x', 'Y': 'y',
                    'Area': 'area', 'Feret': 'feret', 'MinFeret': 'min_feret',
                    'FeretAngle': 'feret_angle', 'Circ.': 'circ', 'AR': 'ar',
                    'Round': 'round', 'Solidity': 'solid'}, errors='raise')
        df_data = df_data.loc[df_data.incl_nb.notnull()]
        df_data['sqr_area'] = df_data.area**0.5
        df_data['ID_specimen'] = ID_spec
        df_data['slice'] = slice
        df_data['incl_type'] = ''
        df_data = df_data.loc[:, fields_data]
    except (KeyError, AttributeError):
        print('Error reading .csv file')
        return
        
    data = data.loc[(data.ID_specimen != ID_spec)|(data.slice != slice)]
    data = pd.concat([data, df_data])
    
    meta = meta.loc[(meta.ID_specimen != ID_spec)|(meta.slice != slice)]
    meta = meta.append({'ID_specimen': ID_spec, 'slice': slice, 
                        'filename': filename, 'img_width': img_width,
                        'img_height': img_height, 'img_area_mm2': img_area}, 
                       ignore_index=True)
 
    save_data(meta, data)


def def_pol_coord():
    print('Which specimen ID? Enter sequential number. <0> for new specimen.')
    print('Other entry does nothing.')
    print('Seq. nb\tID_specimen')
    meta, data = get_data()
    specs = meta.loc[meta.img_width.apply(lambda x: int(x))==0].ID_specimen.unique()
    
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
        
    ser_meta = meta.loc[(meta.ID_specimen==ID_spec)&(meta.slice==slice)].iloc[0]
    df = data.loc[(data.ID_specimen==ID_spec)&(data.slice==slice), data.columns]
    
    if math.isnan(ser_meta.x_c) or math.isnan(ser_meta.y_c) or math.isnan(ser_meta.r_outer):
        print('No center defined. Default values will be inferred from data.')
        x_c = df.x.mean()
        y_c = df.y.mean()
        r_outer = 6500
    else:
        x_c = ser_meta.x_c
        y_c = ser_meta.y_c
        r_outer = ser_meta.r_outer
    
    ok = False
    
    while ok == False:
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
            ok = True
            
        elif ans == '2':
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
            return
        
    df.loc[:, 'r'] = ((df.x - x_c)**2 + (df.y - y_c)**2)**0.5
    df.loc[:, 'theta'] = df.apply(lambda row: ret_th(row.x, row.y, x_c, y_c), axis=1)
    
    x_c = (df.loc[df.r < r_outer].x.max() + df.loc[df.r < r_outer].x.min())/2
    y_c = (df.loc[df.r < r_outer].y.max() + df.loc[df.r < r_outer].y.min())/2
    
    df.loc[:, 'r'] = ((df.x - x_c)**2 + (df.y - y_c)**2)**0.5
    df.loc[:, 'theta'] = df.apply(lambda row: ret_th(row.x, row.y, x_c, y_c), axis=1)
    r_outer = df.loc[df.r < r_outer].r.max()
    
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
        df.loc[df.r > r_outer, 'incl_type'] = '7'
        data.update(df)
        meta.loc[(meta.ID_specimen==ID_spec)&(meta.slice==slice), 'x_c'] = x_c
        meta.loc[(meta.ID_specimen==ID_spec)&(meta.slice==slice), 'y_c'] = y_c
        meta.loc[(meta.ID_specimen==ID_spec)&(meta.slice==slice), 'r_outer'] = r_outer
        save_data(meta, data)

       
def ID_incl():
    print('What mode? <1>: Largest ones (Area); <2>: Largest ones (Feret); <3>: Specific inclusion; <4>: By location, <5>: Review entries.')
    
    try:
        ans = input('[1]...: ')
        if ans == '':
            ans = 1
        
        mode = int(ans)
        
    except ValueError:
        return
    
    if mode == 1 or mode == 2:
        if mode == 1:
            colsort = 'area'
        elif mode ==2:
            colsort = 'feret'
            
        print('Which specimen ID? Enter sequential number. <0> for all specimens. ')
        print('Seq. nb\tID_specimen\tNb. of slices')
        meta, data = get_data()
        specs = meta.ID_specimen.unique()
        for i in range(len(specs)):
            print('{:d}\t\t{:s}\t\t{:d}'.format(i+1, specs[i], data.loc[data.ID_specimen==specs[i]].slice.max()))
            
        try:
            i_spec = int(input('...: '))
                
            if i_spec == 0:
                ID_spec = -1
            elif i_spec > len(specs):
                print('No such sample')
                return 
            else:
                ID_spec = specs[i_spec-1]
        except ValueError:
            return
    
        try:
            
            ans = input('Which slice? <0> for all slices...: ')
            
            if ans == '':
                slice = slice_def
            else:
                slice = int(ans)
                
        except ValueError:
            print('Must enter integer')
            return
            
        if ID_spec == -1:
            df = data
        elif slice == 0:
            df = data.loc[data.ID_specimen == ID_spec]
        else:
            df = data.loc[(data.ID_specimen == ID_spec) & (data.slice == slice)]
        
        df = df.loc[df.incl_type == '']
        cont = True
        while cont == True:
            df = df.sort_values(by=colsort, ascending = False)
            index_incl = df.index[0]
            print('For defect... :')
            print(df.head(1))
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
                data.loc[index_incl, 'incl_type'] = ans
                save_data(meta, data)
                df = df.iloc[1:]
                
            elif ans == '':
                df = df.iloc[1:]
            else:
                cont=False
                return


def divide():
    meta, data = get_data()
    
    print('Choose specimen... enter sequential number')
    print('Average dimensions, millimeters')
    print('\nRectangular specimens')
    print('\tSpec.\tWidth\tHeight\tArea\tDivisions\tArea per division')
    df = meta.loc[meta.img_width > 1, meta.columns].groupby('ID_specimen').agg('mean')
    
    i = 1
    dict_index = {}
    
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
    df = meta.loc[meta.img_width.apply(lambda x: int(x)==0), meta.columns].groupby('ID_specimen').agg('mean')
    for index, row in df.iterrows():
        if row.n_divis_x == 0:
            area_per_div = 0
        else:
            area_per_div = row.img_area_mm2/row.n_divis_x
        print('{:d}\t{:s}\t{:.2f}\t\t{:.2f}\t{:.0f}\t\t{:.2f}'.format(i, index, row.img_height/1000, row.img_area_mm2, 
                row.n_divis_x, area_per_div))
        dict_index[i] = index
        i += 1
        
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
            div_coord_x = x//div_width
            div_coord_y = y//div_height
            return div_coord_x + 1 + div_coord_y*3


        n_divis_x = int(input('Divisions in x ... : '))
        n_divis_y = int(input('Divisions in y ... : '))
        if n_divis_x < 1 or n_divis_y < 1:
            raise ValueError
        
        df =  meta.loc[meta.ID_specimen == spec, meta.columns]
        df.loc[:, 'n_divis_x'] = n_divis_x
        df.loc[:, 'n_divis_y'] = n_divis_y
        df.loc[:, 'divis_area_mm2'] = df.img_area_mm2/(df.n_divis_x*df.n_divis_y)
        
        df2 = data.loc[data.ID_specimen == spec, data.columns]
        df2 = df2.merge(df2.groupby(['ID_specimen', 'slice'])['x', 'y'].transform('min').rename(columns={'x': 'x_min', 'y': 'y_min'}), 
                        on = ['ID_specimen', 'slice'])
        df2 = df2.merge(df.loc[:, ['ID_specimen', 'slice', 'n_divis_x', 'n_divis_y', 'img_width', 'img_height']], on=['ID_specimen', 'slice'])
        df2['div_width'] = df2.img_width/n_divis_x
        df2['div_height'] = df2.img_height/n_divis_y
        
        df2.division = df2.apply(lambda row: get_div_rect(row.x-row.x_min, row.y-row.y_min, row.div_width, row.div_height, row.n_divis_x), axis=1)

        meta.update(df)
        data.update(df2)
        
        return meta, data
        
        
    
    
#Analysis tools
def print_stats():
    meta, data = get_data()
    print('List of specimens studied')
    print('Spec.\tNb. of slices\tTotal area (mm^2)')
    for index, row in meta.groupby('ID_specimen')\
        .agg({'slice': 'nunique', 'img_area_mm2': 'sum'}).iterrows():
            print('{:s}\t{:d}\t\t{:.1f}'.format(index, int(row.slice), 
                                              row.img_area_mm2))
    print('\nStats per image file')
    df1 = data.groupby(['ID_specimen', 'slice'])\
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