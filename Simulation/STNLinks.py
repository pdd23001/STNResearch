from numpy import random
import numpy as np

x_basis_factor=0.4
z_input=int(10e6)
x_input=int(x_basis_factor*z_input)
a_z = random.randint(2, size=z_input)
b_z = random.randint(2, size=z_input)
a_x = random.randint(2, size=x_input)
b_x = random.randint(2, size=x_input)

t_z_a = np.zeros(z_input, dtype=np.int8)
t_z_b = np.zeros(z_input, dtype=np.int8)


t_x_a = np.zeros(x_input, dtype=np.int8)
t_x_b = np.zeros(x_input, dtype=np.int8)


flip_prob = 0.05


for i in range(z_input):
    rand_z_a = random.rand()
    rand_z_b = random.rand()
    if rand_z_a < flip_prob:
        t_z_a[i]=((a_z[i]+1)%2)
    else:
        t_z_a[i]=(int(a_z[i]))

    if rand_z_b < flip_prob:
        t_z_b[i]=((b_z[i]+1)%2)
    else:
        t_z_b[i]=(int(b_z[i]))


for i in range(x_input):
    rand_x_a = random.rand()
    rand_x_b = random.rand()
    if rand_x_a < flip_prob:
        t_x_a[i]=(a_x[i]+1)%2
    else:
        t_x_a[i]=(int(a_x[i]))

    if rand_x_b < flip_prob:    
        t_x_b[i]=((b_x[i]+1)%2)
    else:
        t_x_b[i]=(int(b_x[i]))


xored_z = np.bitwise_xor(t_z_a, t_z_b)
xored_z = np.array(xored_z).astype(int)

b_z = b_z.astype(int)

final_z = np.bitwise_xor(xored_z, b_z)


xored_x = np.bitwise_xor(t_x_a, t_x_b)
xored_x = np.array(xored_x).astype(int)

b_x = b_x.astype(int)

final_x = np.bitwise_xor(xored_x, b_x)

error_count=0
for i in range(x_input):
    if a_x[i]!=final_x[i]:
        error_count+=1

qber=error_count/x_input
print("Error Rate: ", qber)



        


    



        

