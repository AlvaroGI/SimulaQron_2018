from SimulaQron.cqc.pythonLib.cqc import CQCConnection
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
    with CQCConnection("Eve") as Eve:
        for i in range(0,n):
                # Receive qubit from Alice
                q = Eve.recvQubit()

                # Forward the qubit to Bob
                Eve.sendQubit(q, "Bob")


#################################################################################
# EXECUTE
################################################################################
main()
