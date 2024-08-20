import hashlib
from Crypto.Util import number
import sympy
import math
import sys
import time
sys.set_int_max_str_digits(1000000000)
# Function to generate a large prime
def generate_large_prime(bits=1024):
    return number.getPrime(bits)

# Function for cryptographic hash


def calculate_squarings_per_second(n, duration=1):

    start_time = time.time()
    count = 0
    val=0.001
    while time.time() - start_time <= duration:
        count += val
    return count / duration

def cryptographic_hash_function(bit_string: str, k: int) -> int:
    if not all(c in '01' for c in bit_string):
        raise ValueError("The input string must only contain '0' and '1' characters")    
    if len(bit_string) < 2*k:   
        bit_string = bit_string.zfill(2*k)
    elif len(bit_string) > 2*k:  
        bit_string = bit_string[:2*k]
    #print("bit String:",bit_string)
    integer_value = int(bit_string, 2)
    
    return integer_value

# Function to find the next prime greater than the hashed value
def next_prime_of_hashed(hashed_int):
    return sympy.nextprime(hashed_int)

# H' function
def H_prime(m, k):
    hashed_value = cryptographic_hash_function(m, k)
    return next_prime_of_hashed(hashed_value)

# Setup function for VDF
def Setup(k, T):
    p = generate_large_prime()
    q = generate_large_prime()
    n = p * q
    S = calculate_squarings_per_second(n)
    difficulty = int (T*S)
    return n, difficulty, S 

# Eval function for VDF
def Eval(m, n, k, t):
    start_time = time.time()
    x = cryptographic_hash_function(m, k)
    y=x
    for _ in range(1, t+1):
        y = pow(y, 2, n)
    # Compute h_prime
    h_prime = next_prime_of_hashed(x + y)
    res_1 = pow(2, t) // h_prime
    proof_phi = pow(x, res_1, n)
    end_time = time.time()
    eval_time = end_time - start_time
    return y, h_prime, proof_phi, x, eval_time

# Verify function for VDF
def Verify(n, h_prime, proof_phi, x, t):
    start_time = time.time()
    r = pow(2,t, h_prime)
    y1 = pow(proof_phi, h_prime, n)
    y2 = pow(x, r, n)
    y_res = (y1 * y2) % n
    end_time = time.time()
    verify_time = end_time - start_time
    return h_prime == next_prime_of_hashed(x + y_res), verify_time

# Example usage
k = 128             # Security parameter in bits
message = "01010101"
T = 5
n, t, S = Setup(k, T)
y, h_prime, proof_phi, x, eval_time = Eval(message, n, k, t)
print("VDF Evaluation Parameters")
print("Value of n:",n)
print("Difficulty:", t)
print("result (y):", y)
print("h_prime (l):", h_prime)
print("Proof (pi):", proof_phi)
print(f"Evaluation Time: {eval_time:.6f} seconds\n")
res, verify_time = Verify(n, h_prime, proof_phi, x, t)
print("Verification result:", res)
print(f"Verification Time: {verify_time:.6f} seconds\n")

