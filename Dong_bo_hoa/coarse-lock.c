#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <pthread.h>
#define INIT_BALANCE 50
#define NUM_TRANS 5000
int balance = INIT_BALANCE;
int credits = 0;
int debits = 0;
pthread_mutex_t global_lock; // Single mutex for all operations (Coarse Locking)

void *transactions(void *args)
{
    int i, v;
    for (i = 0; i < NUM_TRANS; i++)
    {
        // choose a random value
        srand(time(NULL));
        v = rand() % NUM_TRANS;
        
        // COARSE LOCKING: Lock the entire transaction
        pthread_mutex_lock(&global_lock);
        
        // randomly choose to credit or debit
        if (rand() % 2)
        {
            // credit - all locked together, blocking other threads
            balance = balance + v;
            // Simulate some computation work
            for(int j = 0; j < 100; j++) { v = v * 1.1; }
            credits = credits + v;
            // More computation work
            for(int j = 0; j < 100; j++) { v = v * 0.9; }
        }
        else
        {
            // debit - all locked together, blocking other threads
            balance = balance - v;
            // Simulate some computation work
            for(int j = 0; j < 100; j++) { v = v * 1.1; }
            debits = debits + v;
            // More computation work
            for(int j = 0; j < 100; j++) { v = v * 0.9; }
        }
        
        pthread_mutex_unlock(&global_lock);
    }
    return 0;
}

int main(int argc, char *argv[])
{
    int n_threads, i;
    pthread_t *threads;
    clock_t start_time, end_time;
    double cpu_time_used;
    
    // error check
    if (argc < 2)
    {
        fprintf(stderr, "ERROR: Require number of threads\n");
        exit(1);
    }
    // convert string to int
    n_threads = atol(argv[1]);
    // error check
    if (n_threads <= 0)
    {
        fprintf(stderr, "ERROR: Invalid value for number of threads\n");
        exit(1);
    }
    
    // initialize mutex
    pthread_mutex_init(&global_lock, NULL);
    
    // allocate array of thread identifiers
    threads = calloc(n_threads, sizeof(pthread_t));
    
    // Start timing
    start_time = clock();
    
    // start all threads
    for (i = 0; i < n_threads; i++)
    {
        pthread_create(&threads[i], NULL, transactions, NULL);
    }
    // wait for all threads finish its jobs
    for (i = 0; i < n_threads; i++)
    {
        pthread_join(threads[i], NULL);
    }
    
    // End timing
    end_time = clock();
    cpu_time_used = ((double) (end_time - start_time)) / CLOCKS_PER_SEC;
    
    printf("=== COARSE LOCKING RESULTS ===\n");
    printf("\tCredits:\t%d\n", credits);
    printf("\t Debits:\t%d\n\n", debits);
    printf("%d+%d-%d= \t%d\n", INIT_BALANCE, credits, debits, INIT_BALANCE + credits - debits);
    printf("\t Balance:\t%d\n", balance);
    printf("Execution Time: %.6f seconds\n", cpu_time_used);
    printf("Threads: %d\n", n_threads);
    
    // cleanup
    pthread_mutex_destroy(&global_lock);
    free(threads);
    return 0;
}