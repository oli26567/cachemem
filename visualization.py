import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import subprocess
import threading
import queue
import time
from matplotlib.figure import Figure

class BenchmarkVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Cache Memory Performance Analysis & Control")
        self.root.geometry("1400x900")


        self.bandwidth_file = "results_bandwidth.csv"
        self.latency_file = "results_latency.csv"
        self.matrix_file = "results_matrix.csv"

        self.df_bandwidth = None
        self.df_latency = None
        self.df_matrix = None


        self.log_queue = queue.Queue()
        self.is_running = False


        self.var_n = tk.StringVar(value="512")
        self.var_block = tk.StringVar(value="64")
        self.var_repeats = tk.StringVar(value="3")
        
        self.var_min = tk.StringVar(value="1")
        self.var_max = tk.StringVar(value="8192")

        self.create_widgets()
        self.load_data()
        self.check_queue()

    def create_widgets(self):

        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(header_frame, text="Cache Benchmark Suite", font=("Segoe UI", 18, "bold"))
        title_label.pack(side=tk.LEFT)

        status_frame = ttk.Frame(header_frame)
        status_frame.pack(side=tk.RIGHT)
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, font=("Segoe UI", 12))
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        self.progress = ttk.Progressbar(header_frame, mode='indeterminate')



        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_matrix = ttk.Frame(self.notebook)
        self.tab_bandwidth = ttk.Frame(self.notebook)
        self.tab_latency = ttk.Frame(self.notebook)
        self.tab_log = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_matrix, text="Matrix Multiplication")
        self.notebook.add(self.tab_bandwidth, text="Bandwidth Graph")
        self.notebook.add(self.tab_latency, text="Latency Graph")
        self.notebook.add(self.tab_log, text="Execution Logs")


        self.create_matrix_tab(self.tab_matrix)
        self.create_memory_tab(self.tab_bandwidth, "Bandwidth")
        self.create_memory_tab(self.tab_latency, "Latency")


        self.log_text = scrolledtext.ScrolledText(self.tab_log, state='disabled', font=("Consolas", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def create_matrix_tab(self, parent):

        control_frame = ttk.LabelFrame(parent, text="Benchmark Configuration", padding="10")
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(control_frame, text="Matrix Size (N):", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
        ttk.Entry(control_frame, width=10, textvariable=self.var_n).pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Block Size (B):", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
        ttk.Entry(control_frame, width=10, textvariable=self.var_block).pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Repeats:", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)
        ttk.Entry(control_frame, width=10, textvariable=self.var_repeats).pack(side=tk.LEFT, padx=5)

        self.btn_run_matrix = ttk.Button(control_frame, text="▶ Run Matrix Benchmark", command=self.run_matrix_benchmark)
        self.btn_run_matrix.pack(side=tk.RIGHT, padx=10)


        self.matrix_plot_frame = ttk.Frame(parent)
        self.matrix_plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def create_memory_tab(self, parent, context):
        # Controls
        control_frame = ttk.LabelFrame(parent, text="Benchmark Configuration", padding="10")
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(control_frame, text="Min Size (KB):", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
        ttk.Entry(control_frame, width=10, textvariable=self.var_min).pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Max Size (KB):", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
        ttk.Entry(control_frame, width=10, textvariable=self.var_max).pack(side=tk.LEFT, padx=5)




        if not hasattr(self, 'mem_buttons'): self.mem_buttons = []
        
        btn = ttk.Button(control_frame, text=f"▶ Run {context} Test", command=self.run_memory_benchmark)
        btn.pack(side=tk.RIGHT, padx=10)
        self.mem_buttons.append(btn)


        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        

        if context == "Bandwidth":
            self.bandwidth_plot_frame = frame
        else:
            self.latency_plot_frame = frame

    def log(self, message):
        self.log_queue.put(message)

    def check_queue(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.log_text.config(state='normal')
            self.log_text.insert(tk.END, msg + "\n")
            self.log_text.see(tk.END)
            self.log_text.config(state='disabled')
        
        self.root.after(100, self.check_queue)

    def toggle_ui(self, enable=True):
        state = "normal" if enable else "disabled"
        self.btn_run_matrix.config(state=state)

        if hasattr(self, 'mem_buttons'):
            for btn in self.mem_buttons:
                btn.config(state=state)
        
        if enable:
            self.progress.pack_forget()
            self.status_var.set("Ready")
            self.load_data()
        else:
            self.progress.pack(side=tk.RIGHT, padx=10)
            self.status_var.set("Running Benchmark...")

    def run_command_thread(self, commands, completion_callback=None):
        self.toggle_ui(False)
        self.notebook.select(self.tab_log)
        
        def _target():
            for cmd in commands:
                self.log(f"--- Executing: {' '.join(cmd)} ---")
                try:

                    exe = cmd[0]
                    if os.path.exists(exe + ".exe"):
                        cmd[0] = exe + ".exe"
                    elif os.path.exists(os.path.join("proiectscs", exe + ".exe")):
                        cmd[0] = os.path.join("proiectscs", exe + ".exe")
                    
                    self.log(f"Full path: {cmd[0]}")
                    
                    process = subprocess.Popen(
                        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                        universal_newlines=True, bufsize=1, creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    for line in process.stdout:
                        self.log(line.strip())
                    
                    process.wait()
                    if process.returncode != 0:
                        self.log(f"ERROR: Process exited with code {process.returncode}")
                        err = process.stderr.read()
                        if err: self.log(f"Stderr: {err}")
                except Exception as e:
                    self.log(f"EXCEPTION: {str(e)}")
            
            self.log("--- Done ---")
            self.root.after(0, lambda: self.toggle_ui(True))
            if completion_callback:
                self.root.after(0, completion_callback)

        thread = threading.Thread(target=_target, daemon=True)
        thread.start()

    def run_matrix_benchmark(self):
        n = self.var_n.get()
        block = self.var_block.get()
        repeats = self.var_repeats.get()
        


        commands = [["matrix", n, block, repeats]]
        self.run_command_thread(commands, lambda: self.notebook.select(self.tab_matrix))

    def run_memory_benchmark(self):
        min_kb = self.var_min.get()
        max_kb = self.var_max.get()
        
        commands = [
            ["benchmark_bandwidth", min_kb, max_kb],
            ["benchmark_latency", min_kb, max_kb]
        ]
        self.run_command_thread(commands, lambda: self.notebook.select(self.tab_bandwidth))

    def load_data(self):
        try:
            if os.path.exists(self.bandwidth_file):
                self.df_bandwidth = pd.read_csv(self.bandwidth_file)
                self.plot_bandwidth()
            
            if os.path.exists(self.latency_file):
                self.df_latency = pd.read_csv(self.latency_file)
                self.plot_latency()

            if os.path.exists(self.matrix_file):
                self.df_matrix = pd.read_csv(self.matrix_file)
                self.plot_matrix()
        except Exception as e:
            self.log(f"Error loading data: {e}")

    def plot_matrix(self):
        for widget in self.matrix_plot_frame.winfo_children(): widget.destroy()
        if self.df_matrix is None: return

        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        self.df_matrix.columns = self.df_matrix.columns.str.strip()
        versions = self.df_matrix.iloc[:, 0]
        times = self.df_matrix.iloc[:, 1]
        
        bars = ax.bar(versions, times, color='#2ca02c')
        ax.set_title("Matrix Multiplication Time (Lower is Better)")
        ax.set_ylabel("Time (ms)")
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height, f'{height:.1f}', ha='center', va='bottom')

        canvas = FigureCanvasTkAgg(fig, master=self.matrix_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def plot_bandwidth(self):
        for widget in self.bandwidth_plot_frame.winfo_children(): widget.destroy()
        if self.df_bandwidth is None: return

        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        self.df_bandwidth.columns = self.df_bandwidth.columns.str.strip()
        ax.plot(self.df_bandwidth['BlockKB'], self.df_bandwidth['Bandwidth_MBps'], marker='o', linewidth=2)
        ax.set_xscale('log')
        ax.set_title("Memory Bandwidth (Higher is Better)")
        ax.set_xlabel("Block Size (KB)")
        ax.set_ylabel("Bandwidth (MB/s)")
        ax.grid(True, which="both", linestyle='--', alpha=0.5)

        canvas = FigureCanvasTkAgg(fig, master=self.bandwidth_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def plot_latency(self):
        for widget in self.latency_plot_frame.winfo_children(): widget.destroy()
        if self.df_latency is None: return

        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        self.df_latency.columns = self.df_latency.columns.str.strip()
        ax.plot(self.df_latency['BlockKB'], self.df_latency['Latency_ns'], marker='s', color='red', linewidth=2)
        ax.set_xscale('log')
        ax.set_title("Memory Latency (Lower is Better)")
        ax.set_xlabel("Block Size (KB)")
        ax.set_ylabel("Latency (ns)")
        ax.grid(True, which="both", linestyle='--', alpha=0.5)

        canvas = FigureCanvasTkAgg(fig, master=self.latency_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = BenchmarkVisualizer(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter...")
