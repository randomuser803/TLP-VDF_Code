from Crypto.Util import number
from Crypto.Cipher import AES
import hashlib
import time

# Generate a large prime number
def generate_large_prime(bits=1024):
    return number.getPrime(bits)

# Encrypt the message using AES
def encrypt_message(key, message):
    hashed_key = hashlib.sha256(key).digest()
    cipher = AES.new(hashed_key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(message)
    return (nonce, ciphertext, tag)

# Decrypt the message using AES
def decrypt_message(key, nonce, ciphertext, tag):
    hashed_key = hashlib.sha256(key).digest()
    cipher = AES.new(hashed_key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)

# Calculate the number of squarings per second
def calculate_squarings_per_second(n, duration=1):
    a = number.getRandomRange(2, n-1)
    start_time = time.time()
    count = 0
    val=1.1
    while time.time() - start_time <= duration:
        a = pow(a, 2, n)
        count += val
    return count / duration
    
# Setup Puzzle Params
def Setup(k, T):
    start_time = time.time()
    p = generate_large_prime()
    q = generate_large_prime()
    n = p * q
    phi_n = (p-1) * (q-1)
    S = calculate_squarings_per_second(n)
    t = int(T * S)
    end_time = time.time()
    setup_time = end_time - start_time
    return n, phi_n, t, S, setup_time

# Generate the puzzle according to Shamir's scheme
def PuzGen(m, t, n, phi_n):
    start_time = time.time()
    a = number.getRandomRange(2, n-1)
    k = number.getRandomNBitInteger(160)
    # Encrypt the message using the random key k
    Cm = encrypt_message(k.to_bytes((k.bit_length() + 7) // 8, byteorder='big'), m)
    # Compute b = a^(2^t) mod n, efficiently 
    b = pow(a, pow(2, t, phi_n), n)
    # Compute Ck = k + b mod n
    Ck = (k + b) % n
    end_time = time.time()
    puzzle_gen_time = end_time - start_time
    return Cm, Ck, a, puzzle_gen_time

# Solve the puzzle by performing the squarings
def PuzSol(n, t, Cm, Ck, a):
    start_time = time.time()
    # Compute b = a^(2^t) mod n
    b = a
    for _ in range(t):
        b = pow(b, 2, n)
    k = (Ck - b) % n
    k_bytes = k.to_bytes((k.bit_length() + 7) // 8, byteorder='big')
    nonce, ciphertext, tag = Cm
    try:
        decrypted_message = decrypt_message(k_bytes, nonce, ciphertext, tag)
        end_time = time.time()
        puzzle_sol_time = end_time - start_time
        return decrypted_message.decode('utf-8'), puzzle_sol_time
    except (ValueError, TypeError) as e:
        end_time = time.time()
        puzzle_sol_time = end_time - start_time
        return f"Decryption failed: {str(e)}", puzzle_sol_time

# Example usage
message = b"Hidden Message"
T = 5  # Desired solving time in seconds
k=2048
# Setup Puzzle Params
n, phi_n, t, S, setup_time = Setup(k, T)
# Generate Puzzle
Cm, Ck, a, puzzle_gen_time = PuzGen(message, t, n, phi_n)
print("Puzzle Parameters:")
print(f"Number of squarings per second (S): {S:.2f}")
print("Value of n:", n)
print("Value of T:", T)
print("Value of Cm:", Cm)
print("Value of Ck:", Ck)

print(f"Puzzle Generation Time: {puzzle_gen_time:.6f} seconds\n")
# Solve the puzzle
decrypted_message, puzzle_sol_time = PuzSol(n, t, Cm, Ck, a)
print("Decrypted message:", decrypted_message)
print(f"Puzzle Solution Time: {puzzle_sol_time:.6f} seconds\n")
print(f"Puzzle Setup: {setup_time:.6f} seconds\n")
