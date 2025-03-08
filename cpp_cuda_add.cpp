#include <iostream>

extern "C" void cuda_add(float* a, float* b, float* c, int size);

extern "C" void add_vectors(const float* a, const float* b, float* c, int size) {
    std::cout << "Using CUDA for computation." << std::endl;
    cuda_add(const_cast<float*>(a), const_cast<float*>(b), c, size);
}
