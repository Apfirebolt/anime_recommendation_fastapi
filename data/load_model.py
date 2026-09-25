import torch
import torch.nn as nn
import pickle

# 1. Re-declare the exact same model architecture structure
class AnimeScorePredictor(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(3, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1)
        )

    def forward(self, x):
        return self.network(x)

# 2. Initialize the model and load the saved state weights
loaded_model = AnimeScorePredictor()
loaded_model.load_state_dict(torch.load('anime_score_model.pth', weights_only=True))
loaded_model.eval() # Set to evaluation mode (crucial for inference)

# 3. Load the saved feature scaler
with open('scaler.pkl', 'rb') as f:
    loaded_scaler = pickle.load(f)

print("Model and scaler successfully loaded for inference!")

# ==========================================
# 4. Predict Score for Custom Anime Inputs
# ==========================================
# Define custom raw values: [year, episodes, rank]
# Example: An anime released in 2024, with 12 episodes, and a rank of 150
custom_anime_raw = [[2024.0, 12.0, 150.0],
                    [2010.0, 50.0, 2500.0]] # You can pass a batch of multiple shows too!

# Scale the custom inputs using the exact same training statistics
custom_anime_scaled = loaded_scaler.transform(custom_anime_raw)

# Convert to a PyTorch tensor
custom_tensor = torch.tensor(custom_anime_scaled, dtype=torch.float32)

# Run inference without tracking gradients
with torch.no_grad():
    predicted_scores = loaded_model(custom_tensor)

# Print out predictions
for i, raw_vals in enumerate(custom_anime_raw):
    print(f"\nAnime Input -> Year: {raw_vals[0]}, Episodes: {raw_vals[1]}, Rank: {raw_vals[2]}")
    print(f"AI Predicted MAL Score: {predicted_scores[i].item():.2f}")