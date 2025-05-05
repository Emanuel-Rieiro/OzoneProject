# Archivo usado para cargar y compilar las bases de datos en formato nc4 descargadas de giovanni con el fin de procesar datos del Ozono en Uruguay
import os
import numpy as np
import pandas as pd
from netCDF4 import Dataset

def main():

    # Archivos en el directorio
    onlyfiles = [f for f in os.listdir(os.getcwd()) if os.path.isfile(os.path.join(os.getcwd(), f))]
    
    # Variable del tipo DataFrame en el cual vamos a ir dejando la data
    df_final = pd.DataFrame()

    for filename in onlyfiles:
        # Filtro para solo procesar los archivos descargados
        if filename.split('.')[0][:5] == 'MERRA':
            
            # Cargamos archivo
            nc_data = Dataset(os.path.join(os.getcwd(), filename), 'r')

            # Instanciamos variables
            lon = nc_data.variables['lon'][:]
            lat = nc_data.variables['lat'][:]
            ozone = nc_data.variables['TO3'][0, :, :]

            # Establecemos los límites de los cuales queremos extraer datos (este límite es uruguay)
            lon_min, lon_max = -58.5, -53.0
            lat_min, lat_max = -35.1, -30.1

            # Indices de latitud y longitud de uruguay en la base de datos
            lon_idx = np.where((lon >= lon_min) & (lon <= lon_max))[0]
            lat_idx = np.where((lat >= lat_min) & (lat <= lat_max))[0]
            
            # Loop para obtener la data de manera ordenada
            X = []
            for l_lat in lat_idx:
                for l_lon in lon_idx:
                    x = []
                    x.append(lat[l_lat])
                    x.append(lon[l_lon])
                    x.append(ozone[l_lat,l_lon])
                    X.append(x)

            X = np.asarray(X)

            # Creación del dataframe con la data
            df = pd.DataFrame(X, columns = ['Latitud', 'Longitud', 'Ozono'])
            fecha = filename.split('.')[2]
            df['Fecha'] = fecha

            df_final = pd.concat([df_final, df])

    # Guardamos nuestro archivo final
    df_final.to_excel('MERRA2_M2TMNXSLV_O3_URUGUAY.xlsx', index = False)


if __name__ == "__main__":
    main()