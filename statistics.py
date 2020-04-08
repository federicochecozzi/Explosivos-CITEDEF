# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 12:06:52 2020

@author: Federico
"""

import glob
import pandas as pd
import scipy as sp
from scipy.stats import iqr
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
                        ).drop(
                             columns = "Identifier"
                        ).dropna()
                            
spectredataquery = spectredata.query(
    #   "Sample == ['MST0019-ZnPu','MST0164-ZnPETN','MST0165-ZnRDX','MST0166-ZnTNT']"
        # "(Sample == 'MST0019-ZnPu' & (Spectre != 1 | (Spectre == 1 & Spot == 1) ) ) | " + 
        # "(Sample == 'MST0164-ZnPETN' & (Spectre != [1 , 2] | (Spectre == 2 & Spot != 10) | (Spectre == 1 & Spot != [11 , 10] ) ) ) | " +
        # "(Sample == 'MST0165-ZnRDX' & Spot != 5 &  (Spectre != 1 | (Spectre == 1 & Spot != 6) ) ) | " +
        # "(Sample == 'MST0166-ZnTNT' & Spectre != [1 , 2] )"
#        "Sample == ['MST0148-AlPu','MST0161-AlRDX','MST0162-AlTNT','MST0163-AlPETN']"
        "Spectre != 1 & (Sample == ['MST0161-AlRDX','MST0162-AlTNT','MST0163-AlPETN'] | " +
        "(Sample == 'MST0148-AlPu' & (Spectre != 2 | (Spectre == 2 & Spot != 15) ) ) )"
   #          "Sample == ['MST0209-Suelo10_Zn90','MST0244-Suelo1_TNT99','MST0245-SueloPu']"
             # "(Sample == 'MST0209-Suelo10_Zn90' & (Spectre != 1 | (Spectre == 1 & Spot != 27) ) ) | " +
             # "(Sample == 'MST0244-Suelo1_TNT99' & (Spectre != 1 | (Spectre == 1 & Spot != 31) ) ) | " +
             # "(Sample == 'MST0245-SueloPu' & (Spectre != 1 | (Spectre == 1 & Spot != 30) ) )"
    ).drop(
        columns = ["Spot","Spectre"]
    )
                            
groups = spectredataquery.groupby(["Sample","Wavelength"])

spectrestats = groups.agg( [ sp.median , lambda s : sp.median(s) - sp.stats.iqr(s) , lambda s : sp.median(s) + sp.stats.iqr(s) ] )

spectrestats.columns = ["Median","Median - IQR","Median + IQR"]

spectrestats = spectrestats.reset_index().melt(id_vars=["Sample","Wavelength"], var_name = "Statistic", value_name = "Value" )

palette = ['black'  , 'red' , 'red']

samplegroup = spectrestats.groupby("Sample")
for name, group in samplegroup:
    plt.figure()
    sns.lineplot(
                    data = group, x = "Wavelength", y = "Value", hue = "Statistic", palette = palette
                ).set_title(
                    "Sample = %s"%name    
                )

#implementación en un sólo gráfico, creo que es muy pequeño para un archivo,
#pero conveniente para trabajar con %matplotlib auto
# g = sns.FacetGrid(spectrestats, col="Sample", col_wrap = 2)#, margin_titles = True, height = 1, aspect = 5)
# g = g.map(sns.lineplot, "Wavelength", "Value", "Statistic", palette = palette)