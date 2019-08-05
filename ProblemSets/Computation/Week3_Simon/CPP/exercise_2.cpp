// my *second program in C++
#include <iostream>
#include <math.h>
using namespace std;


int main()
{
	
	float a;
	float b;
	float c;
  
        cout << "Enter a number for a: "; // ask user for a number
	cin >> a; // read number from console and store it in x  

        cout << "Enter a number for b: "; // ask user for a number
        cin >> b; // read number from console and store it in x  

	cout << "Enter a number for c: "; // ask user for a number
        cin >> c;

	float result;
	float result2;
	float part1;

	part1 = b*b -4*a*c;

	if (part1<0){
		cout << "There is no real valued solution to this problem!"<<endl;
	}
	else if(part1 == 0){
		result = -b/(2*a);
		cout << "You have a unique solution to this problem:"<<endl;
		cout << result<<endl;
	}
	else{
		result = (-b + pow(part1, 0.5))/(2*a);
		result2 = (-b - pow(part1, 0.5))/(2*a);
		cout << "You have two solutions to this problem:"<<endl;
		cout << "Solution 1:" << result << endl;
		cout << "Solution 2:" << result2 << endl;
	}
	//TODO: Write the function solution...
	return 0;
}
