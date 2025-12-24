---
date-init: Sunday, December 14th 2025, 5:02:03 pm
date-modified: Wednesday, December 24th 2025, 3:15:48 pm
---

# The Challenge 


In the challenges that follow, we will encounter situations as follows. 

We will look into a state $\ket{\mathcal{S},\psi}$ under attack. I will provide you the stabilizer group $\langle \mathcal{S} \rangle$.

Caséf will smuggle us :

1. Description Briegel's attack circuit 

2. Set of measurements that Briegel had asked him too as set, often she can convince Briegel to remove certain measurements or do a specific measurement, but not always (spy life .. .you know !)  

Even though Caséf can smuggle Briegel's attack circuit, the angle of rotations $\theta$ parameterizing the multi-pauli rotations (like $P(\theta)$ ) will be unavailable to us prior to execution of measurement. Briegel keeps them in a secret ledger until Caséf executes her measurements. So we will have information oly about the pauli-string $P$ that generates the rotation. So we receive a circuit made of sequence of $\mathrm{CZ}$ gates and $P$'s. 

Our tasks would be based around preventing destruction of logical information that might be caused due to the measurements, 