## game-story-outline 

alice had a kingdom 
- in her kingdom relics called 'codex' are important which has secrets o fancient time allowing their kigdom power 
- all the 'codex' are actually quantum infomration encoded into a stabilzier code, os bacily ech of the min \ket{S, \psi} : 
  - \ket{S} is the stabilzer group of the codex
  - \ket{\psi} is the logical qubit state that contains the secret information of the codex 
- only alice knows the stabilzier group of the codex, no on knows the logical state since quantum state cant be copied without ruining (only one copy of ocdex exist)
- the codees used to be quantum system stored in hiddene places 
- but recently the quantum systems whre exposed due to certain natural disaster, 
- Bob , the hacker , is trying to destroy the information in the codex , he's plan to perform a destructive measurement on the physical qubits of the codex, with hopes to destroy (irreversible transfomration induce)  the logical information stored 
- bob has powers to 
  - preapre his own quantum-systems (ancillas for us)
  - perform CZ, H, and multi-qubit rotation gates i.e of the form P(theta) , P \in \mathcal{P}_n over all the system (ancillas + physical qubits of codex)
- he cant do measurement himself and aks his friend Cahrlie to do :
- Charlie can : 
  - perform multi-qubit Pauli Projective measurements (i.e measure an operator P \in  \mathcal{P}_n on all the system (ancillas + physical qubits of codex) ), (reminder aprojective measurement leaves the state in the eigenspace of the measured operator corresponding to the measured eigenvalue, pauli-string has \pm1 eigenvalues) only 
- however charlie is actually an ally of Alice and wants to help her protect the codex

this leads to the game scenario : 

ecah time Bob is attackign a codex, the used will see on his window : 
- the stabilzier generators of the codex (alice can share this info since it doesnt reveal logical info)
- a quantum-circuit that represents Bob's attack plan (the gates he will perform before asking Charlie to measure certain operators), charlie has smuggled this for you, however in the descripttion of the circuit .. : for the multi-qubit rotation gates i.e of the form P(theta), only the operators P is known, but not the angle since Bob can choose it before applying, however Charlie promises that she can later find out what the angles were but only after the measurements are done (this is important since the angle choice can affect the logical measurement outcome)
- and the set of measurements that charlie can perform (charlie is limited in the number of measurements he can do so as not to raise suscpicion to Bob, so the user has to choose wisely) 


----
the basic idea is based around that irreversible (non-unitary operations) must be avoided on the logical system . 

however if the an overall unitary affects the logical system , in a known way , then alice can later correct for it (since she will know the measurement outcomes and the angles of the rotation gates after the measurements are done from charlie) 

---

Given this framework, the user will have to do one or more of the followng things, all in form of secelting options given provided in the screen : 

- choose which measurements charlie should perform (from the list of available measurements) : such measuremetns will always be of the form of multi-qubit Pauli operators
- choose the possible unitary that might have been been applied on the logical system (so that you can revert it) : such unitaries will always be given as sequnce of multi-qubit Pauli rotations gates