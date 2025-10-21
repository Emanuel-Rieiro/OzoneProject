import os
import requests
from secret import GIOVANNI_TOKEN

def download_files_with_token(file_list_path, output_directory, token):
    """Descargar archivos de NASA Earthdata usando token como autentificador.

    Argumentos:
        file_list_path (str): Archivo de texto con los links (un link por línea).
        output_directory (str): Carpeta donde se van a guardar los archivos.
        token (str): NASA Earthdata token para habilitar la comunicación.
    """
    # Headers for token-based authentication
    headers = {"Authorization": f"Bearer {token}"}

    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(file_list_path, 'r') as file:
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
            file_path = os.path.join(output_directory, file_name)

            # Save the file
            with open(file_path, 'wb') as output_file:
                for chunk in response.iter_content(chunk_size=8192):
                    output_file.write(chunk)

            print(f"Downloaded and saved as {file_path}")
        except requests.RequestException as e:
            print(f"Failed to download {url}: {e}")

if __name__ == "__main__":
    import argparse

    # Parse command-line arguments
    file_list = './OZONO/DIARIO/OMDOAO3e/links.txt'
    output_dir = './OZONO/DIARIO/OMDOAO3e'
    token = GIOVANNI_TOKEN

    # Call the download function
    download_files_with_token(file_list, output_dir, token)