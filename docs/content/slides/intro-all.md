---
date-init: Thursday, December 18th 2025, 11:47:23 pm
date-modified: Wednesday, December 24th 2025, 3:22:18 pm
---

# Welcome!

Welcome Professor *(upto HDR)* Ollivier. Glad you accepted to help us!

Our ancient kingdom has stored its most precious secrets as quantum states. They are stored as logical information encoded into stabilizer codes.

A state as such can be represented as $|\mathcal{S},\psi\rangle$.

- $\langle \mathcal{S}  \rangle$ is the stabilizer group used for the encoding. 
- $\psi$ is the secret logical information that has been encoded. 

For any such state, only I know the stabilizer group $\langle \mathcal{S}  \rangle$ that were used for the encoding. However, noone knows the logical information that were actually encoded. 

But we know that we must protect the logical information from being destroyed since those secrets help your kingdom thrive.

- Princess Alaêm, Good Code Kingdom

---

# The Invader and the Spy

However recently, Briegel has been trying to destroy those secrets. He has managed to gain access to the systems that store those quantum states and also developed certain techniques to carry out his plans. 

We have learnt from our spy, that he has the following capabilities:
- He can construct new $|+\rangle$ states. 
- He can perform $CZ$s between qubits on my systems 
- He can also perform pauli-evolutions, which are unitaries of the form $P(\theta) = \mathrm{exp}(-i \frac{\theta}{2} P)$ where $P$ is a multi-qubit pauli operator $P \in \mathcal{P}_{n}$.

He's main idea is to perform irreversible transformations on the encoded logical information, which he can induce via measurements on the system. 

But he lacks measurement capabilities, so he ask his ally Caséf. Caséf has the capability to perform multi-qubit projective measurements over pauli strings. 

Example: For a pauli $M \: \in \:\mathcal{P}_{n}$ a projective measurement $\hat{M}$ over state $\ket{\psi}$ yielding outcome $m$ ($m\in \{0,1\}$) leaves it in the 'post-measurement' state $\hat{M}(m) \: \ket{\psi}$ which is stabilized by $(-1)^{m}M$ i.e $(-1)^{m}M \: \hat{M}(m) \: \ket{\psi} \: = \:\hat{M}(m) \: \ket{\psi}$ 

However, Caséf is a spy working for us. Though
she wants to help us, she cannot blow her cover by denying Briegel's instructions persistently. 



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




---

# The Challenge 


In the challenges that follow, we will encounter situations as follows. 

We will look into a state $\ket{\mathcal{S},\psi}$ under attack. I will provide you the stabilizer group $\langle \mathcal{S} \rangle$.

Caséf will smuggle us :

1. Description Briegel's attack circuit 

2. Set of measurements that Briegel had asked him too as set, often she can convince Briegel to remove certain measurements or do a specific measurement, but not always (spy life .. .you know !)  

Even though Caséf can smuggle Briegel's attack circuit, the angle of rotations $\theta$ parameterizing the multi-pauli rotations (like $P(\theta)$ ) will be unavailable to us prior to execution of measurement. Briegel keeps them in a secret ledger until Caséf executes her measurements. So we will have information oly about the pauli-string $P$ that generates the rotation. So we receive a circuit made of sequence of $\mathrm{CZ}$ gates and $P$'s. 

Our tasks would be based around preventing destruction of logical information that might be caused due to the measurements, 

---

# The UI

Here is how your console will look like :

The panel on the left will display  
- Briegel's attack circuit shown as figure
	- Alaêm's qubit will be indexed as $\mathtt{A_i}$ and Briegel's as $\mathtt{B_{j}}$ 
	- Multi-pauli rotations will appear as boxes : $X_{4}(\theta) \: : \: \mathtt{X \textunderscore 4(th)}$
- Alaêm's message about $\langle S \rangle$ and the measurements 

The panel on the right is where you answer to my specific questions by clicking on the right option.

Buttons you'll have:

- Prev / Next: step through story slides.
- `Skip` : Move to next level

- `Rules` : opens the full story + mechanics reference.
- `Hints` : opens the short 'how to decide' checklist.
- `Restart Game`: resets everything back to the intro.
- Each round has a timer. If it hits zero: game over.

---

Buttons you'll have:

- Prev / Next: step through story slides.
- Skip: jump straight to the first round.
- Start Level 1: begin the game.

In-game:
- Rules: opens the full story + mechanics reference.
- Restart Game: resets everything back to the intro.

---

Each round has a timer. If it hits zero: game over.

If you select a safe option: you survive the round and can click Next Round.

