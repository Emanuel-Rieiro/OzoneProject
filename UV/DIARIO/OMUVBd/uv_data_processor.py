# Archivo usado para cargar y compilar las bases de datos en formato nc4 descargadas de giovanni con el fin de procesar datos del Ozono en Uruguay
import os
import numpy as np
import pandas as pd
from pathlib import Path
from dateutil.parser import parse

from netCDF4 import Dataset


def main():

    output_csv = "OMUVBd_UV_EXT_URUGUAY.csv"
    output_nan_data = "nan_data.csv"
    first = True

    labels = ['CSErythemalDailyDose', 'CSErythemalDoseRate', 'CSIrradiance305', 'CSIrradiance310', 'CSIrradiance324', 'CSIrradiance380', 'CloudOpticalThickness', 'ErythemalDailyDose',
            'ErythemalDoseRate', 'Irradiance305', 'Irradiance310', 'Irradiance324', 'Irradiance380', 'LambertianEquivalentReflectivity', 'SolarZenithAngle', 'ViewingZenithAngle', 'CSUVindex', 'UVindex']


    onlyfiles = [str(f.resolve()) for f in Path('./DATA').rglob("*OMI*he5.nc4")]

    list_notna_df = []
    list_na_df = []

    for i, filename in enumerate(onlyfiles):
        # if i == 100: break; exit();
        try:
            with Dataset(filename, "r") as file:
                variables = file.variables 
                uv_index = file.variables['UVindex'][:]
                lat = file.variables['lat'][:]
                lon = file.variables['lon'][:]
                start_utc = file.getncattr("HDFEOS_ADDITIONAL_FILE_ATTRIBUTES.StartUTC")
                end_utc = file.getncattr("HDFEOS_ADDITIONAL_FILE_ATTRIBUTES.EndUTC")

                start = parse(start_utc)
                end = parse(end_utc)

                data = {}
                try:
                    data = {l: variables[l][:].ravel() for l in labels}
                except Exception as ex:
                    print(ex)

                mid_time = start + (end - start) / 2
                lon_grid, lat_grid = np.meshgrid(lon, lat)  # ambos de shape (lat, lon)

                data.update({
                    'Latitude':  lat_grid.ravel(),
                    'Longitude': lon_grid.ravel(),
                    'Mid_time': [mid_time] * uv_index.size
                })
        except Exception as ex:
            print(ex)
            print("~"*40)
            print(filename)


        df = pd.DataFrame(data)
        df['Mid_time'] = pd.to_datetime(df['Mid_time'], errors='coerce')

        notna_df = df[df['UVindex'].notna()].copy()
        list_notna_df.append(notna_df)

        na_df = df[~df['UVindex'].notna()].copy()
        list_na_df.append(na_df)

    list_notna_df = pd.concat(list_notna_df).sort_values(by='Mid_time')
    list_notna_df.to_csv(
        output_csv,
        mode='a',
        index=False,
        header=first
    )

    list_na_df = pd.concat(list_na_df).sort_values(by='Mid_time')
    list_na_df.to_csv(
        output_nan_data,
        mode='a',
        index=False,
        header=first
    )

    first = False


if __name__ == "__main__":
    main()
