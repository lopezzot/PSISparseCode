import numpy as np
import uproot
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


# --------------------------------------------------
# Configuration
# --------------------------------------------------

ROOT_FILE = "../../build/layer_signals.root"
TREE_NAME = "LayerSignals"

N_LAYERS = 90
N_BINS = 100

RANDOM_SEED = 42
BATCH_SIZE = 64
EPOCHS = 250
LEARNING_RATE = 1e-3

# Set random seeds for reproducibility
np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)

# --------------------------------------------------
# Load ROOT dataset
# --------------------------------------------------

print("Loading dataset...")

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

# transform data to np matrix
X = np.stack(data["layer_edep_MeV"])
Y_counts = np.stack(data["gamma_spectrum"])

generated_mean = np.asarray(
    data["generated_mean_MeV"]
)

generated_sigma = np.asarray(
    data["generated_sigma_MeV"]
)

print("Input shape:", X.shape)
print("Target shape:", Y_counts.shape)


# --------------------------------------------------
# Normalize target spectrum
# --------------------------------------------------

Y = Y_counts / Y_counts.sum(axis=1, keepdims=True)


# --------------------------------------------------
# Train / validation / test split
# --------------------------------------------------

X_train, X_temp, Y_train, Y_temp, mean_train, mean_temp, sigma_train, sigma_temp = train_test_split(
    X,
    Y,
    generated_mean,
    generated_sigma,
    test_size=0.30,
    random_state=RANDOM_SEED,
)

X_val, X_test, Y_val, Y_test, mean_val, mean_test, sigma_val, sigma_test = train_test_split(
    X_temp,
    Y_temp,
    mean_temp,
    sigma_temp,
    test_size=0.50,
    random_state=RANDOM_SEED,
)
# 70% training, 15% validation (during training), 15% test (end of training)

print("Training samples:", len(X_train))
print("Validation samples:", len(X_val))
print("Test samples:", len(X_test))


# --------------------------------------------------
# Standardize input
# --------------------------------------------------

scaler = StandardScaler()
# scale X values according to mean and sigma ((x-mean)/sigma)
# Fit to extract mean and sigma is done only on training set
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)


# --------------------------------------------------
# Convert to PyTorch tensors
# --------------------------------------------------

X_train = torch.tensor(X_train, dtype=torch.float32)
Y_train = torch.tensor(Y_train, dtype=torch.float32)

X_val = torch.tensor(X_val, dtype=torch.float32)
Y_val = torch.tensor(Y_val, dtype=torch.float32)

X_test = torch.tensor(X_test, dtype=torch.float32)
Y_test = torch.tensor(Y_test, dtype=torch.float32)


# --------------------------------------------------
# Neural network
# --------------------------------------------------
# A simple sequential neural network
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

print(model)


# --------------------------------------------------
# Loss and optimizer
# --------------------------------------------------

loss_function = nn.MSELoss()

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE,
)


# --------------------------------------------------
# Training loop
# --------------------------------------------------

for epoch in range(EPOCHS):

    model.train() # inform pytorch model is in training mode

    prediction = model(X_train)

    prediction = torch.softmax(prediction, dim=1) # softmax transform predicted spectrum in positive numbers that add to 1 (probability)

    loss = loss_function(prediction, Y_train) # calculate the loss

    optimizer.zero_grad() # erase optmizer gradients from previous loss
    loss.backward() # calculate new gradients based on the loss
    optimizer.step() # change NN weights


    # Validation

    model.eval()

    with torch.no_grad():

        val_prediction = model(X_val)
        val_prediction = torch.softmax(val_prediction, dim=1)

        val_loss = loss_function(
            val_prediction,
            Y_val,
        )


    print(
        f"Epoch {epoch + 1:3d}/{EPOCHS} "
        f"Train loss: {loss.item():.6f} "
        f"Val loss: {val_loss.item():.6f}"
    )


# --------------------------------------------------
# Test
# --------------------------------------------------

model.eval()

with torch.no_grad():

    test_prediction = model(X_test)
    test_prediction = torch.softmax(test_prediction, dim=1)

    test_loss = loss_function(
        test_prediction,
        Y_test,
    )

print()
print("Final test loss:", test_loss.item())

# --------------------------------------------------
# Compare true and predicted spectra
# --------------------------------------------------

ENERGY_MIN = 0.1
ENERGY_MAX = 100.0

N_EVENTS_TO_PLOT = 10

bin_width = (ENERGY_MAX - ENERGY_MIN) / N_BINS

energy_bins = (
    ENERGY_MIN
    + (np.arange(N_BINS) + 0.5) * bin_width
)

