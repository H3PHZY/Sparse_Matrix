import os

def read_sparse_matrix(file_path):
    """Reads a sparse matrix from a file and stores it as a dictionary."""
    matrix = {}
    with open(file_path, "r") as file:
        lines = file.readlines()

        # Extract rows and columns from first two lines
        rows = int(lines[0].split("=")[1])
        cols = int(lines[1].split("=")[1])

        # Read nonzero values
        for line in lines[2:]:
            line = line.strip()
            if line:  # Ignore empty lines
                try:
                    row, col, value = map(int, line.strip("()").split(","))
                    matrix[(row, col)] = value
                except ValueError:
                    raise ValueError("Input file has wrong format")

    return rows, cols, matrix

def add_matrices(matrix1, matrix2):
    """Performs matrix addition."""
    result = matrix1.copy()
    for key, value in matrix2.items():
        result[key] = result.get(key, 0) + value
        if result[key] == 0:
            del result[key]
    return result

def subtract_matrices(matrix1, matrix2):
    """Performs matrix subtraction."""
    return add_matrices(matrix1, {k: -v for k, v in matrix2.items()})

def multiply_matrices(rows1, cols1, matrix1, rows2, cols2, matrix2):
    """Performs matrix multiplication."""
    if cols1 != rows2:
        raise ValueError("Matrix multiplication is not possible")
    
    result = {}
    for (i, k), v1 in matrix1.items():
        for j in range(cols2):
            if (k, j) in matrix2:
                result[(i, j)] = result.get((i, j), 0) + v1 * matrix2[(k, j)]
    
    return result

def main():
    """User interface to select operation and execute it on two sparse matrices."""
    print("Choose an operation:")
    print("1. Add Matrices")
    print("2. Subtract Matrices")
    print("3. Multiply Matrices")
    
    choice = input("Enter choice (1/2/3): ")

    file1 = input("Enter first matrix file: ")
    file2 = input("Enter second matrix file: ")

    if not os.path.exists(file1) or not os.path.exists(file2):
        print("Error: One or both files do not exist.")
        return

    rows1, cols1, matrix1 = read_sparse_matrix(file1)
    rows2, cols2, matrix2 = read_sparse_matrix(file2)

    if choice == "1":
        result = add_matrices(matrix1, matrix2)
    elif choice == "2":
        result = subtract_matrices(matrix1, matrix2)
    elif choice == "3":
        result = multiply_matrices(rows1, cols1, matrix1, rows2, cols2, matrix2)
    else:
        print("Invalid choice")
        return

    print("Result (nonzero values only):", result)

if __name__ == "__main__":
    main()
