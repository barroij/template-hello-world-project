#include <iostream>
#include "source_1.h"

int main(int argc, char* argv[])
{
	std::cout << "main function entry point" << std::endl;

	MyNamespace::call_function();

	std::cout << "main function exit" << std::endl;
	return 0;
}
