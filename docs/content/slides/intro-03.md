---
date-init: Sunday, December 14th 2025, 5:02:03 pm
date-modified: Friday, December 19th 2025, 5:15:38 pm
---

# The 'Logical' Problem 

Our aim thus is to save the logical information encoded in the states from being ruined due to irreversible transformations due to measurements. 

A reversible logical transformation (a logical unitary) on the system is however fine, as long as we can figure out the transformations exactly, since we can revert it to get the state back. An example is as follows.

Imagine we have the following encoded logical state:  
$$  
\ket{\mathcal{S},\psi}=\alpha\ket{000} \: + e^{i\phi}\:\beta\ket{111},  
$$  
where the logical information in encoded via **unknown coefficients** $\alpha,\beta$ and **phase** $\phi$ , but **known** stabilizer generators $\mathcal{S}=\{Z_{0}Z_{1},Z_{1}Z_{2}\}.$ Verify that the group $\langle{\mathcal{S}}\rangle$ stabilizes $\ket{\mathcal{S}, \psi}$.

Now we will see how three generically different measurements affect the state. 
## Case 1 — Stabilizer measurement (harmless)

Measurement:  
$$  
M_{1}=Z_{0}Z_{1}.  
$$

Since $Z_{0}Z_{1}\ket{000}=+\ket{000}$ and $Z_{0}Z_{1}\ket{111}=+\ket{111}$, the outcome is deterministically $+1$ always 

**Verdict: Deterministic**


## Case 2 — Destabilizer, but correctable

Measurement:  
$$  
M_{2}=X_{0}.  
$$

For the projective measurement $\hat{X}_{0}(m)$ over $X_{0}$ with outcome $(-1)^{m}$, $m\in{0,1}$ we have by definition,  
$$  
(-1)^m X_{0},\hat{X}_{0}(m)\ket{\psi}=\hat{X}_{0}(m)\ket{\psi}.  
$$

Applying it, the post-measurement state becomes:  
$$  
\hat{X}_{0}(m)\ket{\psi}  
= \tfrac{1}{\sqrt{2}}  
\big(\alpha\ket{+}\ket{00}+(-1)^m e^{i\phi}\beta\ket{+}\ket{11}\big).  
$$

Using the stabilizer $Z_{0}Z_{1}$,  
$$  
(Z_{0}Z_{1})^{m}\hat{X}_{0}(m)\ket{\psi}  
= \tfrac{1}{\sqrt{2}}  
\big(\alpha\ket{+}\ket{00}+e^{i\phi}\beta\ket{+}\ket{11}\big).  
$$

The randomness appears only as a  **pauli byproduct** which can be deduced directly from the knowledge of the stabilizer group  $\langle{\mathcal{S}}\rangle$.

**Verdict: Deterministic after Deducible corrections.**



## Case 3 — Logical measurement (irreversible)

Measurement:  
$$  
M_{3}=Z_{0}.  
$$

Observe that the outcome probabilities are now depends on the **unknown** logical information :
$$  
p(+)=|\alpha|^{2},\qquad p(-)=|\beta|^{2}.  
$$

Post‑measurement states thus are $\ket{000}\quad\text{or}\quad\ket{111}$ with $p(+)$ or $p(-)$ respectively. Thus there is no way to recover the initial state $\ket{\mathcal{S},\psi}$ via unitary operation due to our lack of 'logical' knowledge

**Verdict: Irreversible logical transformation**





