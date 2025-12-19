---
date-init: Friday, December 19th 2025, 10:35:21 am
date-modified: Friday, December 19th 2025, 11:13:44 am
---

# Intro slide: Three measurement types (stabilizer, correctable, irreversible)

Imagine we have the following encoded logical state:  
$$  
\ket{\mathcal{S},\psi}=\alpha\ket{000} \: + e^{i\phi}\:\beta\ket{111},  
$$  
where the logical information in encoded via **unknown coefficients** $\alpha,\beta$ and **phase** $\phi$ , but **known** stabilizer generators $\mathcal{S}=\{Z_{0}Z_{1},Z_{1}Z_{2}\}.$ Verify that the group $\braket{\mathcal{S}}$ stabilizes $\ket{\mathcal{S}, \psi}$.

Now we will see how three generically different measurements affect the state. 
## Case 1 — Stabilizer measurement (harmless)

Measurement:  
$$  
M_{1}=Z_{0}Z_{1}.  
$$

Since $Z_{0}Z_{1}\ket{000}=+\ket{000}$ and $Z_{0}Z_{1}\ket{111}=+\ket{111}$, the outcome is deterministically $+1$ always   
$$  
\hat{M}_{1}(0)\ket{\psi}=\ket{\psi}.  
$$

**Verdict: Deterministic**


## Case 2 — Destabilizer, but correctable

Measurement:  
$$  
M_{2}=X_{0}.  
$$

Let $\hat{X}_{0}(m)$ denote the projective measurement of $X_{0}$ with outcome $(-1)^{m}$, $m\in{0,1}$. By definition,  
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

The randomness appears only as a  **pauli byproduct** which can be deduced directly from the knowledge of the stabilizer group  $\braket{\mathcal{S}}$.

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

Post‑measurement states thus are $\ket{000}\quad\text{or}\quad\ket{111}$ with $p(+)$ or $p(-)$ respectively. Thus there is no way to recover the initial state $\ket{\mathcal{S},\psi}$ via unitary operation

**Verdict: Irreversible logical transformation**

---

## Takeaway

- Stabilizer measurement → safe.
    
- Destabilizer measurement → safe _if_ its randomness is correctable.
    
- Logical measurement → irreversible.
    

**In the game, your goal is to avoid Case 3.**