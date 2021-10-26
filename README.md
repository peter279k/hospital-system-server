# hospital-system-server

# Installation

- Using `git clone` command to clone this Git repository.
- Using `pip3 install pipenv --user` command to install pipenv if the pipenv command is not installed.
- If using the Ubuntu 18.04+, the pipenv command will be located on /home/user/.local/bin folder.
- Using the `PATH=$PATH:/home/user-name/.local/bin` command to be available for using pipenv command.
- Using the `pipenv install -e .` to install required dependencies(including local dependencies).

# Usage

- Run `pipenv run uvicorn main:app --reload` to boot the system-server application.
- By default the server is running on `localhost:8000` it suggests using the Reverse proxy to set `80` port number to forward requests to above host server.
- The reverse proxy setting can use the Apache or Nginx HTTP server.
- Above step should be done because the `hospital-system` need that.

# Development environment setup

- Following Installation step and the development environment setup will be done.
