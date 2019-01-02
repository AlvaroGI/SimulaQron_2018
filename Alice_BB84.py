from SimulaQron.cqc.pythonLib.cqc import CQCConnection, qubit
import random
import argparse

################################################################################
# PARSE ARGUMENTS
################################################################################
parser = argparse.ArgumentParser()

parser.add_argument('--n', type=int, default='1',
                    help='Number of qubits.')

FLAGS = parser.parse_args()

n = FLAGS.n

#################################################################################
# MAIN
################################################################################
def main():

    # Initialize the connection
    with CQCConnection("Alice") as Alice:
        for i in range(0,n):
                # Generate a key
                #k = random.randint(0, 1)

                # Create a qubit
                q = qubit(Alice) # A qubit object is initialized with the corresponding
                                 #CQCConnection as input and will be in the state |0⟩

                # Generate random BB84 qubit
                k_BB84 = random.randint(0, 3)

                if k_BB84 == 1:
                    q.X() #|1⟩
                    print("Alice sends state |1⟩")
                elif k_BB84 == 2:
                    q.H() #|+⟩
                    print("Alice sends state |+⟩")
                elif k_BB84 == 3:
                    q.X() #|1⟩
                    q.H() #|-⟩
                    print("Alice sends state |-⟩")
                else:
                    print("Alice sends state |0⟩")

                # Send qubit to Bob (via Eve)
                Alice.sendQubit(q, "Eve")

                # Encode and send a classical message m to Bob
                #m = 0
                #enc = (m + k) % 2
                #Alice.sendClassical("Bob", enc)

                #print("Alice send the message m={} to Bob".format(m))


################################################################################
# EXECUTE
################################################################################
main()
