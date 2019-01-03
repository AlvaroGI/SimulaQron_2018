from SimulaQron.cqc.pythonLib.cqc import CQCConnection, qubit
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
    print("Alice's n is"+str(n))
    with CQCConnection("Alice") as Alice:
        for i in range(0,n):
                print("###############")
                print("Alice works on step"+str(i))
                # Generate a key
                #k = random.randint(0, 1)

                # Create a qubit
                q = qubit(Alice) # A qubit object is initialized with the corresponding
                                 #CQCConnection as input and will be in the state |0⟩

                # Generate random BB84 qubit
                k_BB84 = random.randint(0, 3)

                if k_BB84 == 1:
                    q.X() #|1⟩
                    print("Alice sends state |1>")
                    base.append(0)
                    measure.append(1)
                    
                elif k_BB84 == 2:
                    q.H() #|+⟩
                    print("Alice sends state |+>")
                    base.append(1)
                    measure.append(0)
                elif k_BB84 == 3:
                    q.X() #|1⟩
                    q.H() #|-⟩
                    print("Alice sends state |->")
                    base.append(1)
                    measure.append(1)
                else:
                    print("Alice sends state |0>")
                    base.append(0)
                    measure.append(0)

                # Send qubit to Bob (via Eve)
                Alice.sendQubit(q, "Eve")
                
                time.sleep(1)

                # Encode and send a classical message m to Bob
                #m = 0
                #enc = (m + k) % 2
                #Alice.sendClassical("Bob", enc)

                #print("Alice send the message m={} to Bob".format(m))
        print("=========================")        
        print("Alice sends"+str(base))
        Alice.sendClassical("Eve",base)
        
        
        #Alice receiving Bob's string from Eve
        bob_base=0
        bob_base=Alice.recvClassical()
        bob_base=list(bob_base)
        print("Alice's base is"+str(base))
        print("Alice received from Eve"+str(bob_base))
        
        d_dyn=0
        dcard=[]
        keep=[]
        for i in range(len(bob_base)):
            if base[i]!=bob_base[i]:
                print("Alice detected a basis mistmatch")
                d_dyn=d_dyn+1
                dcard.append(i)
            else:
                keep.append(measure[i])
                continue
            
        delta=d_dyn/len(bob_base)
        print("Alice detected a delta of"+str(delta))
        
        #generate the seed
        seed=[]
        for i in range(len(keep)):
            seed.append(random.randint(0,100))
        print("Alice generated seed"+str(seed))
        
        key=0
        for i in range(len(seed)):
            key=key+seed[i]*keep[i]
            
        key=key%2
        
        #Alice sends key to Bob via Eve
        Alice.sendClassical("Eve",seed)
        
        print("Alice generated key"+str(key))
                
                
                
################################################################################
# EXECUTE
################################################################################
main()
