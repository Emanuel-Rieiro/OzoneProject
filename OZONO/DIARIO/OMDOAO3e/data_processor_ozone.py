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
                ozone_precision = file["HDFEOS/GRIDS/ColumnAmountO3/Data Fields/ColumnAmountO3Precision"][:]
                
                cf = file["HDFEOS/GRIDS/ColumnAmountO3/Data Fields/CloudFraction"][:]
                cf_precision = file["HDFEOS/GRIDS/ColumnAmountO3/Data Fields/CloudFractionPrecision"][:]
                
                cp = file["HDFEOS/GRIDS/ColumnAmountO3/Data Fields/CloudPressure"][:]
                cp_precision = file["HDFEOS/GRIDS/ColumnAmountO3/Data Fields/CloudPressurePrecision"][:]

                et = file["HDFEOS/GRIDS/ColumnAmountO3/Data Fields/EffectiveTemperature"][:]
                et_precision = file["HDFEOS/GRIDS/ColumnAmountO3/Data Fields/EffectiveTemperaturePrecision"][:]

                gc = file["HDFEOS/GRIDS/ColumnAmountO3/Data Fields/GhostColumnAmountO3"][:]
                sza = file["HDFEOS/GRIDS/ColumnAmountO3/Data Fields/SolarZenithAngle"][:]
                th = file["HDFEOS/GRIDS/ColumnAmountO3/Data Fields/TerrainHeight"][:]
                tr = file["HDFEOS/GRIDS/ColumnAmountO3/Data Fields/TerrainReflectivity"][:]
                vza = file["HDFEOS/GRIDS/ColumnAmountO3/Data Fields/ViewingZenithAngle"][:]

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
                    x.append(ozone_precision[l_lat,l_lon])
                    x.append(cf[l_lat,l_lon])
                    x.append(cf_precision[l_lat,l_lon])
                    x.append(cp[l_lat,l_lon])
                    x.append(cp_precision[l_lat,l_lon])
                    x.append(et[l_lat,l_lon])
                    x.append(et_precision[l_lat,l_lon])

                    x.append(gc[l_lat,l_lon])
                    x.append(sza[l_lat,l_lon])
                    x.append(th[l_lat,l_lon])
                    x.append(tr[l_lat,l_lon])
                    x.append(vza[l_lat,l_lon])
                    X.append(x)

            X = np.asarray(X)

            # Creación del dataframe con la data
            df = pd.DataFrame(X, columns = ['Latitud', 
                                'Longitud', 
                                'ColumnAmountO3',
                                'ColumnAmountO3Precision',
                                'CloudFraction',
                                'CloudFractionPrecision',
                                'CloudPressure',
                                'CloudPressure_Precision',
                                'EffectiveTemperature',
                                'EffectiveTemperaturePrecision',
                                'GhostColumnAmountO3',
                                'SolarZenithAngle',
                                'TerrainHeight',
                                'TerrainReflectivity',
                                'ViewingZenithAngle'])
            fecha = filename.split('_')[2].replace('m','')
            df['Fecha'] = fecha

            df_final = pd.concat([df_final, df])

    # Guardamos nuestro archivo final
    df_final.to_csv('OMDOAO3e_O3_URUGUAY_3.csv', index = False)


if __name__ == "__main__":
    main()