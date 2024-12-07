import docker
import yaml
from read_settings_deployment import SERVICE_NAME, VERSION, REGISTRY

docker_client = docker.from_env()


def build_docker_image(image_name, tag, dockerfile_path="."):
    print(f"Build Docker image {image_name}:{tag}...")
    image, build_logs = docker_client.images.build(path=dockerfile_path, tag=f"{image_name}:{tag}")

    for log in build_logs:
        print(log)


def push_docker_image(image_name, tag):
    print("Push Docker image...")
    push_logs = docker_client.images.push(repository=f"{image_name}:{tag}")
    # join the logs to a string
    push_logs = "".join([log for log in push_logs])

    # detect error in the log, e.g. {"errorDetail":{"message":"unauthorized: unauthorized to access repository: medical_history/gmr_production, action: push: unauthorized to access repository: medical_history/gmr_production, action: push"},"error":"unauthorized: unauthorized to access repository: medical_history/gmr_production, action: push: unauthorized to access repository: medical_history/gmr_production, action: push"}
    if "error" in push_logs:
        print(push_logs)

    print(push_logs)


def modify_docker_compose_file(docker_compose_file_url, service_name, image_name, tag):
    with open(docker_compose_file_url, 'r') as file:
        doc = yaml.load(file, Loader=yaml.FullLoader)

    doc['services'][service_name]['image'] = f'{image_name}:{tag}'

    with open(docker_compose_file_url, 'w') as file:
        yaml.dump(doc, file)


if __name__ == '__main__':

    image_name = f'{REGISTRY}/{SERVICE_NAME}'
    modify_docker_compose_file(docker_compose_file_url='docker-compose.yml',
                               service_name=SERVICE_NAME,
                               image_name=image_name, tag=VERSION)
    modify_docker_compose_file(docker_compose_file_url='docker-compose-ssl.yml',
                               service_name=SERVICE_NAME,
                               image_name=image_name, tag=VERSION)
    build_docker_image(image_name, VERSION)
    push_docker_image(image_name, VERSION)

    print("Finished!")
