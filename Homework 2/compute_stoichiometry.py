import tkinter as tk
from tkinter import messagebox
from Chemistry import molesAndCompounds, atomCount, splitOnAtomCount, symbolAndMasses, numberAsSubscript

# The equation from file
with open("/Users/ika/Desktop/Spring_2025/CS5630/Homework 2/Homework 2 short sample input.txt", "r") as file:
    equation = file.readline().strip()
 
"""
Parse equation dynamically for any number of reactants/products - have also ensured that this 
works for all types of balanced checmical equations irrespective of the number of reactants/products
"""
reactants, products = equation.split("=")
reactants = [r.strip() for r in reactants.split("+")]
products = [p.strip() for p in products.split("+")]
compounds = reactants + ["|", "="] + products  # For use in dynamically build of UI structure

print(f"Reactants: {reactants}")
print(f"Products: {products}")
print(f"Full compounds list: {compounds}")

# Ensure UI supports at least 6 columns
while len(compounds) < 6: # Only supports 6 columns for now. 
    compounds.append("")

# Get the atomic masses from periodic table data provided. 
periodic_data = symbolAndMasses("/Users/ika/Desktop/Spring_2025/CS5630/Homework 2/PeriodicTableData.xls")

# Compute molar masses safely
def get_molar_mass(compound):
    atoms = atomCount(compound)
    return sum(float(periodic_data[element]) * int(count) for element, count in atoms.items())

# Store molar masses for all compounds
molar_masses = {compound: get_molar_mass(compound) for compound in compounds if compound and compound not in ["|", "="]}


def transform_to_subscript(compound):
    """
    Method to convert formulas to display subscripts properly
    Ensure all numbers convert except numbers that come first in the compound.

    Args: A list of parsed compounds in the checmical equation, eg: ['3Hg(OH)2', '2H3PO4', 'Hg3(PO4)

    Returns: String compound with transformed subscripts where necessary, eg; Hg(OH)₂
    """
    parts = splitOnAtomCount(compound)
    transformed = ""
    for part in parts:
        transformed += f"{numberAsSubscript(part)}" if (part.isdigit() and parts.index(part) != 0) else part
    return transformed

# GUI Setup
root = tk.Tk()
root.title("Stoichiometry Calculator")

# Display the checmical equation under the title. 
tk.Label(root, text=equation).grid(row=0, column=0, columnspan=6, pady=10)

# First Row: Chemical Names
for i, compound in enumerate(compounds):
    tk.Label(root, text=compound).grid(row=1, column=i, padx=5, pady=5)

# Second Row: Transformed Subscripts
for i, compound in enumerate(compounds):
    transformed = transform_to_subscript(compound) if compound not in ["|", "="] else compound
    tk.Label(root, text=transformed).grid(row=2, column=i, padx=5, pady=5)

# Third Row: User Inputs (Goes into the second cell) & Computed Values
entries = []
for i in range(6):
    entry = tk.Entry(root, justify="center")
    entry.grid(row=3, column=i, padx=5, pady=5)
    entries.append(entry)

# Only ONE user input cell. 
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
        lab_measurement = float(entry_lab_measurement.get())  # user input in grams or moles
        is_moles = checkbox_var.get()

        # Convert the single input to moles if it's in grams
        reference_compound = reactants[1]  # The second reactant is used as input reference
        if not is_moles:
            reference_moles = lab_measurement / molar_masses[reference_compound]  # Convert grams to moles
        else:
            reference_moles = lab_measurement  # Already in moles

        # Compute moles of all reactants based on stoichiometric ratios
        reactant_moles = {}
        reactant_masses = {}  # Track reactant masses correctly
        reactant_moles[reference_compound] = reference_moles  # Ensure input is set properly

        for reactant in reactants:
            if reactant != reference_compound:  # Other reactants should be computed
                parsed_data = molesAndCompounds(reactant)
                if not parsed_data or len(parsed_data) < 2:
                    raise ValueError(f"Error parsing reactant: {reactant}, received: {parsed_data}")
                coefficient = parsed_data[0]
                reactant_moles[reactant] = reference_moles * (coefficient / molesAndCompounds(reference_compound)[0])
        
        # Convert to grams if checkbox is **unchecked**
        for reactant in reactants:
            reactant_masses[reactant] = reactant_moles[reactant] * molar_masses[reactant] if not is_moles else reactant_moles[reactant]

        # Find the limiting reagent correctly based on **moles**
        smallest_ratio = float("inf")
        limiting_reagent = None  # Track a single limiting reagent

        for reactant in reactant_moles:
            ratio = reactant_moles[reactant] / molesAndCompounds(reactant)[0]
            print(f"Checking Limiting Reagent: {reactant}, Ratio: {ratio:.6f}")  # Debugging Output

            if ratio < smallest_ratio:
                smallest_ratio = ratio
                limiting_reagent = reactant  # Track first smallest reagent

        print(f"Final Limiting Reagent: {limiting_reagent}")

        # Compute theoretical yield of products based on limiting reagent
        results = {}
        for compound in products:  # Iterate over all products dynamically
            parsed_data = molesAndCompounds(compound)
            if not parsed_data or len(parsed_data) < 2:
                raise ValueError(f"Error parsing product: {compound}, received: {parsed_data}")

            coefficient = parsed_data[0]
            limiting_coeff = molesAndCompounds(limiting_reagent)[0]
            theoretical_moles = (reactant_moles[limiting_reagent] / limiting_coeff) * coefficient

            # Convert to grams if checkbox is unchecked (grams mode)
            results[compound] = theoretical_moles if is_moles else theoretical_moles * molar_masses[compound]

        # Populate the outputs dynamically for **all valid reactants and products**
        for i, compound in enumerate(compounds):
            if compound not in ["|", "="]:  # Skip separators
                value = reactant_masses.get(compound, results.get(compound, 0))
                entries[i].delete(0, tk.END)
                entries[i].insert(0, f"{value:.4f}")

        # Show Limiting Reagent
        messagebox.showinfo("Limiting Reagent", f"The limiting reagent is {limiting_reagent}.")

    except ValueError:
        messagebox.showerror("Error", "Please enter a valid numeric input.")

# Compute Button (Calls compute_stoichiometry)
compute_button = tk.Button(root, text="Compute", command=compute_stoichiometry)
compute_button.grid(row=4, column=3, padx=5, pady=5)

root.mainloop()