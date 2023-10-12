import os
import subprocess
import glob
import gdown
import time
# from mega import Mega
from tqdm import tqdm
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..utils.py_utils import get_filename, calculate_elapsed_time
from ..colortes import cprint

SUPPORTED_EXTENSIONS = (".ckpt", ".safetensors", ".pt", ".pth")

def parse_args(config):
    """
    Menganalisis argumen yang diberikan.
    
    Args:
        config (dict): Konfigurasi.
        
    Returns:
        dict: Argumen yang dianalisis.
    """

    args = []

    for k, v in config.items():
        if k.startswith("_"):
            args.append(str(v))
        elif v is not None and not isinstance(v, bool):
            args.append(f'--{k}={v}')
        elif isinstance(v, bool) and v:
            args.append(f"--{k}")

    return args

def aria2_download(download_dir: str, filename: str , url: str, quiet: bool=False, user_header: str=None):
    """
    Mengunduh file menggunakan aria2.
    
    Args:
        download_dir (str): Direktori unduhan.
        filename (str): Nama file.
        url (str): URL unduhan.
        quiet (bool, optional): Jika Benar, tidak akan mencetak apa pun. Defaultnya adalah False.
        user_header (str, optional): Header pengguna. Defaultnya adalah Tidak Ada.
    """
    if not quiet:
        start_time = time.time()
        cprint(f"Unduhan {filename} dimulai...", color="green")

    aria2_config = {
        "console-log-level"         : "error",
        "summary-interval"          : 10,
        "header"                    : user_header if "huggingface.co" in url else None,
        "continue"                  : True,
        "max-connection-per-server" : 16,
        "min-split-size"            : "1M",
        "split"                     : 16,
        "dir"                       : download_dir,
        "out"                       : filename,
        "_url"                      : url,
    }
    aria2_args = parse_args(aria2_config)
    subprocess.run(["aria2c", *aria2_args])

    if not quiet:
        elapsed_time = calculate_elapsed_time(start_time)
        cprint(f"Unduhan {filename} selesai dalam {elapsed_time}.", color="green")

def gdown(url: str, dst: str, quiet: bool=False):
    """
    Mengunduh file menggunakan google drive.
    
    Args:
        url (str): URL unduhan.
        dst (str): Direktori tujuan.
        quiet (bool, optional): Jika Benar, tidak akan mencetak apa pun. Defaultnya adalah False.

    Returns:
        str: Nama file.
    """
    if not quiet:
        start_time = time.time()
        cprint(f"Unduhan {url} dimulai pakai Google Drive...", color="green")

    options = {
        "uc?id"         : {},
        "file/d"        : {"fuzzy"      : True},
        "drive/folders" : {"use_cookies": False},
    }

    for key, kwargs in options.items():
        if key in url:
            output = gdown.download(url, os.path.join(dst, ""), quiet=True, **kwargs)
            if not quiet:
                elapsed_time = calculate_elapsed_time(start_time)
                cprint(f"Unduhan {url} selesai dalam {elapsed_time}.", color="green")
            return output
        
        os.chdir(dst)
        output = gdown.download(url, quiet=True, **kwargs)

        if not quiet:
            elapsed_time = calculate_elapsed_time(start_time)
            cprint(f"Unduhan {url} selesai dalam {elapsed_time}.", color="green")

        return output

# MEGA Saat ini tidak di gunakan karena tidak ada cara untuk mengunduh file tanpa login.

def mega(url: str, dst: str, quiet: bool=False):
    """
    Mengunduh file menggunakan mega.nz.
    
    Args:
        url (str): URL unduhan.
        dst (str): Direktori tujuan.
        quiet (bool, optional): Jika Benar, tidak akan mencetak apa pun. Defaultnya adalah False.
        
    Returns:
        str: Nama file.
            
    Raises:
        RuntimeError: Jika mega tidak terpasang.
    """
    if not quiet:
        start_time = time.time()
        cprint(f"Unduhan {url} dimulai pakai Mega...", color="green")

    mega = mega()
    m = mega.login()
    file = m.download_url(url, dst)

    if not quiet:
        elapsed_time = calculate_elapsed_time(start_time)
        cprint(f"Unduhan {url} selesai dalam {elapsed_time}.", color="green")

    return file

def get_modelname(url: str, quiet: bool=False, user_header: str=None) -> None:
    """
    Mendapatkan nama model dari URL.
    
    Args:
        url (str): URL unduhan.
        quiet (bool, optional): Jika Benar, tidak akan mencetak apa pun. Defaultnya adalah False.
        user_header (str, optional): Header pengguna. Defaultnya adalah Tidak Ada.
        
    Returns:
        str: Nama model.
    """
    filename = os.path.basename(url) if "drive/MyDrive" in url or url.endswith(SUPPORTED_EXTENSIONS) else get_filename(url, user_header=user_header)

    if filename.endswith(SUPPORTED_EXTENSIONS):
        if not quiet:
            cprint(f"Nama model: {filename}", color="green")
        return filename
    
    if not quiet:
        cprint("Gagal mendapatkan nama model.", color="flat_red")

    return None

