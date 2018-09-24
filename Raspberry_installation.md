# How to install Raiden on a Raspberry Pi

## Requirements

### Step 1 - Install requirements
To install the needed requirements run
``sudo apt install git pip`` 

### Step 2 - Create temporary swap
Creation of a temporary swap file to avoid memory overflows.
```
sudo dd if=/dev/zero of=/swap bs=1M count=512
sudo mkswap /swap
sudo swapon /swap
```

### Step 3 - Python version > Python3.5
You will also need a python version >3.5. 
Depending on your OS this can be done by might require a manaual compilation.

## Setting up a virtual environment
We highly recommend using a virtual environment to install raiden. 
Installation instructions can be found in the [documentation](https://virtualenvwrapper.readthedocs.io/en/latest/install.html) \
To create a virtual environment run `mkvirtualenv raiden -p PATH/TO/PYTHON3.5<` \

## Install Raiden
Make sure that you are in your raiden virtualenvironment.
To activate your raiden virtualenv run `workon raiden`.\
You can either install the latest release via [Pypi](https://pypi.org/project/raiden/) by running `pip install raiden`.
Or you can install the latest master using `pip install git+https://github.com/raiden-network/raiden.git`