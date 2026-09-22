import uproot
import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


# ============================================================
# Configuration
# ============================================================

ROOT_FILE = "../../build/accelerator_dataset.root"
TREE_NAME = "LayerSignals"

N_LAYERS = 90
N_BINS = 100

ENERGY_MIN = 0.1
ENERGY_MAX = 100.0

RANDOM_SEED = 42

EPOCHS = 250
LEARNING_RATE = 1e-3


# ============================================================
# Reproducibility
# ============================================================

np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)


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


    if (epoch + 1) % 10 == 0:

        print(
            f"Epoch {epoch + 1:4d} | "
            f"Train loss = {loss.item():.6f} | "
            f"Val loss = {val_loss.item():.6f}"
        )


# ============================================================
# Test
# ============================================================

model.eval()

with torch.no_grad():

    test_logits = model(X_test)

    test_prediction = torch.softmax(
        test_logits,
        dim=1,
    )

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
# Reconstructed spectral sigma
# ============================================================

true_sigma = np.sqrt(
    np.sum(
        Y_true
        * (energy_bins[None, :] - true_mean[:, None]) ** 2,
        axis=1,
    )
)

pred_sigma = np.sqrt(
    np.sum(
        Y_pred
        * (energy_bins[None, :] - pred_mean[:, None]) ** 2,
        axis=1,
    )
)


# ============================================================
# Mean and sigma errors
# ============================================================

mean_error = pred_mean - true_mean
sigma_error = pred_sigma - true_sigma


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

print()
print("Spectral sigma:")
print(
    "  Mean error:",
    np.mean(sigma_error),
    "MeV",
)

print(
    "  Mean absolute error:",
    np.mean(np.abs(sigma_error)),
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
# Save reconstructed spectra plots
# ============================================================

PLOT_DIR = "plots_accelerator"

os.makedirs(PLOT_DIR, exist_ok=True)

N_PLOTS = 10

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
