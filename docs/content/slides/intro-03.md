---
date-init: Sunday, December 14th 2025, 5:02:03 pm
date-modified: Wednesday, December 24th 2025, 3:10:15 pm
---

# The 'Logical' Problem 

Our aim thus is to save the logical information encoded in the states from being ruined due to irreversible transformations due to measurements. 

However, if the induced logical transformations is reversible (i.e a logical unitary) we are still safe, as long as we can figure out the transformations exactly, since then we can invert (invert the logical unitary) it to get the state back. An example is as follows.

Imagine we have the following encoded logical state:  
$$  
\ket{\mathcal{S},\psi}=\alpha\ket{000} \: + e^{i\phi}\:\beta\ket{111},  
$$  
where the logical information in encoded via **unknown coefficients** $\alpha,\beta$ and **phase** $\phi$ , the stabilizer generators are $\mathcal{S}=\{Z_{0}Z_{1},Z_{1}Z_{2}\}.$ (Verify that the group $\langle{\mathcal{S}}\rangle$ stabilizes $\ket{\mathcal{S}, \psi}$)

Now we will see how three generically different measurements affect the state. 
## Case 1 — Stabilizer measurement (harmless)

Measurement:  
$$  
M_{1}=Z_{0}Z_{1}.  
$$

Since $Z_{0}Z_{1}\ket{000}=+\ket{000}$ and $Z_{0}Z_{1}\ket{111}=+\ket{111}$ the outcome of measurement $\hat{M_{1}}$ on $\ket{\mathcal{S},\psi}$ is $+1$ deterministically, and the state remains unaffected by the measurement process.  

**Verdict: Deterministic**


## Case 2 — Destabilizer, but correctable

Measurement:  
$$  
M_{2}=X_{0}.  
$$

For the projective measurement $\hat{X}_{0}(m)$, we have by definition,  
$$  
(-1)^m X_{0},\hat{X}_{0}(m)\ket{\psi}=\hat{X}_{0}(m)\ket{\psi}.  
$$

Applying it, the post-measurement state becomes:  
$$  
\hat{X}_{0}(m)\ket{\psi}  
= \tfrac{1}{\sqrt{2}}  
\big(\alpha\ket{+}\ket{00}+(-1)^m e^{i\phi}\beta\ket{+}\ket{11}\big).  
$$

Which can be rewritten using the stabilizer $Z_{0}Z_{1}$ as,  
$$  
(Z_{0}Z_{1})^{m} \:  \:\hat{X}_{0}(m)\ket{\psi}  
= \tfrac{1}{\sqrt{2}}  
\big(\alpha\ket{000}+e^{i\phi}\beta\ket{111}\big).  
$$
i.e we can apply the $Z_{0}Z_{1}$ on the post-measurement state $\:\hat{X}_{0}(m)\ket{\psi}$ conditioned on the measurement outcome $m$ to retrieve $\ket{\mathcal{S}, \psi}$. (Verify this)

Thus randomness appears only as a **pauli byproduct** $Z_{0}Z_{1}$ , which can be deduced directly from the knowledge of the stabilizer group $\langle{\mathcal{S}}\rangle$ and can be used to prevent the stochasticity of the measurement affect the state.

**Verdict: Deterministic after Deducible corrections.**



## Case 3 — Logical measurement (irreversible)

Measurement:  
$$  
M_{3}=Z_{0}.  
$$

Observe that the outcome probabilities for $m=0,1$ now depends on the **unknown** logical information :
$$  
p(m=0)=|\alpha|^{2},\qquad p(m=1)=|\beta|^{2}.  
$$

Post‑measurement states thus are $\hat{M_{3}}(0) \:\ket{\mathcal{S},\psi}\: = \:\ket{000}\quad\text{or}\quad \hat{M_{3}}(1) \:\ket{\mathcal{S},\psi}\: = \:\ket{111}$ with unknown probabilities respectively. Thus there is no way to recover the initial state $\ket{\mathcal{S},\psi}$ via unitary operation due to our lack of 'logical' knowledge, such transformations are logically irreversible.

**Verdict: Irreversible logical transformation**





