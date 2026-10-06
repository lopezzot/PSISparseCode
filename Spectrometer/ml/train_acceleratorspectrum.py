import uproot
import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import os
import argparse
import copy

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


# ============================================================
# Configuration
# ============================================================

parser = argparse.ArgumentParser(
    description="Train the gamma spectrum reconstruction network."
)

parser.add_argument(
    "--input",
    required=True,
    help="Input ROOT file containing the detector dataset.",
)

args = parser.parse_args()

ROOT_FILE = args.input
TREE_NAME = "LayerSignals"

N_LAYERS = 180
N_BINS = 50

ENERGY_MIN = 0.1
ENERGY_MAX = 500.0

RANDOM_SEED = 42

EPOCHS = 1000
LEARNING_RATE = 1e-3
PATIENCE = 75 # for early stopping


# ============================================================
# Reproducibility
# ============================================================

np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)



# ============================================================
# Plot directory
# ============================================================

PLOT_DIR = "plots_accelerator"
os.makedirs(PLOT_DIR, exist_ok=True)

# ============================================================
# Load ROOT dataset
# ============================================================

with uproot.open(ROOT_FILE) as root_file:

    tree = root_file[TREE_NAME]

    data = tree.arrays(
        [
            "layer_edep_MeV",
            "gamma_spectrum",
            "generated_mean_MeV",
            "generated_sigma_MeV",
        ],
        library="np",
    )


# ============================================================
# Build input and target arrays
# ============================================================

# Detector input:
# one feature for each scintillator layer.
X = np.stack(data["layer_edep_MeV"])

# True incident gamma spectrum.
Y_counts = np.stack(data["gamma_spectrum"])

# Normalize the spectrum to obtain a probability distribution.
Y = Y_counts / Y_counts.sum(axis=1, keepdims=True)

# These quantities are kept only for diagnostics.
generated_mean = np.asarray(data["generated_mean_MeV"])
generated_sigma = np.asarray(data["generated_sigma_MeV"])


print("Dataset shape:")
print("X:", X.shape)
print("Y:", Y.shape)

print()
print("Number of events:", len(X))
print("Number of detector layers:", X.shape[1])
print("Number of energy bins:", Y.shape[1])


# ============================================================
# Train / validation / test split
# ============================================================

X_train, X_temp, Y_train, Y_temp = train_test_split(
    X,
    Y,
    test_size=0.30,
    random_state=RANDOM_SEED,
)

X_val, X_test, Y_val, Y_test = train_test_split(
    X_temp,
    Y_temp,
    test_size=0.50,
    random_state=RANDOM_SEED,
)


print()
print("Dataset split:")
print("Training:", X_train.shape[0])
print("Validation:", X_val.shape[0])
print("Test:", X_test.shape[0])


# ============================================================
# Standardize detector inputs
# ============================================================

scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)


# ============================================================
# Convert to PyTorch tensors
# ============================================================

X_train = torch.tensor(X_train, dtype=torch.float32)
X_val = torch.tensor(X_val, dtype=torch.float32)
X_test = torch.tensor(X_test, dtype=torch.float32)

Y_train = torch.tensor(Y_train, dtype=torch.float32)
Y_val = torch.tensor(Y_val, dtype=torch.float32)
Y_test = torch.tensor(Y_test, dtype=torch.float32)


# ============================================================
# Neural network
# ============================================================

class SpectrumNet(nn.Module):

    def __init__(self):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(N_LAYERS, 128),
            nn.ReLU(),

            nn.Linear(128, 256),
            nn.ReLU(),

            nn.Linear(256, 128),
            nn.ReLU(),

            nn.Linear(128, N_BINS),
        )

    def forward(self, x):
        return self.network(x)


model = SpectrumNet()

train_losses = []
val_losses = []

best_val_loss = float("inf")
best_model_state = None
best_epoch = 0
epochs_without_improvement = 0

# ============================================================
# Loss and optimizer
# ============================================================

loss_function = nn.MSELoss()

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE,
)


# ============================================================
# Training
# ============================================================

