#include <iostream>

extern "C" void add_vectors(const float* a, const float* b, float* c, int size) {
    std::cout << "CUDA compilation failed. Using CPU computation." << std::endl;
    for (int i = 0; i < size; i++) {
        c[i] = a[i] + b[i];
    }
}
