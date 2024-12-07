import os
from dotenv import load_dotenv


def load_env(env_url):
    load_dotenv(dotenv_path=env_url)  # load all environment variables from .env file

    settings = {
        # Deployment
        "SERVICE_NAME": os.environ.get('SERVICE_NAME'),
        "VERSION": os.environ.get('VERSION'),
        "REGISTRY": os.environ.get('REGISTRY'),
        "HOST_IP": os.environ.get('HOST_IP'),
        # Log
        "LOG_LEVEL": os.environ.get('LOG_LEVEL'),
    }

    return settings
