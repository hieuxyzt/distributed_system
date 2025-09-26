#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <pthread.h>
#define INIT_BALANCE 50
#define NUM_TRANS 10  // Reduced for debugging
int balance = INIT_BALANCE;
int credits = 0;
int debits = 0;
int credit_count = 0;  // Count how many credit operations
int debit_count = 0;   // Count how many debit operations

void *transactions(void *args)
{
    int thread_id = *((int*)args);
    int i, v;
    int local_credits = 0, local_debits = 0;
    
    for (i = 0; i < NUM_TRANS; i++)
    {
        srand(time(NULL));
        v = rand() % NUM_TRANS;
        if (rand() % 2)
        {
            printf("Thread %d: CREDIT %d\n", thread_id, v);
            balance = balance + v;
            credits = credits + v;
            credit_count++;
            local_credits += v;
        }
        else
        {
            printf("Thread %d: DEBIT %d\n", thread_id, v);
            balance = balance - v;
            debits = debits + v;
            debit_count++;
            local_debits += v;
        }
    }
    printf("Thread %d finished: local_credits=%d, local_debits=%d\n", 
           thread_id, local_credits, local_debits);
    return 0;
}

int main(int argc, char *argv[])
{
    int n_threads = 3, i;
    pthread_t *threads;
    int *thread_ids;
    
    threads = calloc(n_threads, sizeof(pthread_t));
    thread_ids = calloc(n_threads, sizeof(int));
    
    for (i = 0; i < n_threads; i++)
    {
        thread_ids[i] = i;
        pthread_create(&threads[i], NULL, transactions, &thread_ids[i]);
    }
    
    for (i = 0; i < n_threads; i++)
    {
        pthread_join(threads[i], NULL);
    }
    
    printf("\n=== FINAL RESULTS ===\n");
    printf("Credit operations: %d\n", credit_count);
    printf("Debit operations: %d\n", debit_count);
    printf("Credits total: %d\n", credits);
    printf("Debits total: %d\n", debits);
    printf("Balance: %d\n", balance);
    printf("Expected: %d + %d - %d = %d\n", 
           INIT_BALANCE, credits, debits, INIT_BALANCE + credits - debits);
    
    free(threads);
    free(thread_ids);
    return 0;
}