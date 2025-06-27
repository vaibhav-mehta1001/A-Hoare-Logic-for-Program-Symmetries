from verifier import *
import subprocess
import re

## Refactor this into a loop with the a list of file names: 
def extract_total_time(text: str) -> float | None:
    """
    Search text for something like 'Total Time = 123.45', or
    'Total Time: 123', etc.  Returns the number or None.
    """
    
    # allow "Total Time", then : or =, then a number (int or float),
    # optionally followed by non-digit chars (e.g. "ms", "s", etc.)
    # Search for a number after the word "in "
    pattern = r"in\s+([0-9]*\.?[0-9]+)"
    # pattern = r"in [:=]\s*([0-9]*\.?[0-9]+)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        print("–– DEBUG: no match found ––")
        return None
    
    num_str = match.group(1)
    return float(num_str)
  
file_names = [
    "car-translation.py",
    "car-translation2.py",
    "D4.py",
    "D6.py",
    "lorenz.py",
    "gravity.py",
    "AAC.py",
    "two-voter.py",
    "twenty-voter.py"
]
times = []
for fn in file_names:
    # print(f"Verification of {fn[:-3].replace('-', ' ').title()}")
    # print("Program:")
    cmd = (
        f"python {fn}"
    )
    result = subprocess.run(
                cmd,
                shell=True,
                # capture_output=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True  # capture_output as str instead of bytes
            )
    r = result.stdout
    # print(r)
    time = extract_total_time(r)
    times.append((fn,time))

print(f"{'File Name':<25} {'Time (s)':>10}")
print("-" * 37)
for fn, time in times:
      time_str = f"{time:.2f}" if time is not None else "Not found"
      print(f"{fn:<25} {time_str:>10}")