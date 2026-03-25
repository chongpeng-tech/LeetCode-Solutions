class Solution {
public:
    string convertToTitle(int columnNumber) {
        int copy_columnNumber = columnNumber;
        std::string res;
        char temp;
        while(copy_columnNumber > 0){
            temp = (copy_columnNumber - 1) % 26 + 'A';
            
            res = temp + res;
            copy_columnNumber--;
            copy_columnNumber = copy_columnNumber / 26;
        }
        return res;
    }
};