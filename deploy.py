import getpass

import docker
import paramiko
import yaml
from scp import SCPClient

from my_log import configure_logger, debug, info, error
from env_config import load_env

logger = configure_logger(__name__, 'deploy.log', level=info)

try:
    docker_client = docker.from_env()
except Exception as e:
    logger.error(e)
    logger.error("Please check if the docker daemon is running.")
    exit(1)


def build_docker_image(image_name, tag, path, dockerfile):
    logger.info(f"Build Docker image {image_name}:{tag}...")
    logger.debug(f"dockerfile: {path}/{dockerfile}")
    image, build_logs = docker_client.images.build(path=path,
                                                   dockerfile=dockerfile,
                                                   tag=f"{image_name}:{tag}")

    for log in build_logs:
        logger.debug(log)


def push_docker_image(image_name, tag):
    logger.info(f"Push Docker image: {image_name}:{tag}...")
    push_logs = docker_client.images.push(repository=f"{image_name}:{tag}")

    # join the logs to a string because the original logs are stream text a character by a character.
    push_logs = "".join([log for log in push_logs])

    # detect error in the log, e.g. {"errorDetail":{"message":"unauthorized: unauthorized to access repository: medical_history/genlab_production, action: push: unauthorized to access repository: medical_history/genlab_production, action: push"},"error":"unauthorized: unauthorized to access repository: medical_history/genlab_production, action: push: unauthorized to access repository: medical_history/genlab_production, action: push"}
    if "error" in push_logs:
        logger.error(push_logs)

    logger.debug(push_logs)


def modify_docker_compose_file(docker_compose_file_url, service_name, image_name, tag):
    with open(docker_compose_file_url, 'r') as file:
        doc = yaml.load(file, Loader=yaml.FullLoader)

    print(f"Replace the {service_name} image with {image_name}:{tag}")
    doc['services'][service_name]['image'] = f'{image_name}:{tag}'

    with open(docker_compose_file_url, 'w') as file:
        yaml.dump(doc, file)


def ask_staging_or_production():
    while True:
        choice = input("Staging or Production? (s/p): ")
        if choice == "s":
            return "staging"
        elif choice == "p":
            return "production"
        else:
            logger.info("Please enter s or p.")


def ask_server_username_and_password():
    _username = input("Enter your username: ")
    _password = getpass.getpass("Enter your password: ")
    return _username, _password


def get_server_ip():
    _server_ip = input("Enter the server IP or domain name: ")
    return _server_ip


def ask_ssl():
    choice = input("Enable SSL? (y/n): ")
    if choice == 'y' or choice == 'n':
        return choice
    else:
        logger.info("Please enter 'y' or 'n'")
        return ask_ssl()


