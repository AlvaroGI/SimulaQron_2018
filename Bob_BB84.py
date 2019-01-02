from SimulaQron.cqc.pythonLib.cqc import CQCConnection
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
    with CQCConnection("Bob") as Bob:
        for i in range(0,n):
                # Receive qubit from Alice (via Eve)
                q = Bob.recvQubit()

                # Retreive key
                basis = random.randint(0, 1) # 0 = measure in Z, 1 = measure in X
                if basis == 0:
                    k = q.measure()
                    print("Bob's measurement outcome in Std basis: " + str(k))
                else:
                    q.H()
                    k = q.measure()
                    print("Bob's measurement outcome in Hadamard basis: " + str(k))

                # Receive classical encoded message from Alice
                #enc = Bob.recvClassical()[0]

                # Calculate message
                #m = (enc + k) % 2

                #print("Bob retrived the message m={} from Alice.".format(m))


################################################################################
# EXECUTE
################################################################################
main()
