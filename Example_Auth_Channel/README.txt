In this the only thing alice changes is if she does a bit flip (q.X()) operation or not, and everything is in STandard basis, 
so this shows that the quantum channel behaves as expected. 
Also gives an example of how queded up qubits can affect the next full execution. So need to be sure at the beginning
all nodes are flushed of any previous sendQubit commands. Can do this either by running code with Alice not making any more
qubits. Or I think there is a command called q.release or something similar. 
I also suspect that running:
sh run/startAll.sh 
again resets everything to be empty,
