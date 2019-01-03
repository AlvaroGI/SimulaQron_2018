from SimulaQron.cqc.pythonLib.cqc import CQCConnection
import argparse
import time

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
    print("Eve's n is"+str(n))
    with CQCConnection("Eve") as Eve:
        for i in range(0,n):
                print("Eve works on step"+str(i))
                # Receive qubit from Alice
                q = Eve.recvQubit()

                # Forward the qubit to Bob
                Eve.sendQubit(q, "Bob")
                
                
                time.sleep(1)
        
        #Eve forwarding Alice's basis string
        a_base=0
        a_base=Eve.recvClassical()
        a_base=list(a_base)
        print("Eve received from Alice"+str(a_base))
        Eve.sendClassical("Bob",a_base)
        time.sleep(1)
        
        #Eve forwarding Bob's basis string
        b_base=0
        b_base=Eve.recvClassical()
        b_base=list(b_base)
        print("Eve received from Bob"+str(b_base))
        Eve.sendClassical("Alice",b_base)
        time.sleep(1)

#################################################################################
# EXECUTE
################################################################################
main()
