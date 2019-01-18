# SimulaQron_2018
Quantum cryptography project based on SimulaQron (by QuTech).

Authors: Broekhoven, R., Bryce, E., Gómez Iñesta, Á., Miles, S.

January 2018 - TU Delft

# Problem description
Alice and Bob want to generate a shared private key. To do that, we implement a version of the BB84 protocol. Alice will create a set of BB84 states, measure them, and send them to Bob. Eve may or may not attack (attacks consist in measuring the qubits in different bases). Bob will measure these qubits in the Hadamard or Standard basis (at random). Then, Alice and Bob will check the rounds for which they used the same bases and discard the rest of the rounds. Next, they perform a test on some of the remaining measurements to evaluate the error rate. If this rate is larger than a threshold, they abort the protocol. If the error rate is smaller than the threshold, they perform a privacy amplification step. Alice generates a random seed and sends it to Bob. Finally, they XOR the random seed with the raw key (remaining bits after removing the test rounds) to obtain their shared private key.

**Note**: all the users provide a receipt of the communication after receiving some information.

# Usage
#### Requirements
Before running our project, be sure to have SimulaQron installed and running on your computer (see [SimulaQron guide](https://softwarequtech.github.io/SimulaQron/html/GettingStarted.html))

#### Before running
export
```
startAll
```

#### Running the project
-In the 'main' directory, you can find the codes needed to run the simulations.

#### Common errors
close ports
wait after running startAll

# Useful resources
Getting started (SimulaQron): https://softwarequtech.github.io/SimulaQron/html/GettingStarted.html