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
        f"cd sketch-1.7.6/sketch-frontend/ && ./sketch --bnd-inbits 2  test/sk/{file_name}"
    )
    for attempt in range(1, 4):
        try:
            result = subprocess.run(
                sketch_cmd,
                shell=True,
                # capture_output=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True  # capture_output as str instead of bytes
            )
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] {file_name}: exit {e.returncode}")
            # write stderr too
            with open(f"out_{file_name}.txt", "w") as f:
                f.write(e.stdout or "")
                f.write("\n\n--- STDERR ---\n\n")
                f.write(e.stderr or "")
            
            return file_name, None
  
        # write the full stdout for inspection
        r = result.stdout
        if "Rejected"  in result.stdout:
           continue
        with open(f"out_{file_name}.txt", "w") as f:
         f.write(r)

        # extract and return the time
        t = extract_total_time(r)
        return file_name, t
    return file_name, None
def main():
    gen_sketch_programs()
    file_names = [
        'car_x1_update.sk', 'car_y1_update.sk', 'car_v1_update.sk',
        'car_phi1_update.sk', 'car_theta1_update.sk',
        'F1_update_gravity.sk', 'v1_update_gravity.sk', 'v2_update_gravity.sk',
        'x1_update_gravity.sk', 'x2_update_gravity.sk',
        'x_update_lorenz.sk', 'y1_update_lorenz.sk', 'z1_update_lorenz.sk',
        'D4_x1_update.sk', 'D4_x1_update_2.sk', 'D4_y1_update_1.sk', 'D4_y1_update_2.sk',
        'z1_update_AAC.sk', 'x1_update_AAC.sk', 'y1_update_AAC.sk'
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
    tm_x1_1 = None
    tm_y1_1 = None

    for name, tm in results:
        # capture the first halves and skip
        if name == 'D4_x1_update.sk':
            tm_x1_1 = tm
            continue
        if name == 'D4_y1_update_1.sk':
            tm_y1_1 = tm
            continue

        # when we hit the second halves, print combined and skip
        if name == 'D4_x1_update_2.sk':
            if tm_x1_1 is not None and tm is not None:
                combined = tm_x1_1 + tm
                print(f"{'D4_x1_update':<30} {combined:>15}s")
            else:
                print(f"{'D4_x1_update':<30} {'N/A':>15}")
            continue

        if name == 'D4_y1_update_2.sk':
            if tm_y1_1 is not None and tm is not None:
                combined = tm_y1_1 + tm
                print(f"{'D4_y1_update':<30} {combined:>15}s")
            else:
                print(f"{'D4_y1_update':<30} {'N/A':>15}")
            continue

        # all other programs print normally
        time_str = f"{tm:.3f}s" if tm is not None else "N/A"
        print(f"{name:<30} {time_str:>15}")

        
def gen_sketch_programs():
    subprocess.run(["python", "car_sketch_gen.py"])
    subprocess.run(["python", "gravity_sketch_gen.py"])
    subprocess.run(["python", "lorenz_sketch_gen.py"])
    subprocess.run(["python", "AAC_sketch.py"])
    subprocess.run(["python", "D4_sketch_gen.py"])
if __name__ == "__main__":
    main()
