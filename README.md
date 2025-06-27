# A-Hoare-Logic-for-Program-Symmetries
Artifact for A Hoare Logic for Program Symmetries 
# A Hoare Logic for Program Symmetries: Artifact Evaluation

*June 27, 2025*

## 1. Build Instructions and Kick The Tires

To build the project, first ensure that you have downloaded the code into a folder. Ensure that you have python installed. We tested this with Python 3.10.12, but it should work with ≥ Python 3.8.

### Install Z3

To install Z3, in the same folder, clone Z3 from Github ([Z3 Github Repo](https://github.com/Z3Prover/z3)). You may follow the instructions in README there. We reproduce the command sequence that worked for us:

```bash
virtualenv venv
source venv/bin/activate
cd z3
python scripts/mk_make.py --python
cd build
make
make install
venv/bin/z3 -h
# ...
python -c 'import z3; print(z3.get_version_string())'
# ...
```

### Install Python Dependencies

Run `pip install -r requirements.txt` to install the Python dependencies (mpmath, sympy and z3-solver).

### Install Sketch

Download Sketch 1.7.6 from [Sketch Link](https://bitbucket.org/gatoatigrado/sketch-frontend/downloads/). Extract it so that the folder `sketch-1.7.6` is in the same folder as the code is. To install sketch, follow the README which we reproduce here:

#### Simple Setup Instructions:

1. **Dependencies**
   
   Before building you need to have the following tools installed:
   - bash
   - g++
   - flex
   - bison
   
   To run sketch you need to install either Java Runtime (JRE) or JDK, at least version 1.5.

2. **Building the backend**
   
   Under the `sketch-1.7.6` directory, execute:
   ```bash
   cd sketch-backend
   chmod +x ./configure
   ./configure
   make
   cd ..
   ```
   
   **Hint:** if configure or make keeps complaining, you can try install autoconf and libtool. But usually this is not necessary.

3. **Testing the sketch**
   ```bash
   cd sketch-frontend
   chmod +x ./sketch
   ./sketch test/sk/seq/miniTest1.sk
   ```
   
   This should print out the completed sketch.

### 1.1 Kick the Tires

To check that everything is working, make sure you are in the parent directory. 

- To check the verifier is working run `python AAC.py`. If you get "Verification of AAC Flow successful", then you have the verifier up and running.
- To check that the Sketch generator is working run `python run_sketch_kick_the_tires.py`. You should get a table with one row and a message saying "SKETCH WORKS!".

## 2. File Structure

The main source code for the verifier lives in `verifier.py` and the sketch generator lives in `sketch_gen.py`. Each of the other files are examples. The files:

- `car-translation.py`
- `car-translation2.py`
- `D4.py`
- `D6.py`
- `gravity.py`
- `lorenz.py`
- `AAC.py`
- `two-voter.py`
- `twenty-voter.py`

all correspond to examples from Table 1. Each of the examples are explained in the paper.

Files with `sketch_gen.py` as a suffix generate the sketches for synthesizing pre-conditions.

## 3. Running the Benchmarks

### Table 1

To run the benchmarks for Table 1, run `python run_verification_bench.py`. This produces a table of programs along with time taken to verify programs.

We also provide a file `car_translation_false.py` as an example of a property that does not hold.

### Table 3

To run the benchmarks for Table 3, the scaling benchmark, run `python dihedral_scaling_benchmarks.py`. This will first print the loop body of the program being verified then print time taken for each group action.

### Table 2

To run the benchmarks for Table 2, run `python run_sketches.py`. This script first runs all the generated sketches, and calls sketch on each `.sk` file. For the output, you should see a table with assignment statements corresponding to Table 2, along with the sketching times. You may see a "N/A" appear for some rows in the benchmark. If this happens, you might have to re-run the tool a few times – it is due to a non-deterministic error in the SKETCH tool.

The generated sketch files live in the directory `/sketch-1.7.6/sketch-frontend/test/sk/`. The solved sketches are in the parent folder with the prefix 'out'.

We also provide pre-generated sketches in the folder `gen_sketches`, and pre-solved sketches in the folder `gen_sketches/solved_sketches`.

### 3.1 Interpreting Sketches

As we mentioned in the data availability statement, we do not directly parse the sketch output. If you wish to view it, open one of the solved sketch files (with prefix `out`). To see the generated group action, go to the main function and look for the second call to the function `C`. For each argument, there will be an expression, which is the generated pre-group action. 

For example, Figure 1 (in the PDF not shown here, sorry!) shows the generated sketch for the car translation example. On Line 22, we can see that the function `C` is being called with `x + 1.0` and `y + 1.0`, which is the pre-group action for the update to x.

## 4. Reusability Instructions

To define your own group action and programs, refer to the AST in `verifier.py` for the available expressions.

---

