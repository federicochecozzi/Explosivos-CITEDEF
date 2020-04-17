# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 14:41:27 2020

@author: Federico Checozzi
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
                            #La primera línea es la región no nula, la segunda es una región hipotetizada como de interés
                            #Longitudes de onda Zn
                            #"Wavelength > 325 & Wavelength < 645"
                            #"Wavelength > 530 & Wavelength < 630"
                            #"Wavelength > 460 & Wavelength < 630"
                            #Longitudes de onda Al
                            #"Wavelength > 305 & Wavelength < 710"
                            #"Wavelength > 435 & Wavelength < 710"
                            #"Wavelength > 435 & Wavelength < 650"
                            #Longitudes de onda Suelo
                            "Wavelength > 325 & Wavelength < 770"
                            #"Wavelength > 490 & Wavelength < 600"
                        ).pivot_table(
                            values = "Intensity", index = ["Sample","Spot","Spectre"], columns = ["Wavelength"]
                        ).dropna()    

# spectredataquery = spectredata.query(
#       # "Sample == ['MST0019-ZnPu','MST0164-ZnPETN','MST0165-ZnRDX','MST0166-ZnTNT']"
#         "(Sample == 'MST0019-ZnPu' & (Spectre != 1 | (Spectre == 1 & Spot == 1) ) ) | " + 
#         "(Sample == 'MST0164-ZnPETN' & (Spectre != [1 , 2] | (Spectre == 2 & Spot != 10) | (Spectre == 1 & Spot != [11 , 10] ) ) ) | " +
#         "(Sample == 'MST0165-ZnRDX' & Spot != 5 &  (Spectre != 1 | (Spectre == 1 & Spot != 6) ) ) | " +
#         "(Sample == 'MST0166-ZnTNT' & Spectre != [1 , 2] )"
#     )
# spectredataquery = spectredata.query(
#       # "Sample == ['MST0148-AlPu','MST0161-AlRDX','MST0162-AlTNT','MST0163-AlPETN']"
#       "Spectre != 1 & (Sample == ['MST0161-AlRDX','MST0162-AlTNT','MST0163-AlPETN'] | " +
#       "(Sample == 'MST0148-AlPu' & (Spectre != 2 | (Spectre == 2 & Spot != 15) ) ) )"    
#     )
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

#GRÁFICOS
ldapalette = ['blue'  , 'orange' , 'red' , 'green']
ldamarkers = ['o' , '^' , 's' , 'v']
#sólo necesito tres elementos si trabajo con suelo
ldapalette = ldapalette[0:3]
ldamarkers = ldamarkers[0:3]

df2 = df_lda.reset_index(level = 0) #esta línea convierte uno de los índices en una columna porque mucho código funciona más fácil así
ax = sns.scatterplot(data = df2, x = "LDA1", y = "LDA2", hue = 'Sample', palette = ldapalette, style = 'Sample', markers = ldamarkers)
ax.set_title("LDA archivos .spc, precisión = %2.2f %%"%score)
ax.set_xlabel("LDA1")
ax.set_ylabel("LDA2")

#nx, ny = 200, 100
#x_min, x_max = plt.xlim()
#y_min, y_max = plt.ylim()
#xx, yy = sp.meshgrid(sp.linspace(x_min, x_max, nx),
#                     sp.linspace(y_min, y_max, ny))
#Z = lda.predict_proba(sp.c_[xx.ravel(), yy.ravel()])#conceptualmente equivocado
#Z = Z[:, 1].reshape(xx.shape)