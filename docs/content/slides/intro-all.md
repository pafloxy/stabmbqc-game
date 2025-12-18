---
date-init: Thursday, December 18th 2025, 11:47:23 pm
date-modified: Thursday, December 18th 2025, 11:57:04 pm
---

 Welcome Professor (*upto HDR) Ollivier. Glad you accepted to help us!

Our ancient kingdom has stored its most precious secrets as quantum states. They are stored as logical information encoded into stabilizer codes.


A state as such can be represented as $|\mathcal{S},\psi\rangle$.

- $\langle \mathcal{S}  \rangle$ is the stabilzier group used for the encoding. 
- $\psi$ is the secret logical information that has been encoded. 

For any such state, only I know the stabilizer group $\langle \mathcal{S}  \rangle$ that were used for the encoding. However, noone knows the logical information that were actually encoded. 

But we know that we must protect the logical information from being destroyed since those secrets help your kingdom thrive.

---

However recently, Bob has been trying to destroy those secrets. He has managed to gain access to the systems that store those quantum states and also developed certain techniques to carry out his plans. 

We have learnt from our spy, that he has the following capabilities:
- He can construct new $|+\rangle$ states. 
- He can perform $CZ$s between qubits on my systems 
- He can also perform pauli-evolutions, which are unitaries of the form $P(\theta) = \mathrm{exp}(-i \frac{\theta}{2} P)$ where $P$ is a multi-qubit pauli operator $P \in \mathcal{P}_{n}$.

He's main idea is to perform irreversible transformations on the encoded logical information, for which he will need to perform measurements on the system. 

However he lacks measurement capabilities, so he ask his friend asked Charlie to perform those measurements but actually he's a spy  working for us. 

Charlie has the capability to perform multi-qubit projective measurements over pauli strings. For a pauli $M \: \in \:\mathcal{P}_{n}$ a projective measurement $\hat{M}$ over state $\ket{\psi}$ yielding outcome $m$ ($m\in \{0,1\}$) leaves it in the 'post-measurement' state $\hat{M}(m) \: \ket{\psi}$ which is stabilized by $(-1)^{m}M$ i.e $(-1)^{m}M \: \hat{M}(m) \: \ket{\psi} \: = \:\hat{M}(m) \: \ket{\psi}$ 

He wants to help us, but he also cannot blow his cover by denying Bob's instructions persistently. 


---


Our aim thus is to save the logical information encoded in the states from being ruined due to irreversible transformations due to measurements. 

A reversible logical transformation (a logical unitary) on the system is however fine, as long as we can figure out the transformations exactly, since we can revert it to get the state back. 

An example is as follows : 


---


In the challenges that follow, we will encounter situations as follows. 

We will look into a state $\ket{\mathcal{S},\psi}$ under attack. I will provide you the set that generates the stabilizer group $\braket{\mathcal{S}}$.

Charlie will smuggle us :
1. Bob's attack circuit (made of sequence of $\mathrm{CZ}$ and $P(\theta)$) and 
2. Set of measurements that Bob had asked him too as set, often he can convince Bob to remove certain measurements or do a specific measurement, but not always (spy life .. .you know !)  

Our task would be based around preventing destruction of logical information due to measurements, 




---


