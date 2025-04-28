import numpy as np
from numpy import random
from hashlib import sha256

# -------------------------------
# STN Framework Setup
# -------------------------------

x_basis_factor = 0.4
z_input = int(10e8)
x_input = int(x_basis_factor * z_input)
flip_prob = 0.05

# Generate raw keys for Z and X bases
a_z = random.randint(2,size=z_input, dtype=np.uint8) # Alice's raw key
b_z = random.randint(2, size=z_input, dtype=np.uint8) # Bob's raw key

a_x = random.randint(2, size=x_input, dtype=np.uint8)
b_x = random.randint(2, size=x_input, dtype=np.uint8)

# Simulate transmission with noise (bit flips)
t_z_a = np.where(random.rand(z_input) < flip_prob, 1 - a_z, a_z)
t_z_b = np.where(random.rand(z_input) < flip_prob, 1 - b_z, b_z)

t_x_a = np.where(random.rand(x_input) < flip_prob, 1 - a_x, a_x)
t_x_b = np.where(random.rand(x_input) < flip_prob, 1 - b_x, b_x)

# Generate final noisy keys received by Bob (for both bases)
xored_z = np.bitwise_xor(t_z_a, t_z_b)
final_z = np.bitwise_xor(xored_z, b_z)

xored_x = np.bitwise_xor(t_x_a, t_x_b)
final_x = np.bitwise_xor(xored_x, b_x)

# -------------------------------
# QBER Calculation for X Basis
# -------------------------------
error_count = np.sum(a_x != final_x)
qber = error_count / x_input
print("Initial X-Basis QBER: ", qber)

# -------------------------------
# Cascade Error Correction on Z basis (Multi-Iteration with Shuffling)
# -------------------------------

# Initialize global variables for communication rounds
alice_msgs = 0

def parity(bits):
    """Helper: Compute parity of a bit block. This function is carried out by Alice (the server)"""
    return np.sum(bits) % 2

def bin_search_alice_parity(bits):
    "Function for rounds of communication help"
    global alice_msgs
    alice_msgs += 1  
    return parity(bits)      


def binary_search_and_fix(a, b, indices):
    """Binary search to locate and fix an error in a block"""
    start = 0
    end = len(indices) - 1
    while start < end:
        mid = (start + end) // 2
        # Check parity of the first half of the block indices
        if bin_search_alice_parity(a[indices[start:mid+1]]) != parity(b[indices[start:mid+1]]):
            end = mid
        else:
            start = mid + 1
    error_index = indices[start]
    # Flip the error bit in Bob's key
    b[error_index] = 1 - b[error_index]

def cascade_correction_iteration(a_key, b_key, block_size):
    """Single Cascade iteration on a given key (without shuffling)"""
    corrected = b_key.copy()
    n = len(a_key)
    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block_indices = list(range(start, end))
        # Compare block parities; if they differ, use binary search to fix error
        if parity(a_key[start:end]) != parity(corrected[start:end]):
            binary_search_and_fix(a_key, corrected, block_indices)
    return corrected

def cascade_iteration(a_key, b_key, block_size, use_permutation=False):
    """One Cascade iteration that optionally uses a random permutation (shuffling)"""
    n = len(a_key)
    # If using permutation, create a random permutation of indices
    if use_permutation:
        perm = np.random.permutation(n)
        # Permute both keys accordingly
        a_perm = a_key[perm] #permutation can be sent to Alice over a public channel. It doesn't matter if Eve knows it as long as the key before and after permutation is secutre
        b_perm = b_key[perm].copy()
        # Run cascade correction on the permuted keys
        corrected_perm = cascade_correction_iteration(a_perm, b_perm, block_size)
        # Invert the permutation to restore the original order
        inv_perm = np.empty_like(perm)
        inv_perm[perm] = np.arange(n)
        corrected = corrected_perm[inv_perm]
    else:
        # No permutation: work on the keys directly
        corrected = cascade_correction_iteration(a_key, b_key, block_size)
    
    return corrected

def cascade_full_correction(a_key, b_key, block_sizes, use_permutation=True):
    """Run multiple iterations of Cascade with increasing block sizes and shuffling. This is carried out by Bob (the client)"""
    corrected = b_key.copy()
    for block_size in block_sizes:
        if block_size == int(0.73 / qber):
            corrected = cascade_iteration(a_key, corrected, block_size, use_permutation=False)
        else:
            corrected = cascade_iteration(a_key, corrected, block_size, use_permutation)
        print(f"Error Rate After Iteration with Block Size {block_size}: {np.sum(corrected != a_key) / len(a_key)}")
    return corrected

# Define a list of block sizes for successive iterations (you can adjust these values)
# Typically, Cascade uses small blocks first and then larger blocks in later iterations.

first_block_size = int(0.73 / qber) # From cascade documentation.
num_iterations = 7                  # can be modified as per needs (original cascade uses 4)
block_sizes = [int(2**i) * first_block_size for i in range(num_iterations)] 

alice_msgs += num_iterations
bob_msgs = num_iterations - 1

# Apply multi-iteration Cascade on the Z basis
corrected_z = cascade_full_correction(a_z, final_z, block_sizes, use_permutation=True)

# -------------------------------
# Evaluate Cascade Correction Result
# -------------------------------

#This should ideally not be done in a real-world scenario. Just checking to see if error correction works.
errors_after = np.sum(corrected_z != a_z)
error_rate_after = errors_after / z_input
print("Z-Basis Error Rate After Multi-Iteration Cascade: ", error_rate_after)
print("Total Alice Messages Sent: ", alice_msgs)
print("Total Bob Messages Sent: ", bob_msgs)

#Another way to confirm that the reconcilliated key and the original key are the same (Using Hashing). We can send hashes over public channels
hash_a_z = sha256(a_z.tobytes()).hexdigest()
hash_corrected_z = sha256(corrected_z.tobytes()).hexdigest()
print("Key Roncilliation Success Status:", hash_a_z == hash_corrected_z)

