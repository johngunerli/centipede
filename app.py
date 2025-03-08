import subprocess
import os
import ctypes
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

# Paths to compiled shared libraries
CUDA_LIB = "./libcuda_add.so"
CUDA_CPP_LIB = "./libadd_cuda.so"
CPU_CPP_LIB = "./libadd_cpu.so"

def compile_cuda_cpp():
    """
    Tries to compile CUDA first. If it fails, compiles CPU version instead.
    """
    print("Compiling CUDA and C++ code...")

    cuda_compiled = False

    # Try compiling CUDA
    try:
        subprocess.run(
            ["nvcc", "-shared", "-o", CUDA_LIB, "-Xcompiler", "-fPIC", "cuda_add.cu"],
            check=True
        )
        subprocess.run(
            ["g++", "-shared", "-o", CUDA_CPP_LIB, "cpp_cuda_add.cpp", "-L.", "-lcuda_add", "-fPIC"],
            check=True
        )
        cuda_compiled = True
        print("✅ CUDA compilation successful.")
    except subprocess.CalledProcessError:
        print("❌ CUDA compilation failed. Falling back to CPU version.")

    # If CUDA failed, compile the CPU version
    if not cuda_compiled:
        try:
            subprocess.run(
                ["g++", "-shared", "-o", CPU_CPP_LIB, "cpp_cpu_add.cpp", "-fPIC"],
                check=True
            )
            print("✅ CPU version compiled successfully.")
        except subprocess.CalledProcessError:
            print("❌ CPU compilation also failed. Exiting.")
            exit(1)

# Compile before running the server
if not os.path.exists(CUDA_CPP_LIB) and not os.path.exists(CPU_CPP_LIB):
    compile_cuda_cpp()

# Determine which library to use
if os.path.exists(CUDA_CPP_LIB):
    lib = ctypes.CDLL(CUDA_CPP_LIB)
    mode = "CUDA"
elif os.path.exists(CPU_CPP_LIB):
    lib = ctypes.CDLL(CPU_CPP_LIB)
    mode = "CPU"
else:
    print("❌ No valid compiled library found. Exiting.")
    exit(1)

# Define function arguments
lib.add_vectors.argtypes = [
    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(ctypes.c_float),
    ctypes.c_int
]

# FastAPI setup
app = FastAPI()

class AddRequest(BaseModel):
    array1: list[float]
    array2: list[float]

def add_arrays(a, b):
    """
    Calls the CUDA function if available, otherwise falls back to CPU.
    Returns both the computation result and the mode used (CUDA or CPU).
    """
    size = len(a)
    c = np.zeros(size, dtype=np.float32)

    a_ptr = a.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    b_ptr = b.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    c_ptr = c.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

    lib.add_vectors(a_ptr, b_ptr, c_ptr, size)

    return c.tolist(), mode  
# Returning both result and mode

@app.post("/add")
async def add_numbers(request: AddRequest):
    """
    FastAPI endpoint to handle array addition requests.
    Returns result and information about which computation method was used.
    """
    a = np.array(request.array1, dtype=np.float32)
    b = np.array(request.array2, dtype=np.float32)

    if len(a) != len(b):
        return {"error": "Arrays must be of the same length"}

    result, mode_used = add_arrays(a, b)
    return {"result": result, "computation_mode": mode_used}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
