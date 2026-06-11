class Solution {
    public boolean isPalindrome(String s) {
        s.toLowerCase();
        int l = 0;
        int r = s.length() - 1;

        while (l < r) {
            while (!Character.isLetterOrDigit(s.charAt(l)) && l < r) {
                l++;
            }
            while (!Character.isLetterOrDigit(s.charAt(r)) && l < r) {
                r--;
            }
            if (s.charAt(l) != s.charAt(r)) {
                return false;
            }

        }
        return true;
    }
}

public static void main(String[] args) {
    System.out.println("Hello World");
}