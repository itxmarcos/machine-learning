import subprocess
import os

def C_Execution():
    # storing the output
    s = subprocess.check_call("gcc Hello.c -o out1;./out1", shell = True)
    print(", return code", s)

def Cpp_Execution():
    # creating a pipe to child process
    data, temp = os.pipe()
    
    # writing inputs to stdin and using utf-8 to convert it to byte string
    os.write(temp, bytes("7 12\n", "utf-8"));
    os.close(temp)
    
    # storing output as a byte string
    s = subprocess.check_output("g++ Hello.cpp -o out2;./out2", stdin = data, shell = True)
    
    # decoding to print a normal output
    print(s.decode("utf-8"))

# def Java_Execution():
#     # storing the output
#     s = subprocess.check_output("javac Hello.java;java Hello", shell = True)
#     print(s.decode("utf-8"))
    
# Driver functions
if __name__=="__main__":
    C_Execution()
    Cpp_Execution()
    # Java_Execution()