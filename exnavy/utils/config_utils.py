import json
import yaml
import xmltodict
import toml
import requests
import fileinput
from ..colortes import cprint

def determine_file_format():
    """
    Tentukan format file berdasarkan ekstensi nama file.

    Args:
        filename (str): Tempat Filename

    Returns:
        str: Format file (json, yaml, xml, toml, txt, atau css).
    """

    file_extension = filename.lower().split(".")[-1]
    if file_extension in ("json", "yaml", "yml", "xml", "toml", "txt"):
        return file_extension
    else:
        return "txt"
    
def read_config(filename):
    """
    Membaca isi file.

    Args:
        filename (str): Jalur ke file konfigurasi. Bisa berupa JSON, YAML, XML, TOML, atau TXT.

    Returns:
        dict or str: Konfigurasi dibaca dari file. Untuk file TXT, string dikembalikan.
    """
    file_format = determine_file_format(filename)

    if file_format == 'json':
        with open(filename, "r") as f:
            config = json.load(f)

    elif file_format in ("yaml", "yml"):
        with open(filename, "r") as f:
            config = yaml.safe_load(f)

    elif file_format == "xml":
        with open(filename, "r") as f:
            config = xmltodict.parse(f.read())

    elif file_format == "toml":
        with open(filename, "r") as f:
            config = toml.load(f)

    elif file_format == "txt":
        with open(filename, "r") as f:
            config = f.read()

    else:
        with open(filename, 'r') as f:
            config = f.read()

    return config

def write_config(filename, config):
    """
    Tulis konfigurasi ke file.
    
    args:
        filename (str): Jalur ke file konfigurasi. Bisa berupa JSON, YAML, XML, TOML, atau TXT.
        config (dict): Konfigurasi untuk menulis ke file.
    
    """

    file_format = determine_file_format(filename)

    if file_format == "json":
        with open(filename, "w") as f:
            json.dump(config, f, indent=4)
    elif file_format == "yaml" or file_format == "yml":
        with open(filename, "w") as f:
            yaml.dump(config, f)
    elif file_format == "xml":
        with open(filename, "w") as f:
            xml = xmltodict.unparse(config, pretty=True)
            f.write(xml)
    elif file_format == "toml":
        with open(filename, "w") as f:
            toml.dump(config, f)
    else:
        with open(filename, 'w', encoding="utf-8") as f:
            f.write(config)

def get_config(filename):
    """
    Dapatkan konfigurasi dari file.

    Args:
        filename (str): Jalur ke file konfigurasi. Bisa berupa JSON, YAML, XML, TOML, atau TXT.

    Returns:
        dict or str: Konfigurasi dibaca dari file. Untuk file TXT, string dikembalikan.
    """
    config = read_config(filename)
    return config

def change_line(filename, old_string, new_string):
    """
    Ganti string dalam file dengan string lain.

    Args:
        filename (str): Jalur ke file.
        old_string (str): String lama yang akan diganti.
        new_string (str): String yang akan diganti.
    """
    with fileinput.input(files=(filename,), inplace=True) as file:
        for line in file:
            print(line.replace(old_string, new_string), end='')

def pastebin_reader(id):
    if "pastebin.com" in id:
        url = id 
        if 'raw' not in url:
                url = url.replace('pastebin.com', 'pastebin.com/raw')
    else:
        url = "https://pastebin.com/raw/" + id
    response = requests.get(url)
    response.raise_for_status() 
    lines = response.text.split('\n')
    return lines
