import os
import math
import re
import requests
import subprocess
import sys
import time 
from urllib.parse import urlparse, unquote
from ..colortes import cprint

def is_google_colab():
    """
    Memeriksa apakah lingkungan saat ini adalah Google Colab.

    Returns:
        bool: Benar jika itu Google Colab, Salah jika sebaliknya.
    """
    try:
        import google.colab
        return True
    except ImportError:
        return False
    
def is_azure():
    """
    Memeriksa apakah lingkungan saat ini adalah Azure.

    Returns:
        bool: Benar jika itu Azure, Salah jika sebaliknya.
    """
    try:
        import azureml
        return True
    except ImportError:
        return False
    
def is_aws():
    """
    Memeriksa apakah lingkungan saat ini adalah AWS.

    Returns:
        bool: Benar jika itu AWS, Salah jika sebaliknya.
    """
    try:
        import boto3
        return True
    except ImportError:
        return False
    
def is_sagemaker_studio_lab():
    """
    Memeriksa apakah lingkungan saat ini adalah SageMaker Studio Lab.

    Returns:
        bool: Benar jika itu SageMaker Studio Lab, Salah jika sebaliknya.
    """
    return "SageMakerNotebook" in os.environ.get("AWS_EXECUTION_ENV", "")

def is_vastai():
    """
    Memeriksa apakah lingkungan saat ini adalah Vast.ai.

    Returns:
        bool: Benar jika itu Vast.ai, Salah jika sebaliknya.
    """
    try:
        import vastai
        return True
    except ImportError:
        return False
    
def calculate_elapsed_time(start_time):
    """
    Hitung waktu yang berlalu antara waktu mulai tertentu dan waktu saat ini.

    Args:
        start_time (float): Waktu mulai dalam hitungan detik sejak epoch.

    Returns:
        str: String yang diformat mewakili waktu yang telah berlalu.

    Contoh:
        >>> hitung_waktu_berlalu(waktu.waktu() - 30)
        '30 detik'
        >>> hitung_waktu_berlalu(waktu.waktu() - 120)
        '2 menit 0 detik'
    """
    end_time = time.time()
    elapsed_time = int(end_time - start_time)

    if elapsed_time < 60:
        return f"{elapsed_time} detik"
    else:
        mins, secs = divmod(elapsed_time, 60)
        return f"{mins} menit {secs} detik"
    
def get_filename(url, user_header=None):
    """
    Ekstrak nama file dari URL yang diberikan.

    Args:
        url (str): URL untuk mengekstrak nama file.
        user_header (str, optional): Header pengguna. Defaultnya adalah Tidak Ada.

    Returns:
        str: filename.
    """
    headers = {}
    
    if user_header:
        headers['Authorization'] = user_header

    response = requests.head(url, stream=True, headers=headers)
    response.raise_for_status()

    if 'content-disposition' in response.headers:
        content_disposition = response.headers['content-disposition']
        filename = re.findall('filename="?([^"]+)"?', content_disposition)[0]
        if filename:
            return filename[0]
    else:
        url_path = urlparse(url).path
        filename = unquote(os.path.basename(url_path))

    return filename

def get_python_version():
    """
    Mengambil versi Python saat ini.

    Returns:
        str: Versi python saat ini.
    """
    return sys.version

def get_torch_version():
    """
    Mengambil versi torch saat ini.

    Returns:
        str: Versi torch saat ini.
    """
    try: 
        import torch
        return torch.__version__
    except ImportError:
        cprint("Gagal mengambil versi PyTorch: PyTorch tidak diinstal", color="flat_red")
        return None

def informasi_gpu(ambil_nama_gpu=False):
    """
    Mengambil informasi GPU.

    Args (Argumen):
        ambil_nama_gpu (bool, opsional): Apakah mengambil nama GPU. Default adalah False.

    Returns (Mengembalikan):
        str: Informasi GPU.
    """
    command = ["nvidia-smi", "--query-gpu=gpu_name", "--format=csv"]
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        info_gpu = result.stdout.strip()
        if ambil_nama_gpu:
            if 'name' in info_gpu:
                return info_gpu[5:]
        return info_gpu
    else:
        pesan_error = result.stderr.strip()
        if "NVIDIA-SMI has failed" in error_message and "No devices were found" in pesan_error:
            if is_google_colab():
                from google.colab import runtime
                runtime.unassign()
            raise RuntimeError("Tidak ada GPU yang ditemukan. GPU tidak ditugaskan di Google Colab.")
        else:
            raise RuntimeError(f"Pelaksanaan perintah gagal dengan kesalahan: {error_message}")
        
def get_gpu_memory():
    """
    Mengambil jumlah memori GPU yang tersedia.
    
    Returns:
        str: Jumlah memori GPU yang tersedia.
    """

    command    = ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"]
    result     = subprocess.run(command.split(" "), stdout=subprocess.PIPE)
    gpu_memory = result.stdout.strip().decode("utf-8")
    return gpu_memory

def convert_size(size_bytes: int) -> str:
    """
    Mengubah ukuran dalam bytes menjadi ukuran yang lebih mudah dibaca.
    
    Args:
        size_bytes (int): Ukuran dalam bytes.
        
    Returns:
        str: Ukuran yang lebih mudah dibaca.
    """

    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def get_file_size(zip_path: str) -> str:
    """
    Mengambil ukuran file.
    
    Args:
        zip_path (str): Path file.
        
    Returns:
        str: Ukuran file.
    """

    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"File tidak ditemukan: {zip_path}")
    
    initial_size = os.path.getsize(zip_path)
    return convert_size(initial_size)