def copy_files_to_server(server_ip, username, password, file_urls):
    """
    file_urls: list of tuples (source_folder, source_file_name,
    destination_folder, destination_file_name)
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

        # Create the remote directory (it will not do anything if the directory already exists)
        ssh.exec_command(f'mkdir -p {destination_folder}')
        source_file_url = f'{source_folder}/{source_file_name}'

        logger.info(f"scp {source_file_url} {username}@{server_ip}:{destination_folder}/{destination_file_name}")
        scp.put(source_file_url, f'{destination_folder}/{destination_file_name}')

    scp.close()
    ssh.close()


def ask_version(env_url) -> str:
    """
    Ask the version number of the service.
    1. Read the version number from the .env file according to the staging_or_production
    2. Ask the user if the version number is correct
    3. If not, ask the user to enter the correct version number
    4. Save the version number to the .env file
    5. Return the version number
    :return version_number: str
    """
    version_number = None
    logger.debug(env_url)
    with open(env_url, 'r') as file:
        lines = file.readlines()
        for line in lines:
            logger.debug(line)
            if line.startswith("VERSION"):
                version_number = line.split('=')[1].strip().strip("'")
                break
    if version_number is None:
        raise Exception(f"Cannot find the version number in the {env_url}. Please check the file. "
                        f"If there is no version=<replace with your version>, please add it.)")

    logger.info(f"Current version number: {version_number}")
    is_version_number_correct = input("Is the version number correct? (y/n): ")
    if is_version_number_correct == "y":
        return version_number
    elif is_version_number_correct == "n":
        version_number = input("Enter the correct version number: ")
        with open(env_url, 'w') as file:
            for line in lines:
                if line.startswith("version"):
                    line = f"version = '{version_number}'\n"
                file.write(line)
        return version_number
    else:
        logger.info("Incorrect input, you should enter y or n. Please try again.")
        return ask_version(env_url)


def deploy(service_name, version, staging_or_production, host_ip, registry, ssl_enabled):
    # Build and push Docker image
    docker_image_name = f'{registry}/{service_name}' if staging_or_production == 'production' else f'{registry}/{service_name}_staging'

    if ssl_enabled == 'y':
        modify_docker_compose_file(docker_compose_file_url='docker-compose-ssl.yml',
                                   service_name=service_name,
                                   image_name=docker_image_name, tag=version)
    else:
        modify_docker_compose_file(docker_compose_file_url='docker-compose.yml',
                                   service_name=service_name,
                                   image_name=docker_image_name, tag=version)
    if staging_or_production == 'staging':
        dockerfile_name = 'Dockerfile_staging'
    elif staging_or_production == 'production':
        dockerfile_name = 'Dockerfile'
    else:
        raise Exception("staging_or_production is not staging or production.")

    build_docker_image(docker_image_name, version, ".", dockerfile_name)

    # push_docker_image(docker_image_name, version)

    # scp files to server
    destination_folder = f'~/service/{service_name}/{version}'

    files = []

    if ssl_enabled == 'y':
        files.append(('./', 'docker-compose-ssl.yml', destination_folder, 'docker-compose.yml'))
        files.append(('./', 'nginx_ssl.conf', destination_folder, 'nginx.conf'))
    else:
        files.append(('./', 'docker-compose.yml', destination_folder, 'docker-compose.yml'))
        files.append(('./', 'nginx.conf', destination_folder, 'nginx.conf'))

    # copy_files_to_server(server_ip=host_ip, username=username, password=password, file_urls=files)
    logger.info("Finished!")




if __name__ == '__main__':
    # Select staging or production and import env settings
    staging_or_production = ask_staging_or_production()

    if staging_or_production == "staging":
        env_file_url = '.env.staging'
    elif staging_or_production == "production":
        env_file_url = '.env.production'
    else:
        raise Exception("staging_or_production is not staging or production.")

    config = load_env(env_file_url)
    SERVICE_NAME = config['SERVICE_NAME']
    REGISTRY = config['REGISTRY']
    HOST_IP = config['HOST_IP']
    LOG_LEVEL = config['LOG_LEVEL']
    logger = configure_logger(__name__, 'deploy.log', level=LOG_LEVEL)

    VERSION = ask_version(env_file_url)
    username, password = ask_server_username_and_password()
    # ssl_enabled = ask_ssl()
    ssl_enabled = 'n'
    image_name = f"{SERVICE_NAME}:{VERSION}" if staging_or_production == "production" else f"{SERVICE_NAME}_staging:{VERSION}"
    confirm_deploy = input(f"================================\n"
                           f"Registry: {REGISTRY}\n"
                           f"{image_name}\n"
                           f"Env file: {env_file_url}\n"
                           f"Server: {username}@{HOST_IP}\n"
                           f"With SSL: {ssl_enabled}\n"
                           f"================================\n"
                           f"Are you sure to deploy? (y/n): ")
    if confirm_deploy == "y":
        deploy(service_name=SERVICE_NAME, version=VERSION,
               staging_or_production=staging_or_production,
               host_ip=HOST_IP, registry=REGISTRY, ssl_enabled=ssl_enabled)
    else:
        logger.info("Deploy cancelled.")
