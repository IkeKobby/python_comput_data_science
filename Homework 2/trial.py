import tkinter as tk
from tkinter import messagebox
from Chemistry import molesAndCompounds, atomCount, splitOnAtomCount, symbolAndMasses

# Read the equation from file
with open("/Users/ika/Desktop/Spring_2025/CS5630/Homework 2/Homework 2 short sample input.txt", "r") as file:
    equation = file.readline().strip()

# Parse the equation into reactants and products
reactants, products = equation.split("=")
reactants = [r.strip() for r in reactants.split("+")]
products = [p.strip() for p in products.split("+")]
compounds = reactants + products  # Combine reactants & products for UI

# Ensure 6 columns (pad with empty spaces if needed)
while len(compounds) < 6:
    compounds.append("")

# Atomic Mass Data
periodic_data = symbolAndMasses("/Users/ika/Desktop/Spring_2025/CS5630/Homework 2/PeriodicTableData.xls")

# Compute molar masses safely
def get_molar_mass(compound):
    atoms = atomCount(compound)  # Ensures dictionary {'H': '2', 'O': '1'} etc.
    return sum(float(periodic_data[element]) * int(count) for element, count in atoms.items())

# Molar masses dictionary
molar_masses = {compound: get_molar_mass(compound) for compound in compounds if compound}

# Convert formulas to display subscripts
def transform_to_subscript(compound):
    parts = splitOnAtomCount(compound)
    transformed = ""
    for part in parts:
        transformed += f"{chr(8320 + int(part))}" if part.isdigit() else part
    return transformed

# GUI Setup
root = tk.Tk()
root.title("Stoichiometry Calculator")

# Display equation
tk.Label(root, text=equation).grid(row=0, column=0, columnspan=6, pady=10)

# First Row: Chemical Names
for i, compound in enumerate(compounds):
    tk.Label(root, text=compound).grid(row=1, column=i, padx=5, pady=5)

# Second Row: Transformed Atom Count
for i, compound in enumerate(compounds):
    transformed = transform_to_subscript(compound) if compound else ""
    tk.Label(root, text=transformed).grid(row=2, column=i, padx=5, pady=5)

# Third Row: User Inputs & Computed Values
entries = []
for i in range(6):
    entry = tk.Entry(root, justify="center")
    entry.grid(row=3, column=i, padx=5, pady=5)
    entries.append(entry)

# Lab Measurement Input
tk.Label(root, text="Lab Measurement:").grid(row=4, column=0, padx=5, pady=5)
entry_lab_measurement = tk.Entry(root, justify="center")
entry_lab_measurement.grid(row=4, column=1, padx=5, pady=5)

# Checkbox for Moles/Grams - Now linked to automatic updates
checkbox_var = tk.BooleanVar()
checkbox = tk.Checkbutton(root, text="Moles?", variable=checkbox_var, command=lambda: compute_stoichiometry())
checkbox.grid(row=4, column=2, padx=5, pady=5)

# Compute Button
def compute_stoichiometry():
    try:
        lab_measurement = float(entry_lab_measurement.get())
        is_moles = checkbox_var.get()  # Get checkbox state

        # Reference compound for calculations
        reference_compound = compounds[0]
        ref_molar_mass = molar_masses[reference_compound]

        # Compute values
        results = {}
        for compound in compounds:
            if compound:
                ratio = molar_masses[compound] / ref_molar_mass
                results[compound] = (lab_measurement * ratio) if not is_moles else (lab_measurement / ref_molar_mass) * ratio

        # Populate the outputs dynamically
        for i, compound in enumerate(compounds):
            entries[i].delete(0, tk.END)
            entries[i].insert(0, f"{results.get(compound, 0):.4f}")

    except ValueError:
        messagebox.showerror("Error", "Enter a valid lab measurement.")

compute_button = tk.Button(root, text="Compute", command=compute_stoichiometry)
compute_button.grid(row=4, column=3, padx=5, pady=5)

root.mainloop()