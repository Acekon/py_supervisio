import socket
import winreg


def get_sys_info():
    ip = socket.gethostbyname(socket.getfqdn())
    sys_name = socket.gethostname()
    sys_version = {}
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
        for value_name in ["DisplayVersion", "ProductName", "CurrentBuild"]:
            try:
                sys_version[value_name] = winreg.QueryValueEx(key, value_name)[0]
            except FileNotFoundError:
                sys_version[value_name] = ""
    return {"ip": ip, "sys_name": sys_name, "sys_version": sys_version}


def get_user_info():
    user_data = {}
    with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Authentication\LogonUI"
    ) as key:
        for value_name in ["LastLoggedOnUser", "LastLoggedOnUserSID", "LastLoggedOnDisplayName"]:
            try:
                if value_name == 'LastLoggedOnUser':
                    data = winreg.QueryValueEx(key, value_name)[0]
                    user_data[value_name] = data.split('\\')[-1]
                    continue
                user_data[value_name] = winreg.QueryValueEx(key, value_name)[0]
            except FileNotFoundError:
                user_data[value_name] = ""
    return user_data
