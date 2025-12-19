---
date-init: Sunday, December 14th 2025, 5:02:03 pm
date-modified: Friday, December 19th 2025, 5:17:54 pm
---

# The Challenge 


In the challenges that follow, we will encounter situations as follows. 

We will look into a state $\ket{\mathcal{S},\psi}$ under attack. I will provide you the set that generates the stabilizer group $\langle \mathcal{S} \rangle$.

Charlie will smuggle us :

1. Description Bob's attack circuit 

2. Set of measurements that Bob had asked him too as set, often he can convince Bob to remove certain measurements or do a specific measurement, but not always (spy life .. .you know !)  

3. Even though Charlie can smuggle Bob's attack circuit, the angle of rotations $\theta$ that parameterizing the multi-pauli rotations (like $P(\theta)$ ) will be unavailable to us prior to execution of measurement (Bob keeps them in a secret ledger until Charlie measures them). 

4. So we receive a circuit made of sequence of $\mathrm{CZ}$ gates and $P$ multi-pauli rotations. 

Our tasks would be based around preventing destruction of logical information that might be caused due to the measurements, 