import random
import matplotlib.pyplot as plt

# Function to perform the Monte Carlo simulation for both bowls
def monte_carlo_pi_bowls(num_points):
    inside_circle = 0  # Number of points inside the circle
    inside_square = 0  # Number of points inside the square
    total_points = 0  # Total number of points generated
    
    # Lists to store points for plotting
    x_inside_circle = []
    y_inside_circle = []
    x_inside_square_only = []
    y_inside_square_only = []
    x_outside = []
    y_outside = []

    for _ in range(num_points):
        # Randomly generate points (x, y) within the square [-1, 1] x [-1, 1]
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)

        # Check if the point is inside the circle of radius 1 (i.e., inside the circular bowl)
        if x**2 + y**2 <= 1:
            inside_circle += 1
            x_inside_circle.append(x)
            y_inside_circle.append(y)

        # Check if the point is inside the square but not inside the circle (i.e., inside square bowl only)
        elif abs(x) <= 1 and abs(y) <= 1:
            inside_square += 1
            x_inside_square_only.append(x)
            y_inside_square_only.append(y)

        else:
            x_outside.append(x)
            y_outside.append(y)

        total_points += 1

    # Estimate Pi using the ratio of points in the circle to the square
    pi_estimate = 4 * inside_circle / total_points
    return pi_estimate, x_inside_circle, y_inside_circle, x_inside_square_only, y_inside_square_only, x_outside, y_outside

# Number of random points to simulate
num_points = 10000

# Run the simulation
pi_estimate, x_inside_circle, y_inside_circle, x_inside_square_only, y_inside_square_only, x_outside, y_outside = monte_carlo_pi_bowls(num_points)

# Display the result
print(f"Estimated value of Pi: {pi_estimate}")

# Plot the results
plt.figure(figsize=(6, 6))
# Plot points inside the circle bowl
plt.scatter(x_inside_circle, y_inside_circle, color='blue', s=1, label='Inside Circle Bowl')
# Plot points inside the square bowl but outside the circle
plt.scatter(x_inside_square_only, y_inside_square_only, color='green', s=1, label='Inside Square Bowl (Outside Circle)')
# Plot points outside both bowls
plt.scatter(x_outside, y_outside, color='red', s=1, label='Outside Both Bowls')
plt.gca().set_aspect('equal', adjustable='box')  # Equal aspect ratio ensures the circle looks circular
plt.title(f"Monte Carlo Simulation Estimation of Pi\nEstimated Pi: {pi_estimate}")
plt.legend()
plt.show()
