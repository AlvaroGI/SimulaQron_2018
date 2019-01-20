from SimulaQron.cqc.pythonLib.cqc import CQCConnection

import random

import numpy as np
import argparse
import time

################################################################################
# PARSE ARGUMENTS
################################################################################
parser = argparse.ArgumentParser()

parser.add_argument('--a', type=int, default='0',
                    help='Attack (1) or not (0).')

FLAGS = parser.parse_args()

attack = FLAGS.a

################################################################################
# PREVIOUS DEFINITIONS
################################################################################
def Auth_Send_Classical(here, there, num, info):
    '''Send classical information with receipt.
        ---Inputs---
            here: user (node) who SENDS classical info ('Alice', 'Bob' or 'Eve').
            there: user (node) who RECEIVES classical info ('Alice', 'Bob' or 'Eve').
            num: message (int between 0 and 255).
            info: if True, it will print all the information about the process.
        ---Outputs---
            None.'''
    here.sendClassical(there, num)

    # Wait for the receipt from the receiver ('100' is used as codeword)
    while here.recvClassical()[0] != 100:
        pass

    if info == True:
        print("\n",here, " successfully sent the message, ", num, ", to ", there, ".")

    return

#----------------------------------------

def Auth_Recv_Classical(here, there):
    '''Receive classical information.
        ---Inputs---
            here: user (node) who RECEIVES classical info ('Alice', 'Bob' or 'Eve').
            there: user (node) who SENDS classical info ('Alice', 'Bob' or 'Eve').
        ---Outputs---
            num: message received (int).'''
    num = here.recvClassical()

    # Send receipt to the sender ('100' is used as codeword)
    here.sendClassical(there, 100)
    return num

#----------------------------------------

def get_raw_key(xo, test_ind):
    '''Get a list with the elements from xo whose indices are not in test_ind.
        ---Inputs---
            xo: remaining bit string obtained after checking bases-matching (list).
            test_ind: test rounds (list with elements between 0 and len(xo)).
        ---Outputs---
            x: raw key (list).'''
    x = []

    for i in range(0,len(xo)):
        if i in test_ind:
            pass
        else:
            x.append(xo[i])

    return x

#----------------------------------------

def Ext(x, r):
    '''Simple randomness extractor that XORs bit strings x and r.
        ---Inputs---
            x: raw key (n-bits-long list).
            r: extractor seed - uniformly random bit string (n-bits-long list).
        ---Outputs---
            ans: single bit secure key (int).'''
    ans = np.dot(x,r)%2

    return ans

################################################################################
# MAIN
################################################################################
def main():
    # Create lists for Eve's measurements and bases
    Eve_Memory = []
    Eve_basis_memory = []

    # Initialize the connection
    with CQCConnection("Eve") as Eve:

        # Get number of qubits from Alice
        n = Auth_Recv_Classical(Eve, 'Alice')[0]

        #----------------------------------------
        # DISTRIBUTION OF BB84 STATES
        #----------------------------------------
        for i in range(0,n):
            # Receive qubit from Alice
            q = Eve.recvQubit()

            # Attack 1: randomly measuring in Hadamard and Standard bases
            if attack == 1:
                basis = random.randint(0, 1)  # 0.5 of guessing basis correctly
                if basis == 1:
                    q.H()

                Eve_basis_memory.append(basis)
                Eve_Memory.append(q.measure(inplace=True))

            # Attack 2: optimal attack using basis 1/sqrt(2)(|0>+|+>), which yields the
            #           maximum probability of guessing (0.854)
            if attack == 2:
                q.rot_Y(240)
                Eve_Memory.append(q.measure(inplace=True))
                q.rot_Y(32)

            # No attack
                # Do nothing

            # Forward the qubit to Bob
            Eve.sendQubit(q, "Bob")

        if attack == 1:
            print("\n Eve done, her measurements were: ", Eve_Memory)
            print("\n           her bases used were:   ", Eve_basis_memory)
        elif attack == 2:
            print("\n Eve done, her measurements were: ", Eve_Memory)
            print("\n(Her basis was always the same for this attack: 1/sqrt(2)*(|0>+|+>) )")
        else:
            print("\n Eve did not perform any attack.")

        #--------------------------------------------------------------
        # CLASSICAL COMMUNICATION FOR TEST AND PRIVACY AMPLIFICATION
        #--------------------------------------------------------------
        
        #Receive and forward Bob's and Alice's receipt
        rec = Auth_Recv_Classical(Eve, 'Bob')
        rec=list(rec)
        Auth_Send_Classical(Eve, 'Alice', rec, False)
        
        confirm=list(Auth_Recv_Classical(Eve, 'Alice') )
        Auth_Send_Classical(Eve, 'Bob', confirm, False)
        time.sleep(0.3)
        
        
        # Receive and forward string associated with Bob's basis
        Bob_basis_Eve = Auth_Recv_Classical(Eve, 'Bob')
        Bob_basis_Eve = list(Bob_basis_Eve)
        Auth_Send_Classical(Eve, 'Alice', Bob_basis_Eve, False)

        # Receive and forward matching bases
        matching_indices = list(Auth_Recv_Classical(Eve, 'Alice'))
        Auth_Send_Classical(Eve, 'Bob', matching_indices, False)
        #matching_indices = list(matching_indices)

        # Receive and forward test indices
        test_indices = list(Auth_Recv_Classical(Eve, 'Bob')) # Test indices suggested by Bob
        Auth_Send_Classical(Eve, 'Alice', test_indices, False)
        test_Bob = list(Auth_Recv_Classical(Eve, 'Bob')) # Bob's test measurements
        Auth_Send_Classical(Eve, 'Alice', test_Bob, False)

        # Receive and forward random seed
        Rext_Eve = list(Auth_Recv_Classical(Eve, 'Alice'))
        Auth_Send_Classical(Eve, 'Bob', Rext_Eve, False)
        Rext_Eve=list(Rext_Eve)

        time.sleep(2)

        #--------------------------------------------------------------
        # KEY GENERATION
        #--------------------------------------------------------------
        # If Eve performed an attack, try to find the key
        if attack==1 or attack==2:
            # Create new bit-string for Eve with the measurements corresponding
            # to basis-matching rounds
            Eve_Bitstring = []
            for i in matching_indices:
                Eve_Bitstring.append(Eve_Memory[i])

            # Get raw key from the bitstring that includes the test rounds
            Eve_raw_key = get_raw_key(Eve_Bitstring, test_indices)

            if Rext_Eve[0]==222: # 222 is the keyword to abort protocol
                print("\n Eve aborts")
                exit()
            else:
                print("\n Eve's measurements for basis-matching rounds:"+str(Eve_Bitstring))
                print(" Eve's raw key:"+str(Eve_raw_key))
                print(" Eve heard from Alice this random seed:", Rext_Eve)
                key=Ext(Eve_raw_key,Rext_Eve)
                print("Eve generated the key: "+str(key))

################################################################################
# RUN
################################################################################
main()