for epoch in range(EPOCHS):

    model.train()

    optimizer.zero_grad()

    logits = model(X_train)

    # Convert network output into a normalized spectrum.
    prediction = torch.softmax(logits, dim=1)

    loss = loss_function(
        prediction,
        Y_train,
    )

    loss.backward()

    optimizer.step()

    train_loss = loss.item()

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    model.eval()

    with torch.no_grad():

        val_logits = model(X_val)

        val_prediction = torch.softmax(
            val_logits,
            dim=1,
        )

        val_loss = loss_function(
            val_prediction,
            Y_val,
        )

    validation_loss = val_loss.item()

    train_losses.append(train_loss)
    val_losses.append(validation_loss)

    # --------------------------------------------------------
    # Save best model
    # --------------------------------------------------------

    if validation_loss < best_val_loss:

        best_val_loss = validation_loss
        best_epoch = epoch + 1
        best_model_state = copy.deepcopy(model.state_dict())
        epochs_without_improvement = 0

    else:

        epochs_without_improvement += 1

    if (epoch + 1) % 10 == 0:

        print(
            f"Epoch {epoch + 1:4d} | "
            f"Train loss = {loss.item():.6f} | "
            f"Val loss = {val_loss.item():.6f}"
        )

        # --------------------------------------------------------
    # Early stopping
    # --------------------------------------------------------

    if epochs_without_improvement >= PATIENCE:

        print()
        print(
            f"Early stopping at epoch {epoch + 1}. "
            f"Best validation loss at epoch {best_epoch}."
        )

        break

# ============================================================
# Restore best model
# ============================================================

model.load_state_dict(best_model_state)

print()
print("Best epoch:", best_epoch)
print("Best validation loss:", best_val_loss)

# ============================================================
# Training history plot
# ============================================================

plt.figure(figsize=(8, 5))

epochs_completed = np.arange(
    1,
    len(train_losses) + 1,
)

plt.plot(
    epochs_completed,
    train_losses,
    label="Training loss",
    linewidth=2,
)

plt.plot(
    epochs_completed,
    val_losses,
    label="Validation loss",
    linewidth=2,
)

plt.axvline(
    best_epoch,
    linestyle="--",
    linewidth=1.5,
    label=f"Best epoch = {best_epoch}",
)

plt.xlabel("Training epoch")
plt.ylabel("MSE loss")
plt.title("Training history")

plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()

loss_plot_filename = os.path.join(
    PLOT_DIR,
    "training_history.png",
)

plt.savefig(
    loss_plot_filename,
    dpi=200,
    bbox_inches="tight",
)

plt.close()

print()
print(f"Training history saved in: {loss_plot_filename}")

# ============================================================
# Test
# ============================================================

model.eval()

with torch.no_grad():

    test_logits = model(X_test) # get predicted output

    # transform predicted output in a spectrum
    test_prediction = torch.softmax(
        test_logits,
        dim=1,
    )

    # calculate test MSE
    test_loss = loss_function(
        test_prediction,
        Y_test,
    )


print()
print("Final test MSE:", test_loss.item())


# ============================================================
# Convert predictions back to NumPy
# ============================================================

Y_pred = test_prediction.numpy()
Y_true = Y_test.numpy()


# ============================================================
# Energy bin centers
# ============================================================

bin_width = (
    ENERGY_MAX - ENERGY_MIN
) / N_BINS

energy_bins = (
    ENERGY_MIN
    + (np.arange(N_BINS) + 0.5) * bin_width
)


# ============================================================
# Reconstructed spectral mean
# ============================================================

true_mean = np.sum(
    Y_true * energy_bins[None, :],
    axis=1,
)

pred_mean = np.sum(
    Y_pred * energy_bins[None, :],
    axis=1,
)


# ============================================================
# Mean  errors
# ============================================================

mean_error = pred_mean - true_mean


print()
print("Spectral mean:")
print(
    "  Mean error:",
    np.mean(mean_error),
    "MeV",
)

print(
    "  Mean absolute error:",
    np.mean(np.abs(mean_error)),
    "MeV",
)

# ============================================================
# Global spectral MAE
# ============================================================

spectral_mae = np.mean(
    np.abs(Y_pred - Y_true)
)

print()
print("Global spectral MAE:", spectral_mae)

# ============================================================
# Peak position reconstruction
# ============================================================

# Find the energy bin with the maximum probability
# for each true spectrum and each reconstructed spectrum.
#
# This represents the reconstructed peak position,
# not the mean energy of the complete spectrum.
true_peak_indices = np.argmax(
    Y_true,
    axis=1,
)

pred_peak_indices = np.argmax(
    Y_pred,
    axis=1,
)

