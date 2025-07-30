"""
Module for displaying data from an Ethos log file previously imported and preprocessed as a 
DataFrame.

This module provides a function to display and interactively plot selected columns from a 
DataFrame using Matplotlib embedded in a Tkinter window. Users can select which columns to plot 
using scrollable checkboxes, and view up to three data series with separate y-axes.

Functions:
    display_log_data(df, filename): Display an interactive plot window for selected log columns.
"""
import os
import tkinter as tk
from tkinter import messagebox
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

def display_log_data(df, filename):
    """
    Display an interactive plot window for selected log columns.

    Opens a Tkinter window with a scrollable list of checkboxes for each numeric column (except 
    'ElapsedTime'). Users can select up to three columns to plot with separate y-axes, or more 
    columns to plot on a single axis. The plot updates automatically as selections change.

    Args:
        df (pd.DataFrame): The DataFrame containing the log data, including an 'ElapsedTime' column.
        filename (str): The name of the source file (for display purposes).

    Returns:
        None
    """
    # Variable to control axis mode
    use_one_y_axis = tk.BooleanVar(value=False)

    if 'ElapsedTime' not in df.columns:
        messagebox.showerror("Error", "ElapsedTime column not found in data.")
        return

    # Create window
    win = tk.Toplevel()
    win.title("Display Log Data")

    # Frame for checkboxes (now inside a scrollable canvas)
    checkbox_outer_frame = tk.Frame(win)
    checkbox_outer_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    # Create a canvas and a vertical scrollbar for the checkboxes
    checkbox_canvas = tk.Canvas(checkbox_outer_frame, borderwidth=0, height=350)
    scrollbar = tk.Scrollbar(checkbox_outer_frame, orient="vertical", command=checkbox_canvas.yview)
    checkbox_frame = tk.Frame(checkbox_canvas)

    checkbox_frame.bind(
        "<Configure>",
        lambda e: checkbox_canvas.configure(
            scrollregion=checkbox_canvas.bbox("all")
        )
    )

    checkbox_canvas.create_window((0, 0), window=checkbox_frame, anchor="nw")
    checkbox_canvas.configure(yscrollcommand=scrollbar.set)

    checkbox_canvas.pack(side="left", fill="y", expand=False)
    scrollbar.pack(side="right", fill="y")

    # Frame for plot
    plot_frame = tk.Frame(win)
    plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Matplotlib Figure
    fig, ax = plt.subplots(figsize=(6, 4))
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Add navigation toolbar
    toolbar = NavigationToolbar2Tk(canvas, plot_frame)
    
    toolbar.update()
    toolbar.pack(side=tk.TOP, fill=tk.X)

    ax2 = ax.twinx()  # For two y-axes if needed
    ax3 = ax.twinx()  # For three y-axes if needed


    def update_plot(*args):
        ax.clear()
        ax2.clear()
        ax3.clear()

        ax.yaxis.set_visible(True)
        ax2.axis('off')
        ax3.axis('off')

        selected_cols = [col for col, (var, trace_id) in col_vars.items() if var.get()]
        colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple']

        if len(selected_cols) == 0:
            ax.text(0.5, 0.5, 'Select data columns to plot\nusing checkboxes on the left',
                            horizontalalignment='center', verticalalignment='center',
                            transform=ax.transAxes, fontsize=14,
                            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
            ax.set_title(f"Log File: {os.path.basename(filename)}",
                                fontsize=14, fontweight='bold')

        else:
            if use_one_y_axis.get() or len(selected_cols) > 3:
                # Plot all on one axis
                for i, col in enumerate(selected_cols):
                    ax.plot(df['ElapsedTime'], df[col], label=col, color=colors[i % len(colors)])
                ax.set_xlabel('ElapsedTime (s)')
                ax.set_ylabel('Value')
                ax.legend(loc='upper right')
            else:
                # Up to 3 y-axes
                if len(selected_cols) >= 1:
                    lines = ax.plot(df['ElapsedTime'], df[selected_cols[0]],
                                    label=selected_cols[0], color=colors[0])
                    ax.set_xlabel('ElapsedTime (s)')
                    ax.set_ylabel(selected_cols[0], color=colors[0])
                    ax.tick_params(axis='y', labelcolor=colors[0])

                if len(selected_cols) >= 2:
                    ax2.axis('on')
                    ax2.yaxis.set_visible(True)
                    line2 = ax2.plot(df['ElapsedTime'], df[selected_cols[1]],
                                     label=selected_cols[1], color=colors[1])
                    ax2.set_ylabel(selected_cols[1], color=colors[1])
                    ax2.tick_params(axis='y', labelcolor=colors[1])
                    ax2.yaxis.set_label_position('right')
                    lines = lines + line2

                if len(selected_cols) >= 3:
                    ax3.axis('on')
                    ax3.yaxis.set_visible(True)
                    ax3.spines['right'].set_position(('outward', 60))
                    lines3 = ax3.plot(df['ElapsedTime'], df[selected_cols[2]],
                                      label=selected_cols[2], color=colors[2])
                    ax3.set_ylabel(selected_cols[2], color=colors[2])
                    ax3.tick_params(axis='y', labelcolor=colors[2])
                    ax3.yaxis.set_label_position('right')
                    lines = lines + lines3

                labels = [l.get_label() for l in lines]
                ax.legend(lines, labels, loc='upper right')

        # Common plot settings
        ax.set_xlabel("Elapsed Time (seconds)", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.set_title(f"Log File: {os.path.basename(filename)}",
                            fontsize=14, fontweight='bold')

        # Data statistics
        stats_text = ""
        stats_text += f"Date: {df['Date'].iloc[0]}\n"
        stats_text += f"T0: {df['Time'].iloc[0]}\n"
        stats_text += f"Duration: {df['ElapsedTime'].iloc[-1] - df['ElapsedTime'].iloc[0]:.1f}s"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                        fontsize=10, verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

        canvas.draw()

    # Variables for checkboxes
    col_vars = {}

    for col in df.columns:
        if col != 'ElapsedTime' and pd.api.types.is_numeric_dtype(df[col]):
            var = tk.BooleanVar()
            trace_id = var.trace_add('write', update_plot)
            cb = tk.Checkbutton(checkbox_frame, text=col, variable=var)
            cb.pack(anchor='w')
            col_vars[col] = var,trace_id


    def set_all():
        """
        Selects all available data columns for plotting.

        This function sets all checkboxes to True, enabling all numeric columns for display
        in the plot window. In order to avoid updating the plot too frequently, the trace
        is temporarily removed while the variables are updated.
        """
        for col, (var, trace_id) in col_vars.items():
            var.trace_remove('write', trace_id)
            var.set(True)
            new_trace_id = var.trace_add('write', update_plot)
            col_vars[col] = var, new_trace_id

        update_plot()

    def clear_all():
        """
        Clears all selected data columns.

        This function sets all checkboxes to False, clearing the display off all data series
        in the plot window. In order to avoid updating the plot too frequently, the trace
        is temporarily removed while the variables are updated.
        """
        for col, (var, trace_id) in col_vars.items():
            var.trace_remove('write', trace_id)
            var.set(False)
            new_trace_id = var.trace_add('write', update_plot)
            col_vars[col] = var, new_trace_id

        update_plot()

    def toggle_one_y_axis():
        """
        Toggles the use of a single y-axis for all selected data series.

        This function updates the plot to either use one y-axis for all selected columns or
        separate y-axes for up to three columns, depending on the state of the use_one_y_axis variable.
        """
        use_one_y_axis.set(not use_one_y_axis.get())
        one_y_axis_button.config(relief=tk.SUNKEN if use_one_y_axis.get() else tk.FLAT)
        one_y_axis_button.config(bg="white" if use_one_y_axis.get() else btn_frame.cget("background"))

        update_plot()

    btn_frame = tk.Frame(checkbox_frame)
    btn_frame.pack(pady=10, fill=tk.X)
    tk.Button(btn_frame, text="Select All", command=set_all).pack(side=tk.LEFT, padx=2)
    tk.Button(btn_frame, text="Clear All", command=clear_all).pack(side=tk.LEFT, padx=2)

    # Add the one_y_axis_button to the toolbar
    # The image coloring, relief, overrelief, and borderwidth here, along with the modifications in the
    # toggle_one_y_axis method attempt to replicate (or at least approximate) the matplotlib 
    # NavigationToolbar2Tk behavior.
    # First, add a vertical separator 
    separator = tk.Frame(toolbar, height='18p', relief=tk.RIDGE, bg='DarkGray')
    separator.pack(side=tk.LEFT, padx='3p')

    # Then, create the one_y_axis_button
    one_y_axis_image = tk.PhotoImage(file="src/one_y_axis.png")
    one_y_axis_button = tk.Button(master=toolbar, image=one_y_axis_image, relief = tk.FLAT, overrelief=tk.SUNKEN, borderwidth=1, command=toggle_one_y_axis)
    one_y_axis_button.image = one_y_axis_image  # Keep a reference to avoid garbage collection
    one_y_axis_button.pack(side="left")

    toolbar.update()

    # Initial plot
    update_plot()
