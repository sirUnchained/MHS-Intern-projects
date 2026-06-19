"""
Prime Number Program
This program provides three functionalities:
1. Check if a given number is prime.
2. Count prime numbers in the range 0 to 1000.
3. Generate a list of primes in that range and display them in a column.
"""

# -------------------- Part 0: Imports --------------------
import math


# -------------------- Part 1: Check if number is prime --------------------
def is_prime(n: int) -> bool:
    """Return True if n is prime, False otherwise."""
    # Numbers less than 2 are not prime
    if n < 2:
        return False

    # Check divisibility up to sqrt(n) – O(sqrt(n))
    for i in range(2, int(math.isqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


# -------------------- Part 2: Count primes in a range --------------------
def count_primes_in_range(start: int, end: int) -> int:
    """Count prime numbers between start and end (inclusive)."""
    count = 0
    # Use is_prime() for each number – O((end-start+1) * sqrt(m))
    for num in range(start, end + 1):
        if is_prime(num):
            count += 1
    return count


# -------------------- Part 3: List and display primes --------------------
def display_primes_in_range(start: int, end: int) -> None:
    """Print all prime numbers in the given range, 10 per line."""
    # Build list of primes using is_prime()
    primes = [num for num in range(start, end + 1) if is_prime(num)]

    print(f"\nPrime numbers from {start} to {end}:")
    for i, p in enumerate(primes, start=1):
        print(p, end=" ")
        if i % 10 == 0:
            print()  # newline after every 10 numbers
    if primes and len(primes) % 10 != 0:
        print()  # final newline if last line incomplete


# -------------------- Main --------------------
def main():
    # 1) Check primality of a single number
    try:
        user_input = int(input("Enter a positive integer to check for primality: "))
        if is_prime(user_input):
            print(f"{user_input} is a prime number.")
        else:
            print(f"{user_input} is not a prime number.")
    except ValueError:
        print("Invalid input. Please enter an integer.")

    # 2) Get range from user and count primes
    try:
        start_range = int(input("Enter start number: "))
        end_range = int(input("Enter end number: "))
    except ValueError:
        print("Invalid input. Please enter an integer.")
        return  # exit if range invalid

    prime_count = count_primes_in_range(start_range, end_range)
    print(f"\nNumber of primes between {start_range} and {end_range}: {prime_count}")

    # 3) Display the primes in column format
    display_primes_in_range(start_range, end_range)


if __name__ == "__main__":
    main()
