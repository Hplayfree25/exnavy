import os
import zipfile
import requests
import shutil
from .py_utils import get_filename
from tqdm import tqdm
from ..colortes import cprint

def ubuntu_deps(url, dst, desc=None):
    """
    Mengunduh dan mengekstrak paket dependensi Ubuntu.
    
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

        deb_files = [os.path.join(dst, f) for f in os.listdir(dst) if f.endswith(".deb")]
        for deb_files in tqdm(deb_files, desc=desc):
             os.system(f'dpkg -i {deb_files}')
        
        os.remove(filename)
        shutil.rmtree(dst)
    
    elif filename.endswith(".deb"):
        os.system(f'dpkg -i {filename}')
        os.remove(filename)

    if not filename:
        cprint("Gagal menentukan nama file.", color="flat_red")
        return

def unionfuse(fused_dir: str, source_dir: str, destination_dir: str):
    """
    Menggabungkan dua direktori menggunakan FUSE.
    
    Args:
        fused_dir (str): Direktori yang digabungkan.
        source_dir (str): Direktori sumber.
        destination_dir (str): Direktori tujuan.

    Raises:
        RuntimeError: Jika FUSE tidak terpasang.
    """
    try:
        for directory in [source_dir, fused_dir, destination_dir]:
            os.makedirs(directory, exist_ok=True)

        command = f"unionfs-fuse -o cow,allow_other,auto_unmount {source_dir}=RW:{fused_dir}=RO {destination_dir}"
        result = os.system(command)

        if result != 0:
            cprint("FUSE tidak terpasang.", color="flat_red")
            raise RuntimeError("FUSE tidak terpasang.")
        else:
            cprint("FUSE terpasang.", color="flat_green")
        
    except Exception as e:
        cprint(f"Terjadi kesalahan saat menggabungkan direktori: {e}", color="flat_red")
        raise e