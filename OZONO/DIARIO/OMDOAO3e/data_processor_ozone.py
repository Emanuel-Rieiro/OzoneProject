# Archivo usado para cargar y compilar las bases de datos en formato nc4 descargadas de giovanni con el fin de procesar datos del Ozono en Uruguay
import os
import numpy as np
import pandas as pd
import h5py

def main():

    # Archivos en el directorio
    onlyfiles = [f for f in os.listdir(os.getcwd()) if os.path.isfile(os.path.join(os.getcwd(), f))]
    
    # Variable del tipo DataFrame en el cual vamos a ir dejando la data
    df_final = pd.DataFrame()

    for filename in onlyfiles:
        # Filtro para solo procesar los archivos descargados
        if filename.split('-')[0] == 'OMI':
            
            with h5py.File(filename, "r") as file:
                ozone = file["HDFEOS/GRIDS/ColumnAmountO3/Data Fields/ColumnAmountO3"][:]

            lon = np.linspace(-180, 180, ozone.shape[1]).round(3)  # Longitudes
            lat = np.linspace(-90, 90, ozone.shape[0]).round(3)    # Latitudes

            lon_min, lon_max = -58.5, -53.0
            lat_min, lat_max = -35.1, -30.1

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
            fecha = filename.split('_')[2].replace('m','')
            df['Fecha'] = fecha

            df_final = pd.concat([df_final, df])

    # Guardamos nuestro archivo final
    df_final.to_csv('OMDOAO3e_O3_URUGUAY.csv', index = False)


if __name__ == "__main__":
    main()