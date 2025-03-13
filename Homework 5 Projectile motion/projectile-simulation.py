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
    """Derive the four kinematics equations symbolically."""
    # Define symbolic variables
    t, g, v0, theta, h0 = sp.symbols('t g v0 theta h0')
    
    # Define the acceleration in x and y directions
    a_x = 0  # No acceleration in x-direction
    a_y = -g  # Acceleration due to gravity in y-direction
    
    # Derive velocity equations by integrating acceleration
    v_x = sp.integrate(a_x, t) + v0 * sp.cos(theta)  # Initial velocity in x direction
    v_y = sp.integrate(a_y, t) + v0 * sp.sin(theta)  # Initial velocity in y direction
    
    # Derive position equations by integrating velocity
    x = sp.integrate(v_x, t)  # Initial x position = 0
    y = sp.integrate(v_y, t) + h0  # Initial y position = h0
    
    return v_x, v_y, x, y

def compute_trajectory_parameters(v0, angle_rad, h0, g):
    """Compute max height, time for max height, and range."""
    # Define symbolic variables for calculations
    t, theta = sp.symbols('t theta')
    
    # Derive the y-velocity equation
    v_y = v0 * sp.sin(theta) - g * t
    
    # Time to reach max height (when v_y = 0)
    time_to_max_height = sp.solve(v_y.subs(theta, angle_rad), t)[0]
    
    # Position equation for y
    y = h0 + v0 * sp.sin(angle_rad) * t - 0.5 * g * t**2
    
    # Max height (substitute time_to_max_height into y equation)
    max_height = y.subs(t, time_to_max_height)
    
    # Time of flight (when y = 0)
    # We need to solve: h0 + v0*sin(angle_rad)*t - 0.5*g*t^2 = 0
    # This is a quadratic equation: -0.5*g*t^2 + v0*sin(angle_rad)*t + h0 = 0
    # Using the quadratic formula to find the positive root
    a = -0.5 * g
    b = v0 * sp.sin(angle_rad)
    c = h0
    
    # Calculate discriminant
    discriminant = b**2 - 4*a*c
    
    # We need the positive root (time when projectile hits ground)
    time_of_flight = (-b + sp.sqrt(discriminant)) / (2*a)
    
    # Calculate range (x position when y = 0)
    x = v0 * sp.cos(angle_rad) * t
    
    # Substitute time_of_flight into x to get range
    projectile_range = x.subs(t, time_of_flight)
    
    return float(time_to_max_height), float(max_height), float(projectile_range)

def plot_trajectory(h0, v0, angle_rad, time_to_max_height, max_height, projectile_range, g):
    """Plot the trajectory of the projectile."""
    # Calculate time of flight
    # Using the formula: t = (v0*sin(θ) + sqrt((v0*sin(θ))^2 + 2*g*h0))/g
    flight_time = (v0 * np.sin(angle_rad) + np.sqrt((v0 * np.sin(angle_rad))**2 + 2 * g * h0)) / g
    
    # Create time points
    t = np.linspace(0, flight_time, 1000)
    
    # Calculate x and y positions
    x = v0 * np.cos(angle_rad) * t
    y = h0 + v0 * np.sin(angle_rad) * t - 0.5 * g * t**2
    
    # Plot the trajectory
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, 'b-', label=f'Angle: {math.degrees(angle_rad):.1f}°')
    
    # Mark initial position, max height, and landing point
    plt.plot(0, h0, 'ro', label='Initial Position')
    plt.plot(v0 * np.cos(angle_rad) * time_to_max_height, max_height, 'go', label='Max Height')
    plt.plot(projectile_range, 0, 'mo', label='Landing Point')
    
    # Add grid and labels
    plt.grid(True)
    plt.xlabel('Distance (m)')
    plt.ylabel('Height (m)')
    plt.title('Projectile Motion Trajectory')
    plt.legend()
    
    # Set axis limits
    plt.xlim(0, projectile_range * 1.1)
    plt.ylim(0, max_height * 1.1)
    
    plt.show()

