import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colorbar as colorbar
import matplotlib.colors as colors

# Data
path_cumulative_vals = [1307.36, 620.00, 947.93, 699.62, 719.70, 567.23]
drift_vals = [5.94, 3.23, 5.18, 3.72, 3.79, 4.24]
diffusion_vals = [14.82, 3.40, 8.94, 5.08, 5.94, 6.19]

# Function to plot a vertical colorbar
def plot_colorbar(values, title, cmap='turbo'):
    norm = colors.Normalize(vmin=min(values), vmax=max(values))
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    fig, ax = plt.subplots(figsize=(1.2, 4))
    fig.subplots_adjust(right=0.3)
    cbar = fig.colorbar(sm, cax=ax, orientation='vertical')
    cbar.set_label(title)
    plt.show()

# Plot vertical colorbars
plot_colorbar(path_cumulative_vals, 'Path Cumulative')
plot_colorbar(drift_vals, 'Drift')
plot_colorbar(diffusion_vals, 'Diffusion')

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors

# Define the data ranges and labels
colorbar_specs = [
    (0.0, 1307.36, 'cumulative path'),
    (0.0, 5.94, 'drift'),
    (0.0, 14.82, 'diffusion')
]

# Loop to create and save each colorbar
for vmin, vmax, label in colorbar_specs:
    fig, ax = plt.subplots(figsize=(0.5, 2.5))  # 0.5in wide, 2.5in tall
    norm = colors.Normalize(vmin=vmin, vmax=vmax)
    sm = cm.ScalarMappable(cmap='turbo', norm=norm)
    sm.set_array([])

    cbar = fig.colorbar(sm, cax=ax, orientation='vertical')
    cbar.set_label(label)

    filename = f"/home/pablo/Desktop/PhD/projects/GastruloidRegistrationSizeProject/figures/sample_1_colorbar_{label}.svg"
    fig.savefig(filename, format='svg', bbox_inches='tight')
    plt.close(fig)

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors

# Define range and label
vmin, vmax = 0.0, 14.82
label = 'diffusion'

# Create horizontal colorbar
fig, ax = plt.subplots(figsize=(5, 1.0))  # 325px wide
norm = colors.Normalize(vmin=vmin, vmax=vmax)
sm = cm.ScalarMappable(cmap='turbo', norm=norm)
sm.set_array([])

cbar = fig.colorbar(sm, cax=ax, orientation='horizontal')

# Set ticks at min and max and label them
cbar.set_ticks([vmin, vmax])
cbar.set_ticklabels(['min', 'max'])
fig.subplots_adjust(bottom=0.3)

# Save or display
filename = f"/home/pablo/Desktop/PhD/projects/GastruloidRegistrationSizeProject/figures/general_colorbar.svg"
fig.savefig(filename, format='svg', bbox_inches='tight')
plt.show()


import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd

filename = f"/home/pablo/Desktop/PhD/projects/GastruloidRegistrationSizeProject/figures/sample_table_transposed_portrait.pdf"

# Define the data
data = {
    "Sample 1": [1307.36, 5.94, 14.82],
    "Sample 2": [620.00, 3.23, 3.40],
    "Sample 3": [947.93, 5.18, 8.94],
    "Sample 4": [699.62, 3.72, 5.08],
    "Sample 5": [719.70, 3.79, 5.94]
}
index = ["Cumulative path", "Drift", "Diffusion"]

# Create DataFrame and transpose it
df = pd.DataFrame(data, index=index).transpose()

# Plot the table in portrait layout
fig, ax = plt.subplots(figsize=(2, 5))  # Taller and narrower
ax.axis('tight')
ax.axis('off')

# Create table
table = ax.table(cellText=df.values,
                 rowLabels=df.index,
                 colLabels=df.columns,
                 loc='center',
                 cellLoc='center',
                 rowLoc='center')

# Save to PDF
with PdfPages(filename) as pdf:
    pdf.savefig(fig, bbox_inches='tight')

plt.close(fig)