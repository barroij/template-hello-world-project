#include "source_1.h"
#include "subfolder/source_2.h"

#include <iostream>

namespace MyNamespace {
	void call_function() {
		std::cout << get_hello_text() << std::endl;
	}
}