# Convert predictions and targets to NumPy
predicted_spectra = test_prediction.numpy()
true_spectra = Y_test.numpy()

# Make sure we do not request more events than available
n_events = min(N_EVENTS_TO_PLOT, len(test_prediction))

# Loop over test events
for event_index in range(n_events):

    true_spectrum = true_spectra[event_index]
    predicted_spectrum = predicted_spectra[event_index]

    # Calculate true mean
    true_mean = np.sum(
        energy_bins * true_spectrum
    )

    # Calculate ML mean
    predicted_mean = np.sum(
        energy_bins * predicted_spectrum
    )

    # Calculate true sigma
    true_sigma = np.sqrt(
        np.sum(
            (energy_bins - true_mean) ** 2
            * true_spectrum
        )
    )

    # Calculate ML sigma
    predicted_sigma = np.sqrt(
        np.sum(
            (energy_bins - predicted_mean) ** 2
            * predicted_spectrum
        )
    )

    # Print results
    print()
    print(f"Test event {event_index}")
    print(f"True mean:       {true_mean:.2f} MeV")
    print(f"ML mean:         {predicted_mean:.2f} MeV")
    print(f"True sigma:      {true_sigma:.2f} MeV")
    print(f"ML sigma:        {predicted_sigma:.2f} MeV")

    # Plot true and predicted spectrum
    plt.figure(figsize=(10, 6))

    plt.plot(
        energy_bins,
        true_spectrum,
        label="True spectrum",
    )

    plt.plot(
        energy_bins,
        predicted_spectrum,
        label="ML reconstructed spectrum",
    )

    plt.xlabel("Gamma energy [MeV]")
    plt.ylabel("Probability")

    plt.title(f"Test event {event_index}")

    plt.legend()
    plt.grid()

    # Save plot
    plt.savefig(
        f"spectrum_comparison_event_{event_index}.png",
        dpi=150,
    )

    plt.close()

# --------------------------------------------------
# Evaluate mean and sigma on the full test set
# --------------------------------------------------

predicted_means = np.sum(
    predicted_spectra * energy_bins,
    axis=1,
)

predicted_sigmas = np.sqrt(
    np.sum(
        (energy_bins[None, :] - predicted_means[:, None]) ** 2
        * predicted_spectra,
        axis=1,
    )
)

# Errors
mean_errors = predicted_means - mean_test
sigma_errors = predicted_sigmas - sigma_test

# Absolute errors
mean_absolute_errors = np.abs(mean_errors)
sigma_absolute_errors = np.abs(sigma_errors)

# Print statistics
print()
print("========================================")
print("Mean reconstruction")
print("========================================")

print(f"Mean error:      {np.mean(mean_errors):.3f} MeV")
print(f"Mean absolute error: {np.mean(mean_absolute_errors):.3f} MeV")
print(f"Mean error RMS:   {np.sqrt(np.mean(mean_errors ** 2)):.3f} MeV")

print()
print("========================================")
print("Sigma reconstruction")
print("========================================")

print(f"Sigma error:      {np.mean(sigma_errors):.3f} MeV")
print(f"Sigma absolute error: {np.mean(sigma_absolute_errors):.3f} MeV")
print(f"Sigma error RMS:   {np.sqrt(np.mean(sigma_errors ** 2)):.3f} MeV")

# --------------------------------------------------
# Mean scatter plot
# --------------------------------------------------

plt.figure(figsize=(7, 7))

plt.scatter(
    mean_test,
    predicted_means,
    alpha=0.5,
)

plt.plot(
    [ENERGY_MIN, ENERGY_MAX],
    [ENERGY_MIN, ENERGY_MAX],
    linestyle="--",
)

plt.xlabel("True mean [MeV]")
plt.ylabel("ML mean [MeV]")
plt.title("Mean reconstruction")

plt.grid()

plt.savefig(
    "mean_true_vs_ml.png",
    dpi=150,
)

plt.close()

# --------------------------------------------------
# Sigma scatter plot
# --------------------------------------------------

max_sigma = max(
    np.max(sigma_test),
    np.max(predicted_sigmas),
)

plt.figure(figsize=(7, 7))

plt.scatter(
    sigma_test,
    predicted_sigmas,
    alpha=0.5,
)

plt.plot(
    [0, max_sigma],
    [0, max_sigma],
    linestyle="--",
)

plt.xlabel("True sigma [MeV]")
plt.ylabel("ML sigma [MeV]")
plt.title("Sigma reconstruction")

plt.grid()

plt.savefig(
    "sigma_true_vs_ml.png",
    dpi=150,
)

plt.close()
