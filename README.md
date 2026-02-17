# Testing and Analysing Cache Memory Access Time

This project is a performance analysis tool I built to explore how a computer's memory hierarchy affects how fast software runs. By combining a high-performance engine written in **C** with a **Python** visualization dashboard, the app shows the direct link between low-level hardware behavior and code efficiency.

---

## Functionality

- **Memory Hierarchy Profiling**: The tool measures and plots latency and bandwidth, making it easy to see the physical boundaries between L1, L2, L3 caches, and the Main Memory (RAM).
- **Algorithmic Efficiency Analysis**: I included a study on Matrix Multiplication to show how the way you access memory directly determines the execution speed.
- **Hardware-Aware Optimization**: The project demonstrates how **Loop Blocking (Tiling)** keeps data within the fastest cache levels, which helps prevent the CPU from stalling while waiting for data from RAM.
- **Precision Timing**: To get accurate results on Windows, I used a custom nanosecond-resolution timer (`QueryPerformanceCounter`) so that even the fastest L1 cache hits are recorded correctly.

---

## How It Works

The project is structured as a pipeline that connects low-level hardware testing with data visualization. I used **Python** to build a manager that handles the test configurations and launches the measurement scripts written in **C**. The C scripts handle the actual memory access operations, like reading through memory addresses or copying data blocks, to see how the CPU performs under different conditions.



After the tests run, the results are saved into **CSV files**. The Python interface then reads these files and uses Matplotlib to generate the final graphs. These charts show the "latency spikes" and "bandwidth drops" that happen when the data size exceeds the L1, L2, or L3 cache capacity and the system has to go all the way to the RAM.

---

## Technologies Used

- **Languages:** C (for the core benchmarking logic) and Python (for the GUI and graphs).
- **GUI Framework:** Tkinter.
- **Data Visualization:** Matplotlib.
- **Design:** Modular architecture with a clear split between the C measurement core and the Python analytics layer.

---

## Future Improvements

- Add **SIMD/Vectorization** support to test the maximum theoretical bandwidth of the processor.
- Implement **Multithreading** to see how performance changes when multiple cores compete for the same cache.
- Add an **Auto-Detect** feature to compare my measured results against the official CPU specs.
