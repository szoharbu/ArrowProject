extern "C" void my_cpp_function();

int fibonacci(int n){
    // Base case: if n is 0 or 1, return n
    if (n <= 1){
        return n;
    }
    // Recursive case: sum of the two preceding Fibonacci numbers
    return fibonacci(n - 1) + fibonacci(n - 2);
}

void my_cpp_function() {
    // C++ functionality
    int x = 42;
    int n = 5;
    int result = fibonacci(n);
}

