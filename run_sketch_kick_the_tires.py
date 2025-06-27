import subprocess
import re
from typing import Optional, Tuple, List

def extract_total_time(text: str) -> float | None:
    """
    Search text for something like 'Total Time = 123.45', or
    'Total Time: 123', etc.  Returns the number or None.
    """
    
    # allow "Total Time", then : or =, then a number (int or float),
    # optionally followed by non-digit chars (e.g. "ms", "s", etc.)
    pattern = r"Total\s+Time\s*[:=]\s*([0-9]*\.?[0-9]+)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        print("–– DEBUG: no match found ––")
        return None
    
    num_str = match.group(1)
    return float(num_str)/1000.0 

def run_and_record_sketch(file_name: str, out_dir: str) -> Tuple[str, Optional[float]]:
    """
    Runs sketch on test/sk/<file_name>, writes full stdout to out_<file_name>.txt,
    and returns (file_name, extracted_time).
    """
    sketch_cmd = (
        f"cd sketch-1.7.6/sketch-frontend/ && ./sketch --bnd-inbits 3 --slv-lightverif test/sk/{file_name}"
    )
    # try:
    result = subprocess.run(
            sketch_cmd,
            shell=True,
            capture_output=True,
            text=True  # capture_output as str instead of bytes
        )
    # # except subprocess.CalledProcessError as e:
    #     print(f"[ERROR] {file_name}: exit {e.returncode}")
    #     # write stderr too, if you like
    #     with open(f"out_{file_name}.txt", "w") as f:
    #         f.write(e.stdout or "")
    #         f.write("\n\n--- STDERR ---\n\n")
    #         f.write(e.stderr or "")
    #     return file_name, None
  
    # write the full stdout for inspection
    r = result.stdout
    # print(r)
    with open(f"out_{file_name}.txt", "w") as f:
        f.write(r)

    # extract and return the time
    t = extract_total_time(r)
    return file_name, t

def main():
    file_names = [
        'car_x1_update.sk' 
    ]

    results: List[Tuple[str, Optional[float]]] = []

    for fn in file_names:
        print(f"Running sketch on {fn}…", end=" ")
        name, tm = run_and_record_sketch(fn, out_dir="sk-outputs/")
        status = f"{tm:.3f}s" if tm is not None else "FAILED"
        # print(status)
        results.append((name, tm))

    # print a nice table
    print("\n=== Sketch Run Times ===")
    print(f"{'Program':<30} {'Sketching Time':>12}")
    print("-" * 44)
    for name, tm in results:
        time_str = f"{tm:.3f}s" if tm is not None else "N/A"
        print(f"{name:<30} {time_str:>12}")
    print("SKETCH WORKS!")
def gen_sketch_programs():
    subprocess.run(["python", "car_sketch_gen.py"])

if __name__ == "__main__":
    main()
