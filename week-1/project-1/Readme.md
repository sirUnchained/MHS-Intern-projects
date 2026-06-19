# Prime Number Utility

A simple Python program that provides three essential prime‑number operations:

1. **Check** if a single number is prime.
2. **Count** all prime numbers in a user‑specified range.
3. **Display** all primes in that range, formatted 10 per line.

The program uses efficient trial division up to √n and is suitable for educational purposes or quick prime‑related tasks.

---

## Features

- **Primality Test** – `is_prime(n)` returns `True`/`False` for any integer ≥ 0.
- **Count Primes** – `count_primes_in_range(start, end)` returns the total number of primes in the interval.
- **Pretty Display** – `display_primes_in_range(start, end)` prints the primes in columns (10 per row) for easy reading.
- **Interactive** – prompts the user for input via the console.
- **Error Handling** – gracefully handles non‑integer inputs.

---

## Requirements

- Python 3.8 or later (uses `math.isqrt`).

---

## Installation

1. Clone or download the script file (e.g., `prime_program.py`).
2. Ensure Python is installed on your system.
3. No external libraries are needed – only the standard library.

---

## Usage

Run the script from your terminal:

```bash
python prime_program.py
```