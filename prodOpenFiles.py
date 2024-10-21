import json
import subprocess
import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from jinja2 import Template
from ldap3 import Server, Connection, ALL, NTLM, SUBTREE

app = FastAPI()

# Secret key for session management for the FastAPI web application
app.add_middleware(SessionMiddleware, secret_key="secret-session-key")

# LDAP Configuration - You will need to modify this section to match your domain
LDAP_SERVER = 'ldaps://domain.local:636'
LDAP_SEARCH_BASE = 'OU=SBSUsers,OU=Users,OU=MyBusiness,DC=domain,DC=local' # This example is for if you have a deep subtree base for the OU of where to search for your users with the authorized access
LDAP_DOMAIN = 'domain.local'
LDAP_GROUP = 'ShareManagement' # This is the security group the script will look through to validate the authenticating users permissions

def authenticate_ldap_user(username: str, password: str) -> bool:
    """Authenticate user using username, search for DN, and perform the bind."""

    try:
        # Connect to LDAP server over LDAPS
        server = Server(LDAP_SERVER, get_info=ALL, use_ssl=True)

        # Retrieve the domain search account credentials from environment variables
        search_user = os.getenv("LDAP_SEARCH_USER")
        search_password = os.getenv("LDAP_SEARCH_PASSWORD")

        if not search_user or not search_password:
            print("Missing LDAP credentials. Ensure environment variables are set.")
            return False

        # Construct the DN dynamically based on the retrieved environment variables
        search_dn = f"CN={search_user},{LDAP_SEARCH_BASE}"

        # Use the constructed DN to bind for the search
        conn = Connection(server, user=search_dn, password=search_password)

        # Bind with the search DN to perform the DN search
        if not conn.bind():
            print(f"Failed to bind to LDAP server for search: {conn.result}")
            return False

        # Search for the user's DN using their sAMAccountName (username)
        search_filter = f"(sAMAccountName={username})"
        conn.search(search_base=LDAP_SEARCH_BASE, search_filter=search_filter, search_scope=SUBTREE, attributes=['distinguishedName'])

        if not conn.entries:
            print(f"User {username} not found in LDAP.")
            return False

        # Get the distinguished name (DN) of the user
        user_dn = conn.entries[0].distinguishedName.value
        print(f"Found user DN: {user_dn}")

        # Now, try binding as the user with their password
        user_conn = Connection(server, user=user_dn, password=password)

        if not user_conn.bind():
            print(f"Failed to bind as {username}: {user_conn.result}")
            return False

        print("Bind successful!")
        return True

    except Exception as e:
        print(f"LDAP authentication error: {e}")
        return False

