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
            
            print(filename)
            # Cargamos la data y la ponemos en variables
            with h5py.File(filename, "r") as file:
                uv_data = file["HDFEOS/GRIDS/OMI UVB Product/Data Fields/UVindex"][:]

            # Create latitude and longitude grids
            lons = np.linspace(-180, 180, uv_data.shape[1]).round(3)  # Longitudes
            lats = np.linspace(-90, 90, uv_data.shape[0]).round(3)    # Latitudes

            lon_min, lon_max = -58.7, -53.0
            lat_min, lat_max = -35.1, -30.1

            lon_idx = np.where((lons >= lon_min) & (lons <= lon_max))[0]
            lat_idx = np.where((lats >= lat_min) & (lats <= lat_max))[0]

            # Loop para obtener la data de manera ordenada
            X = []
            
            for l_lat in lat_idx:
                for l_lon in lon_idx:
                    x = []
                    x.append(lats[l_lat])
                    x.append(lons[l_lon])
                    x.append(uv_data[l_lat,l_lon])
                    X.append(x)
                    
            X = np.asarray(X)

            # Creación del dataframe con la data
            df = pd.DataFrame(X, columns = ['Latitud', 'Longitud', 'UV'])
            fecha = filename.split('_')[2].replace('m','')
            df['Fecha'] = fecha

            df_final = pd.concat([df_final, df])

    # Guardamos nuestro archivo final
    df_final.to_csv('OMUVBd_UV_URUGUAY.csv', index = False)


if __name__ == "__main__":
    main()