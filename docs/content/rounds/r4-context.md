---
date-init: Friday, December 19th 2025, 4:06:05 pm
date-modified: Friday, December 19th 2025, 6:47:31 pm
---

Thanks for figuring the unitary, I applied its inverse and retrieved the original state. 

But Bob won't give up. This time he has introduced another multi-pauli rotation $X_{3}X_{1}(\theta_{2})$ along with the previous $X_{4}(\theta)$. 

Same state as before with stabilizer generators 
$\mathcal{S} = \{ X_{0}Z_{2} \: , \: X_{1}Z_{2} \: , \: Z_{0}Z_{1}X_{2}Z_{3} \: , \: Z_{2}X_{3}Z_4\}$


Charlie is allowed measurements: $\{Z_{1}, Z_{3}, Z_{0}\}$. He can discard one measurement like before. 

Heard Bob's busy with a new idea .. something called 'gflow' but anyway it will keep him busy.

This problem seems a bit complicated. I have a few ideas :

1. Main problem is anti-commutations between the rotations. And I feel rotations that don't commute with measurements cause trouble.

2. I observed that we can use stabilizers to rewrite generators of multi-pauli rotations, even if we don't know the rotation angles.

3. For example if we have $P(\theta)$ acting on a state $\ket{\psi}$ stabilized by $S$ ie $S \ket{\psi}=\ket{\psi}$ then $P(\theta)\ket{\psi} \equiv PS(\theta) \ket{\psi} = \mathrm{exp}(-i \frac{\theta}{2} PS)\ket{\psi}$

4. But the above doesn't work if we have another rotation $Q(\alpha)$ as $P(\theta) \:Q(\alpha) \:\ket{\psi}$ and $[Q,P] \neq 0$.

5. We can use these idea to rewrite the multi-pauli rotations, thus affect the commutation  
