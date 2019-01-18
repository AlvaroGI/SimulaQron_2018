from SimulaQron.cqc.pythonLib.cqc import CQCConnection

import random

import numpy as np
import argparse

################################################################################
# PARSE ARGUMENTS
################################################################################
parser = argparse.ArgumentParser()

parser.add_argument('--t', type=int, default='5',
                    help='Number of test bits.')

FLAGS = parser.parse_args()

################################################################################
# PREVIOUS DEFINITIONS
################################################################################
def Auth_Send_Classical(here, there, num, info):                                                      #
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
                                                                                              #
def Auth_Recv_Classical(here, there):                                                         #
    '''Receive classical information.
        ---Inputs---
            here: user (node) who RECEIVES classical info ('Alice', 'Bob' or 'Eve').
            there: user (node) who SENDS classical info ('Alice', 'Bob' or 'Eve').
        ---Outputs---
            num: message received (int).'''
    num = here.recvClassical()

    # Send receipt to the sender ('100' is used as codeword)
    here.sendClassical(there, 100)

    return num                                                                                #

#----------------------------------------

def IceWall():
    '''Function used for debugging. Not used in the final version.'''
    while True:
        pass

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
    # Define number of test bits and parameters for the generation of BB84 states
    Num_to_check=FLAGS.t
    Bob_outputs = [] # Bob's measurements on the qubits (list)
    Bob_basis_memory = [] # Bob's bases (list)
    coun = 0

    # Initialize connection
    with CQCConnection("Bob") as Bob:

        #----------------------------------------
        # DISTRIBUTION OF BB84 STATES
        #----------------------------------------
        # Get number of qubits from Alice
        n = Auth_Recv_Classical(Bob, 'Alice')[0]

        for i in range(0,n):
                # Receive qubit from Alice (via Eve)
                q = Bob.recvQubit()

                # Measure in random basis (Hadamard or Standard)
                basis = random.randint(0, 1)
                if basis == 1:
                    q.H()

                Bob_basis_memory.append(basis)
                Bob_outputs.append(q.measure(inplace=False))

                coun += 1

        #----------------------------------------
        # CHECK MATCHING BASES
        #----------------------------------------
        print("\n----------------------------Check matching bases----------------------------")
        # Send Bob's bases choice to Alice (via Eve)
        Auth_Send_Classical(Bob, 'Eve', Bob_basis_memory, False)

        # Receive list of matching bases from Alice
        matches = list(Auth_Recv_Classical(Bob, 'Eve'))

        print(" Bob is told by Alice to keep measurements number ", matches, "(matching bases)")

        # Create new bit-string for Alice with the measurements corresponding
        # to basis-matching rounds
        print("\n Bob's measurements are ", Bob_outputs)
        Bob_Bitstring = []
        for i in matches:
            Bob_Bitstring.append(Bob_outputs[i])
        print(" Bob's measurements for basis-matching rounds:", Bob_Bitstring)

        #----------------------------------------
        # TEST: ERROR RATE COMPUTATION
        #----------------------------------------
        print("\n--------------------------------Test--------------------------------")
        # Randomly pick test rounds
        test_indices = random.sample(range(0,len(Bob_Bitstring)),round(n/4))
        test_Bob=[]
        for i in test_indices:
            test_Bob.append(Bob_Bitstring[i])
        print("\n Bob wants to test measurements number", test_indices, ", whose results are", test_Bob)
        Auth_Send_Classical(Bob, 'Alice', test_indices, False)
        Auth_Send_Classical(Bob, 'Alice', test_Bob, False)

        #-------------------------------------------------
        # GENERATE PRIVATE KEY (PRIVACY AMPLIFICATION)
        #-------------------------------------------------
        # Receive the random seed from Alice (for extractor)
        R_ext = list(Auth_Recv_Classical(Bob, 'Eve'))
        if R_ext == [222]:
            print("(!) Errorrate is too high, Bob aborts protocol \n")
            exit()
        print("\n Bob's raw key:", R_ext)

        # Apply extractor on Bob's raw key
        key = []
        key = Ext(Bob_Bitstring, R_ext)
        print("Bob's private key:", key)

################################################################################
# RUN
################################################################################
main()
