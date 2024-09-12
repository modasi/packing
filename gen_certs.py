import os
import subprocess
from config import *

def generate_self_signed_cert(common_name, cert_path, key_path):
    command = f"openssl req -x509 -newkey rsa:4096 -keyout {key_path} -out {cert_path} -days 365 -nodes " \
              f"-subj \"/CN={common_name}/C={CERT_COUNTRY}/ST={CERT_STATE}/L={CERT_LOCALITY}/O={CERT_ORGANIZATION}/OU={CERT_ORGANIZATIONAL_UNIT}/emailAddress={CERT_EMAIL}\""
    subprocess.run(command, shell=True, check=True)

def generate_pfx(cert_path, key_path, pfx_path, password):
    command = f"openssl pkcs12 -export -out {pfx_path} -inkey {key_path} -in {cert_path} -password pass:{password}"
    subprocess.run(command, shell=True, check=True)

def main():
    cert_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), CERT_DIR)
    
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)
    
    # Generate certificate for macOS
    macos_cert_path = os.path.join(cert_dir, MACOS_CERT_FILENAME)
    macos_key_path = os.path.join(cert_dir, MACOS_KEY_FILENAME)
    generate_self_signed_cert(f"{CERT_COMMON_NAME} macOS Developer", macos_cert_path, macos_key_path)
    print("macOS certificate generated")

    # Generate certificate for Windows
    windows_cert_path = os.path.join(cert_dir, WINDOWS_CERT_FILENAME)
    windows_key_path = os.path.join(cert_dir, WINDOWS_KEY_FILENAME)
    windows_pfx_path = os.path.join(cert_dir, WINDOWS_PFX_FILENAME)
    generate_self_signed_cert(f"{CERT_COMMON_NAME} Windows Developer", windows_cert_path, windows_key_path)
    generate_pfx(windows_cert_path, windows_key_path, windows_pfx_path, PFX_PASSWORD)
    print("Windows certificate generated")

if __name__ == "__main__":
    main()