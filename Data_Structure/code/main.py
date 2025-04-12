import unittest
import os

class SparseMatrix:
    def __init__(self, file_path=None, rows=0, cols=0):
        self.rows = rows
        self.cols = cols
        self.data = {}  # Store values as {(row, col): value}
        
        if file_path:
            self._load_from_file(file_path)
    
    def _load_from_file(self, file_path):
        """Reads the sparse matrix from the file and stores it in dictionary form."""
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                self.rows = int(lines[0].split('=')[1].strip())
                self.cols = int(lines[1].split('=')[1].strip())
                
                for line in lines[2:]:
                    line = line.strip()
                    if not line:
                        continue  # Ignore empty lines
                    
                    if not (line.startswith("(") and line.endswith(")")):
                        raise ValueError("Input file has wrong format")
                    
                    elements = line[1:-1].split(",")
                    if len(elements) != 3:
                        raise ValueError("Input file has wrong format")
                    
                    try:
                        row, col, value = map(int, [elem.strip() for elem in elements])
                    except ValueError:
                        raise ValueError("Input file has wrong format")
                    
                    self.set_element(row, col, value)
                    
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: File {file_path} not found.")
    
    def get_element(self, row, col):
        """Returns the value at the specified position or zero if not present."""
        return self.data.get((row, col), 0)
    
    def set_element(self, row, col, value):
        """Sets a value in the sparse matrix."""
        if value == 0:
            self.data.pop((row, col), None)  # Remove entry if value is zero
        else:
            self.data[(row, col)] = value
    
    def display(self):
        """Displays non-zero elements of the sparse matrix."""
        print(f"SparseMatrix({self.rows}x{self.cols}) with {len(self.data)} non-zero elements")
        for (row, col), value in sorted(self.data.items()):
            print(f"({row}, {col}): {value}")
    
    def save_to_file(self, filename):
        """Writes the sparse matrix to a file in the required format."""
        with open(filename, 'w') as f:
            f.write(f"rows={self.rows}\n")
            f.write(f"cols={self.cols}\n")
            for (row, col), value in sorted(self.data.items()):
                f.write(f"({row}, {col}, {value})\n")

def add_matrices(mat1, mat2):
    """Add two sparse matrices."""
    max_rows = max(mat1.rows, mat2.rows)
    max_cols = max(mat1.cols, mat2.cols)
    
    result = SparseMatrix(rows=max_rows, cols=max_cols)
    
    # Add elements from mat1
    for (row, col), value in mat1.data.items():
        result.set_element(row, col, value + mat2.get_element(row, col))
    
    # Add elements from mat2 (if they weren't already in mat1)
    for (row, col), value in mat2.data.items():
        if (row, col) not in mat1.data:
            result.set_element(row, col, value)
    
    return result

def subtract_matrices(mat1, mat2):
    """Subtract two sparse matrices."""
    max_rows = max(mat1.rows, mat2.rows)
    max_cols = max(mat1.cols, mat2.cols)
    
    result = SparseMatrix(rows=max_rows, cols=max_cols)
    
    # Subtract elements from mat1
    for (row, col), value in mat1.data.items():
        result.set_element(row, col, value - mat2.get_element(row, col))
    
    # Handle elements that are only in mat2
    for (row, col), value in mat2.data.items():
        if (row, col) not in mat1.data:
            result.set_element(row, col, -value)
    
    return result

def multiply_matrices(mat1, mat2):
    """
    Multiply two sparse matrices with optimized implementation for large matrices.
    """
    if mat1.cols != mat2.rows:
        raise ValueError("Matrix multiplication is not possible: Column count of first matrix must equal row count of second matrix")
    
    result = SparseMatrix(rows=mat1.rows, cols=mat2.cols)
    
    # Create a column-wise index for mat2 to speed up lookups
    col_index = {}
    for (row, col), value in mat2.data.items():
        if col not in col_index:
            col_index[col] = []
        col_index[col].append((row, value))
    
    # For each non-zero element in mat1
    for (row1, col1), value1 in mat1.data.items():
        # For each column in the result matrix
        for result_col in col_index.keys():
            # Get all non-zero elements in this column of mat2
            for row2, value2 in col_index[result_col]:
                if col1 == row2:  # If we have a match
                    current = result.get_element(row1, result_col)
                    result.set_element(row1, result_col, current + value1 * value2)
    
    return result

class TestSparseMatrix(unittest.TestCase):
    def setUp(self):
        self.m1 = SparseMatrix(rows=3, cols=3)
        self.m1.set_element(0, 1, 5)
        self.m1.set_element(1, 2, 10)
        
        self.m2 = SparseMatrix(rows=3, cols=3)
        self.m2.set_element(0, 1, 2)
        self.m2.set_element(1, 2, 8)
    
    def test_addition(self):
        result = add_matrices(self.m1, self.m2)
        self.assertEqual(result.get_element(0, 1), 7)
        self.assertEqual(result.get_element(1, 2), 18)
    
    def test_subtraction(self):
        result = subtract_matrices(self.m1, self.m2)
        self.assertEqual(result.get_element(0, 1), 3)
        self.assertEqual(result.get_element(1, 2), 2)
    
    def test_multiplication(self):
        # Test with matrices that will produce non-zero results
        m1 = SparseMatrix(rows=2, cols=2)
        m1.set_element(0, 0, 1)
        m1.set_element(0, 1, 2)
        
        m2 = SparseMatrix(rows=2, cols=2)
        m2.set_element(0, 0, 3)
        m2.set_element(1, 0, 4)
        
        result = multiply_matrices(m1, m2)
        self.assertEqual(result.get_element(0, 0), 11)  # 1*3 + 2*4

def main():
    print("Sparse Matrix Operations")
    
    # Get input file paths from user
    file1 = input("Enter path for first matrix file: ").strip()
    file2 = input("Enter path for second matrix file: ").strip()

    try:
        # Load matrices
        mat1 = SparseMatrix(file1)
        mat2 = SparseMatrix(file2)
        
        # Display matrix information
        print("\nMatrix 1:")
        mat1.display()
        print("\nMatrix 2:")
        mat2.display()

        # Choose operation
        print("\nChoose operation:\n1. Addition\n2. Subtraction\n3. Multiplication")
        choice = input("Enter your choice (1/2/3): ").strip()

        result = None  # Store the result matrix

        if choice == '1':
            result = add_matrices(mat1, mat2)
        elif choice == '2':
            result = subtract_matrices(mat1, mat2)
        elif choice == '3':
            result = multiply_matrices(mat1, mat2)
        else:
            print("❌ Invalid choice!")
            return
        
        # If operation was successful, display and save the result
        if result:
            print("\nResult matrix:")
            result.display()
            
            output_file = input("\nEnter output file name (default: result_matrix.txt): ").strip()
            if not output_file:
                output_file = "result_matrix.txt"  # Default output file
            result.save_to_file(output_file)
            print(f"✅ Result saved to {output_file}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    # Run tests if argument is "test"
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        unittest.main(argv=['first-arg-is-ignored'])
    else:
        main()