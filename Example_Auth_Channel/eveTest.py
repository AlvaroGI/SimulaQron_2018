from SimulaQron.cqc.pythonLib.cqc import CQCConnection

import random

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
	x = 1
	while x == 1:
		pass

#####################################################################################################
#
# main
#
def main():
# define Eve_Memory as infinitely large array space.
	Eve_Memory =[]
	n=5  # Need to either recieve this from Alice or have a method of giving up when it seems alice has finished.

# Initialize the connection
	with CQCConnection("Eve") as Eve:
	
		for i in range(0,n):  
		# Receive qubit from Alice
			q = Eve.recvQubit()
		# Attack  -- (q.measure(inplace=True) outputs the post measurement state 
				#  -- (q.measure()) will destroy the qubit and then you can't forward
			Eve_Memory.append([q.measure(inplace=True)])  

		# Forward the qubit to Bob
			Eve.sendQubit(q, "Bob")	
		
		
	# To be sure I have this line to send a message to Alice when Eve is ready for the next qubit.
	# (might not be needed)
	#	Auth_Send_Classical(Eve, 'Alice', 200, False)

	print("\n Eve done, her measurements were: ", Eve_Memory)
	

##################################################################################################
main()


######### Comments------------------------------------
############## I'm a little curious as Eve sometimes prints the fact she recieved the qubit before Alice makes it, it works out ok though and everything should be where i expect it. Maybe the print to terminal isn't as simple as first come first serve?

	#q.release()      # O m g --------- this is a command. There was a remainig qubit stuck in Bob. It went after using it once. But I think its possible to get a back up built up somehow. Anyway. if we can implement this at the beginning of each script without it throwing an error we'd be safe. As itherwise its difficult to spot the leftover qubit.
	# Alterantively can stop comment out alice making more qubits and execute a few times, to flush the qubits out to bobs destructuve measure



## Also used the autheticated msg receipts 100, 200, 300 etc but there is probably a cleaner way of doing this.