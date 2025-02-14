import tkinter as tk
from tkinter import messagebox
from Chemistry import molesAndCompounds, atomCount, splitOnAtomCount, symbolAndMasses, numberAsSubscript

# Read the equation from file
with open("/Users/ika/Desktop/Spring_2025/CS5630/python_comput_data_science/Homework 2/Homework 2 short sample input.txt", "r") as file:
    equation = file.readline().strip()

# Parse equation dynamically
reactants, products = equation.split("=")
reactants = [r.strip() for r in reactants.split("+")]
products = [p.strip() for p in products.split("+")]

# Include separators but replace "|" with an empty string
compounds = reactants + [""] + ["="] + products  

# Ensure UI supports at least 6 columns
while len(compounds) < 6:
    compounds.append("")

# Get atomic masses from periodic table data
periodic_data = symbolAndMasses("/Users/ika/Desktop/Spring_2025/CS5630/python_comput_data_science/Homework 2/PeriodicTableData.xls")

# Compute molar masses safely
def get_molar_mass(compound):
    atoms = atomCount(compound)
    return sum(float(periodic_data[element]) * int(count) for element, count in atoms.items())

# Store molar masses
molar_masses = {compound: get_molar_mass(compound) for compound in compounds if compound not in ["", "="]}

# Convert formulas to display subscripts properly
def transform_to_subscript(compound):
    if compound == "=":
        return "="
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
    tk.Entry(root, justify="center", width=10, state="readonly",
             readonlybackground="white", fg="black").grid(row=1, column=i, padx=5, pady=5)
    tk.Label(root, text=compound).grid(row=1, column=i, padx=5, pady=5)

# Second Row: Transformed Subscripts
for i, compound in enumerate(compounds):
    transformed = transform_to_subscript(compound)
    tk.Entry(root, justify="center", width=10, state="readonly",
             readonlybackground="white", fg="black").grid(row=2, column=i, padx=5, pady=5)
    tk.Label(root, text=transformed).grid(row=2, column=i, padx=5, pady=5)

# Third Row: User Inputs & Computed Values
entries = []
for i, compound in enumerate(compounds):
    entry = tk.Entry(root, justify="center")
    entry.grid(row=3, column=i, padx=5, pady=5)
    entries.append(entry)

# Label for user input cell
input_label = tk.Label(root, text="Input Cell", fg="gray", font=("Arial", 10, "italic"))
input_label.grid(row=4, column=1, pady=2)

# Checkbox for Moles/Grams
checkbox_var = tk.BooleanVar()
checkbox = tk.Checkbutton(root, text="Moles?", variable=checkbox_var)
checkbox.grid(row=4, column=2, padx=5, pady=5)

# **Explicitly store which reactant was entered by the user**
user_input_storage = {}
user_selected_input = None  # Track which reactant was entered

# Compute Stoichiometry while keeping the correct input cell unchanged
def compute_stoichiometry():
    try:
        global user_selected_input  
        is_moles = checkbox_var.get()

        # Identify the reactant where the user entered a value
        user_input_reactant = None
        user_input_value = None
        user_input_index = None

        for i, reactant in enumerate(reactants):
            value = entries[i].get().strip()
            if value:  # User input found
                user_input_reactant = reactant
                user_input_value = float(value)
                user_input_index = i
                break  # Stop once we find the first non-empty input

        if user_input_reactant is None:
            messagebox.showerror("Error", "Please enter a measurement for at least one reactant.")
            return

        # **Ensure the correct input reactant remains stored**
        if user_selected_input is None or user_selected_input != user_input_reactant:
            user_selected_input = user_input_reactant  
            user_input_storage[user_selected_input] = user_input_value  

        # **Prevent modifying user input**
        if user_selected_input in user_input_storage:
            user_input_value = user_input_storage[user_selected_input]

        # Convert only if needed (for computation, not storage)
        reference_moles = user_input_value if is_moles else user_input_value / molar_masses[user_selected_input]

        # Compute moles of all reactants based on ratios
        reactant_moles = {user_selected_input: reference_moles}
        for reactant in reactants:
            if reactant != user_selected_input:
                coefficient = molesAndCompounds(reactant)[0]
                user_coeff = molesAndCompounds(user_selected_input)[0]
                reactant_moles[reactant] = reference_moles * (coefficient / user_coeff)

        # Find the limiting reagent
        smallest_ratio = float("inf")
        limiting_reagent = None  

        for reactant in reactant_moles:
            ratio = reactant_moles[reactant] / molesAndCompounds(reactant)[0]
            if ratio < smallest_ratio:
                smallest_ratio = ratio
                limiting_reagent = reactant

        # Compute theoretical yield of products
        results = {}
        for compound in products:  
            coefficient = molesAndCompounds(compound)[0]
            limiting_coeff = molesAndCompounds(limiting_reagent)[0]
            theoretical_moles = (reactant_moles[limiting_reagent] / limiting_coeff) * coefficient

            # Convert to grams if unchecked
            results[compound] = theoretical_moles if is_moles else theoretical_moles * molar_masses[compound]

        # **Update outputs while keeping the user input unchanged**
        for i, compound in enumerate(compounds):
            if i == user_input_index:  
                continue  # Do not modify user input
            if compound not in ["", "="]:  
                value = reactant_moles.get(compound, results.get(compound, 0))
                entries[i].delete(0, tk.END)
                entries[i].insert(0, f"{value:.4f}")

        # **Ensure user input remains intact**
        entries[user_input_index].delete(0, tk.END)
        entries[user_input_index].insert(0, f"{user_input_storage[user_selected_input]:.4f}")

        # Show Limiting Reagent
        messagebox.showinfo("Limiting Reagent", f"The limiting reagent is {limiting_reagent}.")

    except ValueError:
        messagebox.showerror("Error", "Please enter a valid numeric input.")

# Compute Button
compute_button = tk.Button(root, text="Compute", command=compute_stoichiometry)
compute_button.grid(row=4, column=3, padx=5, pady=5)

root.mainloop()