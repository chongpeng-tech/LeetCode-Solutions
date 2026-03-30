class Solution:
    def transpose(self, matrix: List[List[int]]) -> List[List[int]]:
        row = len(matrix)
        col = len(matrix[0])
        new_row = col
        new_col = row
        ans = []
        for i in range(new_row):
            ans.append([0] * new_col)
        for i in range(row):
            for j in range(col):
                ans[j][i] =  matrix[i][j]
        return ans