def download(url: str, dst: str, filename:str= None, user_header: str=None, quiet: bool=False):
    """
    Mengunduh file.
    
    Args:
        url (str): URL unduhan.
        dst (str): Direktori tujuan.
        filename (str, optional): Nama file. Defaultnya adalah Tidak Ada.
        user_header (str, optional): Header pengguna. Defaultnya adalah Tidak Ada.
        quiet (bool, optional): Jika Benar, tidak akan mencetak apa pun. Defaultnya adalah False.
        
    Returns:
        str: Nama file.
    """

    if not filename:
        filename = get_modelname(url, quiet=quiet)

    if "drive.google.com" in url:
        gdown(url, dst, quiet=quiet)

    elif "drive/MyDrive" in url:
        if not quiet:
            start_time = time.time()
            cprint(f"Copy '{filename}' ...", color="green")
        Path(os.path.join(dst, filename)).write_bytes(Path(url).read_bytes())
        if not quiet:
            elapsed_time = calculate_elapsed_time(start_time)
            cprint(f"Copy '{filename}' selesai dalam {elapsed_time}.", color="green")

    else:
        if "huggingface.co" in url:
            url = url.replace("/blob/", "/resolve/")
        aria2_download(dst, filename, url, user_header=user_header, quiet=quiet)

def batch_download(urls: list, dst: str, desc: str = None, user_header: str = None, quiet: bool = False) -> None:
    """
    Mengunduh beberapa file secara bersamaan.
    
    Args:
        urls (list): Daftar URL unduhan.
        dst (str): Direktori tujuan.
        desc (str, optional): Deskripsi untuk tqdm. Defaultnya adalah Tidak Ada.
        user_header (str, optional): Header pengguna. Defaultnya adalah Tidak Ada.
        quiet (bool, optional): Jika Benar, tidak akan mencetak apa pun. Defaultnya adalah False.
    """
    if desc is None:
        desc = "Download...."
    
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(download, url, dst, user_header=user_header, quiet=quiet) for url in urls]
        with tqdm(total=len(futures), unit='file', disable=quiet, desc=cprint(desc, color="green", tqdm_desc=True)) as pbar:
            for futures in as_completed(futures):
                try:
                    futures.result()
                    pbar.update(1)
                except Exception as e:
                    cprint(f"Unduhan gagal: {e}", color="flat_red")

def download_from_github(repo: str, dst: str, filename: str, quiet: bool=False):
    """
    Mengunduh file dari github.
    
    Args:
        repo (str): Nama repositori.
        dst (str): Direktori tujuan.
        filename (str): Nama file.
        quiet (bool, optional): Jika Benar, tidak akan mencetak apa pun. Defaultnya adalah False.
    """
    url      = f"https://raw.githubusercontent.com/{repo}/master/{filename}"
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        with open(os.path.join(dst, filename), "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        if not quiet:
            cprint(f"Repo {filename} from {repo} to {dst}", color="green")

        else:
            cprint(f"Repo {filename} from {repo} to {dst} telah gagal.", color="flat_red")

def get_most_recent_file(directory: str, quiet: bool=False):
    """
    Mendapatkan file terbaru dari direktori.
    
    Args:
        directory (str): Direktori.
        quiet (bool, optional): Jika Benar, tidak akan mencetak apa pun. Defaultnya adalah False.
        
    Returns:
        str: Nama file.
    """
    cprint(f"Mencari file terbaru di {directory}...", color="green")

    files = glob.glob(os.path.join(directory, "*"))
    if not files:
        if not quiet:
            cprint(f"Tidak ada file di {directory}.", color="flat_red")
        return None

    latest_file = max(files, key=os.path.getctime)
    basename = os.path.basename(most_recent_file)

    if basename.endswith(SUPPORTED_EXTENSIONS):
        if not quiet:
            cprint(f"File terbaru di dapatkan: {basename}", color="green")

    return basename

def get_filepath(url: str, dst: str, quiet: bool=False):
    """
    Mendapatkan path file.
    
    Args:
        url (str): URL unduhan.
        dst (str): Direktori tujuan.
        quiet (bool, optional): Jika Benar, tidak akan mencetak apa pun. Defaultnya adalah False.
        
    Returns:
        str: Path file.
    """

    filename = get_modelname(url, quiet=True)

    if not filename or not filename.endswith(SUPPORTED_EXTENSIONS):
        most_recent_file = get_most_recent_file(dst, quiet=quiet)
        filename = os.path.basename(most_recent_file)

    return os.path.join(dst, filename)