import datetime
import pytz

COLORS = {
    "default"      : "\033[0m",
    "black"        : "\033[0;30m",
    "red"          : "\033[0;31m",
    "green"        : "\033[0;32m",
    "yellow"       : "\033[0;33m",
    "blue"         : "\033[0;34m",
    "purple"       : "\033[0;35m",
    "cyan"         : "\033[0;36m",
    "white"        : "\033[0;37m",
    "light_red"    : "\033[1;31m",
    "light_green"  : "\033[1;32m",
    "light_yellow" : "\033[1;33m",
    "light_blue"   : "\033[1;34m",
    "light_purple" : "\033[1;35m",
    "light_cyan"   : "\033[1;36m",
    "light_white"  : "\033[1;37m",
    "flat_black"   : "\033[38;2;0;0;0m",
    "flat_red"     : "\033[38;2;204;102;102m",
    "flat_yellow"  : "\033[38;2;255;204;0m",
    "flat_blue"    : "\033[38;2;0;102;204m",
    "flat_purple"  : "\033[38;2;153;51;255m",
    "flat_orange"  : "\033[38;2;255;153;0m",
    "flat_green"   : "\033[38;2;0;204;102m",
    "flat_gray"    : "\033[38;2;128;128;128m",
    "flat_cyan"    : "\033[38;2;0;255;255m",
    "flat_pink"    : "\033[38;2;255;0;255m",
    "flat_white"   : "\033[38;2;255;255;255m",
    }

style_codes = {
    "normal"      : "\033[0m",
    "bold"        : "\033[1m",
    "italic"      : "\033[3m",
    "underline"   : "\033[4m",
    "blink"       : "\033[5m",
    "inverse"     : "\033[7m",
    "strikethrough": "\033[9m",
}

def cprint(*args, color="default", style="normal", bg_color=None, reset=True, timestamp=False, line=None, tqdm_desc=False, timestamp_format='%Y-%m-%d %H:%M:%S', prefix=None, suffix=None, timezone=None):
    """
    Mencetak teks berwarna di konsol.

    Args:
        *args            : Teks yang akan dicetak.
        color            : Warna teks. Standarnya adalah "default".
        style            : Gaya teks. Standarnya adalah "normal".
        bg_color         : Warna latar belakang. Standarnya adalah Tidak Ada.
        reset            : Apakah akan mengatur ulang warna setelah pencetakan. Standarnya adalah True.
        timestamp        : Jika disetel ke True, ini akan menambahkan stempel waktu di awal pencetakan. Standarnya adalah Salah.
        line             : Jika disediakan, akan mencetak jumlah baris yang sama sebelum teks. Standarnya adalah Tidak Ada.
        tqdm_desc        : Jika digunakan sebagai deskripsi di tqdm. Standarnya adalah Salah.
        timestamp_format : Format stempel waktu jika stempel waktu Benar. Standarnya adalah '%Y-%m-%d %H:%M:%S'.
        prefix           : Awalan opsional untuk teks. Standarnya adalah Tidak Ada.
        suffix           : Akhiran opsional untuk teks. Standarnya adalah Tidak Ada.
        timezone         : Zona waktu yang digunakan untuk stempel waktu. Jika Tidak Ada, zona waktu lokal akan digunakan.

    Returns:
        None
    """

    if color not in COLORS:
        raise ValueError(f"Invalid color value '{color}'. Available options are: {', '.join(COLORS.keys())}")
    
    if style not in style_codes:
        raise ValueError(f"Invalid style value '{style}'. Available options are: {', '.join(style_codes.keys())}")
    
    if bg_color is not None and bg_color not in COLORS:
        raise ValueError(f"Invalid bg_color value '{bg_color}'. Available options are: {', '.join(COLORS.keys())}")
    
    color_start = style_codes[style] + COLORS[color]
    if bg_color:
        bg_color_code = "\033[4" + COLORS[bg_color][3:]
        color_start += bg_color_code
    color_end = COLORS["default"] if reset else ""
    formatted_text = " ".join(str(arg) for arg in args)

    if prefix:
        formatted_text = prefix + formatted_text

    if suffix:
        formatted_text += suffix

    if timestamp:
        now = datetime.datetime.now(pytz.timezone(timezone)) if timezone else datetime.datetime.now()
        formatted_text = now.strftime(timestamp_format) + " " + formatted_text

    if line:
        formatted_text = "\n" * line + formatted_text

    if tqdm_desc:
        return color_start + formatted_text

    else:
        print(color_start + formatted_text + color_end)

def print_line(length, color="default", style="normal", bg_color=None, reset=True):
    """
    Mencetak garis tanda sama dengan.

    Args:
        length: Panjang garis.
        color: Warna teks. Standarnya adalah "standar".
        style: Gaya teks. Standarnya adalah "normal".
        bg_color: Warna latar belakang. Standarnya adalah Tidak Ada.
        reset: Apakah akan mengatur ulang warna setelah pencetakan. Standarnya adalah True.

    Returns:
        None
    """
    line = "=" * length
    cprint(line, color=color, style=style, bg_color=bg_color, reset=reset)