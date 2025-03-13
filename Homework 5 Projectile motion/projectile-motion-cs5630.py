import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import sympy as sp
import math

def read_input_file(file_path):
    """Read the input file and extract height, velocity, and angle."""
    with open(file_path, 'r') as file:
        data = file.readline().strip().split()
        if len(data) != 3:
            raise ValueError("Input file should contain exactly 3 values: height, velocity, angle")
        height = float(data[0])
        velocity = float(data[1])
        angle_deg = float(data[2])
        angle_rad = math.radians(angle_deg)
    
    return height, velocity, angle_deg, angle_rad

def derive_kinematics_equations():
    """Derive the four kinematics equations symbolically using SymPy."""
    # Define symbolic variables
    t, g, v0, theta, h0 = sp.symbols('t g v0 theta h0', real=True)
    
    # Define the acceleration in x and y directions (vectors)
    a_x = 0  # No acceleration in x-direction
    a_y = -g  # Acceleration due to gravity in y-direction
    
    # Derive velocity equations by integrating acceleration
    # v(t) = ∫ a dt
    v_x = sp.integrate(a_x, t) + v0 * sp.cos(theta)  # Include initial velocity in x
    v_y = sp.integrate(a_y, t) + v0 * sp.sin(theta)  # Include initial velocity in y
    
    # Derive position equations by integrating velocity
    # s(t) = ∫ v(t) dt
    x = sp.integrate(v_x, t)  # Initial x position = 0
    y = sp.integrate(v_y, t) + h0  # Initial y position = h0
    
    return v_x, v_y, x, y

def compute_trajectory_parameters(v0, angle_rad, h0, g):
    """
    Compute max height, time for max height, and range using SymPy.
    Uses symbolic calculations rather than hardcoded formulas.
    """
    # Define symbolic variables
    t, v0_sym, theta, h0_sym, g_sym = sp.symbols('t v0 theta h0 g', real=True)
    
    # Velocity in y-direction as a function of time
    v_y = v0_sym * sp.sin(theta) - g_sym * t
    
    # Time to reach max height (when v_y = 0)
    # Substitute the known values into the symbolic equation
    v_y_eq = v_y.subs([(v0_sym, v0), (theta, angle_rad), (g_sym, g)])
    time_to_max_height = sp.solve(v_y_eq, t)[0]
    
    # Position equation for y
    y = h0_sym + v0_sym * sp.sin(theta) * t - 0.5 * g_sym * t**2
    
    # Max height (substitute time_to_max_height into y equation)
    y_eq = y.subs([(h0_sym, h0), (v0_sym, v0), (theta, angle_rad), (g_sym, g)])
    max_height = y_eq.subs(t, time_to_max_height)
    
    # Time of flight (when y = 0)
    # Use the quadratic formula to find the positive root
    # We want to solve: 0 = h0 + v0*sin(θ)*t - 0.5*g*t²
    # This is a quadratic: -0.5*g*t² + v0*sin(θ)*t + h0 = 0
    
    # Define the quadratic equation coefficients
    a = -0.5 * g
    b = v0 * sp.sin(angle_rad)
    c = h0
    
    # Use the quadratic formula to find time of flight
    discriminant = b**2 - 4*a*c
    
    # Function to find the positive root (when the projectile hits the ground)
    # We use simplify to ensure the most simplified form
    time_of_flight_expr = sp.simplify((-b + sp.sqrt(discriminant)) / (2*a))
    time_of_flight = float(time_of_flight_expr)
    
    # Calculate range (x position when y = 0)
    x_expr = v0 * sp.cos(angle_rad) * t
    projectile_range = float(x_expr.subs(t, time_of_flight))
    
    # Return as Python floats for easier use in plotting
    return float(time_to_max_height), float(max_height), float(projectile_range)

