import tkinter as tk
from tkinter import messagebox
from Chemistry import molesAndCompounds, atomCount, splitOnAtomCount, symbolAndMasses, numberAsSubscript

# Read the equation from file
with open("/Users/ika/Desktop/Spring_2025/CS5630/Homework 2/Homework 2 short sample input.txt", "r") as file:
    equation = file.readline().strip()

# Parse equation into reactants and products
reactants, products = equation.split("=")
reactants = [r.strip() for r in reactants.split("+")]
products = [p.strip() for p in products.split("+")]
compounds = reactants + ["|", "="] + products  # Combine reactants & products for UI

# Ensure 6 columns (pad with empty spaces if needed)
while len(compounds) < 6:
    compounds.append("")

# Get atomic masses from periodic table data
periodic_data = symbolAndMasses("/Users/ika/Desktop/Spring_2025/CS5630/Homework 2/PeriodicTableData.xls")

# Compute molar masses safely
def get_molar_mass(compound):
    atoms = atomCount(compound)
    return sum(float(periodic_data[element]) * int(count) for element, count in atoms.items())

# Store molar masses for all compounds
molar_masses = {compound: get_molar_mass(compound) for compound in compounds if compound and compound not in ["|", "="]}

# Convert formulas to display subscripts
def transform_to_subscript(compound):
    parts = splitOnAtomCount(compound)
    transformed = ""
    for part in parts:
        transformed += f"{numberAsSubscript(part)}" if (part.isdigit() and parts.index(part) != 0) else part
    return transformed

# GUI Setup
root = tk.Tk()
root.title("Stoichiometry Calculator")

# Display equation
tk.Label(root, text=equation).grid(row=0, column=0, columnspan=6, pady=10)

# First Row: Chemical Names
for i, compound in enumerate(compounds):
    tk.Label(root, text=compound).grid(row=1, column=i, padx=5, pady=5)

# Second Row: Transformed Subscripts
for i, compound in enumerate(compounds):
    transformed = transform_to_subscript(compound) if compound not in ["|", "="] else compound
    tk.Label(root, text=transformed).grid(row=2, column=i, padx=5, pady=5)

# Third Row: User Inputs & Computed Values
entries = []
for i in range(6):
    entry = tk.Entry(root, justify="center")
    entry.grid(row=3, column=i, padx=5, pady=5)
    entries.append(entry)

# Only ONE user input in the 2nd column
tk.Label(root, text="Lab Measurement (grams):").grid(row=4, column=0, padx=5, pady=5)
entry_lab_measurement = tk.Entry(root, justify="center")
entry_lab_measurement.grid(row=4, column=1, padx=5, pady=5)

# Checkbox for Moles/Grams - Calls Compute Function on Toggle
checkbox_var = tk.BooleanVar()
checkbox = tk.Checkbutton(root, text="Moles?", variable=checkbox_var, command=lambda: compute_stoichiometry())
checkbox.grid(row=4, column=2, padx=5, pady=5)

# Function to Compute Stoichiometry with Limiting Reagent
def compute_stoichiometry():
    try:
        lab_measurement = float(entry_lab_measurement.get())  # Single user input in grams or moles
        is_moles = checkbox_var.get()

        # Convert the single input to moles if it's in grams
        reference_compound = reactants[1]  # The second reactant is used as input reference
        if not is_moles:
            reference_moles = lab_measurement / molar_masses[reference_compound]  # Convert grams to moles
        else:
            reference_moles = lab_measurement  # Already in moles

        # Compute moles of all reactants based on stoichiometric ratios
        reactant_moles = {}
        for reactant in reactants:
            coefficient = molesAndCompounds(reactant)[0]
            reactant_moles[reactant] = reference_moles * (coefficient / molesAndCompounds(reference_compound)[0])

        # Find the limiting reagent correctly based on **moles**
        smallest_ratio = float("inf")
        limiting_reagents = []  # Allow multiple limiting reagents

        for reactant in reactant_moles:
            ratio = reactant_moles[reactant] / molesAndCompounds(reactant)[0]
            print(f"Checking Limiting Reagent: {reactant}, Ratio: {ratio:.6f}")  # Debugging Output

            if ratio < smallest_ratio:
                smallest_ratio = ratio
                limiting_reagents = [reactant]  # Reset list with new smallest
            elif ratio == smallest_ratio:
                limiting_reagents.append(reactant)  # Add if tied

        print(f"Final Limiting Reagents: {', '.join(limiting_reagents)}")


        # Compute theoretical yield of products based on limiting reagent
        results = {}
        for compound in compounds:
            if compound in ["|", "="]:  # Skip non-molecular placeholders
                continue
            coefficient = molesAndCompounds(compound)[0]

            # Compute product yield for each limiting reagent and take the minimum
            possible_yields = []
            for limiting_reagent in limiting_reagents:  # Now handling multiple reagents
                limiting_coeff = molesAndCompounds(limiting_reagent)[0]
                possible_yields.append((reactant_moles[limiting_reagent] / limiting_coeff) * coefficient)

            theoretical_moles = min(possible_yields)  # Take the smallest amount produced

            # Convert to grams if checkbox is unchecked (grams mode)
            results[compound] = theoretical_moles if is_moles else theoretical_moles * molar_masses[compound]


        # Populate the outputs dynamically
        for i, compound in enumerate(compounds):
            if compound not in ["|", "="]:  # Only update molecule cells
                entries[i].delete(0, tk.END)
                entries[i].insert(0, f"{results.get(compound, 0):.4f}")

        # Show Limiting Reagent(s)
        if len(limiting_reagents) == 1:
            messagebox.showinfo("Limiting Reagent", f"The limiting reagent is {limiting_reagents[0]}.")
        else:
            messagebox.showinfo("Limiting Reagents", f"The limiting reagents are {', '.join(limiting_reagents)}.")


    except ValueError:
        messagebox.showerror("Error", "Please enter a valid numeric input.")

# Compute Button (Calls compute_stoichiometry)
compute_button = tk.Button(root, text="Compute", command=compute_stoichiometry)
compute_button.grid(row=4, column=3, padx=5, pady=5)

root.mainloop()