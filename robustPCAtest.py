# -*- coding: utf-8 -*-
"""
Created on Wed May 26 16:20:41 2021

@author: Federico
"""
import glob
#import os
import pandas as pd
import scipy as sp
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import RobustScaler
#from sklearn.preprocessing import LabelEncoder
#from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
import r_pca as r_pca

#PROCESAMIENTO DE DATOS
files = glob.glob('*.xlsx')
#https://stackoverflow.com/questions/65254535/xlrd-biffh-xlrderror-excel-xlsx-file-not-supported
                
spectredata = pd.concat(
                            [pd.read_excel(file, skiprows = list(range(1,6)),engine='openpyxl')
                             .assign(Sample = file.rstrip(".xlsx"))
                             for file in files]
                            , ignore_index = True, sort = True
                        ).rename(
                            columns = {"Filename-->" : "Wavelength"}    
                        ).melt(
                            id_vars=["Sample","Wavelength"], var_name = "Identifier", value_name = "Intensity"    
                        ).assign(
                            Spot = lambda df: pd.to_numeric(df.Identifier.str[4:8]), 
                            Spectre = lambda df: pd.to_numeric(df.Identifier.str[8:12])    
                        #).query(
                            #Longitudes de onda Suelo
                            #"Wavelength > 325 & Wavelength < 770"
                        #    "Wavelength > 490 & Wavelength < 600"
                        ).pivot_table(
                            values = "Intensity", index = ["Sample","Spot","Spectre"], columns = ["Wavelength"]
                        ).dropna()   
                            
spectredataquery = spectredata.query(
#        "Sample == ['MST0209-Suelo10_Zn90','MST0244-Suelo1_TNT99','MST0245-SueloPu']"
        #"Sample == ['MST0209-Suelo10_Zn90']"
        # "Sample == ['MST0148-AlPu','MST0161-AlRDX','MST0162-AlTNT','MST0163-AlPETN']"
        "Sample == ['MST0162-AlTNT']"
)   

spectrematrix = spectredataquery.to_numpy()

#Robust data centering
scaler = RobustScaler(with_centering=True, with_scaling=False)
scaler.fit(spectrematrix)
spectres_centered = scaler.transform(spectrematrix)

# use R_pca to estimate the degraded data as L + S, where L is low rank, and S is sparse
rpca = r_pca.R_pca(spectrematrix)
L, S = rpca.fit(max_iter=10000, iter_print=100)

# visually inspect results (requires matplotlib)
#rpca.plot_fit()
#plt.show()

# principal component analysis on the "cleaned up" signal matrix L to avoid outlier effects when obtaining the components
ncomp = 7
pca=PCA(n_components = ncomp) 
pca.fit(L) #reminder that principal components depend on maximum variance directions, not the absolute coordinates of a data cluster
spectres_pca = pca.transform(spectres_centered)
spectres_variance = pca.singular_values_

#You can do two statistical tests to find outliers once you have the 
#robust principal components, check Hubert et al (2005) for details

#score distance measures how far from the center of the data cluster in the transformed space is a particular measurement
SD = (np.sum(np.divide(spectres_pca ** 2, spectres_variance), axis = 1)) ** (1/2)
cutoffSD = sp.stats.chi2.isf(0.025,ncomp) ** (1/2) # squared root of chi squared, with 7 degrees of freedom and 97.5% quantile cutoff

#orthogonal distance measures PCA's error fit for every measurement
#OD = sp.linalg.norm(S, axis = 1) #orthogonal distance, that's it, the norm of the parts not projected on PCA space
OD = sp.linalg.norm(spectres_centered - pca.inverse_transform(spectres_pca), axis = 1)
cutoffOD = (np.median(OD ** (2/3)) + sp.stats.norm.isf(0.025) * sp.stats.median_abs_deviation(OD ** (2/3))) ** (3/2)

#add new columns to the dataframe
#spectredataquery["Orthogonal distance"] = OD
#spectredataquery["Score distance"] = SD
spectredataquery["Outlier"] = pd.Categorical(np.logical_or(OD > cutoffOD, SD > cutoffSD))

#shape the dataframe so it's appropiated to use with FacetGrid
#spectredatareshaped = spectredataquery.reset_index().assign(
#                                NSpot = lambda df: df.Spot % 3 + 3 * (df.Spot % 3 == 0)
#                            ).drop(
#                                columns = ["Sample","NSpot"]
#                            ).melt(
#                                id_vars=["Spectre","Spot","Outlier"], var_name = "Wavelength", value_name = "Intensity"    
#                            )

spectredatareshaped = spectredataquery.reset_index().drop(
                                columns = ["Sample"]
                            ).melt(
                                id_vars=["Spectre","Spot","Outlier"], var_name = "Wavelength", value_name = "Intensity"    
                            )

#graphs spectra, outliers have different hue
sns.set(font_scale=0.8)
g = sns.FacetGrid(spectredatareshaped, col="Spot", row="Spectre", hue="Outlier", margin_titles = True, height = 1, aspect = 5)
g = g.map(plt.plot,"Wavelength", "Intensity")
#g.savefig("Resultados\\" + name + ".jpg")
sns.set(font_scale=1)