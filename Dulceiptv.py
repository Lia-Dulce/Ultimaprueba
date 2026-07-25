import os
from concurrent.futures import ThreadPoolExecutor
import requests

# Nombres de los archivos
INPUT_FILE = "urls.txt"
OUTPUT_FILE = "activas.txt"

# Configuración
TIMEOUT = 5
MAX_WORKERS = 10


def check_iptv_url(url):
    url = url.strip()
    if not url or url.startswith("#"):  # Ignora líneas vacías o comentarios
        return None, False, None

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.head(
            url, headers=headers, timeout=TIMEOUT, allow_redirects=True
        )
        if response.status_code in [405, 403]:
            response = requests.get(
                url, headers=headers, timeout=TIMEOUT, stream=True
            )
            response.close()

        if response.status_code == 200:
            return url, True, response.status_code
        else:
            return url, False, response.status_code
    except requests.RequestException:
        return url, False, "Error"


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: No se encontró el archivo '{INPUT_FILE}'.")
        print("Crea un archivo llamado 'urls.txt' con una URL por línea.")
        return

    # Leer URLs del archivo de entrada
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    print(
        f"Cargadas {len(urls)} URLs desde '{INPUT_FILE}'. Escaneando...\n"
        + "-" * 50
    )

    online_urls = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = executor.map(check_iptv_url, urls)
        for url, is_online, status in results:
            if url is None:
                continue
            if is_online:
                print(f"[ONLINE] ({status}) -> {url}")
                online_urls.append(url)
            else:
                print(f"[OFFLINE] ({status}) -> {url}")

    # Guardar las URLs funcionales en el archivo de salida
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for url in online_urls:
            f.write(f"{url}\n")

    print("\n" + "=" * 50)
    print(
        f"Escaneo finalizado. Se guardaron {len(online_urls)} URLs activas en '{OUTPUT_FILE}'."
    )


if __name__ == "__main__":
    main()
