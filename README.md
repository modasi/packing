# App Packaging and Signing Tool

This tool automates the process of packaging and signing applications for both macOS and Windows platforms.

## Features

- Generate self-signed certificates for code signing
- Sign and package macOS applications (.app)
- Create and sign macOS disk images (.dmg)
- Sign Windows executables and DLLs
- Create Windows installers (placeholder functionality)

## Prerequisites

- Python 3.6+
- For macOS:
  - Xcode Command Line Tools
  - A valid Apple Developer ID
- For Windows:
  - Windows SDK (for signtool)
  - OpenSSL

## Setup

1. Clone this repository:

   ```
   git clone https://github.com/modasi/packing.git
   cd packing
   ```
2. Edit the `config.py` file to set your application details and certificate information.
3. Generate certificates:

   ```
   python gen_certs.py
   ```
4. Prepare your application files:

   - For macOS: Place your `.app` bundle in the `build.mac` directory.
   - For Windows: Place your executable and DLLs in the `build.win` directory.

## Usage

Run the packaging script:
