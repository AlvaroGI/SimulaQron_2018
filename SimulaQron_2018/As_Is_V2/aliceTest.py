from SimulaQron.cqc.pythonLib.cqc import CQCConnection, qubit

import random

import numpy as np
import time
#----------------------------------------
def BB84State_decider(n):
    flip = [random.randint(0, 1) for f in range(0, n)]
    basis = [random.randint(0, 1) for b in range(0, n)]
    return flip, basis
    
#----------------------------------------   
def Qubit_builder(here, flip, basis):
# Create a qubit
    q=qubit(here)   #   q=qubit(Alice, 4) e.g 4 ::  Does is there any argument inputs where we can address or get extra features?
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
    
#  Classical authentification channel #########################################################
###############################################################################################
def Auth_Send_Classical(here, there, num, info):                                                      #
    # here = the node sending message (here input would be Alice)                             #
    # there = where to send the message    (must in string form so 'there')                   #
    # num = the number (0<num<256) (message)                                                  #
    # If info = True, then it will give you info about where classical info gets sent
    here.sendClassical(there, num)  
                                                              #
    while here.recvClassical()[0] != 100:                                                         #
        pass  #Could have a write to file as an error log, that overwrites (No response Here '#s message to There) until
                # satisfied where it will then overwite with a blank or the print line below  #
    
    if info == True:
        print("\n",here, " successfully sent the message, ", num, ", to ", there, ".")        #
        
    return                                                                                    #
                                                                                              #
def Auth_Recv_Classical(here, there):                                                         #
    # here = the node expecting the message (here input would be Alice)                       #
    # there = Expected sendoer of the message    (must in string form so 'there')             #
    num = here.recvClassical()              #### Might need to check it doesn't recieve an# old message
                                                #### Also might be worth seeing if make num ac#cept a list rather than just the first element
    here.sendClassical(there, 100)  # Used 100 as a "Receipt codeword" might need special number#s for each connection? (if the channels are quiet probs not
    return num                                                                                #
###############################################################################################

def IceWall():
    # Just a function to stop the code goung further for debugging
    x = 1
    while x == 1:
        pass
        
def Ext(x, r):
    ans = np.dot(x,r)%2
    return ans
    

#####################################################################################################
#
# main
#
def main():
# initialise working dummys
    n = 20
    ErrorThreshold=0.2
    flip, basis = BB84State_decider(n)
    print("\n-----------------------------Distribution--------------------------------")
# Initialize the connection
    with CQCConnection("Alice") as Alice:
    
    # Telling Bob (and eve) how many qubits to expect. Eve would obviously know this too.
        Auth_Send_Classical(Alice, 'Bob', n, False) # Does this breach security? Can we avoid it?
        Auth_Send_Classical(Alice, 'Eve', n, False)
    
        for i in range(0,n):  
        # Prepare qubit
            q=Qubit_builder(Alice, flip[i],basis[i])

        # Send qubit to Bob (via Eve)
            Alice.sendQubit(q, "Eve")       # Comment out this line and execute a few times to flush.
        # Tested and after this point q = "Not active qubit". Now allowed to make the next qubit, 
        # so can prepare next one.

