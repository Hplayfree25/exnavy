import os
import zipfile
import requests
import shutil
from .py_utils import get_filename
from tqdm import tqdm
from ..colortes import cprint

def windows_deps(url, dst, desc=None):
    """
    Mengunduh dan mengekstrak paket dependensi Windows.
    
    Args:
        url (str): URL untuk mengekstrak nama file.
        dst (str): Direktori tujuan.
        desc (str, optional): Deskripsi untuk tqdm. Defaultnya adalah Tidak Ada.
    """

    os.makedirs(dst, exist_ok=True)
    filename = get_filename(url)

    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    if filename.endswith(".zip"):
        with zipfile.ZipFile(filename, "r") as deps:
            deps.extractall(dst)

        if desc is None:
            desc = cprint("Menginstall...", color="green", tqdm_desc=True)

        installer_files = [os.path.join(dst, f) for f in os.listdir(dst) if f.endswith(".msi") or f.endswith(".exe")]
        for installer in tqdm(installer, desc=desc):
             os.system(f'start /wait {installer}')
        
        os.remove(filename)
        shutil.rmtree(dst)

    elif filename.endswith(".msi") or filename.endswith(".exe"):
        os.system(f'start /wait {filename}')
        os.remove(filename)

    if not filename:
        cprint("Gagal menentukan nama file.", color="flat_red")
        return