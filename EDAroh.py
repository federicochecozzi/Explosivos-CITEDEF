# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 16:45:28 2020

@author: Federico Checozzi
"""

import glob
import pandas as pd
import scipy as sp
import matplotlib.pyplot as plt
import seaborn as sns

#PROCESAMIENTO DE DATOS
files = glob.glob('*.xlsx')
                
spectredata = pd.concat(
                            [pd.read_excel(file, skiprows = list(range(1,6)))
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
                        ).assign(
                            NSpot = lambda df: df.Spot % 3 + 3 * (df.Spot % 3 == 0)#por alguna razón es horriblemente ineficiente
                        ).drop(
                            columns = "Identifier"
                        ).dropna()    

#groups = spectredata.groupby(["Sample","Spot"])

# for name, group in groups:
#     plt.figure()
#     ax = sns.lineplot(data = group, x = "Wavelength", y = "Intensity", hue = "Spectre", legend = False)
#     ax.set_title("Sample: %s, Spot: %d"%name)

groups = spectredata.groupby(["Sample"])

sns.set(font_scale=0.8)
for name, group in groups:
    g = sns.FacetGrid(group, col="NSpot", row="Spectre", margin_titles = True, height = 1, aspect = 5)
    g = g.map(plt.plot,"Wavelength", "Intensity")
    g.savefig("Resultados\\" + name + ".jpg")
sns.set(font_scale=1)