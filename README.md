# hospital-system-server

# Installation

- Using `git clone` command to clone this Git repository.
- Using `pip3 install pipenv --user` command to install pipenv if the pipenv command is not installed.
- If using the Ubuntu 18.04+, the pipenv command will be located on /home/user/.local/bin folder.
- Using the `PATH=$PATH:/home/user-name/.local/bin` command to be available for using pipenv command.
- Using the `pipenv install -e .` to install required dependencies(including local dependencies).

# Usage

- Run `pipenv run uvicorn main:app --reload` to boot the system-server application.

# Development environment setup

- Following Installation step and the development environment setup will be done.
