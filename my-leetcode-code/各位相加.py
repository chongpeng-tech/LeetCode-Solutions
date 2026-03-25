class Solution:
    def addDigits(self, num: int) -> int:
        ans = num
        while ans >= 10:
            digit = str(ans)
            length = len(digit)
            new_ans = 0
            for i in range(length):
                new_ans += int(digit[i])
            ans = new_ans
        return ans