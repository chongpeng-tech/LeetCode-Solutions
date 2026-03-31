class Solution:
    def maxScore(self, s: str) -> int:
        length = len(s)
        ans = 0
        #包头不包尾，不用特意去减1
        for i in range(1, length):
            temp_left = s[:i].count('0')
            temp_right = s[i:].count('1')
            temp_ans = temp_left + temp_right
            ans = max(ans, temp_ans)
        return ans