def animate_trajectory(h0, v0, angle_rad, g):
    """Create an animation of the projectile motion."""
    # Calculate time of flight
    flight_time = (v0 * np.sin(angle_rad) + np.sqrt((v0 * np.sin(angle_rad))**2 + 2 * g * h0)) / g
    
    # Create time points
    t = np.linspace(0, flight_time, 100)
    
    # Calculate x and y positions
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
    ani = FuncAnimation(fig, update, frames=100, init_func=init, blit=True, interval=flight_time*10)
    
    plt.show()
    
    return ani

def plot_multiple_trajectories(h0, v0, g):
    """Plot trajectories for different angles (for CS 5630 requirement)."""
    angles_deg = [15, 30, 45, 75]
    
    plt.figure(figsize=(12, 8))
    
    # First plot the user-specified trajectory
    # Calculate time of flight for the original angle
    flight_time = (v0 * np.sin(angle_rad) + np.sqrt((v0 * np.sin(angle_rad))**2 + 2 * g * h0)) / g
    
    # Create time points
    t = np.linspace(0, flight_time, 1000)
    
    # Calculate x and y positions
    x = v0 * np.cos(angle_rad) * t
    y = h0 + v0 * np.sin(angle_rad) * t - 0.5 * g * t**2
    
    # Plot the original trajectory
    plt.plot(x, y, 'b-', linewidth=2, label=f'Angle: {math.degrees(angle_rad):.1f}°')
    
    # Plot trajectories for additional angles
    colors = ['r-', 'g-', 'm-', 'c-']
    
    for i, angle in enumerate(angles_deg):
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
    
    # Add grid and labels
    plt.grid(True)
    plt.xlabel('Distance (m)')
    plt.ylabel('Height (m)')
    plt.title('Projectile Motion Trajectories for Different Angles')
    plt.legend()
    
    # Set axis limits to fit all trajectories
    plt.xlim(0, plt.xlim()[1])
    plt.ylim(0, plt.ylim()[1])
    
    plt.show()

if __name__ == "__main__":
    # Constants
    g = 9.8  # Acceleration due to gravity (m/s^2)
    
    # Get input file path from user
    # file_path = input("Enter the path to the input file: ")
    
    # Read input filen
    h0, v0, angle_deg, angle_rad = read_input_file('Homework 5 short sample input.txt')
    
    # Print input values
    print("\nInput Values:")
    print(f"Height above ground: {h0} m")
    print(f"Initial velocity: {v0} m/s")
    print(f"Angle: {angle_deg}° ({angle_rad:.4f} rad)")
    
    # Derive kinematics equations
    print("\nDeriving kinematics equations...")
    v_x, v_y, x, y = derive_kinematics_equations()
    
    # Print the hard-coded equations and derived equations
    print("\nHard-coded Projectile Equations:")
    print("s(t) = ∫ v(t) dt")
    print("v(t) = ∫ a dt")
    
    print("\nDerived Kinematics Equations:")
    print(f"Velocity in x-direction: v_x(t) = {v_x}")
    print(f"Velocity in y-direction: v_y(t) = {v_y}")
    print(f"Position in x-direction: x(t) = {x}")
    print(f"Position in y-direction: y(t) = {y}")
    
    # Compute max height, time for max height, and range
    print("\nComputing trajectory parameters...")
    time_to_max_height, max_height, projectile_range = compute_trajectory_parameters(v0, angle_rad, h0, g)
    
    # Print computed values
    print("\nComputed Values:")
    print(f"Time to reach maximum height: {time_to_max_height:.4f} s")
    print(f"Maximum height from the ground: {max_height:.4f} m")
    print(f"Range: {projectile_range:.4f} m")
    
    # Plot trajectory
    print("\nPlotting trajectory...")
    plot_trajectory(h0, v0, angle_rad, time_to_max_height, max_height, projectile_range, g)
    
    # Ask if user wants to see multiple trajectories (for CS 5630)
    cs_5630 = input("\nAre you a CS 5630 student? (y/n): ").lower() == 'y'
    if cs_5630:
        print("\nPlotting multiple trajectories...")
        plot_multiple_trajectories(h0, v0, g)
    
    # Ask if user wants to see animation (bonus)
    animate = input("\nDo you want to see an animation of the projectile motion? (y/n): ").lower() == 'y'
    if animate:
        print("\nCreating animation...")
        animation = animate_trajectory(h0, v0, angle_rad, g)
    
    print("\nProgram completed successfully!")
