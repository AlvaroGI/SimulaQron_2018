from SimulaQron.cqc.pythonLib.cqc import CQCConnection
import random
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
    base=[]
    measure=[]
    print("Bob's n is"+str(n))
    with CQCConnection("Bob") as Bob:
        for i in range(0,n):
                print("Bob works on step"+str(i))
                # Receive qubit from Alice (via Eve)
                q = Bob.recvQubit()

                # Retreive key
                basis = random.randint(0, 1) # 0 = measure in Z, 1 = measure in X
                if basis == 0:
                    k = q.measure()
                    print("Bob's measurement outcome in Std basis: " + str(k))
                    base.append(0)
                    measure.append(k)
                else:
                    q.H()
                    k = q.measure()
                    print("Bob's measurement outcome in Hadamard basis: " + str(k))
                    base.append(1)
                    measure.append(k)
                    
                time.sleep(1)

                # Receive classical encoded message from Alice
                #enc = Bob.recvClassical()[0]

                # Calculate message
                #m = (enc + k) % 2

                #print("Bob retrived the message m={} from Alice.".format(m))
        
        Bob.sendClassical("Eve",base)
        time.sleep(1)
        
        
        print("Here"+str(base))
        bob_base=0
        bob_base=Bob.recvClassical()
        bob_base=list(bob_base)
        print("Bob received"+str(bob_base))
        print("Bob's base is"+str(base))
        
        d_dyn=0
        dcard=[]
        keep=[]
        for i in range(len(base)):
            if base[i]!=bob_base[i]:
                print("Bob detected a base mismatch")
                d_dyn=d_dyn+1
                dcard.append(i)
            else:
                keep.append(measure[i])
                continue
        delta=d_dyn/len(bob_base)
        
        print(r'Bob\'s $\Delta$ is '+str(delta))
        
        key=sum(keep)%2
        
        print("Bob generated key"+str(key))
        
        
        
        


################################################################################
# EXECUTE
################################################################################
main()
