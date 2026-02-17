#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "win_clock.h"

int N = 512;
int BLOCK = 64;
int REPEATS = 3;

double *A;
double *B;
double *C;


#define IDX(i, j, n) ((i) * (n) + (j))

void init_matrix(double *M, int n) {
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            M[IDX(i, j, n)] = rand() % 10;
}

void zero_matrix(double *M, int n) {
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            M[IDX(i, j, n)] = 0.0;
}


void multiply_ijk(double *A, double *B, double *C, int n) {
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            for (int k = 0; k < n; k++)
                C[IDX(i, j, n)] += A[IDX(i, k, n)] * B[IDX(k, j, n)];
}


void multiply_ikj(double *A, double *B, double *C, int n) {
    for (int i = 0; i < n; i++)
        for (int k = 0; k < n; k++)
            for (int j = 0; j < n; j++)
                C[IDX(i, j, n)] += A[IDX(i, k, n)] * B[IDX(k, j, n)];
}


void multiply_jik(double *A, double *B, double *C, int n) {
    for (int j = 0; j < n; j++)
        for (int i = 0; i < n; i++)
            for (int k = 0; k < n; k++)
                C[IDX(i, j, n)] += A[IDX(i, k, n)] * B[IDX(k, j, n)];
}


void multiply_jki(double *A, double *B, double *C, int n) {
    for (int j = 0; j < n; j++)
        for (int k = 0; k < n; k++)
            for (int i = 0; i < n; i++)
                C[IDX(i, j, n)] += A[IDX(i, k, n)] * B[IDX(k, j, n)];
}


void multiply_kij(double *A, double *B, double *C, int n) {
    for (int k = 0; k < n; k++)
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                C[IDX(i, j, n)] += A[IDX(i, k, n)] * B[IDX(k, j, n)];
}


void multiply_kji(double *A, double *B, double *C, int n) {
    for (int k = 0; k < n; k++)
        for (int j = 0; j < n; j++)
            for (int i = 0; i < n; i++)
                C[IDX(i, j, n)] += A[IDX(i, k, n)] * B[IDX(k, j, n)];
}


void multiply_blocked(double *A, double *B, double *C, int n) {
    for (int ii = 0; ii < n; ii += BLOCK)
        for (int jj = 0; jj < n; jj += BLOCK)
            for (int kk = 0; kk < n; kk += BLOCK)
                for (int i = ii; i < ii + BLOCK && i < n; i++)
                    for (int k = kk; k < kk + BLOCK && k < n; k++)
                        for (int j = jj; j < jj + BLOCK && j < n; j++)
                            C[IDX(i, j, n)] += A[IDX(i, k, n)] * B[IDX(k, j, n)];
}

double measure(void (*func)(double*, double*, double*, int)) {
    zero_matrix(C, N);

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC_RAW, &start);
    func(A, B, C, N);
    clock_gettime(CLOCK_MONOTONIC_RAW, &end);

    return (end.tv_sec - start.tv_sec) * 1000.0 + (end.tv_nsec - start.tv_nsec) / 1e6;
}

double run_and_average(void (*func)(double*, double*, double*, int)) {
    double total = 0.0;
    for (int r = 0; r < REPEATS; r++) {
        total += measure(func);
    }
    return total / REPEATS;
}

int main(int argc, char* argv[]) {

    if (argc > 1) N = atoi(argv[1]);
    if (argc > 2) BLOCK = atoi(argv[2]);
    if (argc > 3) REPEATS = atoi(argv[3]);

    if (N <= 0) N = 512;
    if (BLOCK <= 0) BLOCK = 64;
    if (REPEATS <= 0) REPEATS = 3;

    printf("Running Matrix Benchmark with N=%d, BLOCK=%d, REPEATS=%d\n", N, BLOCK, REPEATS);

    A = (double*)malloc(N * N * sizeof(double));
    B = (double*)malloc(N * N * sizeof(double));
    C = (double*)malloc(N * N * sizeof(double));

    if (!A || !B || !C) {
        printf("Memory allocation failed!\n");
        return 1;
    }

    FILE* fp = fopen("results_matrix.csv", "w");
    if (!fp) {
        printf("Could not open results_matrix.csv\n");
        return 1;
    }

    fprintf(fp, "Version,Time_ms\n");

    init_matrix(A, N);
    init_matrix(B, N);

    printf("Testing IJK...\n");
    fprintf(fp, "IJK,%.2f\n", run_and_average(multiply_ijk));
    
    printf("Testing IKJ...\n");
    fprintf(fp, "IKJ,%.2f\n", run_and_average(multiply_ikj));
    
    printf("Testing JIK...\n");
    fprintf(fp, "JIK,%.2f\n", run_and_average(multiply_jik));
    
    printf("Testing JKI...\n");
    fprintf(fp, "JKI,%.2f\n", run_and_average(multiply_jki));
    
    printf("Testing KIJ...\n");
    fprintf(fp, "KIJ,%.2f\n", run_and_average(multiply_kij));
    
    printf("Testing KJI...\n");
    fprintf(fp, "KJI,%.2f\n", run_and_average(multiply_kji));
    
    printf("Testing Blocked (Block=%d)...\n", BLOCK);
    fprintf(fp, "BLOCKED_%d,%.2f\n", BLOCK, run_and_average(multiply_blocked));

    fclose(fp);
    printf("Saved: results_matrix.csv\n");
    
    free(A);
    free(B);
    free(C);
    
    return 0;
}
