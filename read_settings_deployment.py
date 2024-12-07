import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.deployment")

SERVICE_NAME = os.environ.get('SERVICE_NAME')
VERSION = os.environ.get('VERSION')
REGISTRY = os.environ.get('REGISTRY')
HOST_IP = os.environ.get('HOST_IP')
