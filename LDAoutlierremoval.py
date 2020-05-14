# -*- coding: utf-8 -*-
"""
Created on Tue May 12 15:41:13 2020

@author: Federico
"""


import glob
#import os
import pandas as pd
import scipy as sp
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
#from sklearn.model_selection import train_test_split
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
                            Spot = lambda df: pd.to_numeric(df.Identifier.str[4:8]), Spectre = lambda df: pd.to_numeric(df.Identifier.str[8:12])    
                        ).query(
                            #Longitudes de onda Suelo
                            #"Wavelength > 325 & Wavelength < 770"
                            "Wavelength > 490 & Wavelength < 600"
                        ).pivot_table(
                            values = "Intensity", index = ["Sample","Spot","Spectre"], columns = ["Wavelength"]
                        ).dropna()    


spectredataquery = spectredata.query(
#        "Sample == ['MST0209-Suelo10_Zn90','MST0244-Suelo1_TNT99','MST0245-SueloPu']"
        "(Sample == 'MST0209-Suelo10_Zn90' & (Spectre != 1 | (Spectre == 1 & Spot != 27) ) ) | " +
        "(Sample == 'MST0244-Suelo1_TNT99' & (Spectre != 1 | (Spectre == 1 & Spot != 31) ) ) | " +
        "(Sample == 'MST0245-SueloPu' & (Spectre != 1 | (Spectre == 1 & Spot != 30) ) )"       
)                           

#normalizamos los datos
# scaler=StandardScaler()
# scaler.fit(spectredataquery)
# spectres_scaled=scaler.transform(spectredataquery)

#generación de etiquetas de clase numéricas para cargar en el LDA
classstring = spectredataquery.reset_index(level = 0).Sample
le = LabelEncoder()
classcode = le.fit_transform(classstring)

#separación entre entrenamiento y muestras de prueba
#X_train, X_test, y_train, y_test = train_test_split(spectres_scaled, classcode, test_size=0.2, random_state=0) 
    
#LDA
lda=LDA(n_components=2)#ajustar dependiendo del número de grupos (n_components = ngrupos - 1) 
#lda.fit(X_train,y_train)
#Xlda_train=lda.transform(X_train)
lda.fit(spectredataquery,classcode)
spectres_lda=lda.transform(spectredataquery)
score = 100*lda.score(spectredataquery,classcode)
# lda.fit(spectres_scaled,classcode)
# spectres_lda=lda.transform(spectres_scaled)
# score = 100*lda.score(spectres_scaled,classcode)

#Por desgracia scikit devuelve arrays, así que creo un dataframe con los resultados del PCA y los índices de los datos originales
#df_lda =  pd.DataFrame(data = Xlda_train, columns=["LDA" + str(i) for i in range(1,4)])
df_lda =  pd.DataFrame(data = spectres_lda, columns=["LDA" + str(i) for i in range(1,3)])#ajustar por número de grupos
df_lda.index = spectredataquery.index

df2 = df_lda.reset_index() #esta línea convierte uno de los índices en una columna porque mucho código funciona más fácil así

mask = (df2["Sample"] == "MST0209-Suelo10_Zn90") | ((df2["Sample"] == "MST0244-Suelo1_TNT99") & (df2["LDA2"] < 0.2)) | ((df2["Sample"] == "MST0245-SueloPu") & (df2["LDA2"] > 0.2))
df3 = df2[mask]

#GRÁFICOS
ldapalette = ['blue'  , 'orange' , 'red' , 'green']
ldamarkers = ['o' , '^' , 's' , 'v']
#sólo necesito tres elementos si trabajo con suelo
ldapalette = ldapalette[0:3]
ldamarkers = ldamarkers[0:3]

ax = sns.scatterplot(data = df3, x = "LDA1", y = "LDA2", hue = 'Sample', palette = ldapalette, style = 'Sample', markers = ldamarkers)
ax.set_title("LDA archivos .spc, precisión = %2.2f %%"%score)
ax.set_xlabel("LDA1")
ax.set_ylabel("LDA2")

#parte 2: LDA sin los outliers detectados en LDA
spectredata2 = ((spectredataquery.reset_index())[mask]).set_index(["Sample", "Spot", "Spectre"])

classstring2 = spectredata2.reset_index(level = 0).Sample
classcode2 = le.fit_transform(classstring2)

lda2=LDA(n_components=2)#ajustar dependiendo del número de grupos (n_components = ngrupos - 1) 
#lda.fit(X_train,y_train)
#Xlda_train=lda.transform(X_train)
lda2.fit(spectredata2,classcode2)
spectres_lda2=lda2.transform(spectredata2)
score2 = 100*lda2.score(spectredata2,classcode2)

df_lda2 =  pd.DataFrame(data = spectres_lda2, columns=["LDA" + str(i) for i in range(1,3)])#ajustar por número de grupos
df_lda2.index = spectredata2.index

df4 = df_lda2.reset_index()

ax = sns.scatterplot(data = df4, x = "LDA1", y = "LDA2", hue = 'Sample', palette = ldapalette, style = 'Sample', markers = ldamarkers)
ax.set_title("LDA archivos .spc, precisión = %2.2f %%"%score2)
ax.set_xlabel("LDA1")
ax.set_ylabel("LDA2")