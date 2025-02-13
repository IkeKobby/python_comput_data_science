import tkinter as tk
from tkinter import messagebox
from Chemistry import molesAndCompounds, atomCount, splitOnAtomCount, symbolAndMasses, numberAsSubscript

# Read the equation from file
with open("/Users/ika/Desktop/Spring_2025/CS5630/python_comput_data_science/Homework 2/Homework 2 short sample input.txt", "r") as file:
    equation = file.readline().strip()

# Parse equation dynamically for any number of reactants/products
reactants, products = equation.split("=")
reactants = [r.strip() for r in reactants.split("+")]
products = [p.strip() for p in products.split("+")]

# Include separators, but replace "|" with an empty string
compounds = reactants + [""] + ["="] + products  # "|" replaced with ""

# Ensure UI supports at least 6 columns
while len(compounds) < 6:
    compounds.append("")

# Get atomic masses from periodic table data
periodic_data = symbolAndMasses("/Users/ika/Desktop/Spring_2025/CS5630/python_comput_data_science/Homework 2/PeriodicTableData.xls")

# Compute molar masses safely
def get_molar_mass(compound):
    atoms = atomCount(compound)
    return sum(float(periodic_data[element]) * int(count) for element, count in atoms.items())

# Store molar masses for all compounds
molar_masses = {compound: get_molar_mass(compound) for compound in compounds if compound not in ["", "="]}

# Convert formulas to display subscripts properly
def transform_to_subscript(compound):
    if compound == "=":  # ✅ Ensure "=" is not transformed
        return "="
    parts = splitOnAtomCount(compound)
    transformed = ""
    for part in parts:
        transformed += f"{numberAsSubscript(part)}" if (part.isdigit() and parts.index(part) != 0) else part  # Ensure all numbers convert
    return transformed

# GUI Setup
root = tk.Tk()
root.title("Stoichiometry Calculator")

# Display equation
tk.Label(root, text=equation).grid(row=0, column=0, columnspan=6, pady=10)

# First Row: Chemical Names (Includes `=` but NOT `|`)
for i, compound in enumerate(compounds):
    tk.Entry(root, justify="center", width=10, state="readonly",
             readonlybackground="white", fg="black").grid(row=1, column=i, padx=5, pady=5)
    tk.Label(root, text=compound).grid(row=1, column=i, padx=5, pady=5)

# Second Row: Transformed Subscripts (Ensures `=` remains visible)
for i, compound in enumerate(compounds):
    transformed = transform_to_subscript(compound)  # ✅ This will now keep "=" visible
    tk.Entry(root, justify="center", width=10, state="readonly",
             readonlybackground="white", fg="black").grid(row=2, column=i, padx=5, pady=5)
    tk.Label(root, text=transformed).grid(row=2, column=i, padx=5, pady=5)

# Third Row: User Inputs & Computed Values (Now includes `=` but NOT `|`)
entries = []
for i, compound in enumerate(compounds):
    entry = tk.Entry(root, justify="center")
    entry.grid(row=3, column=i, padx=5, pady=5)
    entries.append(entry)

# Get the column index of the second reactant where users should enter their measurement
input_col_index = reactants.index(reactants[1])

# Add a label below the input field to indicate where to enter measurement
input_label = tk.Label(root, text="Input Cell", fg="gray", font=("Arial", 10, "italic"))
input_label.grid(row=4, column=input_col_index, pady=2)

# Checkbox for Moles/Grams (Only Converts, Doesn't Compute)
checkbox_var = tk.BooleanVar()
checkbox = tk.Checkbutton(root, text="Moles?", variable=checkbox_var)
checkbox.grid(row=4, column=2, padx=5, pady=5)

# Function to Compute Stoichiometry with Limiting Reagent
def compute_stoichiometry():
    try:
        # Get the user input directly from the second reactant's cell
        reference_compound = reactants[1]  # The second reactant is used as input reference
        lab_measurement = float(entries[input_col_index].get())  
        is_moles = checkbox_var.get()

        # Convert only the other compounds, not the user input
        reference_moles = lab_measurement if is_moles else lab_measurement / molar_masses[reference_compound]

        # Compute moles of all reactants based on stoichiometric ratios
        reactant_moles = {reference_compound: reference_moles}

        for reactant in reactants:
            if reactant != reference_compound:  # Other reactants should be computed
                coefficient = molesAndCompounds(reactant)[0]
                reactant_moles[reactant] = reference_moles * (coefficient / molesAndCompounds(reference_compound)[0])

        # Find the limiting reagent correctly based on **moles**
        smallest_ratio = float("inf")
        limiting_reagent = None  

        for reactant in reactant_moles:
            ratio = reactant_moles[reactant] / molesAndCompounds(reactant)[0]
            print(f"Checking Limiting Reagent: {reactant}, Ratio: {ratio:.6f}")  # Debugging Output

            if ratio < smallest_ratio:
                smallest_ratio = ratio
                limiting_reagent = reactant  # Track first smallest reagent

        print(f"Final Limiting Reagent: {limiting_reagent}")

        # Compute theoretical yield of products based on limiting reagent
        results = {}
        for compound in products:  
            coefficient = molesAndCompounds(compound)[0]
            limiting_coeff = molesAndCompounds(limiting_reagent)[0]
            theoretical_moles = (reactant_moles[limiting_reagent] / limiting_coeff) * coefficient

            # Convert to grams if checkbox is unchecked (grams mode)
            results[compound] = theoretical_moles if is_moles else theoretical_moles * molar_masses[compound]

        # Populate the outputs dynamically for all valid reactants and products (except user input)
        for i, compound in enumerate(compounds):
            if compound not in ["", "="]:  # Skip separators
                value = reactant_moles.get(compound, results.get(compound, 0))
                if compound != reference_compound:  # Do NOT change user input cell
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