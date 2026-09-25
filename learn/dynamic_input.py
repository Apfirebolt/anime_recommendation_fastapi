import torch
import torch.nn as nn
import torch.optim as optim
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# 1. Define your model (same structure)
class DynamicScorePredictor(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(3, 16),
            nn.ReLU(),
            nn.Linear(16, 1)
        )
    def forward(self, x):
        return self.network(x)

model = DynamicScorePredictor()
criterion = nn.MSELoss()
# Use a lower learning rate for live updates so a single rogue user input doesn't ruin the model
optimizer = optim.Adam(model.parameters(), lr=0.001)

class LiveFeedback(BaseModel):
    year: float
    episodes: float
    rank: float
    actual_score: str  # What the user says the score actually should be

@app.post("/live-learn")
def update_model_live(feedback: LiveFeedback):
    model.train() # Keep model in training mode
    
    # Format incoming dynamic data into tensors
    x_new = torch.tensor([[feedback.year, feedback.episodes, feedback.rank]], dtype=torch.float32)
    y_true = torch.tensor([[float(feedback.actual_score)]], dtype=torch.float32)

    # --- THE ONLINE LEARNING STEP ---
    optimizer.zero_grad()               # Clear past gradients
    prediction = model(x_new)           # Forward pass with new data
    loss = criterion(prediction, y_true)# Calculate error against user reality
    loss.backward()                     # Backpropagate error
    optimizer.step()                    # Mutate weights dynamically!
    # ---------------------------------

    return {
        "status": "Success! Model weights updated with live input.",
        "calculated_loss": loss.item()
    }