import getpass

import paramiko
from scp import SCPClient
from read_settings_deployment import SERVICE_NAME, VERSION, HOST_IP


def get_username_and_password():
    _username = input("Enter your username: ")
    _password = getpass.getpass("Enter your password: ")
    return _username, _password


def get_server_ip():
    _server_ip = input("Enter the server IP: ")

    # Validate the IP address
    server_ip_parts = _server_ip.split('.')
    if len(server_ip_parts) != 4:
        print("Invalid IP address")
        return get_server_ip()
    else:
        for server_ip_part in server_ip_parts:
            if not server_ip_part.isdigit() or not 0 <= int(server_ip_part) <= 255:
                print("Invalid IP address")
                return get_server_ip()

    return _server_ip


def get_ssl_enabled():
    _ssl_enabled = input("Enable SSL? (y/n): ")
    if _ssl_enabled == 'y' or _ssl_enabled == 'n':
        return _ssl_enabled
    else:
        print("Please enter 'y' or 'n'")
        return get_ssl_enabled()


def copy_files_to_server(server_ip, username, password, file_urls):
    """
    file_urls: list of tuples (source_folder, source_file_name, destination_folder, destination_file_name)
    """
    ssh = paramiko.SSHClient()

    # Automatically add server's SSH key (without checking)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the server
    ssh.connect(hostname=server_ip, username=username, password=password)

    # Define an SCP client over the SSH connection
    scp = SCPClient(ssh.get_transport())

    for file_url in file_urls:
        source_folder, source_file_name, destination_folder, destination_file_name = file_url
        # Remove '/' at the end of the source folder (if there is any)
        if source_folder[-1] == '/':
            source_folder = source_folder[:-1]

        # Make the remote directory (it will not do anything if the directory already exists)
        ssh.exec_command(f'mkdir -p {destination_folder}')
        source_file_url = f'{source_folder}/{source_file_name}'

        print(f"scp {source_file_url} {username}@{server_ip}:{destination_folder}/{destination_file_name}")
        scp.put(source_file_url, f'{destination_folder}/{destination_file_name}')

    scp.close()
    ssh.close()


if __name__ == '__main__':
    username, password = get_username_and_password()
    ssl_enabled = get_ssl_enabled()

    destination_folder = f'~/service/{SERVICE_NAME}/{VERSION}'
    destination_ssl_folder = f'{destination_folder}/ssl'

    # files = [('./', '.env.production', destination_folder, '.env'), ]
    files = []
    if ssl_enabled == 'y':
        files.append(('./', 'docker-compose-ssl.yml', destination_folder, 'docker-compose.yml'))
        files.append(('./', 'nginx_ssl.conf', destination_folder, 'nginx.conf'))
    else:
        files.append(('./', 'docker-compose.yml', destination_folder, 'docker-compose.yml'))
        files.append(('./', 'nginx.conf', destination_folder, 'nginx.conf'))

    copy_files_to_server(server_ip=HOST_IP, username=username, password=password,
                         file_urls=files)
    print("Finished!")
