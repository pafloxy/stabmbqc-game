# Notation 

pauli strings written as : 'X0 X1 Z2'  means X on qubit 0, X on qubit 1, Z on qubit 2


# rounds plan



## example-0 
nqubit= 5 (alice 0,1,2; bob 3,4)
ALice-Stab : {X0 X1, X1 X2 }
Bob-Stab : {X3, X4}

Circuit : CZ(0,1) , CZ(0,4) , CZ(1, 3), CZ(2, 4)  

### Problem : 

#### stage 1: 
Select Measurement string that is not a logical op
options: 
1. (correct) Z1 
2. Y0 Y1 X2 Z3
3. Z0 Z1 Z2
4. Z0 Z2 X3


## example-1
nqubit= 5 (alice 0,1,2; bob 3,4)
ALice-Stab : {X0X1, X1X2 }
Bob-Stab : {X3, X4}

Circuit : CZ(1, 3), X1(theta1), CZ(0,1) , CZ(0,4) , X3(theta2) ,  CZ(2, 4)  

### Problem :

#### stage 1
Select Measurement string that is not a logical op 
options:

#### stage 2 
based on the measurement selected previously, select the pauli-evolution that was implemented (described as logical ops only)



## example-2
nqubit= 5 (alice 0,1,2; bob 3,4)
ALice-Stab : {X0X1, X1X2 }
Bob-Stab : {X3, X4}

Circuit : CZ(1, 3), X1(theta1), CZ(0,1) , CZ(0,4) , X3(theta2) ,  CZ(2, 4)  



