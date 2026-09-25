import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import pickle

# ==========================================
# STEP 1: Load and Clean the Dataset
# ==========================================
# Replace 'anime_dataset.csv' with your actual file path/name
file_path = 'data/anime_dataset.csv' 

print(f"Loading data from {file_path}...")
df = pd.read_csv(file_path)

# Select our target and selected features
cols = ['score', 'year', 'episodes', 'rank']
df_subset = df[cols].dropna()

# Separate features (X) and target (y)
X_raw = df_subset[['year', 'episodes', 'rank']].values
y_raw = df_subset['score'].values

print(f"Dataset loaded successfully! Total valid samples: {len(X_raw)}")

# ==========================================
# STEP 2: Normalize and Convert to Tensors
# ==========================================
# Neural networks require features to be scaled properly
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_raw)

# Convert NumPy arrays to PyTorch Tensors
X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
y_tensor = torch.tensor(y_raw, dtype=torch.float32).unsqueeze(1) # Shape: [N, 1]

# Set up DataLoader for mini-batch training
dataset = TensorDataset(X_tensor, y_tensor)
dataloader = DataLoader(dataset, batch_size=64, shuffle=True)

# ==========================================
# STEP 3: Define the PyTorch Neural Network
# ==========================================
class AnimeScorePredictor(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(3, 16),  # 3 input features -> 16 hidden nodes
            nn.ReLU(),
            nn.Linear(16, 8),   # Hidden layer 2
            nn.ReLU(),
            nn.Linear(8, 1)     # 1 continuous output (Score)
        )

    def forward(self, x):
        return self.network(x)

model = AnimeScorePredictor()
criterion = nn.MSELoss()                  # Mean Squared Error for regression
optimizer = optim.Adam(model.parameters(), lr=0.01) # Adam Optimizer

# ==========================================
# STEP 4: Training Loop
# ==========================================
epochs = 100
epoch_losses = []

print("\nStarting model training...")
model.train()
for epoch in range(epochs):
    epoch_loss = 0.0
    for batch_X, batch_y in dataloader:
        optimizer.zero_grad()               # Clear past gradients
        predictions = model(batch_X)        # Forward pass
        loss = criterion(predictions, batch_y) # Compute loss
        loss.backward()                     # Backpropagation
        optimizer.step()                    # Update weights
        
        epoch_loss += loss.item() * batch_X.size(0)
    
    avg_loss = epoch_loss / len(dataset)
    epoch_losses.append(avg_loss)
    
    if (epoch + 1) % 20 == 0:
        print(f"Epoch [{epoch+1}/{epochs}] — Loss (MSE): {avg_loss:.4f}")

print("Training complete!\n")

# ==========================================
# STEP 5: Evaluation & Graph Visualization
# ==========================================
model.eval()
with torch.no_grad():
    all_preds = model(X_tensor).numpy().flatten()

# 1. Save the PyTorch model weights (state_dict)
torch.save(model.state_dict(), 'anime_score_model.pth')
print("Model weights saved to 'anime_score_model.pth'")

# 2. Save the fitted StandardScaler so future inputs are scaled identically
with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
print("Data scaler saved to 'scaler.pkl'")