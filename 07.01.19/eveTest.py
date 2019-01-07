'''
eveTest.py
runs alongside aliceTest.py & bobTest.py when executing run.sh
The set of scripts simulates the BB84 protocol with a powerful eavesdropper eve
'''

from SimulaQron.cqc.pythonLib.cqc import CQCConnection

import random
import numpy as np
import time

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

def Find_same_basis(Node1, Node2, num = 50.0):
	'''
Input: Node1 = an array of Node1's basis choice (0 = standard, 1 = Hadamard)
Input: Node2 = array of size = Node1. Contains Node2 basis choice.
Input: num = Percentage of the matching cases to use for the key. Default = 1/2 
	'''
	Test_Locs = []
# Print error if Nodes are not of same length
	if len(Node1) != len(Node2):
		print(colours.FAIL, "\n\n Error! \t\t\t The array sent by Node2, did",
			"\n\t\t\t not have equal length to Node1. Node1 has length", 
			"\n\t\t\t", len(Node1), ", and Node2 has length ", len(Node2),".")
		print(colours.BOLD, "\n\t\t\t Killing code...")
		sys.exit

# Else continue
	Combine = np.bitwise_xor(Node1, Node2)
	Real_Locs = list(np.where(Combine == 0)[0])
	Number_of_matches = len(Real_Locs)
	Key_length = round(Number_of_matches*(num/100.0))
	
	if Number_of_matches <= 1:
		Print(colours.Fail, "\n\n Error! There were too few matches! Does", 
			" this look correct?\nAlice chose: ", Alice, "\nBob chose: ", Bob)
		print(colours.BOLD, "\n\t\t\t Killing code...")
		sys.exit

# if not using all cases for the key, need to randomly pick which to use.
	while len(Real_Locs) >= Key_length:
		piece = np.random.choice(Real_Locs)
		Real_Locs.remove(piece)
		Test_Locs.append(piece)
	
	print(Real_Locs , Test_Locs)
	return Real_Locs , Test_Locs
	
# ==================================================================== Main == #
# ============================================================================ #
def main():
	Eve_Memory = []
	Eve_basis_memory = []
	Receiving_Qubits = True
	tally = 0

# Initialize the connection
	with CQCConnection("Eve") as Eve:
		'''
Alice tells bob how many qubits there are so he knows when to stop. 
Is there a way to do this that doesn't leak security info (length of string to 
eve)? Could maybe do a timeout, but it might cause bob to finish too early if 
alice or eve have a slower process than expected. I think best to do a combo. 
Timeout, then send a query to alice with his message length, and the bases he 
measured in. Then if messages are missing, can restart.
		'''
		while Receiving_Qubits == True:
		# Receive qubit from Alice
			q = Eve.recvQubit()

		# Attack
			basis = random.randint(0, 1)  # 50:50 of guessing basis correctly
			if basis == 1:
				q.H()
			
			Eve_basis_memory.append(basis)
			Eve_Memory.append(q.measure(inplace=True))

		# Forward the qubit to Bob after checking he's ready
			Auth_Send_Classical(Eve, 'Bob', 5)
			Eve.sendQubit(q, "Bob")
			
		# Tell Alice you're ready for next qubit and check if she will send more
			Receiving_Qubits = bool(Auth_Recv_Classical(Eve, 'Alice')[0])
			
	# If Alice is finished, eve exits the while loop, now pass this info to bob
		Auth_Send_Classical(Eve, 'Bob', 0)

# ======================================================= Discussion Phase === #
	# Bob Basis choice   (Can match with own)
		Bob_Basis_choice = Auth_Recv_Classical(Eve, 'Bob')
		Bob_Basis_choice = list(Bob_Basis_choice)
		
		time.sleep(1)
		
		Auth_Send_Classical(Eve, 'Alice', Bob_Basis_choice)

# ============================================================= Test Phase === #
	# Test key index (If eve measured in same basis as any at these positions
	# Eve will have the correct outcome. But they won't ever use these as the 
	# real key
		Test_Key_Index = Auth_Recv_Classical(Eve, 'Alice')
		Test_Key_Index = list(Test_Key_Index)
		
		time.sleep(1)
		
		Auth_Send_Classical(Eve, 'Bob', Test_Key_Index)
		
	# random array for test extractor function. Can attempt to use it with 
	# 'test key index' but outcome won't give any info on the real key
		R_ext_test = Auth_Recv_Classical(Eve, 'Alice')
		R_ext_test = list(R_ext_test)
		
		time.sleep(1)
		
		Auth_Send_Classical(Eve, 'Bob', R_ext_test)
		
	# Bobs test key Could work out his measurement outcomes with this, but wont
	# give out any meaningful infp
		Test_key = Auth_Recv_Classical(Eve, 'Bob')
		Test_key = list(Test_key)
		
		print("Eve sees test key ", Test_key)
		
		time.sleep(1)
	
		Auth_Send_Classical(Eve, 'Alice', Test_key)

# ============================================================= Real Phase === #
	# Real key index. Definietly record, if the basis choice matches eve's this 
	# means eve knows with certaintly the correct bit.
		Key_Index = Auth_Recv_Classical(Eve, 'Alice')
		Key_Index = list(Key_Index)
		
		time.sleep(1)

		Auth_Send_Classical(Eve, 'Bob', Key_Index)
		
	# And the real random bitstring for real key. Again useful.
		R_ext = Auth_Recv_Classical(Eve, 'Alice')
		R_ext = list(R_ext)
		
		time.sleep(1)
		
		Auth_Send_Classical(Eve, 'Bob', R_ext)
		
# ===================================================== Eve Analysis Phase === #
	# first check how which basis choices agreed with Bob
		Useful_index , garbage = Find_same_basis(Node1, Node2, 100.0)

	# Then check test key index, see how many elements eve and bob both 
	# correctly guessed
		correct_register = []
		for choice in Useful_index:
			if choice == any(Key_index):
				correct_register.append(choice)
			
	# Then see how much of the extractor function you can work out
		win = 0
		ans = np.bitwise_xor(Eve_Memory, R_ext)
		print("\n Eve's knowledge of the key is:")
		for pos in range(0,len(Eve_Memory)):
			if pos == any(correct_register):
				print("| ",ans(pos)," |")
				win += 1
			else:
				print("| X |")
				
		WinRate = win/len(R_ext)
		
		print("\n Eve knows ", WinRate*100, "% of the key with confidence")
# ============================================================================ #
# ================================ END ======================================= #
main()

'''
----------------------- Comments------------------------------------------------
q.release()  ---------> this is a command. There was a remaining qubit stuck in 
Bob. It went after using it once. But I think its possible to get a back up 
built up somehow. Anyway. if we can implement this at the beginning of each 
script without it throwing an error we'd be safe. As itherwise its difficult to 
spot the leftover qubit.
Alterantively can stop comment out alice making more qubits and execute a few 
times, to flush the qubits out to bobs destructuve measure

Used the autheticated msg receipts 100, 200, 300 etc but there is probably a 
cleaner way of doing this.


Can perhaps send longer messages with https://www.geeksforgeeks.org/program-to-add-two-binary-strings/
and things like np.packbits(), np.unpackbits(), np.binary_repr()

'''