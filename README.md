## Raiden Train Demo
A model train  is traveling the world (in our case it's just a circle but hey we all have fanatasy ;) ).
Durint it's travels it passes multiple tollgates asking it to pay for the next section.
The train however has a Raiden node on board and an open payment channel with it's home toll station.
Since the tollgate mafia knows eachother they all have statechannels among them in such a ways as Displayed in Image 1 \
[Image 1 - Network Topology](Images/Network_topology.png) \
With the Raiden Network the train is now able to pay each and every tollage on it's travel in real time, without the need to stop at any point in time. 

## Setup on the "main" Computer
The "main computer" is a UDOO x84 Ultra. It has an embedded arduino 101 which is used to control the train's power supply. 
Therefore the arduino listens to the serial input and gives 3,3V to the GPIO pin 3. This switches the High speed switch on. 
As soon as the the 3,3V are set to 0V the switch turns off and the train doesn't get any power anymore. 
A circuit diagram like illustration can be cound in [Image 2 - Cicruit Diagram](Images/circuit_diagram.jpg).\
The UDOO runs a virtualenvironment with all dependencies provided in the requirements-receiver.txt as well as raiden installed via pip(requirements.txt is WIP).

## Setup on the Raspberry Pi Zero W
The Raspberypi has a Raiden Service in /etc/systemd/system/raiden.service.\
It calls the shell script in ~/demo-train/StartServiceRaiden/StartService.sh during the bootup process. This takes ~5 minutes.\
The raspberry uses two virtualenvironments. One is the "raiden" virtualenv which is used by the shell script to run raiden. Ofcourse it requires raiden to be installed `pip install raiden`. The other one is called "demo" and should be used to run "sender_main.py".

## Blockchain Setup
Right now the demo uses the Kovan Testnet.\
All accounts hold a certain balance of "Raiden Demo Tokens". The Raiden Demo Token as address is `0xDe99085F789f99568f891c6370fB6b7dD4C90323` and it is a minimalistic standard ERC20 Token. The channels as illustrated in Image 1 are all unidirectional with a balance of 1000 and a timeout of 500.



## Processing Setup

Right now we work with a separate server mock, that provides an endpoint with random addresses. The endpoint will be modelled exactly
like in a later production version (same endpoints, same JSON-data).

First, you need to install the python dependencies for the asynchronous server:
It requires Python 3.7 (!Check if this is a problem with raiden!).

`pip install --r requirements.txt`

The http library for processing needs to be put in the processing library folder:

https://github.com/runemadsen/HTTP-Requests-for-Processing/releases

Then the server has to be started:

`hypercorn server_mock:app`


Now run the `processing/processing.pde` in Processing 3
