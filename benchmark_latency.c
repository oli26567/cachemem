#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdint.h>
#include "win_clock.h"

#define KB 1024
#define NUM_ACCESSES 1000000

void shuffle(int *array, int n) {
    for (int i = n - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        int temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
}

double measure_latency(int block_size) {
    int num_elements = block_size / 64;
    if (num_elements < 2) num_elements = 2;

    int *indices = malloc(num_elements * sizeof(int));
    if (!indices) return -1;

    for (int i = 0; i < num_elements; i++) {
        indices[i] = i;
    }

    srand((unsigned int)time(NULL));
    shuffle(indices, num_elements);

    int *chain = malloc(num_elements * sizeof(int));
    if (!chain) {
        free(indices);
        return -1;
    }

    for (int i = 0; i < num_elements - 1; i++) {
        chain[indices[i]] = indices[i+1];
    }
    chain[indices[num_elements-1]] = indices[0];

    struct timespec start, end;
    int current = 0;

    clock_gettime(CLOCK_MONOTONIC_RAW, &start);

    for (int i = 0; i < NUM_ACCESSES; i++) {
        current = chain[current];
    }

    clock_gettime(CLOCK_MONOTONIC_RAW, &end);

    if (current == -1) printf("%d", current);

    free(indices);
    free(chain);

    double ns = (double)(end.tv_sec - start.tv_sec) * 1e9 + (double)(end.tv_nsec - start.tv_nsec);
    return ns / NUM_ACCESSES;
}

int main(int argc, char* argv[]) {
    int min_kb = 1;
    int max_kb = 8192;

    if (argc > 1) min_kb = atoi(argv[1]);
    if (argc > 2) max_kb = atoi(argv[2]);

    if (min_kb <= 0) min_kb = 1;
    if (max_kb < min_kb) max_kb = min_kb;

    printf("Running Random Latency Benchmark: %d KB to %d KB\n", min_kb, max_kb);

    FILE* fp = fopen("results_latency.csv", "w");
    if (!fp) {
        printf("Could not open file.\n");
        return 1;
    }

    fprintf(fp, "BlockKB,Latency_ns\n");
    printf("Block(KB)\tLatency(ns)\n");

    for (int size_kb = min_kb; size_kb <= max_kb; size_kb *= 2) {
        double latency = measure_latency(size_kb * KB);
        printf("%d\t\t%.2f\n", size_kb, latency);
        fprintf(fp, "%d,%.2f\n", size_kb, latency);
    }

    fclose(fp);
    printf("\nSaved: results_latency.csv\n");
    return 0;
}