# SimulaQron_2018
Quantum cryptography project based on SimulaQron (by QuTech).

Authors: Broekhoven, R., Bryce, E., Gómez Iñesta, Á., Miles, S.

January 2018 - TU Delft

# Problem description
Alice and Bob want to generate a shared private key. To do that, we implement a version of the BB84 protocol. Alice will create a set of BB84 states, measure them, and send them to Bob. Eve may or may not attack (attacks consist in measuring the qubits in different bases). Bob will measure these qubits in the Hadamard or Standard basis (at random). Then, Alice and Bob will check the rounds for which they used the same bases and discard the rest of the rounds. Next, they perform a test on some of the remaining measurements to evaluate the error rate. If this rate is larger than a threshold, they abort the protocol. If the error rate is smaller than the threshold, they perform a privacy amplification step. Alice generates a random seed and sends it to Bob. Finally, they XOR the random seed with the raw key (remaining bits after removing the test rounds) to obtain their shared private key.

**Note**: all the users provide a receipt of the communication after receiving some information.

# Usage
#### Requirements
Be sure to have SimulaQron installed and running on your computer (see [SimulaQron guide](https://softwarequtech.github.io/SimulaQron/html/GettingStarted.html)).

#### Before running
First, be sure to have executed 
```
export NETSIM=YOURPATH/SimulaQron
export PYTHONPATH=YOURPATH:$PYTHONPATH
```
where YOURPATH corresponds to the directory in which you have installed SimulaQron (e.g. a virtualenv).

To start the network with three nodes (Alice, Bob and Eve), run
```
startAll.sh
```
in the 'main' directory.

#### Running the project
You can find the codes needed to run the simulations in the 'main' directory:
* **startAll.sh**: used to start the simulated network.
* **run.sh**: execute this code (`sh run.sh`) to run the simulation. You can externally parse the following arguments:
	- q - number of qubits (up to 20).
	- a - no attack (0), attack measuring in Hadamard or Standard basis at random (1), or attack using the optimal POVM (2).
	- t - fraction of matching-basis rounds used for test.
	- e - error threshold (%).
* **aliceTest.py** / **bobTest.py** / **eveTest.py**: Python codes for Alice, Bob and Eve. Feel free to check them out (they are described in deep with comments inside the files).
* **clean_ports_Mac.sh**: if you are working on OS X, this will close all the processes running on local ports 8801 to 8809.

As an example, `sh run.sh -q 18 -a 0 -t 0.5 -e 0.1` takes 18 qubits in the simulation, no attack is performed, half of the matching-basis rounds are used for test, and the error threshold is 10%.

#### Common errors
Sometimes, a process is running in the local ports that we use to create the simulated network. If you get a related error, you can restart those ports. If you are using OS X, you can simply run `sh clean_ports_Mac.sh`. Note that this will kill all the processes running on local ports 8801 to 8809. Be sure that you are not killing something important.

If there is an issue with the communication in the network, you can restart the local ports, run `sh startAll.sh`, and wait for a while until all the 'remaining communications' from previous processes are done.

# Useful resources
* [This project Github](https://github.com/AlvaroGI/SimulaQron_2018).
* [SimulaQron](https://softwarequtech.github.io/SimulaQron/html/GettingStarted.html).