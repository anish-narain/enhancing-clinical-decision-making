import torch
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
import torch.nn as nn
import torch.nn.functional as F

import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

import torch_explain as te
from torch_explain import datasets

# Dataset loaded
x, c, y = datasets.xor(500)

# Quick visualisation (displays the first 5 values of each tensor)
print("Sample x values:", x[:5])
print("Sample c values:", c[:5])
print("Sample y values:", y[:5])

# Will use this class in order to provide batches for DataLoader
class XORdataset(Dataset):
    def __init__(self, x, c, y):
        self.x = x
        self.c = c
        self.y = y

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.x[idx], self.c[idx], self.y[idx]
    
def createDataLoader(x_dataset, c_dataset, y_dataset):
  # Using the datasets generated above, split it into training and testing data
  x_train, x_test, c_train, c_test, y_train, y_test = train_test_split(x_dataset, c_dataset, y_dataset, test_size=0.33, random_state=42)

  # Create instances of the XORdataset for training and testing
  train_dataset = XORdataset(x_train, c_train, y_train)
  test_dataset = XORdataset(x_test, c_test, y_test)

  # Define the batch size
  batch_size = 5

  # Create DataLoader instances for training and testing
  train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
  test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

  return train_loader, test_loader

# Just for my own testing and viewing
visualising_dataset = XORdataset(x, c, y)

# Access the data at index 5
sample_x, sample_c, sample_y = visualising_dataset[5]

# Print the retrieved data to see the values
print("Sample x value:", sample_x)
print("Sample c value:", sample_c)
print("Sample y value:", sample_y)

visualising_train_loader, visualising_test_loader = createDataLoader(x, c, y)

# Fetch the first batch from the training DataLoader
first_batch = next(iter(visualising_train_loader))

# Unpack the first batch
x_batch, c_batch, y_batch = first_batch

# Print the values (number of values depends on batch_size)
print("First batch x values:", x_batch)
print("First batch c values:", c_batch)
print("First batch y values:", y_batch)

# Another method for accessing one batch at a time (used later)
i = 0
for i, batch in enumerate(visualising_train_loader):
  if i == 0:
    x_batch, c_batch, y_batch = batch
    print("First batch c values:", c_batch)
  i+=1

class model(nn.Module):
    def __init__(self, input_size, hidden_dim, output_dim):
        super(model, self).__init__()
        self.linear1 = nn.Linear(input_size, hidden_dim)
        self.linear2 = nn.Linear(hidden_dim, output_dim)  

    def forward(self, x):
        x = self.linear1(x)
        x = F.relu(x)
        x = self.linear2(x)
        probability = torch.sigmoid(x)  # Sigmoid activation for binary classification
        return probability
    
def train(x_size, c_size, c_dimension, y_dimension, x_to_c_learning_rate, c_to_y_learning_rate, epochs, train_loader):
    torch.manual_seed(25)

    x_to_c = model(x_size, c_dimension, 2) # concept predictor (outputs 2 values)
    c_to_y = model(c_size, y_dimension, 1) # label predictor

    criterion = nn.BCELoss() # Binary cross-entropy loss
    x_to_c_optimiser = torch.optim.SGD(x_to_c.parameters(), lr = x_to_c_learning_rate)
    c_to_y_optimiser = torch.optim.SGD(c_to_y.parameters(), lr = c_to_y_learning_rate)


    # Initialising useful lists
    x_to_c_loss_values = []
    c_to_y_loss_values = []

    x_to_c_predictions = []
    c_to_y_predictions = []

    epochs_count = []

    ground_truth_c = []
    ground_truth_y = []


    # Training loop
    for epoch in epochs:
      epochs_count.append(epoch)

      # Training loop for concept predictor model ===============================
      running_x_to_c_loss = 0.0

      for i, batch in enumerate(train_loader):
        x, c, _ = batch
        ground_truth_c.append(c)
        x = x.to(x_to_c.linear1.weight.dtype) # ensures data type of input tensor x matches data type of weights of the first linear layer

        predicted_c = x_to_c(x)
        x_to_c_predictions.append(predicted_c.detach().numpy())
        c_loss = criterion(predicted_c, c.float())

        x_to_c_optimiser.zero_grad()
        c_loss.backward()
        x_to_c_optimiser.step()

        running_x_to_c_loss += c_loss.item()

      x_to_c_loss_values.append(running_x_to_c_loss/len(train_loader))

      # Training loop for label predictor model =================================
      running_c_to_y_loss = 0.0

      for i, batch in enumerate(train_loader):
        _, c, y = batch
        ground_truth_y.append(y)

        predicted_y = c_to_y(c)
        c_to_y_predictions.append(predicted_y.detach().numpy())
        y_loss = criterion(predicted_y, y.float())

        c_to_y_optimiser.zero_grad()
        y_loss.backward()
        c_to_y_optimiser.step()

        running_c_to_y_loss += y_loss.item()

      c_to_y_loss_values.append(running_c_to_y_loss/len(train_loader))

    return x_to_c_loss_values, c_to_y_loss_values, x_to_c_predictions, c_to_y_predictions, epochs_count, ground_truth_c, ground_truth_y

# Parameters
x_size = x.shape[1]
c_size = c.shape[1]
c_dimension = 10
y_dimension = 10
x_to_c_learning_rate = 0.01
c_to_y_learning_rate = 0.01
epochs = list(range(400))  # Training for N number of epochs

# Run the training
x_to_c_loss_values, c_to_y_loss_values, x_to_c_predictions, c_to_y_predictions, epochs_count, ground_truth_c, ground_truth_y = train(
    x_size, c_size, c_dimension, y_dimension, x_to_c_learning_rate, c_to_y_learning_rate, epochs, visualising_train_loader
)

# Visualizing the results
# Plotting the loss for both models
plt.figure(figsize=(12, 6))
plt.plot(epochs_count, x_to_c_loss_values, label='Concept Model Loss')
plt.plot(epochs_count, c_to_y_loss_values, label='Label Model Loss')
plt.title('Training Loss Per Epoch')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)
plt.show()

def evaluate_model_metrics(predictions, ground_truth, loss_values):
    """
    Evaluate metrics for the model predictions against the ground truth labels.

    Args:
    predictions (list of np.array): List of predictions from each epoch (each array corresponds to an epoch).
    ground_truth (list of torch.Tensor): List of ground truth labels.
    loss_values (list): List of loss values for each epoch.

    Returns:
    dict: A dictionary containing evaluated metrics.
    """
    # Convert predictions and ground truths to a single array for evaluation
    predictions_flat = np.concatenate(predictions, axis=0)
    ground_truth_flat = np.concatenate([gt.numpy() for gt in ground_truth], axis=0)

    # Binarize predictions for accuracy, precision, recall calculation
    predictions_binarized = (predictions_flat > 0.5).astype(int)

    # Calculate metrics
    accuracy = accuracy_score(ground_truth_flat, predictions_binarized)
    precision = precision_score(ground_truth_flat, predictions_binarized, average='macro', zero_division=1)
    recall = recall_score(ground_truth_flat, predictions_binarized, average='macro')
    f1 = f1_score(ground_truth_flat, predictions_binarized, average='macro')
    mean_loss = np.mean(loss_values)

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "mean_loss": mean_loss
    }

x_to_c_metrics = evaluate_model_metrics(x_to_c_predictions, ground_truth_c, x_to_c_loss_values)
print("x_to_c model metrics:", x_to_c_metrics)

c_to_y_metrics = evaluate_model_metrics(c_to_y_predictions, ground_truth_y, c_to_y_loss_values)
print("c_to_y model metrics:", c_to_y_metrics)