def plot_trajectory(h0, v0, angle_rad, time_to_max_height, max_height, projectile_range, g, angle_deg):
    """Plot the trajectory of the projectile."""
    # Calculate time of flight using the formula derived from the quadratic equation
    # t = (v0*sin(θ) + sqrt((v0*sin(θ))² + 2*g*h0))/g
    flight_time = (v0 * np.sin(angle_rad) + np.sqrt((v0 * np.sin(angle_rad))**2 + 2 * g * h0)) / g
    
    # Create time points for plotting
    t = np.linspace(0, flight_time, 1000)
    
    # Calculate x and y coordinates at each time point
    x = v0 * np.cos(angle_rad) * t
    y = h0 + v0 * np.sin(angle_rad) * t - 0.5 * g * t**2
    
    # Create a new plot
    plt.figure(figsize=(12, 8))
    
    # Plot the trajectory
    plt.plot(x, y, 'b-', label=f'Angle: {angle_deg}°')
    
    # Mark key points
    plt.plot(0, h0, 'ro', label='Initial Position')
    plt.plot(v0 * np.cos(angle_rad) * time_to_max_height, max_height, 'go', label='Max Height')
    plt.plot(projectile_range, 0, 'mo', label='Landing Point')
    
    # Add grid, labels, and title
    plt.grid(True)
    plt.xlabel('Distance (m)')
    plt.ylabel('Height (m)')
    plt.title('Projectile Motion Trajectory')
    plt.legend()
    
    # Set axis limits
    plt.xlim(0, projectile_range * 1.1)
    plt.ylim(0, max_height * 1.1)
    
    return plt.gcf()  # Return the figure object for the multi-angle plot

def plot_multiple_trajectories(h0, v0, angle_rad, angle_deg, g):
    """
    Plot trajectories for multiple angles as required for CS 5630.
    Show angles: 15°, 30°, 45°, 75° and the original angle.
    """
    # Define the additional angles in degrees
    additional_angles_deg = [15, 30, 45, 75]
    
    # Create a new figure
    plt.figure(figsize=(12, 8))
    
    # Calculate and plot the original trajectory
    # Calculate time of flight for user input angle
    flight_time = (v0 * np.sin(angle_rad) + np.sqrt((v0 * np.sin(angle_rad))**2 + 2 * g * h0)) / g
    t = np.linspace(0, flight_time, 1000)
    x = v0 * np.cos(angle_rad) * t
    y = h0 + v0 * np.sin(angle_rad) * t - 0.5 * g * t**2
    plt.plot(x, y, 'b-', linewidth=2, label=f'Original Angle: {angle_deg}°')
    
    # Plot trajectories for additional angles with different colors
    colors = ['r-', 'g-', 'm-', 'c-']
    
    for i, angle in enumerate(additional_angles_deg):
        angle_rad_i = math.radians(angle)
        
        # Calculate time of flight
        flight_time_i = (v0 * np.sin(angle_rad_i) + np.sqrt((v0 * np.sin(angle_rad_i))**2 + 2 * g * h0)) / g
        
        # Create time points
        t_i = np.linspace(0, flight_time_i, 1000)
        
        # Calculate x and y positions
        x_i = v0 * np.cos(angle_rad_i) * t_i
        y_i = h0 + v0 * np.sin(angle_rad_i) * t_i - 0.5 * g * t_i**2
        
        # Plot the trajectory
        plt.plot(x_i, y_i, colors[i], linewidth=2, label=f'Angle: {angle}°')
    
    # Add grid, labels, and title
    plt.grid(True)
    plt.xlabel('Distance (m)')
    plt.ylabel('Height (m)')
    plt.title('Projectile Motion Trajectories for Different Angles')
    plt.legend()
    
    # Adjust axis limits to fit all trajectories
    plt.xlim(0, plt.xlim()[1])
    plt.ylim(0, plt.ylim()[1])
    
    plt.show()

