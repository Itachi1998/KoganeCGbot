#Guess the Output
def find_kth_smallest_in_sorted_matrix(matrix, k):
    n_rows = len(matrix) # Get number of rows (the length fo the matrix list) = 3 (it is not 2 because length counts the elements)
    n_cols = len(matrix[0]) # Get the number of elements in the first index of matrix, which would be = 3
    low = matrix[0][0] # get the first element of the first index of the matrix which is 1
    # low = 1  
    high = matrix[n_rows - 1][n_cols - 1] # get the index of matricx[3 - 1][3 - 1] which is matrix[2][2] = 15
    # high = 15
    while low <= high:
        mid = (low + high) // 2 
        count = 0
        j = n_cols - 1
        for i in range(n_rows):
            while j >= 0 and matrix[i][j] > mid:
                j -= 1 
            count += (j + 1)  
        if count < k:
            low = mid + 1
        else:
            high = mid - 1
    
    return low

matrix1 = [[1,5,9],[10,11,13],[12,13,15]]
k1 = 8

print(find_kth_smallest_in_sorted_matrix(matrix1, k1))

