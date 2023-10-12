import subprocess
import os
import concurrent.futures
import requests
from tqdm import tqdm
from urllib.parse import urlparse
from ..colortes import cprint

def clone_repos(url, cwd=None, directory=None, branch=None, commit_hash=None, recursive=False, quiet=False, batch=False):
    """
    Clone a git repository.
    
    args:
        url         (str)               : URL Git atau Dictonary.
        cwd         (str, optional)     : Direktori kerja untuk perintah subproses. Defaultnya adalah Tidak Ada.
        directory   (str, optional)     : Direktori tempat repositori harus dikloning. Defaultnya adalah Tidak Ada.
        branch      (str, optional)     : Cabang untuk checkout. Defaultnya adalah Tidak Ada.
        commit_hash (str, optional)     : Hash komit untuk checkout. Defaultnya adalah Tidak Ada.
        recursive   (bool, optional)    : Tandai untuk mengkloning submodul secara rekursif. Defaultnya adalah Salah.
    """
    try:
        parsed_url = urlparse(url).path.split('/')[-1].replace('.git', '')

        if not directory:
            directory = parsed_url

        if os.path.exists(os.path.join(cwd, parsed_url) if cwd else directory):
            message = f"Directory '{parsed_url}' sudah ada."
            if not quiet and not batch:
                color = "yellow"
                cprint(message, color=color)
            return message
        
        cmd = ['git', 'clone', url, directory]
        if branch:
            cmd.extend(["-b", branch])
        if commit_hash:
            cmd.extend(["-c", f"advice.detachedHead=false", commit_hash])
        if recursive:
            cmd.append("--recursive")
        if quiet:
            cmd.append("--quiet")
        if batch:
            cmd.append("--batch")
        if directory:
            cmd.append(directory)
        
        result = subprocess.run(cmd, text=True, cwd=cwd, capture_output=True)

        if result.returncode == 0:
            message = f"Mengcloning '{parsed_url}' telah berhasil."
        else:
            message = f"Mengcloning '{parsed_url}' telah gagal: {result.stderr}"

        if not quiet and not batch:
            color = "green" if result.returncode == 0 else "red"
            cprint(message, color=color)

        if commit_hash and directory:
            checkout_repo(directory, commit_hash, quiet=quiet, batch=batch)

    except Exception as e:
        message = f"Gagal Cloning Repository karena : {e}"
        if not quiet and not batch:
            color = "red"
            cprint(message, color=color)
        return None
    
    return message

def checkout_repo(directory, reference, create=False, args="", quiet=False, batch=False):
    """
    Periksa referensi spesifik di repositori Git.
    
    Args:
        directory  (str)   : Direktori repositori.
        reference  (str)   : Cabang atau komit hash untuk checkout.
        create     (bool)  : Apakah akan membuat cabang baru. Defaultnya adalah Salah.
        args       (str)   : Argumen tambahan untuk perintah checkout.
        quiet      (bool)  : Apakah akan menampilkan pesan. Defaultnya adalah Salah.
        batch      (bool)  : Apakah akan menampilkan pesan. Defaultnya adalah Salah.
    """
    try:
        cmd = ['git', 'checkout']
        if create:
            cmd.append("-b")
        cmd.append(reference)
        if args:
            cmd.append(args)
        
        result = subprocess.run(cmd, text=True, cwd=directory, capture_output=True)

        if result.returncode == 0:
            message = f"Berhasil checkout ke '{reference}'."
        else:
            message = f"Gagal checkout ke '{reference}': {result.stderr}"
        
    except Exception as e:
        message = f"Terjadi kesalahan tak terduga saat memeriksa repositori: {str(e)}"

    if not quiet and not batch:
        color = "green" if result.returncode == 0 else "red"
        cprint(message, color=color)

    return message

