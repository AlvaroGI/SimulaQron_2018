from SimulaQron.cqc.pythonLib.cqc import CQCConnection, qubit

import random

import numpy as np
#----------------------------------------
def BB84State_decider(n):
	flip = [random.randint(0, 1) for f in range(0, n)]
	basis = [random.randint(0, 1) for b in range(0, n)]
	return flip, basis
	
#----------------------------------------	
def Qubit_builder(here, flip, basis):
# Create a qubit
	q=qubit(here)	#	q=qubit(Alice, 4) e.g 4 ::  Does is there any argument inputs where we can address or get extra features?
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
def Auth_Send_Classical(here, there, num, info):													  #
	# here = the node sending message (here input would be Alice)							  #
	# there = where to send the message    (must in string form so 'there')					  #
	# num = the number (0<num<256) (message)											      #
	# If info = True, then it will give you info about where classical info gets sent
	here.sendClassical(there, num)	
															  #
	while here.recvClassical()[0] != 100:														  #
		pass  #Could have a write to file as an error log, that overwrites (No response Here '#s message to There) until
				# satisfied where it will then overwite with a blank or the print line below  #
	
	if info == True:
		print("\n",here, " successfully sent the message, ", num, ", to ", there, ".")		  #
		
	return																					  #
																							  #
def Auth_Recv_Classical(here, there):														  #
	# here = the node expecting the message (here input would be Alice)						  #
	# there = Expected sendoer of the message    (must in string form so 'there')			  #
	num = here.recvClassical()				#### Might need to check it doesn't recieve an# old message
												#### Also might be worth seeing if make num ac#cept a list rather than just the first element
	here.sendClassical(there, 100)  # Used 100 as a "Receipt codeword" might need special number#s for each connection? (if the channels are quiet probs not
	return num																				  #
###############################################################################################

def IceWall():
	# Just a function to stop the code goung further for debugging
	x = 1
	while x == 1:
		pass
		
def Ext(x, r):
	ans = np.dot(x,r)
	return ans
	

#####################################################################################################
#
# main
#
def main():
# initialise working dummys
	n = 10
	flip, basis = BB84State_decider(n)
	
# Initialize the connection
	with CQCConnection("Alice") as Alice:
	
	# Telling Bob (and eve) how many qubits to expect. Eve would obviously know this too.
		Auth_Send_Classical(Alice, 'Bob', n, False) # Does this breach security? Can we avoid it?
		Auth_Send_Classical(Alice, 'Eve', n, False)
	
		for i in range(0,n):  
		# Prepare qubit
			q=Qubit_builder(Alice, flip[i],basis[i])

		# Send qubit to Bob (via Eve)
			Alice.sendQubit(q, "Eve")		# Comment out this line and execute a few times to flush.
		# Tested and after this point q = "Not active qubit". Now allowed to make the next qubit, 
		# so can prepare next one.

#-------Just in case Eve lets alice know whe she is ready for next qubit------------- Redundant%
#-------trigger = 1995 # Random declaration
#-------while trigger != 200:
#-------	trigger = Auth_Recv_Classical(Alice, 'Eve')
#-------
#-------print("Alice knows eve is ready")------------------------------------------------------%

	# End of for loop -------------------------------------------
	
	# Receive string associated with Bob's basis
	
		Bad_Locs = []
		Bob_Basis = Auth_Recv_Classical(Alice, 'Bob')
		Bob_Basis = np.array(list(Bob_Basis))
		basis = np.array(basis)
		filter_Basis = basis ^ Bob_Basis
		#keyx2 = np.count_nonzero(filter_Basis)
		
		Good_Locs = np.where(filter_Basis == 0)[0]
		Matching_Choices = Good_Locs.size
		key_length = round(Matching_Choices/1)	# Some notes say the key length should be ~ half 
												# the size of the number of matching qubits, and 
												# Alice randomly picks them. Although I don't see 
												# the benfit of this as we need to send this index
												# publically and eve can just see it. Left it in 
												# for now though. To remove just change that 2 to a 1
												
		Pub_Key_index = Good_Locs #  If want to use fewer than in Good_Locs, can use this random chice 
								  # 	function, but need to condition it so that it doesnt choose 
								  # 	the same state twice.np.random.choice(Good_Locs, key_length)
		print("HEY ALice here \n\n  Alice used:", basis, "\n\n    Bob used:", Bob_Basis)
		

	# Send Pub_key_index to Bob
		Pub_Key = list(Pub_Key_index)
		print("pub key = ", Pub_Key, " PubKey INdex is = ", Pub_Key_index)
		Auth_Send_Classical(Alice, 'Bob', 9, True)
		
		print("flag \n\n\n\n")

		
	# Create new bistring for Alice with chosen index
#		Alice_Bitstring = []
#		for ite in range(0,(Pub_Key_index.size)):
#			print("\n Ite is ", ite, " and flip(5) is ", flip[5])
#			Alice_Bitstring.append(flip[Pub_Key[ite]])
	
		print("\n Alice says the Pub index is ", Pub_Key)

	# Create the random bit string for the extractor
#		R_ext = [random.randint(0, 1) for a in range(0, Pub_Key.size)]
#		[random.randint(0, 1) for f in range(0, n)]
		
	# Apply extractor on Alice Bitstring
#		key = []
#		key = Ext(Alice_Bitstring, R_ext)
		
	# Send this public key over.
#		Auth_Send_Classical(Alice, 'Bob', R_ext, True)
		


	print("Alice end")
		
		
		
		

		
		
		
	
	
	
	
	
	
	
	
	
	
	
		
	#	print("All qubits sent. Wait for Bob to say he got them.")
	#	Auth_Send_Classical(Alice, 'Bob', 99, False)    # Could have Alice send a random number every 
	#	# This function has	wait for receipt built in	# iteration whilst the qubits are sending, so 
	#	print(" Bob texted back! ")						# if eve doesn't know to look for 99 then she
														# won't know when to stop looking or wen to 
														# expect the public key to be sent. Could even
														# send a few extra states from alice that eve 
														# would measure, even though bob stopped already.
														
	# Alice sends the the encrypted message
	
		
					
		

		
					# Encode and send a classical message m to Bob
			#			m = [0, 1, 0, 1, 1]
			#
			#			enc = (m+k) % 2
			#			Alice.sendClassical("Bob", enc)

			#			print("Alice send the message k={} to Bob".format(mes))

##################################################################################################
main()