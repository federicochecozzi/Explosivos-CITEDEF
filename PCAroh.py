# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 16:36:05 2020

@author: Federico Checozzi
"""

import glob
#import os
import pandas as pd
#import scipy as sp
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
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
                        ).query(
                            #Longitudes de onda Zn
                            #"Wavelength > 325 & Wavelength < 645"
                            #"Wavelength > 530 & Wavelength < 630"
                            #Longitudes de onda Al
                            #"Wavelength > 305 & Wavelength < 710"
                            #"Wavelength > 435 & Wavelength < 710"
                            #Longitudes de onda Suelo
                            #"Wavelength > 325 & Wavelength < 770"
                            "Wavelength > 490 & Wavelength < 600"
                        ).pivot_table(
                            values = "Intensity", index = ["Sample","Spot","Spectre"], columns = ["Wavelength"]
                        ).dropna()    

#spectredataquery = spectredata.query(
#         "Sample == ['MST0019-ZnPu','MST0164-ZnPETN','MST0165-ZnRDX','MST0166-ZnTNT']"
     #     "(Sample == 'MST0019-ZnPu' & (Spectre != 1 | (Spectre == 1 & Spot == 1) ) ) | " + 
     #     "(Sample == 'MST0164-ZnPETN' & (Spectre != [1 , 2] | (Spectre == 2 & Spot != 10) | (Spectre == 1 & Spot != [11 , 10] ) ) ) | " +
     #     "(Sample == 'MST0165-ZnRDX' & Spot != 5 &  (Spectre != 1 | (Spectre == 1 & Spot != 6) ) ) | " +
     #     "(Sample == 'MST0166-ZnTNT' & Spectre != [1 , 2] )"
     # )
#spectredataquery = spectredata.query(
#       "Sample == ['MST0148-AlPu','MST0161-AlRDX','MST0162-AlTNT','MST0163-AlPETN']"
#       "Spectre != 1 & (Sample == ['MST0161-AlRDX','MST0162-AlTNT','MST0163-AlPETN'] | " +
#       "(Sample == 'MST0148-AlPu' & (Spectre != 2 | (Spectre == 2 & Spot != 15) ) ) )"    
#    )
spectredataquery = spectredata.query(
#          "Sample == ['MST0209-Suelo10_Zn90','MST0244-Suelo1_TNT99','MST0245-SueloPu']"
             "(Sample == 'MST0209-Suelo10_Zn90' & (Spectre != 1 | (Spectre == 1 & Spot != 27) ) ) | " +
             "(Sample == 'MST0244-Suelo1_TNT99' & (Spectre != 1 | (Spectre == 1 & Spot != 31) ) ) | " +
             "(Sample == 'MST0245-SueloPu' & (Spectre != 1 | (Spectre == 1 & Spot != 30) ) )"       
      )                            
                            
#normalizamos los datos
# scaler=StandardScaler()
# scaler.fit(spectredataquery)
# spectres_scaled=scaler.transform(spectredataquery)
     
#Instanciamos objeto PCA y aplicamos
pca=PCA(n_components=7) 
# pca.fit(spectres_scaled)
# spectres_pca=pca.transform(spectres_scaled) # convertimos nuestros datos con las nuevas dimensiones de PCA
pca.fit(spectredataquery)
spectres_pca=pca.transform(spectredataquery)

#Por desgracia scikit devuelve arrays, así que creo un dataframe con los resultados del PCA y los índices de los datos originales
df_pca =  pd.DataFrame(data = spectres_pca, columns=["PCA" + str(i) for i in range(1,8)])
df_pca.index = spectredataquery.index

#GRÁFICOS

explained = 100 * pca.explained_variance_ratio_

pcapalette = ['blue'  , 'orange' , 'red' , 'green']
pcamarkers = ['o' , '^' , 's' , 'v']
#cambiar dependiendo del número de grupos
pcapalette = pcapalette[0:3]
pcamarkers = pcamarkers[0:3]

df2 = df_pca.reset_index(level = 0) #esta línea convierte uno de los índices en una columna porque mucho código funciona más fácil así
ax = sns.scatterplot(data = df2, x = "PCA1", y = "PCA2", hue = 'Sample', palette = pcapalette, style = 'Sample', markers = pcamarkers)
ax.set_title("PCA archivos .spc")
ax.set_xlabel("PCA1 %2.2f %%"%explained[0])
ax.set_ylabel("PCA2 %2.2f %%"%explained[1])