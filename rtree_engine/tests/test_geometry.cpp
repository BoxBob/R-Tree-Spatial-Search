#include <gtest/gtest.h>
#include "../src/geometry.h" // Go up one directory to find the src folder

TEST(RectangleTest, Intersection) {
    Rectangle r1 = {{0.0, 0.0}, {2.0, 2.0}};
    
    // Case 1: Overlapping
    Rectangle r2 = {{1.0, 1.0}, {3.0, 3.0}};
    EXPECT_TRUE(r1.intersects(r2));
    EXPECT_TRUE(r2.intersects(r1));

    // Case 2: No overlap
    Rectangle r3 = {{3.0, 3.0}, {5.0, 5.0}};
    EXPECT_FALSE(r1.intersects(r3));
    EXPECT_FALSE(r3.intersects(r1));

    // Case 3: Contained
    Rectangle r4 = {{0.5, 0.5}, {1.5, 1.5}};
    EXPECT_TRUE(r1.intersects(r4));
    EXPECT_TRUE(r4.intersects(r1));

    // Case 4: Touching edges
    Rectangle r5 = {{2.0, 0.0}, {4.0, 2.0}};
    EXPECT_TRUE(r1.intersects(r5));
    EXPECT_TRUE(r5.intersects(r1));
}

TEST(RectangleTest, Area) {
    Rectangle r1 = {{0.0, 0.0}, {2.0, 3.0}};
    EXPECT_DOUBLE_EQ(r1.area(), 6.0);

    Rectangle r2 = {{10.0, 10.0}, {10.0, 20.0}};
    EXPECT_DOUBLE_EQ(r2.area(), 0.0);
}