# Login template - Change to match branding for client.
login_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }
        .container {
            margin-top: 50px;
        }
        .login-box {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            display: inline-block;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            box-sizing: border-box;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        input[type="submit"] {
            background-color: #d3d3d3; /* Light gray for the button */
            color: white;
            padding: 14px 20px;
            margin: 8px 0;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
        }
        input[type="submit"]:hover {
            background-color: #c0c0c0; /* Darker shade of light gray for hover effect */
        }
        footer {
            margin-top: 20px;
            font-size: small;
            color: gray;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-box">
            <h2>Login</h2>
            <form action="/login" method="post">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required><br>
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required><br>
                <input type="submit" value="Login">
            </form>
            <p>{{ message }}</p>
        </div>
    </div>
    <footer>
        Made with ❤️ by Computer Networking Solutions, Inc.
    </footer>
</body>
</html>
"""

# Files Template - Change to match branding for client. There is a logo file, as well as colors to update to match client branding
files_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Open Server Files</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #d3d3d3; /* Light gray for the header */
            padding: 10px;
        }
        .header img {
            max-width: 200px; /* Fixed logo size */
            height: auto;
        }
        .logout {
            display: flex;
            align-items: center;
            color: black;
            font-size: 16px;
        }
        .logout img {
            max-width: 48px; /* logout image */
            max-height: 48px;
            margin-left: 8px;
        }
        h2 {
            text-align: center;
            margin-top: 20px;
            font-size: 24px;
            color: #333;
        }
        .search-box {
            margin: 20px auto;
            text-align: center;
        }
        .search-box input[type="text"] {
            width: 50%;
            padding: 12px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 16px;
        }
        table {
            border-collapse: collapse;
            width: 80%;
            margin: 20px auto;
            background-color: white;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #d3d3d3; /* Light gray for table headers */
            color: black;
        }
        tr:hover {
            background-color: #f1f1f1;
        }
        .tooltip {
            visibility: hidden;
            position: absolute;
            background-color: #f9f9f9;
            border: 1px solid black;
            padding: 5px;
            z-index: 1;
        }
        td:hover .tooltip {
            visibility: visible;
        }
        footer {
            text-align: center;
            margin-top: 20px;
            font-size: small;
            color: gray;
        }
    </style>
    <script>
        function filterFiles() {
            const filter = document.getElementById("searchBox").value.toLowerCase();
            const rows = document.getElementById("filesTable").rows;
            for (let i = 1; i < rows.length; i++) {
                const fileName = rows[i].cells[1].innerText.toLowerCase();
                if (fileName.includes(filter)) {
                    rows[i].style.display = "";
                } else {
                    rows[i].style.display = "none";
                }
            }
        }
    </script>
</head>
<body>
    <div class="header">
        <img src="https://path.to.clients/logo.png" alt="Logo">
        <a href="/logout" class="logout">Logout
            <img src="https://i.ibb.co/3zfNJS0/logout.png" alt="Logout">
        </a>
    </div>
    <h2>Open Server Files</h2>
    <div class="search-box">
        <input type="text" id="searchBox" onkeyup="filterFiles()" placeholder="Search for files...">
    </div>
    <table id="filesTable">
    <thead>
        <tr>
            <th>Client Hostname</th>
            <th>File Path</th>
            <th>User</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {% for file in files %}
        <tr>
            <td>
                <div style="position:relative;">
                    <span>{{ file["Hostname"] }}</span>
                    <div class="tooltip">IP: {{ file["ClientComputerName"] }}</div>
                </div>
            </td>
            <td>{{ file["Path"] }}</td>
            <td>{{ file["ClientUserName"] }}</td>
            <td>
                <button type="button" onclick="confirmRelease('{{ file['FileId'] }}', '{{ file['Path'] }}')">Release</button>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<!-- Confirmation Modal -->
<div id="confirmModal" style="display:none; position:fixed; top:50%; left:50%; transform:translate(-50%, -50%); background-color:white; padding:20px; border:1px solid #ccc; z-index:1000;">
    <p id="fileInfo"></p>
    <form id="releaseForm" action="/release" method="post">
        <input type="hidden" name="file_id" id="file_id">
        <button type="submit">Confirm</button>
        <button type="button" onclick="closeModal()">Cancel</button>
    </form>
</div>
<div id="modalOverlay" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background-color:rgba(0, 0, 0, 0.5); z-index:999;" onclick="closeModal()"></div>

<script>
    function confirmRelease(fileId, filePath) {
        // Set file details in the modal
        document.getElementById('fileInfo').innerText = `Are you sure you want to release the file: ${filePath}?`;
        document.getElementById('file_id').value = fileId;
    
        // Show the modal and overlay
        document.getElementById('confirmModal').style.display = 'block';
        document.getElementById('modalOverlay').style.display = 'block';
    }

    function closeModal() {
        // Hide the modal and overlay
        document.getElementById('confirmModal').style.display = 'none';
        document.getElementById('modalOverlay').style.display = 'none';
    }
</script>

    <footer>
        Made with ❤️ by Computer Networking Solutions, Inc.
    </footer>
</body>
</html>
"""

def query_open_files():
    """Run PowerShell to get the list of open files, including FileId."""
    command = [
        "powershell",
        "-Command",
        """
        $openFiles = Get-SmbOpenFile | Select-Object -Property ClientComputerName,Path,ClientUserName,ClientIp,FileId
        $openFiles | ForEach-Object {
            $hostname = try { [Net.DNS]::GetHostByAddress($_.ClientComputerName).HostName } catch { $_.ClientComputerName }
            [pscustomobject]@{
                Path = $_.Path
                ClientUserName = $_.ClientUserName
                ClientComputerName = $_.ClientComputerName
                Hostname = $hostname
                FileId = $_.FileId
            }
        } | ConvertTo-Json
        """
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    
    open_files = []
    if result.returncode == 0:
        open_files = json.loads(result.stdout)  # Parse JSON from PowerShell output

    return open_files

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the login page."""
    if request.session.get("authenticated"):
        return RedirectResponse(url="/files")
    return Template(login_template).render(message="")

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle login form submission with LDAP authentication."""
    if authenticate_ldap_user(username, password):
        request.session["authenticated"] = True
        return RedirectResponse(url="/files", status_code=302)
    return Template(login_template).render(message="Invalid credentials or not part of the ShareManagement group.") # Change group name here if changed

@app.get("/files", response_class=HTMLResponse)
async def show_files(request: Request):
    """Show open files after login."""
    if not request.session.get("authenticated"):
        return RedirectResponse(url="/")
    files = query_open_files()
    return Template(files_template).render(files=files)

@app.post("/release")
async def release_file(request: Request, file_id: str = Form(...)):
    """Release a file by closing it using the FileId."""
    if not request.session.get("authenticated"):
        return RedirectResponse(url="/")
    
    # PowerShell command to close the file by FileId, with -Force to bypass confirmation
    command = [
        "powershell",
        "-Command",
        f"Close-SmbOpenFile -FileId {file_id} -Force"
    ]
    
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        return RedirectResponse(url="/files", status_code=302)
    else:
        return HTMLResponse(content=f"Failed to release file: {result.stderr}", status_code=500)

@app.get("/logout")
async def logout(request: Request):
    """Log the user out."""
    request.session.clear()
    return RedirectResponse(url="/")
