import os
import math
import pandas as pd
import matplotlib.pyplot as plt

# Cargo archivos
folder_path = '/content/drive/MyDrive/OzoneProject'

df_ozono_OMDOAO_3 = pd.read_csv(f'{folder_path}/OZONO/DIARIO/OMDOAO3e_O3_URUGUAY_3.csv')
df_uv_2 = pd.read_csv(f'{folder_path}/UV/DIARIO/OMUVBd_UV_URUGUAY_2.csv')

# Función para asignar pixel
def zona_pixel(lat,lon = 0):
  lat = (math.ceil(abs(lat) - 30) - 1) * 6
  lon = 59 - math.ceil(abs(lon))
  zona = lat + lon

  return zona

# Asignando pixel
df_ozono_OMDOAO_3['zona'] = df_ozono_OMDOAO_3.apply(lambda row: zona_pixel(row['Latitud'], row['Longitud']), axis=1)
df_uv_2['zona'] = df_uv_2.apply(lambda row: zona_pixel(row['Latitud'], row['Longitud']), axis=1)

df_ozono_OMDOAO_3['Key'] = df_ozono_OMDOAO_3['Latitud'].astype(str) + df_ozono_OMDOAO_3['Longitud'].astype(str) + df_ozono_OMDOAO_3['Fecha'].astype(str)

df_final_3 = df_ozono_OMDOAO_3.drop('Key', axis = 1).copy()

df_uv_copy = df_uv_2.copy()
df_uv_copy['zona'] = df_uv_copy['zona'].astype('int64')

df_final_3 = pd.merge(df_final_3, df_uv_copy[['UV','Fecha','zona']], on=['zona','Fecha'], how='left',suffixes=['','_OMUVBd'])

print(df_final_3.head())

print(f"\nShape of the merged DataFrame: {df_final_3.shape}")

# Display columns in the merged dataframe
print("\nColumns in the merged DataFrame:")
print(df_final_3.columns.tolist())

df_final_3.to_csv(f'{folder_path}/BASE_FINAL_3.csv', index= 'False')