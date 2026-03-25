class Solution:
    def xorOperation(self, n: int, start: int) -> int:
        ans = 0
        for i in range(n):
            current_num = start + 2*i
            ans ^= current_num
        return ans