#-------Just in case Eve lets alice know whe she is ready for next qubit------------- Redundant%
#-------trigger = 1995 # Random declaration
#-------while trigger != 200:
#-------    trigger = Auth_Recv_Classical(Alice, 'Eve')
#-------
#-------print("Alice knows eve is ready")------------------------------------------------------%

    # End of for loop -------------------------------------------
    
    # Receive string associated with Bob's basis
    
        Bad_Locs = []
        Bob_Basis = Auth_Recv_Classical(Alice, 'Eve')
        Bob_Basis = np.array(list(Bob_Basis))
        basis = np.array(basis)
        filter_Basis = basis ^ Bob_Basis
        #keyx2 = np.count_nonzero(filter_Basis)
        
        Good_Locs = np.where(filter_Basis == 0)[0]
        Matching_Choices = Good_Locs.size
        key_length = round(Matching_Choices/1)  # Some notes say the key length should be ~ half 
                                                # the size of the number of matching qubits, and 
                                                # Alice randomly picks them. Although I don't see 
                                                # the benfit of this as we need to send this index
                                                # publically and eve can just see it. Left it in 
                                                # for now though. To remove just change that 2 to a 1
                                                
        Pub_Key_index = Good_Locs #  If want to use fewer than in Good_Locs, can use this random chice 
                                  #     function, but need to condition it so that it doesnt choose 
                                  #     the same state twice.np.random.choice(Good_Locs, key_length)
        print("\n Alice used the basisses:", basis, "\n   Bob used the basisses:", Bob_Basis,"\n")
        

    # Send Pub_key_index to Bob
        Pub_Key = list(Pub_Key_index)
        print("\n Alice says to keep measurements", Pub_Key) 
        Auth_Send_Classical(Alice, 'Eve', Pub_Key, False)
        time.sleep(1)  
    # Create new bistring for Alice with chosen index
        print("\n Alice Measurements are ", flip)
        Alice_Bitstring = []
        for i in Pub_Key_index:
           # print("\n useful measurement  is ", i, " and measurement is ", flip[i])
            Alice_Bitstring.append(flip[i])
        print("\n The measurements Alice can use for extraction are", Alice_Bitstring)
    
    # Determine error rate
        Check_Bitstring_Index=list(Auth_Recv_Classical(Alice, 'Bob'))
        Check_Bitstring_Bob=list(Auth_Recv_Classical(Alice, 'Bob'))
        Check_Bitstring_Alice=[]
        for i in Check_Bitstring_Index:
            Check_Bitstring_Alice.append(Alice_Bitstring[i])
        print("Alice checks the measurements", Check_Bitstring_Index, "which are", Check_Bitstring_Alice)
        ErrorAmount=0
        for i in range(0,len(Check_Bitstring_Alice)):
            if Check_Bitstring_Alice[i] != Check_Bitstring_Bob[i]:
                ErrorAmount=ErrorAmount+1        
        print("Alice concludes there have been ", ErrorAmount, "errors \n")
        ErrorRate=ErrorAmount/len(Check_Bitstring_Alice)
        print("The Errorrate is", ErrorRate)
        if ErrorRate > ErrorThreshold:
           print("Errorrate too high, Alice aborts protecol \n")
           Auth_Send_Classical(Alice,'Eve', 222, False)
           exit()   
    # Create the random bit string for the extractor
        R_ext = [random.randint(0, 1) for a in range(0, Pub_Key_index.size)]
        print("\n Alice random part of the extractor is", R_ext)
#       [random.randint(0, 1) for f in range(0, n)]
        
    # Apply extractor on Alice Bitstring
        key = []
        key = Ext(Alice_Bitstring, R_ext)
        print("\n Alice has retreived the secure key", key)

    # Send the random part over.
        R_ext=list(R_ext)
        Auth_Send_Classical(Alice, 'Eve', R_ext, False)
        



        
        
        
        

        
        
        
    
    
    
    
    
    
    
    
    
    
    
        
    #   print("All qubits sent. Wait for Bob to say he got them.")
    #   Auth_Send_Classical(Alice, 'Bob', 99, False)    # Could have Alice send a random number every 
    #   # This function has wait for receipt built in   # iteration whilst the qubits are sending, so 
    #   print(" Bob texted back! ")                     # if eve doesn't know to look for 99 then she
                                                        # won't know when to stop looking or wen to 
                                                        # expect the public key to be sent. Could even
                                                        # send a few extra states from alice that eve 
                                                        # would measure, even though bob stopped already.
                                                        
    # Alice sends the the encrypted message
    
        
                    
        

        
                    # Encode and send a classical message m to Bob
            #           m = [0, 1, 0, 1, 1]
            #
            #           enc = (m+k) % 2
            #           Alice.sendClassical("Bob", enc)

            #           print("Alice send the message k={} to Bob".format(mes))

##################################################################################################
main()
