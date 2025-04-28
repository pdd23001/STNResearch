Z_INPUT = int(100000000)
X_BASIS_FACTOR = 0.4
X_INPUT = int(X_BASIS_FACTOR * Z_INPUT)
FLIP_PROB = 0.05

from bitarray import bitarray
from bitarray.util import urandom
import random

def flip_bits(orig, p):
    """
    Global Noise Function: Simulate bit flips in the transmission.
    """
    mask = bitarray((random.random() < p) for _ in range(len(orig)))
    return orig ^ mask

class Node:
    def __init__(self, left_node=None, right_node=None):
        self.left_node = left_node
        self.right_node = right_node
        self.right_key_z = urandom(Z_INPUT)
        self.right_key_x = urandom(X_INPUT)
        if self.left_node:
            self.left_key_z = flip_bits(self.left_node.right_key_z, FLIP_PROB) 
            self.left_key_x = flip_bits(self.left_node.right_key_x, FLIP_PROB)
        
        
    def xor_l_r(self, basis):
        if basis == 'z':
            return self.left_key_z ^ self.right_key_z
        elif basis == 'x':
            return self.left_key_x ^ self.right_key_x
        else:
            raise ValueError("Basis must be either 'z' or 'x'")
        
    def xor_until_now(self, basis):
        if self.left_node.left_node is None:
            return self.xor_l_r(basis)
        else:
            return self.left_node.xor_until_now(basis) ^ self.xor_l_r(basis)
    

class STN_Network:
    def __init__(self, num_stns=1):

        self.alice=Node()
        cur_node=self.alice

        for i in range(num_stns):
            cur_node.right_node=Node(left_node=cur_node)
            cur_node=cur_node.right_node

        self.bob=Node(left_node=cur_node)
    
    def get_final_key(self, basis):
        if basis == 'z':
            return self.bob.left_node.xor_until_now(basis) ^ self.bob.left_key_z
        elif basis == 'x':
            return self.bob.left_node.xor_until_now(basis) ^ self.bob.left_key_x
        else:
            raise ValueError("Basis must be either 'z' or 'x'")
    
    def final_x_error(self):
        final_x = self.get_final_key('x')
        error_count = (self.alice.right_key_x ^ final_x).count()
        qber = error_count / X_INPUT
        return qber

if __name__=="__main__":
    nwork=STN_Network(num_stns=1)
    qber=nwork.final_x_error()
    print("Final X-Basis QBER: ", qber)



