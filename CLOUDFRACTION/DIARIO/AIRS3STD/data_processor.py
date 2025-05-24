# Archivo usado para cargar y compilar las bases de datos en formato nc4 descargadas de giovanni con el fin de procesar datos del Ozono en Uruguay
import os
import numpy as np
import pandas as pd
import requests
from secret import GIOVANNI_TOKEN
from pyhdf.SD import SD, SDC

def extraer_data(file_name):

    giovanni_lats = [-34.5, -33.5, -32.5, -31.5, -30.5]
    giovanni_lons = [-58.5, -57.5, -56.5, -55.5, -54.5, -53.5]

    hdf = SD(file_name, SDC.READ)
    
    cf_data = hdf.select("CloudFrc_A")[:]

    data_to_get = cf_data[120:125,121:127]

    X = []
    for lat in range(len(giovanni_lats)):
        for lon in range(len(giovanni_lons)):
            x = []
            print(giovanni_lats[lat],giovanni_lons[lon], data_to_get[len(giovanni_lats) - 1 - lat, lon])
            x.append(giovanni_lats[lat])
            x.append(giovanni_lons[lon])
            x.append(data_to_get[len(giovanni_lats) - 1 - lat, lon])
            X.append(x)

    X = np.asarray(X)

    df = pd.DataFrame(X, columns = ['Latitude','Longitude','CloudFraction'])
    fecha = ''.join(file_name.split('.')[1:4])
    df['Fecha'] = fecha

    return df


if __name__ == "__main__":

    # dataset previo
    df_final = pd.read_csv('AIRS3STD7_CF_URUGUAY_4.csv')
    file_list = 'links.txt'
    token = GIOVANNI_TOKEN
    headers = {"Authorization": f"Bearer {token}"}

    with open(file_list, 'r') as file:
        urls = file.readlines()

    for idx, url in enumerate(urls):
        url = url.strip()
        if not url:
            continue

        try:
            print(f"Downloading file {idx + 1}/{len(urls)}: {url}")
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()

            # Extract file name from the URL
            file_name = url.split("/")[-1]

            # Save the file
            with open(file_name, 'wb') as output_file:
                for chunk in response.iter_content(chunk_size=8192):
                    output_file.write(chunk)

            print(f"Downloaded and saved as {file_name}")

            df = extraer_data(file_name)

            print(f"Data extracted from {file_name}")

            df_final = pd.concat([df_final, df])

            # Guardamos nuestro archivo final
            df_final.to_csv('AIRS3STD7_CF_URUGUAY_5.csv', index = False)

            print(f"Database successfully updated")

            os.remove(file_name)

        except requests.RequestException as e:
            print(f"Failed to download {url}: {e}")
