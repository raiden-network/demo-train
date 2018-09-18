## Raiden Train Demo
A model train  is traveling the world (in our case it's just a circle but hey we all have fanatasy ;) ).
Durint it's travels it passes multiple tollgates asking it to pay for the next section.
The train however has a Raiden node on board and an open payment channel with it's home toll station.
Since the tollgate mafia knows eachother they all have statechannels among them in such a ways as Displayed in Image 1 \
[Image 1 - Network Topology]("~/demo/Images/Network_topology.png") \
With the Raiden Network the train is now able to pay each and every tollage on it's travel in real time, without the need to stop at any point in time. 

## Setup on the "main" Computer
The main computer requires on virtualenvironment with all dependencies as well as raiden installed via pip(requirements.txt is WIP).

## Setup on the Raspberry Pi Zero W
The Raspberypi has a Raiden Service in /etc/systemd/system/raiden.service.\
It calls the shell script in ~/demo/StartServiceRaiden/StartService.sh during the bootup process. This takes ~5 minutes.\
The raspberry uses two virtualenvironments. One is the "raiden" virtualenv which is used by the shell script to run raiden. Ofcourse it requires raiden to be installed `pip install raiden`. The other one is called "demo" and should be used to run "sender_main.py".

## Blockchain Setup
Right now the demo uses the Ropsten Testnet.\
All accounts hold a certain balance of "Raiden Demo Tokens". The Raiden Demo Token as address is `0xed6612cf4E07982490b8512acC51ff7c474438B0` and it is a minimalistic standard ERC20 Token. The channels as illustrated in Image 1 are all bilateral with a balance of 1000 and a timeout of 500.

