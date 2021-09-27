#Configuration Instructions

**Windows**

1. Install jdk1.8 onto your machine in location C:\Program Files\Java
2. Install Maven and upload folder in location C:\Program Files\
3. Install Ant and upload folder in location C:\Program Files\
4. Download the .jar file for Junit 3.8.1 and drop it in C:\Program Files\apache-ant-1.10.11-bin\apache-ant-1.10.11\lib
5. Update JAVA_HOME user variable to jdk1.8.0*
6. Add the following Path user environmental variables:
    
    C:\Program Files\apache-maven-3.8.2-bin\apache-maven-3.8.2\bin
    
    %JAVA_HOME%
    
    %ANT_HOME%\bin
7. Add a new system variable:
   
    Variable Name: ANT_HOME

    Variable Value: C:\Program Files\apache-ant-1.10.11-bin\apache-ant-1.10.11


**Linux**

TODO

**Links**

JDK1.8: https://www.oracle.com/java/technologies/downloads/#java8-windows

Maven: https://maven.apache.org/download.cgi

Ant: https://ant.apache.org/bindownload.cgi

Junit 3.8.1: https://repo1.maven.org/maven2/junit/junit/3.8.1/