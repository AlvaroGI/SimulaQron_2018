from SimulaQron.cqc.pythonLib.cqc import CQCConnection, qubit

import random

import numpy as np
import time
from datetime import datetime
import argparse

################################################################################
# PARSE ARGUMENTS
################################################################################
parser = argparse.ArgumentParser()

parser.add_argument('--q', type=int, default='20',
                    help='Number of qubits.')

parser.add_argument('--e', type=float, default='0.1',
                    help='Error threshold (%).')

FLAGS = parser.parse_args()

################################################################################
# PREVIOUS DEFINITIONS
################################################################################
def BB84State_decider(n):
    '''Picks two n-bits strings uniformly at random.
        ---Inputs---
            n: length of the final strings.
        ---Outputs---
            flip: n-bits string (n-bits-long list).
            basis: n-bits string (n-bits-long list).'''
    flip = [random.randint(0, 1) for f in range(0, n)]
    basis = [random.randint(0, 1) for b in range(0, n)]
    return flip, basis

#----------------------------------------

def Qubit_builder(here, flip, basis):
    '''Prepares a qubit.
        ---Inputs---
            here: user (node) who prepares the qubit ('Alice', 'Bob' or 'Eve').
            flip: 0 for state 0 and 1 for state 1.
            basis: 0 for Standard basis, 1 for Hadamard basis.
        ---Outputs---
            q: final qubit.'''
    # Create the qubit
    q=qubit(here)

    # Encode the qubit
    if flip == 1:
        q.X()
    else:
        pass

    if basis == 1:
        q.H()
    else:
        pass

    return q

#----------------------------------------

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

    return num                                                                                #

#----------------------------------------

def IceWall():
    '''Function used for debugging. Not used in the final version.'''
    x = 1
    while x == 1:
        pass

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
    # Define number of qubits, error threshold (%) and generation of BB84 states
    n = FLAGS.q
    error_threshold = FLAGS.e
    flip, basis = BB84State_decider(n)

    # Initialize connection
    with CQCConnection("Alice") as Alice:
        #----------------------------------------
        # DISTRIBUTION OF BB84 STATES
        #----------------------------------------
        print("\n\n-----------------Distribution of BB84 states in progress-----------------")

        # Tell Bob (and Eve) how many qubits to expect (Eve would obviously know this too)
        Auth_Send_Classical(Alice, 'Bob', n, False)
        Auth_Send_Classical(Alice, 'Eve', n, False)

        # Prepare and send n qubits
        for i in range(0,n):
            # Prepare qubit
            q=Qubit_builder(Alice, flip[i],basis[i])

            # Send qubit to Bob (via Eve)
            Alice.sendQubit(q, "Eve") # Comment out this line and execute a few times to flush.

        #----------------------------------------
        # CHECK MATCHING BASES
        #----------------------------------------
        # Receive string associated with Bob's basis
        Bob_basis = Auth_Recv_Classical(Alice, 'Eve')
        Bob_basis = np.array(list(Bob_basis))

        # Get matchig bases indices
        basis = np.array(basis)
        filter_basis = basis ^ Bob_basis
        matching_indices = np.where(filter_basis == 0)[0]

        print("\n Alice used the bases:", basis, "\n   Bob used the bases:", Bob_basis,"\n")
        matches = list(matching_indices)
        print("\n Alice decides to keep measurements number", matches, "(matching bases)")

        # Send matches to Bob (via Eve)
        Auth_Send_Classical(Alice, 'Eve', matches, False)
        time.sleep(1)

        # Create new bit-string for Alice with the measurements corresponding
        # to basis-matching rounds
        print("\n Alice measurements are", flip)
        Alice_Bitstring = []
        for i in matching_indices:
            Alice_Bitstring.append(flip[i])
        print(" Alice's measurements for basis-matching rounds:", Alice_Bitstring)

        #----------------------------------------
        # TEST: ERROR RATE COMPUTATION
        #----------------------------------------
        # Prepare test measurements
        test_indices=list(Auth_Recv_Classical(Alice, 'Bob')) # Test indices suggested by Bob
        test_Bob=list(Auth_Recv_Classical(Alice, 'Bob')) # Bob's test measurements

        test_Alice=[] # Alice's test measurements
        for i in test_indices:
            test_Alice.append(Alice_Bitstring[i])

        print(" Alice tests on measurements number", test_indices, ", whose results are", test_Alice)

        # Compute error rate and abort if necessary
        error_count = 0
        for i in range(0,len(test_Alice)):
            if test_Alice[i] != test_Bob[i]:
                error_count=error_count+1
        print(" Alice concludes there have been ", error_count, "errors \n")

        error_rate = error_count/len(test_Alice)
        print("The error rate is", error_rate)

        if error_rate > error_threshold:
           print("(!) error_rate too high, Alice aborts protocol")
           Auth_Send_Classical(Alice,'Eve', 222, False)
           exit()

        #-------------------------------------------------
        # GENERATE PRIVATE KEY (PRIVACY AMPLIFICATION)
        #-------------------------------------------------
        # Get raw key from the bitstring that includes the test rounds
        Alice_raw_key = get_raw_key(Alice_Bitstring, test_indices)

        # Create the random seed for the randomness extractor
        R_ext = [random.randint(0, 1) for a in range(0, len(Alice_raw_key))]

        # Apply extractor on Alice's raw key
        key = Ext(Alice_raw_key, R_ext)
        print("\n Alice's raw key:", Alice_raw_key)
        print(" Alice's random seed for the extractor:", R_ext)
        print("Alice's private key:", key)

        # Save key into a file
        date_ = str(datetime.now().date())
        time_ = str(datetime.now().time())
        file = open("logs_keys/%s_%s.txt" % (date_,time_),"a")
        file.write(str(key))
        file.close()

        # Send the seed to Bob (via Eve)
        R_ext=list(R_ext)
        Auth_Send_Classical(Alice, 'Eve', R_ext, False)

################################################################################
# RUN
################################################################################
main()