def animate_trajectory(h0, v0, angle_rad, g):
    """
    Create an animation of the projectile motion (for bonus points).
    Shows the projectile position at each point in time over the full duration.
    """
    # Calculate time of flight
    flight_time = (v0 * np.sin(angle_rad) + np.sqrt((v0 * np.sin(angle_rad))**2 + 2 * g * h0)) / g
    
    # Create time points for the animation
    t = np.linspace(0, flight_time, 100)
    
    # Calculate x and y positions at each time point
    x = v0 * np.cos(angle_rad) * t
    y = h0 + v0 * np.sin(angle_rad) * t - 0.5 * g * t**2
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Set axis limits
    max_height = h0 + (v0**2 * np.sin(angle_rad)**2) / (2 * g)
    ax.set_xlim(0, v0 * np.cos(angle_rad) * flight_time * 1.1)
    ax.set_ylim(0, max_height * 1.1)
    
    # Add grid and labels
    ax.grid(True)
    ax.set_xlabel('Distance (m)')
    ax.set_ylabel('Height (m)')
    ax.set_title('Projectile Motion Animation')
    
    # Initialize the point and path
    point, = ax.plot([], [], 'ro', markersize=10)
    path, = ax.plot([], [], 'b-', linewidth=2)
    
    # Initialize the time text
    time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
    
    # Initialize empty lists for the path
    path_x, path_y = [], []
    
    def init():
        """Initialize the animation."""
        point.set_data([], [])
        path.set_data([], [])
        time_text.set_text('')
        return point, path, time_text
    
    def update(frame):
        """Update the animation at each frame."""
        # Calculate current position
        current_t = frame * flight_time / 99  # Normalize to get actual time
        current_x = v0 * np.cos(angle_rad) * current_t
        current_y = h0 + v0 * np.sin(angle_rad) * current_t - 0.5 * g * current_t**2
        
        # Update point position
        point.set_data([current_x], [current_y])
        
        # Update path
        path_x.append(current_x)
        path_y.append(current_y)
        path.set_data(path_x, path_y)
        
        # Update time text
        time_text.set_text(f'Time: {current_t:.2f} s')
        
        return point, path, time_text
    
    # Create the animation
    # Use flight_time*10 for the interval to make the animation run for approximately flight_time seconds
    ani = FuncAnimation(fig, update, frames=100, init_func=init, blit=True, interval=flight_time*10)
    
    plt.show()
    
    return ani

def pretty_print_equations(v_x, v_y, x, y):
    """
    Pretty-print the symbolic equations derived using SymPy.
    This ensures equations are displayed in a readable mathematical format.
    """
    # Print the hard-coded equations
    print("\n--- Hard-coded Projectile Equations ---")
    print("s(t) = ∫ v(t) dt     # Position is the integral of velocity")
    print("v(t) = ∫ a dt        # Velocity is the integral of acceleration")
    
    # Print the derived kinematics equations
    print("\n--- Derived Kinematics Equations ---")
    print(f"Velocity in x-direction: v_x(t) = {sp.pretty(v_x)}")
    print(f"Velocity in y-direction: v_y(t) = {sp.pretty(v_y)}")
    print(f"Position in x-direction: x(t) = {sp.pretty(x)}")
    print(f"Position in y-direction: y(t) = {sp.pretty(y)}")

def main():
    """Main function to run the projectile motion simulation."""
    # Constants
    g = 9.8  # Acceleration due to gravity (m/s^2)
    
    # Read input file
    try:
        file_path = "Homework 5 short sample input.txt"
        h0, v0, angle_deg, angle_rad = read_input_file(file_path)
        
        print("\n=== Projectile Motion Simulation ===")
        print("\nInput Values:")
        print(f"Height above ground: {h0} m")
        print(f"Initial velocity: {v0} m/s")
        print(f"Angle: {angle_deg}° ({angle_rad:.4f} rad)")
        
        # Derive kinematics equations
        print("\nDeriving kinematics equations...")
        v_x, v_y, x, y = derive_kinematics_equations()
        
        # Pretty-print the equations
        pretty_print_equations(v_x, v_y, x, y)
        
        # Compute trajectory parameters
        print("\nComputing trajectory parameters...")
        time_to_max_height, max_height, projectile_range = compute_trajectory_parameters(v0, angle_rad, h0, g)
        
        # Print computed values
        print("\nComputed Values:")
        print(f"Time to reach maximum height: {time_to_max_height:.4f} s")
        print(f"Maximum height from the ground: {max_height:.4f} m")
        print(f"Range: {projectile_range:.4f} m")
        
        # Plot trajectory for the input angle
        print("\nPlotting trajectory...")
        plot_trajectory(h0, v0, angle_rad, time_to_max_height, max_height, projectile_range, g, angle_deg)
        
        # As a CS 5630 student, plot additional trajectories
        print("\nPlotting multiple trajectories (CS 5630 requirement)...")
        plot_multiple_trajectories(h0, v0, angle_rad, angle_deg, g)
        
        # Ask if user wants to see animation (bonus)
        animate_option = input("\nDo you want to see an animation of the projectile motion? (y/n): ").lower()
        if animate_option == 'y':
            print("\nCreating animation...")
            animation = animate_trajectory(h0, v0, angle_rad, g)
        
        print("\nProgram completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
if __name__ == "__main__":
    main()