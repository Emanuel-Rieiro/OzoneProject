import os
import requests
from secret import GIOVANNI_TOKEN

def download_files_with_token(file_list_path, output_directory, token):
    """Download files from NASA Earthdata using a token for authentication.

    Args:
        file_list_path (str): Path to the text file containing URLs (one URL per line).
        output_directory (str): Directory where the files will be saved.
        token (str): NASA Earthdata token for authentication.
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
    file_list = './UV/DIARIO/OMUVBd/links.txt'
    output_dir = './UV/DIARIO/OMUVBd'
    token = GIOVANNI_TOKEN

    # Call the download function
    download_files_with_token(file_list, output_dir, token)