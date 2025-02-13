import tkinter as tk
from tkinter import messagebox
from Chemistry import molesAndCompounds, atomCount, splitOnAtomCount

# Define atomic masses (in g/mol) for common elements
atomic_masses = {
    "H": 1.008,
    "O": 16.00,
    "Hg": 200.59,
    "P": 30.97
}

def compute_stoichiometry():
    try:
        # Get the lab measurement from the user
        lab_measurement = float(entry_lab_measurement.get())
        is_moles = checkbox_var.get()

        # Parse the compounds and coefficients from the chemical equation
        coefficients = [3, 2, 1, 6]  # Coefficients for Hg(OH)2, H3PO4, Hg3(PO4)2, H2O
        compounds = ["Hg(OH)2", "H3PO4", "Hg3(PO4)2", "H2O"]

        # Compute molar masses using the helper module
        molar_masses = {}
        for compound in compounds:
            atom_counts = atomCount(compound)  # Get atom counts using the helper module
            molar_masses[compound] = sum(atomic_masses[atom] * count for atom, count in atom_counts.items())

        # Calculate results
        results = {}
        for i, compound in enumerate(compounds):
            coefficient = coefficients[i]
            if is_moles:
                results[compound] = lab_measurement / coefficients[0] * coefficient
            else:
                results[compound] = (lab_measurement / coefficients[0] * coefficient) * molar_masses[compound]

        # Populate the results into the output row
        for i, compound in enumerate(compounds):
            output_entries[i].delete(0, tk.END)
            output_entries[i].insert(0, f"{results[compound]:.4f}")

    except ValueError:
        messagebox.showerror("Error", "Please enter a valid lab measurement.")

def on_checkbox_toggle():
    compute_stoichiometry()

# Main GUI Application
root = tk.Tk()
root.title("Stoichiometry Calculator")

# Input Row (Equation)
tk.Label(root, text="3Hg(OH)2 + 2H3PO4 = Hg3(PO4)2 + 6H2O").grid(row=0, column=0, columnspan=6, pady=10)

# Transformed Values (Molar Masses)
molar_masses_display = ["234.59", "98.00", "701.56", "18.015"]
for i, molar_mass in enumerate(molar_masses_display):
    tk.Label(root, text=f"{molar_mass} g/mol").grid(row=1, column=i, padx=5, pady=5)

# Output Row (Results)
output_entries = []
for i in range(4):
    entry = tk.Entry(root, justify="center")
    entry.grid(row=2, column=i, padx=5, pady=5)
    output_entries.append(entry)

# Lab Measurement Input
tk.Label(root, text="Lab Measurement:").grid(row=3, column=0, padx=5, pady=5)
entry_lab_measurement = tk.Entry(root, justify="center")
entry_lab_measurement.grid(row=3, column=1, padx=5, pady=5)

# Checkbox for Moles/Grams
checkbox_var = tk.BooleanVar()
checkbox = tk.Checkbutton(root, text="Moles?", variable=checkbox_var, command=on_checkbox_toggle)
checkbox.grid(row=3, column=2, padx=5, pady=5)

# Compute Button
compute_button = tk.Button(root, text="Compute", command=compute_stoichiometry)
compute_button.grid(row=3, column=3, padx=5, pady=5)

# Run the application
root.mainloop()