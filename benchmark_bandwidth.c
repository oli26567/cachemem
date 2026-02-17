#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "win_clock.h"

#define KB 1024
#define MB (1024.0 * 1024.0)
#define COPY_REPEATS 2000

double measure_bandwidth(int block_size) {
    char* src = malloc(block_size);
    char* dst = malloc(block_size);

    if (!src || !dst) return -1;

    for (int i = 0; i < block_size; i++)
        src[i] = (char)(i % 256);

    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC_RAW, &start);

    for (int r = 0; r < COPY_REPEATS; r++)
        memcpy(dst, src, block_size);

    clock_gettime(CLOCK_MONOTONIC_RAW, &end);

    free(src);
    free(dst);

    double seconds = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;

    double total_mb = (double)block_size * COPY_REPEATS / MB;

    return total_mb / seconds;
}

int main(int argc, char* argv[]) {
    int min_kb = 1;
    int max_kb = 8192;

    if (argc > 1) min_kb = atoi(argv[1]);
    if (argc > 2) max_kb = atoi(argv[2]);

    if (min_kb <= 0) min_kb = 1;
    if (max_kb < min_kb) max_kb = min_kb;

    printf("Running Bandwidth Benchmark: %d KB to %d KB\n", min_kb, max_kb);
    FILE* fp = fopen("results_bandwidth.csv", "w");
    if (!fp) {
         printf("Could not open file.\n");
         return 1;
    }
    
    fprintf(fp, "BlockKB,Bandwidth_MBps\n");

    printf("Block(KB)\tBW(MB/s)\n");

    for (int size_kb = min_kb; size_kb <= max_kb; size_kb *= 2) {
        double bw = measure_bandwidth(size_kb * KB);
        printf("%d\t\t%.2f\n", size_kb, bw);
        fprintf(fp, "%d,%.2f\n", size_kb, bw);
    }

    fclose(fp);
    printf("\nSaved: results_bandwidth.csv\n");
    return 0;
}
