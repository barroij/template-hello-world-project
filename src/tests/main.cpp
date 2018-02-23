#include "gtest/gtest.h"
#include "subfolder/source_2.h"
#include <string>

TEST(TestFolder, Test) {
    EXPECT_EQ (std::string("Hello and Welcom to this template project"), MyNamespace::get_hello_text());
}

int main(int argc, char **argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}