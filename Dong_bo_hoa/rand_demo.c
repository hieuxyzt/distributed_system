#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <limits.h>

int main() {
    printf("RAND_MAX value: %d\n\n", RAND_MAX);
    
    // Without seeding - always same sequence
    printf("Without srand() - same sequence every time:\n");
    for (int i = 0; i < 5; i++) {
        printf("rand() = %d\n", rand());
    }
    
    printf("\nWith srand(time(NULL)) - different each run:\n");
    srand(time(NULL));
    for (int i = 0; i < 5; i++) {
        printf("rand() = %d\n", rand());
    }
    
    printf("\nCommon patterns:\n");
    srand(time(NULL));
    printf("rand() %% 100 = %d (0-99)\n", rand() % 100);
    printf("rand() %% 2 = %d (0 or 1)\n", rand() % 2);
    printf("rand() %% 10 + 1 = %d (1-10)\n", rand() % 10 + 1);
    
    printf("\nFloat conversion:\n");
    printf("(double)rand()/RAND_MAX = %.6f (0.0-1.0)\n", (double)rand()/RAND_MAX);
    
    return 0;
}