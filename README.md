# GenLab-Frontend

## Introduction

GenLab-Frontend, is the web UI for the GenLab system.

## Development evnvironment setup
### Prerequisites
- NVM:  
  Follow the instruction to install https://github.com/nvm-sh/nvm
  - See the Node.js version from the Dockerfile: 
    - Find the version in Dockerfile e.g. "FROM node:18.16.1"
    - Install the same version of Node.js with NVM
    ```bash
    nvm install 18.16.1
    ```
- Vue CLI:   
Install the Vue Command Line Interface globally.
```bash
npm install -g @vue/cli
```
- NPM:  
Install the required packages
```bash
npm install
```

### Run the development server
cd into the project directory and run it:
```bash
npm run serve
```

### View in the browser

The following urls and parameters load the sample his_data, which were fake cases for demo.
his_data_id=1, 2, 3, or 4 will load the sample his_data for demo.

```
// Progress Note Demo
http://localhost:8080/?his_data_id=1

// Weekly Summary Demo
http://localhost:8080/?his_data_id=2

// Sensitive Information Redaction Demo
http://localhost:8080/?his_data_id=3

// Discharge Note
http://localhost:8080/?his_data_id=4

```

## Production deployment

### Prerequisites

- Ubuntu server 22.04
- Docker installed on the server
- A private Docker registry

### Deployment steps
You may deploy with the deploy.py script, or manually deploy with the following steps.
#### Deploy with deploy.py
Because it uses python script to deploy, you need to activate the python virtual environment first.
1. Activate the python virtual environment. It is recommended to use the env created by GenLab backend project.
```bash
conda activate <virtual_environment_name> 
```
2. Run the deploy.py script
```bash
python deploy.py
```
3. The script will ask you to input the docker image version, the server user name, and password. And it will create the docker image, push it to the registry, and copy the docker-compose.yml and nginx.conf files to ~/service/genlab_fe/{version} on the server.
4. Login to the server, cd into the folder, check if the file is correct, and run the docker-compose.yml file
```bash
cd ~/service/genlab_fe/{version}
nano docker-compose.yml # check the docker-compose.yml content is correct
cd ~/service/genlab_fe/{previous_version}
docker-compose down
cd ~/service/genlab_fe/{version}
docker-compose up -d
```
#### Manually deploy

1. Build the docker image for the frontend from the Dockerfile_vue

```bash
docker build -t <image>:<tag> -f Dockerfile .
```

2. Login to the docker registry (if you have not logged in)

```bash
docker login <docker_registry_url>
```

3. Push the docker image to the docker registry

```bash
docker push <docker_registry_url>/genlab_fe:<version>
```

4. Copy the docker-compose.yml (or docker-compose-ssl.yml if using SSL) to the server

```bash
scp docker-compose.yml <user>@<server_ip>:<path>
```

5. Copy the nginx.conf (nginx_ssl.conf if using SSL) to the server

```bash
scp nginx.conf <user>@<server_ip>:<path>
```

6. Optional: If you don't use SSL, please skip this step. Copy the SSL key and crt files to the server.

```bash
scp <key_file> <user>@<server_ip>:<path>
scp <crt_file> <user>@<server_ip>:<path>
scp <chain_crt_file> <user>@<server_ip>:<path>
```

7. Run the docker-compose.yml file

```bash
cd <path>
docker-compose down
docker-compose up -d
```

### Backend

Refer to the backend project's README.md for the deployment instructions.
