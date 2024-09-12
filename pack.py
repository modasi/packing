import os
import subprocess
import sys
import platform
import glob
import shutil
from config import *

def check_environment():
    print("Checking environment...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check required directories
    required_dirs = [BUILD_MAC_DIR, BUILD_WIN_DIR, CERT_DIR]
    for dir_name in required_dirs:
        dir_path = os.path.join(current_dir, dir_name)
        if not os.path.exists(dir_path):
            print(f"Creating directory: {dir_path}")
            os.makedirs(dir_path)
    
    # Check required tools
    if platform.system() == "Darwin":
        tools = ['codesign', 'xcrun', 'ditto', 'hdiutil']
    elif platform.system() == "Windows":
        tools = ['signtool']
    else:
        print("Unsupported operating system")
        sys.exit(1)

    for tool in tools:
        if shutil.which(tool) is None:
            print(f"Error: {tool} is not installed or not in PATH")
            sys.exit(1)
    
    print("Environment check completed")

def sign_macos_app(app_path, identity):
    print(f"Signing macOS application: {app_path}")
    # Sign all internal components
    for root, dirs, files in os.walk(app_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(('.dylib', '.so')) or (file.startswith('lib') and '.' not in file):
                command = f"codesign --force --options runtime --sign '{identity}' '{file_path}'"
                subprocess.run(command, shell=True, check=True)
    
    # Finally, sign the entire .app bundle
    command = f"codesign --force --options runtime --sign '{identity}' '{app_path}'"
    subprocess.run(command, shell=True, check=True)

def notarize_macos_app(app_path, apple_id, password, team_id):
    print(f"Notarizing macOS application: {app_path}")
    # Create a temporary zip file
    zip_path = f"{app_path}.zip"
    subprocess.run(f"ditto -c -k --keepParent '{app_path}' '{zip_path}'", shell=True, check=True)
    
    # Submit notarization request
    command = f"xcrun altool --notarize-app --primary-bundle-id '{COMPANY_NAME}.{APP_NAME}' " \
              f"--username '{apple_id}' --password '{password}' --team-id '{team_id}' --file '{zip_path}'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    # Parse output to get request UUID
    uuid = None
    for line in result.stdout.splitlines():
        if "RequestUUID" in line:
            uuid = line.split("=")[1].strip()
            break
    
    if not uuid:
        print("Notarization submission failed")
        sys.exit(1)
    
    print(f"Notarization request submitted, UUID: {uuid}")
    print("Please wait for the notarization process to complete, then run the stapler command to staple the notarization result")
    
    # Clean up temporary zip file
    os.remove(zip_path)

def create_macos_dmg(app_path, dmg_path):
    print(f"Creating macOS DMG: {dmg_path}")
    command = f"hdiutil create -volname '{APP_NAME}' -srcfolder '{app_path}' -ov -format UDZO '{dmg_path}'"
    subprocess.run(command, shell=True, check=True)

def sign_windows_files(dir_path, cert_path, cert_password):
    print(f"Signing Windows files: {dir_path}")
    for ext in ('*.exe', '*.dll'):
        for file_path in glob.glob(os.path.join(dir_path, '**', ext), recursive=True):
            command = f"signtool sign /f {cert_path} /p {cert_password} /tr http://timestamp.digicert.com /td sha256 /fd sha256 {file_path}"
            subprocess.run(command, shell=True, check=True)

def create_windows_installer(dir_path, installer_path):
    print(f"Creating Windows installer: {installer_path}")
    # Implement the logic for creating the installer here
    # You can use tools like NSIS or Inno Setup
    pass

def main():
    check_environment()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))

    if platform.system() == "Darwin":
        # macOS processing flow
        app_path = os.path.join(current_dir, BUILD_MAC_DIR, f"{APP_NAME}.app")
        dmg_path = os.path.join(current_dir, BUILD_MAC_DIR, f"{APP_NAME}.dmg")

        if not os.path.exists(app_path):
            print(f"Error: {app_path} does not exist")
            sys.exit(1)

        sign_macos_app(app_path, MACOS_IDENTITY)
        notarize_macos_app(app_path, EMAIL, MACOS_APP_SPECIFIC_PASSWORD, MACOS_TEAM_ID)
        create_macos_dmg(app_path, dmg_path)

    elif platform.system() == "Windows":
        # Windows processing flow
        dir_path = os.path.join(current_dir, BUILD_WIN_DIR)
        cert_path = os.path.join(current_dir, CERT_DIR, WINDOWS_PFX_FILENAME)
        installer_path = os.path.join(current_dir, BUILD_WIN_DIR, f"{APP_NAME}Installer.exe")

        if not os.path.exists(dir_path):
            print(f"Error: {dir_path} does not exist")
            sys.exit(1)
        if not os.path.exists(cert_path):
            print(f"Error: {cert_path} does not exist")
            sys.exit(1)

        sign_windows_files(dir_path, cert_path, WINDOWS_CERT_PASSWORD)
        create_windows_installer(dir_path, installer_path)

    else:
        print("Unsupported operating system")
        sys.exit(1)

if __name__ == "__main__":
    main()