def patch_repo(url, dir, cwd, path=None, args=None, whitespace_fix=False, quiet=False):
    """
    Fungsi untuk menambal repo dengan argumen tertentu
    
    Args:
        url (str): URL untuk file patch.
        dir (str): Tempat untuk menyimpan repositori yang dikloning.
        cwd (str): Direktori kerja untuk perintah subproses.
        args (list, optional): Argumen tambahan untuk perintah patch.
        whitespace_fix (bool, optional): Apakah akan menerapkan '--whitespace=fix' argument.
        
    Returns:
        CompletedProcess: Proses selesai.
    """

    if not isinstance(url, str) or not isinstance(dir, str) or not isinstance(cwd, str):
        raise ValueError("'url', 'dir' and 'cwd' harus berupa string.")
    
    if args is not None and not isinstance(args, list):
        raise ValueError("'args' harus berupa list.")
    
    if not isinstance(whitespace_fix, bool):
        raise ValueError("'whitespace_fix' harus berupa boolean.")
    
    os.makedirs(dir, exist_ok=True)

    filename=""

    if url:
        filename = urlparse(url).path.split('/')[-1].replace('.git', '')
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(os.path.join(dir, filename), 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
        except Exception as e:
            if not quiet:
                print(f"Kesalahan mengunduh dari {url}. Kesalahan: {str(e)}")
            return
        
    elif path:
        filename = os.path.basename(url)
    
    if not path:
        path = os.path.join(dir, filename)

        cmd = ['git', 'apply']

    if whitespace_fix:
        cmd.append('--whitespace=fix')
    if args:
        cmd.extend(args)
    cmd.append(path)

    try:
        return subprocess.run(cmd, cwd=cwd, check=True)
    except subprocess.CalledProcessError as e:
        if not quiet:
            cprint(f"Terjadi kesalahan saat menerapkan tambalan. Kesalahan: {str(e)}", color="flat_red")

def reset_repo(directory, commit, hard=False, args="", quiet=False):
    """
    Menyetel ulang repositori Git ke penerapan tertentu.
    
    Args:
        directory (str): Direktori repositori.
        commit (str): Commit untuk mengatur ulang.
        hard (bool, optional): Apakah akan melakukan hard reset. Standarnya adalah Salah.
        args (str, optional): Argumen tambahan untuk perintah reset.
        quiet (bool, optional): Apakah akan mencetak pesan. Standarnya adalah Salah.
    """
    try:
        cmd = ["git", "reset"]
        if hard:
            cmd.append("--hard")
        cmd.append(commit)
        if args:
            cmd.extend(args.split())

        result = subprocess.run(cmd, text=True, cwd=directory, capture_output=True)

        if result.returncode == 0:
            message = f"Reset berhasil. HEAD sekarang di {commit}"
        else:
            message = f"Penyetelan ulang gagal. Kesalahan: {result.stderr}"
    except Exception as e:
        message = f"Terjadi kesalahan tak terduga saat mengatur ulang repositori: {str(e)}"

    if not quiet:
        color = "green" if result.returncode == 0 else "red"
        cprint(message, color=color)

    return message

def update_repo(fetch=False, pull=True, origin=None, cwd=None, args="", quiet=False, batch=False):
    """
    Update a Git repository.
    
    Args:
        fetch (bool, optional): Apakah akan mengambil repositori. Standarnya adalah Salah.
        pull (bool, optional): Apakah akan pull repositori. Standarnya adalah Benar.
        origin (str, optional): Remote untuk fetch/pull. Standarnya adalah Tidak Ada.
        cwd (str, optional): Direktori kerja untuk perintah subproses. Standarnya adalah Tidak Ada.
        args (str, optional): Argumen tambahan untuk perintah pull.
        quiet (bool, optional): Apakah akan menampilkan pesan. Standarnya adalah Salah.
    """
    try:
        repo_name, _, _ = validate_repo(cwd)

        message = ""

        if fetch:
            cmd = ["git", "fetch"]
            if origin:
                cmd.append(origin)
            result = subprocess.run(cmd, text=True, cwd=cwd, capture_output=True)

            if result.returncode != 0:
                message = f"Terjadi kesalahan saat mengambil repositori di {cwd}: {result.stderr}"

        if pull:
            cmd = ["git", "pull"]
            if args:
                cmd.extend(args.split(" "))
            result = subprocess.run(cmd, text=True, cwd=cwd, capture_output=True)

            if result.returncode != 0:
                message = f"Terjadi kesalahan saat pull di {cwd}: {result.stderr}"
            elif "Already up to date." in result.stdout:
                # message = f"'{repo_name}' sudah diperbarui ke versi terbaru"
                pass
            else:
                message = f"'{repo_name}' telah diperbarui ke versi terbaru"

        if not quiet and not batch:
            color = "green" if not any(item in message for item in ["Gagal", "Kesalahan", "gagal", "kesalahan"]) else "red"
            cprint(message, color=color)

    except Exception as e:
        message = f"Error while updating the repository: {e}"
        if not quiet and not batch:
            color = "red"
            cprint(message, color=color)
        return None

    return message

def batch_clone(urls, cwd=None, directory=None, branch=None, commit_hash=None, recursive=False, quiet=False):
    """
    Mengkloning beberapa repositori Git secara paralel.

    Args:
        urls        (list)              : URL list of Git repositories.
        desc        (str, optional)     : Deskripsi untuk ditampilkan di bilah kemajuan. Defaultnya adalah "Kloning...".
        cwd         (str, optional)     : Direktori kerja untuk perintah subproses. Defaultnya adalah Tidak Ada.
        directory   (str, optional)     : Direktori tempat repositori harus dikloning. Defaultnya adalah Tidak Ada.
        branch      (str, optional)     : Cabang untuk checkout. Defaultnya adalah Tidak Ada.
        commit_hash (str, optional)     : Hash komit untuk checkout. Defaultnya adalah Tidak Ada.
        recursive   (bool, optional)    : Tandai untuk mengkloning submodul secara rekursif. Defaultnya adalah Salah.
    """

    if desc is None:
        desc = cprint("Cloning...", color="green", tqdm_desc=True)

    results = {}  # Simpan pesan status clone

    # Menggunakan ThreadPoolExecutor buat clone repositori secara paralel coyyy
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(clone_repos, url, cwd=cwd, directory=directory, branch=branch, commit_hash=commit_hash, recursive=recursive, quiet=quiet, batch=True): url for url in urls}

        for future in tqdm(concurrent.futures.as_completed(futures), total=len(urls), desc=desc):
            try:
                results[future] = future.result()
            except Exception as e:
                cprint(f"Gagal kloning karena : {e}", color="flat_red")
                return None
            
    if not quiet:
        if not any(message for message in results.values()):
                cprint()
        for future, message in results.items():
            if message:
                if "already exists" in message.lower():
                    color = "yellow"
                elif not any(item.lower() in message.lower() for item in ["failed", "error"]):
                    color = "green"
                else:
                    color = "red"
                cprint(" [-]", message, color=color)
        cprint()

