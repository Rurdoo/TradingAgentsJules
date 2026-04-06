import time
import re
from tradingagents.agents.utils.memory import FinancialSituationMemory

def benchmark():
    mem = FinancialSituationMemory("test")
    text = "This is a test sentence with some punctuation! And some more words, testing 1 2 3. High inflation rate with rising interest rates and declining consumer spending."

    # Warmup
    for _ in range(100):
        mem._tokenize(text)

    start_time = time.perf_counter()
    for _ in range(100000):
        mem._tokenize(text)
    end_time = time.perf_counter()

    duration = end_time - start_time
    print(f"Time taken for 100,000 iterations: {duration:.4f} seconds")

if __name__ == "__main__":
    benchmark()
