# How to install Raiden on a Raspberry Pi


## Requirements

### Install Python3.6
Raiden uses >Python3.5.  Therefore you will need a python version >3.5. Depending on your OS you can either installid via PPA `sudo apt install python3.6`. \
But if you run e.g. raspbian you will need to compile Python yourself.\
First install the needed Pre-requisites:
```
sudo apt install build-essential checkinstall
sudo apt install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
```
Next step is downloading Python 3.6 from the [Python site](https://www.python.org/downloads/).
```
cd ~
wget https://www.python.org/ftp/python/3.6.0/Python-3.6.0.tgz
tar xzf Python-3.6.0.tgz
``` 
Next you will need to compile it. This step will take some time, so make sure to grab a cup of coffee.
```
cd Python-3.6.0
sudo bash configure
sudo make altinstall
```
You can check if the installation of Python3.6 was successfull by running ` python3.6 -V`. This should return `Python 3.6.0`


## Setting up a virtual environment
We highly recommend using a virtual environment to install raiden.\
Instructions about how to install virtualenv and virtualenvwrapper can be found in it's [documentation](https://virtualenvwrapper.readthedocs.io/en/latest/install.html). \
To create a virtual environment run `mkvirtualenv raiden -p PATH/TO/PYTHON3.6` 


## Install Raiden
Please make sure that you are in your raiden virtualenvironment.
To activate your raiden virtualenv run `workon raiden`.\
You can either install the latest release via [Pypi](https://pypi.org/project/raiden/) by running `pip install raiden`.
Or you can install the latest master using `pip install git+https://github.com/raiden-network/raiden.git`