def batch_update(repos, fetch=False, pull=True, origin=None, cwd=None, args="", quiet=False):
    """
    Update Pararel Git repository.
    
    Args:
        fetch       (bool, optional)        : Tandai untuk melakukan pengambilan. Defaultnya adalah Salah.
        pull        (bool, optional)        : Tandai untuk melakukan tarikan. Defaultnya adalah Benar.
        origin      (str, optional)         : Remote untuk memperbarui. Defaultnya adalah Tidak Ada.
        directory   (str or list, optional) : Direktori atau direktori tempat repositori berada. Defaultnya adalah Tidak Ada.
        args        (str, optional)         : Argumen tambahan untuk perintah git. Defaultnya adalah "".
        quiet       (bool, optional)        : Tandai untuk menyembunyikan status pembaruan pencetakan. Defaultnya adalah Benar.
        desc        (str, optional)         : Deskripsi untuk ditampilkan di bilah kemajuan. Defaultnya adalah "Memperbarui...".
    
    Returns:
        dict: Sebuah file yang berisi nama repositori dan status pembaruan.
    """
    if not isinstance(directory, list):
        directory = [os.path.join(directory, name) for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]

    if desc is None:
        desc = cprint("Updating...", color="green", tqdm_desc=True)

    results = {}  # Simpan pesan status update

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(update_repo, fetch=fetch, pull=pull, origin=origin, cwd=cwd, args=args, quiet=quiet, batch=True): cwd for cwd in directory}
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(directory), desc=desc):
            try:
                results[future] = future.result()  # Simpan pesan status pembaruan
            except Exception as e:
                cprint(f"Kesalahan saat memperbarui repositori: {e}", color="flat_red")
                return None
            
    if not quiet:
        if not any(message for message in results.values()):
                cprint()
        for future, message in results.items():
            if message:
                if not any(item.lower() in message.lower() for item in ["gagal", "kesalahan"]):
                    color = "green"
                else:
                    if "sudah ada" in message.lower():
                        color = "yellow"
                    else:
                        color = "red"
                cprint(f" [-]", message, color=color)
    

# ========================================================================================================

def validate_repo(directory):
    """
    Memvalidasi repositori Git.

    Args:
        directory (str): Direktori tempat repositori Git berada.

    Returns:
        tuple: Nama repositori, hash penerapan saat ini, dan cabang saat ini.
    """

    def get_current_commit_hash():
        result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=directory)
        return result.stdout.strip()

    def get_current_branch():
        result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, cwd=directory)
        return result.stdout.strip()

    def get_repo_name():
        result = subprocess.run(["git", "config", "--get", "remote.origin.url"], capture_output=True, text=True, cwd=directory)
        output = result.stdout.strip()
        if result.returncode == 0 and output:
            url = output
            repo_name = url.split("/")[-1].split(".")[0]  # Ekstark nama repo
            username = url.split("/")[-2]  # Ekstrak nama pengguna
            return f"{username}/{repo_name}"
        else:
            raise ValueError(f"Gagal mendapatkan nama repositori untuk direktori: {directory}")

    current_commit_hash = get_current_commit_hash()
    current_branch = get_current_branch()
    repo_name = get_repo_name()

    return repo_name, current_commit_hash, current_branch