import random
import math
import matplotlib.pyplot as plt

# Fungsi untuk menjalankan simulasi Monte Carlo untuk menghitung π
def monte_carlo_pi(num_samples):
    inside_circle = 0
    x_inside = []
    y_inside = []
    x_outside = []
    y_outside = []
    
    for _ in range(num_samples):
        # Pilih titik acak (x, y) dalam kotak persegi
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        
        # Cek apakah titik berada di dalam lingkaran
        if x**2 + y**2 <= 1:
            inside_circle += 1
            x_inside.append(x)
            y_inside.append(y)
        else:
            x_outside.append(x)
            y_outside.append(y)
    
    # Estimasi nilai π
    pi_estimate = (inside_circle / num_samples) * 4
    return pi_estimate, x_inside, y_inside, x_outside, y_outside

# Jumlah sampel yang akan digunakan dalam simulasi
num_samples = 10000

# Jalankan simulasi
pi_estimate, x_inside, y_inside, x_outside, y_outside = monte_carlo_pi(num_samples)

# Tampilkan hasil estimasi nilai π
print(f"Estimasi nilai π: {pi_estimate}")

# Visualisasi hasil simulasi
plt.figure(figsize=(6, 6))
plt.scatter(x_inside, y_inside, color='green', s=1, label="Titik dalam lingkaran")
plt.scatter(x_outside, y_outside, color='red', s=1, label="Titik di luar lingkaran")
plt.legend()
plt.title(f"Monte Carlo Simulasi untuk Estimasi π (Dengan {num_samples} Sampel)")
plt.xlabel("X")
plt.ylabel("Y")
plt.gca().set_aspect('equal', adjustable='box')
plt.show()
