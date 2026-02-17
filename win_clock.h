#ifndef WIN_CLOCK_H
#define WIN_CLOCK_H

#ifdef _WIN32
#include <windows.h>
#include <time.h>

#ifndef CLOCK_MONOTONIC_RAW
#define CLOCK_MONOTONIC_RAW 4
#endif

static int clock_gettime(int type, struct timespec* ts)
{
    static LARGE_INTEGER freq;
    LARGE_INTEGER count;

    if (!freq.QuadPart)
        QueryPerformanceFrequency(&freq);

    QueryPerformanceCounter(&count);

    ts->tv_sec = count.QuadPart / freq.QuadPart;
    ts->tv_nsec = (long)((count.QuadPart % freq.QuadPart) * 1000000000LL / freq.QuadPart);

    return 0;
}

#endif

#endif