# Convert peak-bin indices into physical energies
# using the corresponding bin centers.
true_peak_energy = energy_bins[
    true_peak_indices
]

pred_peak_energy = energy_bins[
    pred_peak_indices
]

# Calculate the peak-position error for every event.
#
# Positive value:
#   predicted peak is at higher energy than the true peak.
#
# Negative value:
#   predicted peak is at lower energy than the true peak.
peak_error = (
    pred_peak_energy
    - true_peak_energy
)


# ============================================================
# Peak position statistics
# ============================================================

peak_mean_error = np.mean(
    peak_error
)

peak_mae = np.mean(
    np.abs(peak_error)
)

peak_rmse = np.sqrt(
    np.mean(peak_error ** 2)
)


print()
print("Peak position:")
print(
    "  Mean error:",
    peak_mean_error,
    "MeV",
)

print(
    "  Mean absolute error:",
    peak_mae,
    "MeV",
)

print(
    "  RMSE:",
    peak_rmse,
    "MeV",
)


# ============================================================
# True vs predicted peak position
# ============================================================

true_peak_indices = np.argmax(Y_true, axis=1)
pred_peak_indices = np.argmax(Y_pred, axis=1)
true_peak_energy = energy_bins[true_peak_indices]
pred_peak_energy = energy_bins[pred_peak_indices]

plt.figure(figsize=(7, 7))

plt.scatter(
    true_peak_energy,
    pred_peak_energy,
    alpha=0.5,
)

# Ideal reconstruction:
# predicted peak energy = true peak energy.
min_energy = min(
    true_peak_energy.min(),
    pred_peak_energy.min(),
)

max_energy = max(
    true_peak_energy.max(),
    pred_peak_energy.max(),
)

plt.plot(
    [min_energy, max_energy],
    [min_energy, max_energy],
    linestyle="--",
    linewidth=2,
    label="Ideal reconstruction",
)

plt.xlabel("True peak position [MeV]")
plt.ylabel("Predicted peak position [MeV]")
plt.title("True vs predicted peak position")

plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()

peak_scatter_filename = os.path.join(
    PLOT_DIR,
    "peak_position_scatter.png",
)

plt.savefig(
    peak_scatter_filename,
    dpi=200,
    bbox_inches="tight",
)

plt.close()

print()
print(
    f"Peak-position scatter plot saved in: "
    f"{peak_scatter_filename}"
)

# ============================================================
# Peak position error distribution
# ============================================================

plt.figure(figsize=(8, 5))

plt.hist(
    peak_error,
    bins=30,
)

plt.axvline(
    0.0,
    linestyle="--",
    linewidth=2,
    label="Zero error",
)

plt.xlabel(
    "Peak position error [MeV]"
)

plt.ylabel("Number of test events")

plt.title(
    "Distribution of peak position errors"
)

plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()

peak_error_hist_filename = os.path.join(
    PLOT_DIR,
    "peak_position_error_histogram.png",
)

plt.savefig(
    peak_error_hist_filename,
    dpi=200,
    bbox_inches="tight",
)

plt.close()

print(
    f"Peak-error histogram saved in: "
    f"{peak_error_hist_filename}"
)

# ============================================================
# Save reconstructed spectra plots
# ============================================================

N_PLOTS = 20

# Select a few test events.
plot_indices = np.linspace(
    0,
    len(Y_test) - 1,
    N_PLOTS,
    dtype=int,
)


for plot_number, index in enumerate(plot_indices):

    plt.figure(figsize=(9, 5))

    plt.step(
        energy_bins,
        Y_true[index],
        where="mid",
        label="Truth",
        linewidth=2,
    )

    plt.step(
        energy_bins,
        Y_pred[index],
        where="mid",
        label="Prediction",
        linewidth=2,
    )

    plt.xlabel("Gamma energy [MeV]")
    plt.ylabel("Normalized counts")

    plt.title(
        f"Test event {index} | "
        f"True mean = {true_mean[index]:.2f} MeV | "
        f"Predicted mean = {pred_mean[index]:.2f} MeV"
    )

    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    filename = os.path.join(
        PLOT_DIR,
        f"spectrum_event_{plot_number + 1}.png",
    )

    plt.savefig(
        filename,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()

print()
print(f"Plots saved in: {PLOT_DIR}/")
