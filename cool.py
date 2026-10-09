import torch
import torch.nn as nn
import torch.optim as optim

class MonteCarloLayer(nn.Module):
    """
    A neural network layer that runs a mini Monte Carlo simulation 
    on input features during the forward pass.
    """
    def __init__(self, in_features, out_features, n_simulations=100):
        super().__init__()
        self.n_simulations = n_simulations
        self.fc_mean = nn.Linear(in_features, out_features)
        self.fc_std = nn.Linear(in_features, out_features)

    def forward(self, x):
        # 1. Predict a base mean and log-std from input
        mean = self.fc_mean(x)
        # Ensure standard deviation is positive
        std = torch.softplus(self.fc_std(x))

        # 2. Monte Carlo Simulation: Draw N random samples per batch item
        # Shape of noise: [batch_size, n_simulations, out_features]
        epsilon = torch.randn(x.size(0), self.n_simulations, mean.size(-1), device=x.device)
        
        # Expand mean and std to match simulation samples
        mean_exp = mean.unsqueeze(1).expand(-1, self.n_simulations, -1)
        std_exp = std.unsqueeze(1).expand(-1, self.n_simulations, -1)

        # Simulated outcomes
        simulated_samples = mean_exp + std_exp * epsilon  # Reparameterization trick

        # 3. Aggregate results (e.g., mean and standard deviation across simulations)
        mc_output_mean = simulated_samples.mean(dim=1)
        mc_output_std = simulated_samples.std(dim=1)

        # Return concatenated stats or just the mean/expected value
        return torch.cat([mc_output_mean, mc_output_std], dim=-1)


# Quick test of the network
class NetWithMC(nn.Module):
    def __init__(self):
        super().__init__()
        # Input dim 10 -> Monte Carlo Layer (simulates 50 paths) -> Output
        self.mc_layer = MonteCarloLayer(in_features=10, out_features=5, n_simulations=50)
        self.final_fc = nn.Linear(5 * 2, 1) # 5 mean + 5 std = 10 features

    def forward(self, x):
        x = self.mc_layer(x)
        return self.final_fc(x)

# Run a dummy forward and backward pass
model = NetWithMC()
dummy_input = torch.randn(32, 10) # Batch of 32, 10 features
output = model(dummy_input)
loss = output.sum()
loss.backward() # Gradients flow right through the Monte Carlo sampling step
print("Forward output shape:", output.shape)
