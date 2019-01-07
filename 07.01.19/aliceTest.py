'''
aliceTest.py
runs alongside bobTest.py & eveTest.py when executing run.sh
The set of scripts simulates the BB84 protocol with a powerful eavesdropper eve
'''

from SimulaQron.cqc.pythonLib.cqc import CQCConnection, qubit

import random
import numpy as np
import time

class colours:
	WARNING = '\033[93m'
	Fail = '\033[91m'
# ============================================================================ #
def BB84State_decider(n):
	flip = [random.randint(0, 1) for f in range(0, n)]
	basis = [random.randint(0, 1) for b in range(0, n)]
	return flip, basis
# ============================================================================ #
# ============================================================================ #
def Qubit_builder(here, flip, basis):
# Create a qubit
	q=qubit(here)   
# Encode the qubit 
	if flip == 1:
		q.X()
		
	if basis == 1:
		q.H()

	return q
# ============================================================================ #
# --------------------------------- Classical authentification channel --------% 
# ============================================================================ #
def Auth_Send_Classical(here, there, num, info = False):
	'''                                     
here = the node sending message (here input would be Alice)
there = where to send the message    (must in string form so 'there')
num = the number (0<num<256) (message)
If info = True, then it will give you info about where classical info gets sent
	'''
	here.sendClassical(there, num)  

	while here.recvClassical(timout=10)[0] != 100:
		pass
		
	if info == True:
		print("\n",here, " successfully sent the message, ", num,
			", to ", there, ".")

	return

# ============================================================================ #
def Auth_Recv_Classical(here, there):
	'''
here = the node expecting the message (here input would be Alice)
there = Expected sendoer of the message (must be in string form so 'there')
	'''
	num = here.recvClassical(timout=10)
	here.sendClassical(there, 100)   # Used 100 as a "Receipt codeword" 
	return num
# ============================================================================ #
# ============================================================================ #
def Find_same_basis(Node1, Node2, num = 50.0):
	'''
Input: Node1 = an array of Node1's basis choice (0 = standard, 1 = Hadamard)
Input: Node2 = array of size = Node1. Contains Node2 basis choice.
Input: num = Percentage of the matching cases to use for the key. Default = 1/2 
	'''
	Test_Locs = []
# Print error if Nodes are not of same length
	if len(Node1) != len(Node2):
		print("\n\n Error! \t\t\t The array sent by Node2, did",
			"\n\t\t\t not have equal length to Node1. Node1 has length", 
			"\n\t\t\t", len(Node1), ", and Node2 has length ", len(Node2),".")

# Else continue
	Combine = np.bitwise_xor(Node1, Node2)
	Real_Locs = list(np.where(Combine == 0)[0])
	Number_of_matches = len(Real_Locs)
	Key_length = round(Number_of_matches*(num/100.0))
	
	if Number_of_matches <= 1:
		Print("\n\n Error! There were too few matches! Does", 
			" this look correct?\nAlice chose: ", Alice, "\nBob chose: ", Bob)

# if not using all cases for the key, need to randomly pick which to use.
	while len(Real_Locs) >= Key_length:
		piece = np.random.choice(Real_Locs)
		Real_Locs.remove(piece)
		Test_Locs.append(piece)
	
	return Real_Locs , Test_Locs
# ============================================================================ #
# ============================================================================ #
def Ext(x, r):
	ans = np.bitwise_xor(x,r)
	return ans
# ============================================================================ #
# ============================================================================ #
def Error_rate(Node1, Node2):
	'''
Input: Node1 and Node2. Both arrays of equal size.
Calculates rate from suming the number f events where Node1 and Node2 had
different value at the same index position. 
Then number of error events/total number of elements
	'''
	print(" n1 = ", Node1, "n2 = ", Node2)
	combine = Node1 ^ Node2
	Rate = sum(combine)/len(Node1)
	return Rate
# ==================================================================== Main == #
# ============================================================================ #
def main():
# initialise working dummys
	n = 50
	flip, basis = BB84State_decider(n)
	Security_requirement = 0.3

# Initialise the connection
	with CQCConnection("Alice") as Alice:
	
		for i in range(0,n):  
		# Prepare qubit
			q=Qubit_builder(Alice, flip[i],basis[i])

		# Send qubit to Bob (via Eve)
			Alice.sendQubit(q, "Eve")
			time.sleep(1)
			
		# Check Eve is ready for the next qubit (using Auth_classical channel
			if i == n-1:
				Auth_Send_Classical(Alice, 'Eve', 0)
			else:
				Auth_Send_Classical(Alice, 'Eve', 5)
				
# ======================================================= Discussion Phase === #
		print("\n At discussion phase.")
	# Receive string associated with Bob's basis
		Bad_Locs = []
		Bob_Basis = Auth_Recv_Classical(Alice, 'Eve')
		Bob = list(Bob_Basis)
	# Find where Alice and Bob measured in the same basis
		PubKey, Pub_Test = Find_same_basis(basis, Bob)
		
# ============================================================= Test Phase === #
		print("\n At test phase.")
	# Send Test_Key to Bob
		Pub_Test = list(Pub_Test)
		Auth_Send_Classical(Alice, 'Eve', Pub_Test)
		time.sleep(1)
		
	# Create the random bit string for the extractor
		R_ext_Test = [random.randint(0, 1) for tt in range(0, len(Pub_Test))]
		
	# Send the random part over.
		R_ext_Test=list(R_ext_Test)
		Auth_Send_Classical(Alice, 'Eve', R_ext_Test)
		  
	# Create new bitstring for Test with test index
		Test_Bitstring = []
		for i in Pub_Test:
			Test_Bitstring.append(flip[i])
		
	# Apply extractor on Test Bitstring
		key_Test = []
		key_Test = Ext(Test_Bitstring, R_ext_Test)

	# Wait for Bob to send his test key.
		Bob_Test = Auth_Recv_Classical(Alice, 'Eve')
		print("\nAlice saw the key was : ", Bob_Test)
		Bob_Test = list(Bob_Test)
		print(" \n and alice saw : ", Bob_Test)
		
	# Find error rate
		Rate = Error_rate(key_Test, Bob_Test)
		print("\n\aRate of error was calculated to be ", Rate*100, "%.")
		if Rate > Security_requirement:
			print("\n Error rate was larger than the set security requirement.")
		
# ============================================================= Real Phase === #
		print("\n At real phase.")
	# Send Pub_key_index to Bob
		Auth_Send_Classical(Alice, 'Eve', PubKey, True)
		time.sleep(1)
		print(PubKey)
		
	# Create the random bit string for the extractor
		R_ext = [random.randint(0, 1) for a in range(0, len(PubKey))]
		
	# Send the random part over.
		R_ext=list(R_ext)
		Auth_Send_Classical(Alice, 'Bob', R_ext)
		  
	# Create new bitstring for Alice with chosen index
		Alice_Bitstring = []
		for i in PubKey:
			Alice_Bitstring.append(flip[i])
		
	# Apply extractor on Alice Bitstring
		key = []
		key = Ext(Alice_Bitstring, R_ext)
		print("\n Alice has retrieved the secure key", key)
# ============================================================================ #
# ================================ END ======================================= #
main()