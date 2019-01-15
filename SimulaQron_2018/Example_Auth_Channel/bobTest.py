from SimulaQron.cqc.pythonLib.cqc import CQCConnection

#  Classical authentification channel #########################################################
###############################################################################################
def Auth_Send_Classical(here, there, num, info):													  #
	# here = the node sending message (here input would be Alice)							  #
	# there = where to send the message    (must in string form so 'there')					  #
	# num = the number (0<num<256) (message)											      #
	# If info = True, then it will give you info about where classical info gets sent
	here.sendClassical(there, num)															  #
	while here.recvClassical()[0] != 100:														  #
		pass  #Could have a write to file as an error log, that overwrites (No response Here '#s message to There) until
				# satisfied where it will then overwite with a blank or the print line below  #
	if info == True:
		print("\n",here, " successfully sent the message, ", num, ", to ", there, ".")			  #
	
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


def IceWall():
	# Just a function to stop the code goung further for debugging
	while True:
		pass
		
#####################################################################################################
#
# main
#
def main():
# Define Bob_Memory, enc (= Encoded message)
	enc = []

# Initialize the connection
	with CQCConnection("Bob") as Bob:
	
	# Alice tells bob how many qubits there are so he knows when to stop. 
	# Is there a way to do this that doesn't leak security info (length of string to eve)
	# Could maybe do a timeout, but it might cause bob to finish too early if alice or eve have a slower process than expected.
	# I think best to do a combo. Timeout, then send a query to alice with his message length, and the bases he measured in
	# Then if messages are missing, can restart.
	# But for now, lets just get it working:
	
		n = Auth_Recv_Classical(Bob, 'Alice') # I'm hoping since this will only execute once I 
											# won't get an error where it remembers past result	
											# Checked and the classical channel is empty again
											# after sending n. This is good.										
	# Start recieving ------------------------------------------------------
		for i in range(0,n):  	
		# Receive qubit from Alice (via Eve)
			q = Bob.recvQubit()

		# Retreive key
			enc.append([q.measure()])
		

		
		
		
		
		
	# Receive classical encoded message from Alice
#		enc = Bob.recvClassical()[0]
#
#	# Calculate message-----------------------------------------------------
#		m = (enc + k) % 2
#
#		print("Bob retrived the message m={} from Alice.".format(m))

	print("\n Bob done, his measurements were: ", enc)

	

##################################################################################################
main()