import paramiko
import time
from django.conf import settings


def ssh_host(hostname, username, password, vendor, tftp_path):
    ftp_username = settings.FTP_USERNAME
    ftp_password = settings.FTP_PASSWORD
    ftp_root = settings.FTP_ROOT
    server = settings.SERVER
    local_file = "/tmp/tftp_saved_config.cfg"
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=hostname, username=username, password=password)
        time.sleep(1)
        remote_connection = ssh_client.invoke_shell()
        time.sleep(1)
        if vendor.lower() == "fortigate":
            remote_connection.send(f"execute backup config tftp {tftp_path} {server}\n")
            time.sleep(5)
            remote_connection.send("exit\n")
            time.sleep(0.5)
        elif vendor.lower() == "cisco":
            remote_connection.send("copy running-config tftp:\n")
            time.sleep(0.5)
            remote_connection.send(f"{server}\n")
            time.sleep(0.5)
            remote_connection.send(f"{tftp_path}\n")
            time.sleep(5)
            remote_connection.send("exit\n")
            time.sleep(0.5)
        elif vendor.lower() == "huawei":
            remote_connection.send("save tftp_saved_config.cfg\n")
            time.sleep(0.5)
            remote_connection.send("y\n")
            time.sleep(10)
            remote_connection.send(f"tftp {server} put tftp_saved_config.cfg {tftp_path}\n")
            time.sleep(5)
            remote_connection.send("delete tftp_saved_config.cfg\n")
            time.sleep(0.5)
            remote_connection.send("y\n")
            time.sleep(0.5)
            remote_connection.send("quit\n")
            time.sleep(0.5)
        elif vendor.lower() == "juniper":
            remote_connection.send(f"show configuration | save {local_file}\n")
            time.sleep(1)
            remote_connection.send(
                f"file copy {local_file} ftp://{ftp_username}:{ftp_password}@{server}{ftp_root}{tftp_path}\n"
            )
            time.sleep(5)
            remote_connection.send("file delete /tmp/tftp_saved_config.cfg\n")
            time.sleep(0.5)
            remote_connection.send("exit\n")
            time.sleep(0.5)
        elif vendor.lower() == "raisecom":
            remote_connection.send(f"upload running-config tftp {server} {tftp_path}\n")
            time.sleep(10)
            remote_connection.send("quit\n")
            time.sleep(2)
        # output = remote_connection.recv(65535)
        # print(output)
        ssh_client.close()
        return ""
    except paramiko.AuthenticationException:
        return "ERROR: SSH AUTH"
    except paramiko.SSHException:
        return "ERROR: SSH"
    except OSError:
        return "ERROR: SSH OSError"
