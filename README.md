# Open Server Shares Service

This repository contains a Windows service for running a FastAPI-based web application (`prodOpenFiles.py`) that allows users to view and manage open server files. The service uses LDAP authentication and is designed to run persistently in a Windows domain environment.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Setup](#setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Logs](#logs)
- [Troubleshooting](#troubleshooting)

## Overview

The **Open Server Shares Service** is a FastAPI-based web application that provides a web interface for viewing and releasing open server files. The service uses LDAPS for authentication and securely fetches credentials from environment variables. The application runs as a Windows service, ensuring it remains persistent and restarts automatically on server reboots.

## Features

- **View open server files**: Users can view files that are currently open on the server.
- **Release open files**: Users can release open files from the server through a web interface.
- **LDAPS authentication**: Securely authenticate users against an LDAP server.
- **Persistent Windows service**: The application runs as a Windows service, ensuring uptime and automatic restarts.

## Setup

### Prerequisites

1. **Python 3.x** installed on your system.
2. **Windows Server** environment (or Windows workstation).
3. **Administrator privileges** for creating and managing services.

### Step 1: Clone the Repository

```bash
git clone https://github.com/OlsenSM91/Open-Server-Shares.git
cd Open-Server-Shares
```

### Step 2: Install Required Python Packages

Install the necessary dependencies using pip:

```bash
pip install fastapi uvicorn ldap3 pywin32
```

### Step 3: Set Up Environment Variables

Set the LDAPS search user credentials as environment variables on the server. Open **PowerShell** as an administrator and execute the following commands:

```powershell
[System.Environment]::SetEnvironmentVariable("LDAP_SEARCH_USER", "Search User DN", "Machine")
[System.Environment]::SetEnvironmentVariable("LDAP_SEARCH_PASSWORD", 'PasswordInSingleQuotesHere', "Machine")
```

### Step 4: Configure the Project Directory

Your project directory should look like this:

```
Open-Server-Shares/
│
├── prodOpenFiles.py      # FastAPI web application script
├── service_log.txt		  # Service Wrapper Log File to Investigate Issues (Only present after running `service_wrapper.py`)
├── service_wrapper.py    # Python script to create and manage the Windows service
└── README.md             # This README file
```

### Step 5: Register the Windows Service

Run the following command from an **Administrator PowerShell** window to register the service:

```powershell
python service_wrapper.py install
```

### Step 6: Start the Windows Service

Start the newly created Windows service:

```powershell
python service_wrapper.py start
```

You can confirm that the service is running by opening the **Services** console (`services.msc`) and checking the status of **Open Server Shares Service**.

## Configuration

- **LDAPS Server Configuration**: Modify the LDAP configuration in `prodOpenFiles.py` as needed for your domain environment.
- **Service Configuration**: Adjust the `service_wrapper.py` script to change the service name, display name, or description as needed.

## Usage

Once the service is running, you can access the web application in your browser using the configured server’s IP address or hostname and the specified port:

```
http://your-server-ip-or-hostname:9001
```

1. **Login** using your domain credentials.
2. **View open server files** in the web interface.
3. **Release files** by clicking the "Release" button.

## Logs

All service-related logs are saved to a log file located at:

```
C:\CNS4U\service_log.txt
```

This log file captures service events, including errors, service status, and output from the `uvicorn` process.

## Troubleshooting

### Common Issues

1. **Service Not Starting Automatically on Reboot**:
   Ensure the service startup type is set to **Automatic** using the following command:

   ```powershell
   Set-Service -Name "OpenShares" -StartupType Automatic
   ```

2. **Issues with Environment Variables**:
   Verify the environment variables using PowerShell:

   ```powershell
   echo $env:LDAP_SEARCH_USER
   ```

3. **Service Logs**:
   Check the service log (`C:\CNS4U\service_log.txt`) for detailed information about the service and any issues encountered during execution.

## License

This project is licensed under the The Unlicense License. See the [LICENSE](./LICENSE) file for details.

## Acknowledgments

- **Computer Networking Solutions, Inc.** for the project concept and implementation.
- **[pywin32](https://github.com/mhammond/pywin32)** for the Python Windows service utilities.

### Additional Notes
- Make sure to replace `"Search User DN"` and `"PasswordInSingleQuotesHere"` with actual values when setting environment variables.
- You can also customize the project details and replace links with real URLs where applicable (e.g., GitHub repository URL, License file link).
