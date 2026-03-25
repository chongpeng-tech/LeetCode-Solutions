class Solution:
    def smallestEvenMultiple(self, n: int) -> int:
        if n % 2 == 0:
            ans = n
            return ans
        else:
            ans = n * 2
            return ans
            