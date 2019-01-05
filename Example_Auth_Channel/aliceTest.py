from SimulaQron.cqc.pythonLib.cqc import CQCConnection, qubit

import random

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
	num = here.recvClassical()[0]				#### Might need to check it doesn't recieve an# old message
												#### Also might be worth seeing if make num ac#cept a list rather than just the first element
	here.sendClassical(there, 100)  # Used 100 as a "Receipt codeword" might need special number#s for each connection? (if the channels are quiet probs not
	return num																				  #
###############################################################################################

#  Quantum authentification channel #########################################################
###############################################################################################
# Not sure if this is possible/needed.														  #
###############################################################################################

def IceWall():
	# Just a function to stop the code goung further for debugging
	x = 1
	while x == 1:
		pass
	

#####################################################################################################
#
# main
#
def main():
# initialise some working dummys
	n = 5
	flip, basis = BB84State_decider(n)
	print(flip)
# Initialize the connection
	with CQCConnection("Alice") as Alice:
	# Telling Bob how many qubits to expect. Eve would obviously know this too. Does this breach security? Can we avoid it?
		Auth_Send_Classical(Alice, 'Bob', n, False)
	
		for i in range(0,n):  
		# Prepare qubit
			q=Qubit_builder(Alice, flip[i],0) #flip[i], basis[i])<-------------------------------------# Key not randomised active!!!!!!!!!!!!!!!!!!!

		# Send qubit to Bob (via Eve)

			Alice.sendQubit(q, "Eve")
		# Tested and after this point q = "Not active qubit". Now allowed to make the next qubit, 
		# so can prepare next one.

		


#-------Just in case Eve lets alice know whe she is ready for next qubit------------- Redundant%
#-------trigger = 1995 # Random declaration
#-------while trigger != 200:
#-------	trigger = Auth_Recv_Classical(Alice, 'Eve')
#-------
#-------print("Alice knows eve is ready")------------------------------------------------------%

	# End of for loop -------------------------------------------
		
#		print("All qubits sent. Wait for Bob to say he got them.")
#		while trigger != 300:
#			trigger = Auth_Recv_Classical(Alice, 'Bob')
		
					# Encode and send a classical message m to Bob
			#			m = [0, 1, 0, 1, 1]
			#
			#			enc = (m+k) % 2
			#			Alice.sendClassical("Bob", enc)

			#			print("Alice send the message k={} to Bob".format(mes))

##################################################################################################
main()