import subprocess
import os
import zipfile
import rarfile
import shutil
from collections import defaultdict
from ..colortes import cprint

def extract_package(package_name, target_directory, overwrite=False):
    """
    Mengekstrak sebuah paket. Paketnya bisa dalam format tar, lz4, rar, atau zip.

    Args:
        package_name (str): Nama file paket.
        target_directory (str): Direktori dimana paket akan diekstraksi.
        overwrite (bool, optional): Apakah akan menimpa direktori jika sudah ada. Defaultnya adalah Salah.

    Raises:
        subprocess.CalledProcessError: Jika proses ekstraksi gagal.

    Returns:
        None
    """

    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    if package_name.endswith(".tar.lz4"):
        tar_args = ["tar", "-xI", "lz4", "-f", package_name, "--directory", target_directory]
        if overwrite:
            tar_args.append("--overwrite-dir")

        try:
            subprocess.check_output(tar_args, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            cprint(f"Ekstraksi paket gagal karena kesalahan: {e.output.decode()}", color="flat_red")
            raise e
    elif package_name.endswith(".zip"):
        try:
            with zipfile.ZipFile(package_name, 'r') as zip_ref:
                zip_ref.extractall(target_directory)
        except Exception as e:
            cprint(f"Ekstraksi paket gagal karena kesalahan: {str(e)}", color="flat_red")
    elif package_name.endswith(".rar"):
        try:
            with rarfile.RarFile(package_name, 'r') as rar_ref:
                rar_ref.extractall(target_directory)
        except Exception as e:
            cprint(f"Ekstraksi paket gagal karena kesalahan: {str(e)}", color="flat_red")
    else:
        cprint(f"Format paket tidak didukung.: {package_name}", color="flat_red")

def nested_zip_extractor(zip_path, extract_to):
    """
    Fungsi ini mengekstrak file dari file zip, mempertahankan struktur direktori bersarang.
    
    Args:
    zip_path (str): Jalur ke file zip yang akan diekstraksi.
    extract_to (str): Direktori tempat mengekstrak konten file zip.
    """

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            dir_map = defaultdict(list)
            for name in zip_ref.namelist():
                if not name.endswith('/'):
                    parts = name.split('/')
                    for i in range(1, len(parts)):
                        dir_map['/'.join(parts[:i])].append(name)

            subfolders = [folder for folder in dir_map.keys() if len(dir_map[folder]) > 0]
            if len(subfolders) == 1:
                extract_to = os.path.join(extract_to, subfolders[0])

            for member in zip_ref.infolist():
                if not member.is_dir():
                    parts = member.filename.split('/')
                    for i in range(len(parts) - 1, 0, -1):
                        directory = '/'.join(parts[:i])
                        if len(dir_map[directory]) > 1 or i == 1:
                            target_path = os.path.join(extract_to, *parts[i-1:])
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            with zip_ref.open(member) as source, open(target_path, 'wb') as target:
                                shutil.copyfileobj(source, target)
                            break

    except FileNotFoundError:
        cprint(f"File {zip_path} tidak ada.", color="flat_red")
    except PermissionError:
        cprint(f"Izin ditolak untuk membuat direktori atau file.", color="flat_red")
    except Exception as e:
        cprint(f"Terjadi kesalahan: {str(e)}", color="flat_red")
    