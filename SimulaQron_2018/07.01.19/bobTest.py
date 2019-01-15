'''
bobTest.py
runs alongside aliceTest.py & eveTest.py when executing run.sh
The set of scripts simulates the BB84 protocol with a powerful eavesdropper eve
'''

from SimulaQron.cqc.pythonLib.cqc import CQCConnection

import random
import time

import numpy as np

# --------------Classical authentification channel-----------------------------% 
# ============================================================================ #
def Auth_Send_Classical(here, there, num, info = False):
	'''                                     
here = the node sending message (here input would be Alice)
there = where to send the message    (must in string form so 'there')
num = the number (0<num<256) (message)
If info = True, then it will give you info about where classical info gets sent
	'''
	here.sendClassical(there, num)  

	while here.recvClassical()[0] != 100:
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
def Ext(x, r):
	ans = np.bitwise_xor(x,r)
	return ans
	
# ==================================================================== Main == #
# ============================================================================ #
def main():
	meas = []
	Bob_basis_memory = []
	Receiving_Qubits = True

# Initialize the connection
	with CQCConnection("Bob") as Bob:	
	# Start recieving ---------------------------------------------------------
		while True:
		# Keep checking if Alice has sent a receipt request
			Receiving_Qubits = bool(Auth_Recv_Classical(Bob, 'Eve')[0])
			if Receiving_Qubits == False:
				break
		# Receive qubit from Alice (via Eve)
			q = Bob.recvQubit()

		# Retreive key
			basis = 1#random.randint(0, 1)  # 50:50 of guessing basis correctly
			if basis == 1:
				q.H()
			
			Bob_basis_memory.append(basis)
			meas.append(q.measure(inplace=False))
		
# ======================================================= Discussion Phase === #
	# Send Alice your Basis choice
		Auth_Send_Classical(Bob, 'Eve', Bob_basis_memory)
		
# ============================================================= Test Phase === #
	# Wait for reply with the decided outcomes to use
		Test_key = Auth_Recv_Classical(Bob, 'Eve')
		Test_key = list(Test_key)
		
	# Form Bitstring with the outcomes tagged in the shared choices
		Test_Bitstring = []
		for i in Test_key:
			Test_Bitstring.append(meas[i])
	
	# Wait to recieve the Public Random key (for extractor)
		R_ext_test = Auth_Recv_Classical(Bob, 'Eve')
		R_ext_test = list(R_ext_test)
		
	# Apply extractor on Bob Bitstring
		keyTest = []
		keyTest = Ext(Test_Bitstring, R_ext_test)
		
	# Send keyTest to Alice to calculate error rate.
		Auth_Send_Classical(Bob, 'Eve', list(keyTest))		

# ============================================================= Real Phase === #
	# Wait for next basis index after Alice checks channel is secure.
		Pub_Key_index = Auth_Recv_Classical(Bob, 'Eve')
		Pub_Key = list(Pub_Key_index)

	# Form Bitstring with the outcomes tagged in the shared choices
		Bob_Bitstring = []
		for i in Pub_Key_index:
			Bob_Bitstring.append(meas[i])
	
	# Wait to receive the Public Random key (for extractor)
		R_ext = Auth_Recv_Classical(Bob, 'Eve')
		R_ext=list(R_ext)		
			
	# Apply extractor on Bob Bitstring
		key = []
		key = Ext(Bob_Bitstring, R_ext)
		print("\n Bob has retreived the secure key", key)
# ============================================================================ #
# ================================ END ======================================= #
main()