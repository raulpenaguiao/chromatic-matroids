from matroid_chromatic import compute_conjecture_matrix
import numpy as np

def matrix_to_latex(matrix):
    latex_str = "\\begin{bmatrix}\n"
    for row in matrix:
        latex_str += " & ".join(map(str, row)) + " \\\\\n"
    latex_str += "\\end{bmatrix}"
    return latex_str


if __name__ == "__main__":
    d = int( input("Enter the value of d: ") )
    result_matrix, set_comp, matroids = compute_conjecture_matrix(d)
    result_matrix = matrix_to_latex(result_matrix)#If you want to print the matrix in latex format
    print(result_matrix)
    print("Set compositions:")
    print(set_comp)
    print("Matroids:")
    print(matroids)

