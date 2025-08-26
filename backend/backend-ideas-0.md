i will enter n_alice and n_bob values for alcie and bobs qubit number 

initalize bob squbit to all plus state, for alice i will enter k_alice  use ` generate_stabilizer_generators` to genrate k stabilzier generators for alices system of n_alice  qubits. 

the qubit indices sohuld be such that alices qubits are from 1 to n_alice and bobs qubits are from n_alice+1 to n_alice +1 + n_bob 

then i need a random function that creates a ransdom CZ entangling operation between alice and bob's qubits, it can also create cz between bobs qubits, but not between alices qubits.


write a funciont ot compute the updates stablziers generators of alice and bobs stabilzier generators (k_alice + n_bob number of them) after the CZ entanglin from the previous function 


a fucntion that woud take the given stabilixer genrators (here from the above function) and would compute a set of independent pauli-strings where such that they all anti-commute with a singel genrator of the input stabilizer generators and commute with all the others, and returns this set of anti-commmutnge generators

then there should bea function that would take the anti-commuting generators from the previous function and would rearrage the genrators (keeping them from the same group) such that there atleast few such that there support are only on bobs qubits (i.e. they have identity on alices qubits)



