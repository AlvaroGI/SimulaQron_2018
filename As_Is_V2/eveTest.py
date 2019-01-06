from SimulaQron.cqc.pythonLib.cqc import CQCConnection

import random

import numpy as np

#  Classical authentification channel #########################################################
###############################################################################################
def Auth_Send_Classical(here, there, num, info):                                                      #
    # here = the node sending message (here input would be Alice)                             #
    # there = where to send the message    (must in string form so 'there')                   #
    # num = the number (0<num<256) (message)                                                  #
    # If info = True, then it will give you info about where classical info gets sent
    here.sendClassical(there, num)                                                            #
    while here.recvClassical()[0] != 100:                                                         #
        pass  #Could have a write to file as an error log, that overwrites (No response Here '#s message to There) until
                # satisfied where it will then overwite with a blank or the print line below  #
    
    if info == True:
        print("\n",here, " successfully sent the message, ", num, ", to ", there, ".")            #
    
    return                                                                                    #
                                                                                              #
def Auth_Recv_Classical(here, there):   
# Maybe add flag to say skip if no signal comes after some time?                                                      #

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
# define Eve_Memory as infinitely large array space.
    Eve_Memory = []
    Eve_basis_memory = []

# Initialize the connection
    with CQCConnection("Eve") as Eve:
    
    # Alice tells bob how many qubits there are so he knows when to stop. 
    # Is there a way to do this that doesn't leak security info (length of string to eve)
    # Could maybe do a timeout, but it might cause bob to finish too early if alice or eve have a slower process than expected.
    # I think best to do a combo. Timeout, then send a query to alice with his message length, and the bases he measured in
    # Then if messages are missing, can restar 
        n = Auth_Recv_Classical(Eve, 'Alice')[0]    # I'm hoping since this will only execute once I 
                                                # won't get an error where it remembers past result 
                                                # Checked and the classical channel is empty again
                                                # after sending n. This is good.    
    
        for i in range(0,n):
        # Receive qubit from Alice
            q = Eve.recvQubit()
            
        # Attack  -- (q.measure(inplace=True) outputs the post measurement state 
                #  -- (q.measure()) will destroy the qubit and then you can't forward
           # basis = random.randint(0, 1)  # 50:50 of guessing basis correctly
           # if basis == 1:
            #    q.H()
            
           # Eve_basis_memory.append(basis)
           # Eve_Memory.append(q.measure(inplace=True))%
        # ------------------------------------------------- #

        # Forward the qubit to Bob
            Eve.sendQubit(q, "Bob") 
        print("\n Eve done, her measurements were: ", Eve_Memory)
        print("\n           her basis used were: ", Eve_basis_memory)

        Bob_Basis_Eve = Auth_Recv_Classical(Eve, 'Bob')
        Bob_Basis_Eve = list(Bob_Basis_Eve)
        Auth_Send_Classical(Eve, 'Alice', Bob_Basis_Eve, False)
        
#-------# To be sure I have this line to send a message to Alice when Eve is ready for the next qubit.------Redundant%
#-------# (might not be needed)
#-------    Auth_Send_Classical(Eve, 'Alice', 200, False)------------------------------------------------------------%
       # Rext_Eve = Auth_Recv_Classical(Eve, 'Alice')
       # Rext_Eve = list(Rext_Eve)
       # Auth_Send_Classical(Eve, 'Bob', Rext_Eve, False)  

##################################################################################################
main()


######### Comments------------------------------------
############## I'm a little curious as Eve sometimes prints the fact she recieved the qubit before Alice makes it, it works out ok though and everything should be where i expect it. Maybe the print to terminal isn't as simple as first come first serve?

    #q.release()      # O m g --------- this is a command. There was a remainig qubit stuck in Bob. It went after using it once. But I think its possible to get a back up built up somehow. Anyway. if we can implement this at the beginning of each script without it throwing an error we'd be safe. As itherwise its difficult to spot the leftover qubit.
    # Alterantively can stop comment out alice making more qubits and execute a few times, to flush the qubits out to bobs destructuve measure



## Also used the autheticated msg receipts 100, 200, 300 etc but there is probably a cleaner way of doing this.
