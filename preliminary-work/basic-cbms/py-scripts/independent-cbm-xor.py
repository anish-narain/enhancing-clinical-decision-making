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
    
def createDataLoader(x_dataset, c_dataset, y_dataset, batch_size):
  # Using the datasets generated above, split it into training and testing data
  x_train, x_test, c_train, c_test, y_train, y_test = train_test_split(x_dataset, c_dataset, y_dataset, test_size=0.33, random_state=42)

  # Create instances of the XORdataset for training and testing
  train_dataset = XORdataset(x_train, c_train, y_train)
  test_dataset = XORdataset(x_test, c_test, y_test)

  # Define the batch size
  loader_batch_size = batch_size

  # Create DataLoader instances for training and testing
  train_loader = DataLoader(train_dataset, batch_size=loader_batch_size, shuffle=True)
  test_loader = DataLoader(test_dataset, batch_size=loader_batch_size, shuffle=False)

  return train_loader, test_loader

class model(nn.Module):
    def __init__(self, input_size, hidden_dim, output_size):
        super(model, self).__init__()
        self.linear1 = nn.Linear(input_size, hidden_dim)
        self.linear2 = nn.Linear(hidden_dim, output_size)  

    def forward(self, x):
        x = self.linear1(x)
        x = F.relu(x)
        x = self.linear2(x)
        probability = torch.sigmoid(x)  # Sigmoid activation for binary classification
        return probability
    
def train(x_size, c_size, c_dimension, y_dimension, x_to_c_learning_rate, c_to_y_learning_rate, epochs, train_loader, test_loader):
    torch.manual_seed(25)

    x_to_c = model(x_size, c_dimension, 2) # concept predictor (outputs 2 values)
    c_to_y = model(c_size, y_dimension, 1) # label predictor

    criterion = nn.BCELoss() # Binary cross-entropy loss
    x_to_c_optimiser = torch.optim.SGD(x_to_c.parameters(), lr = x_to_c_learning_rate)
    c_to_y_optimiser = torch.optim.SGD(c_to_y.parameters(), lr = c_to_y_learning_rate)

    # Initialising useful lists
    # For training
    x_to_c_loss_values, c_to_y_loss_values = [], []
    x_to_c_predictions, c_to_y_predictions = [], []
    epochs_count = []
    ground_truth_c, ground_truth_y = [], []
    x_to_c_accuracy_values, c_to_y_accuracy_values = [], []
    # For testing
    x_to_c_test_loss_values, c_to_y_test_loss_values = [], []
    x_to_c_test_accuracy_values, c_to_y_test_accuracy_values = [], []

    for epoch in epochs:
      epochs_count.append(epoch)
      
      # Training Loop ==========================================================
      # Instantiating values for training
      running_x_to_c_loss, running_c_to_y_loss = 0.0, 0.0
      x_to_c_correct, c_to_y_correct, total_samples = 0, 0, 0

      for i, batch in enumerate(train_loader):
        x, c, y = batch

        # Add ground truths from the dataset
        ground_truth_c.append(c)
        ground_truth_y.append(y)

        # Forward pass through x_to_c
        x = x.to(x_to_c.linear1.weight.dtype) # ensures data type of input tensor x matches data type of weights of the first linear layer
        predicted_c = x_to_c(x)
        x_to_c_predictions.append(predicted_c.detach().numpy())
        c_loss = criterion(predicted_c, c.float())

        # Backward pass and optimisation for x_to_c
        x_to_c_optimiser.zero_grad()
        c_loss.backward()
        x_to_c_optimiser.step()

        # Accumulate x_to_c loss value and correct predictions
        running_x_to_c_loss += c_loss.item()
        x_to_c_correct += ((predicted_c.round() == c).sum(dim=1) == 2).float().sum().item()

        # Forward pass through c_to_y
        predicted_y = c_to_y(c)
        c_to_y_predictions.append(predicted_y.detach().numpy())
        y_loss = criterion(predicted_y, y.float())

        # Backward pass and optimisation for x_to_c
        c_to_y_optimiser.zero_grad()
        y_loss.backward()
        c_to_y_optimiser.step()

        # Accumulate c_to_y loss value and correct predictions
        running_c_to_y_loss += y_loss.item()
        c_to_y_correct += (predicted_y.round() == y).float().sum().item()

        total_samples += len(y)

      x_to_c_loss_values.append(running_x_to_c_loss/len(train_loader))
      c_to_y_loss_values.append(running_c_to_y_loss/len(train_loader))
      x_to_c_accuracy_values.append(x_to_c_correct / total_samples)
      c_to_y_accuracy_values.append(c_to_y_correct / total_samples)

      # Testing Loop ===========================================================
      x_to_c.eval()
      c_to_y.eval()

      # Instantiating values for testing
      running_x_to_c_test_loss, running_c_to_y_test_loss = 0.0, 0.0
      x_to_c_test_correct, c_to_y_test_correct, total_test_samples = 0, 0, 0

      with torch.no_grad():
        for x, c, y in test_loader:
            # Forward pass through x_to_c
            predicted_c = x_to_c(x.to(dtype=x_to_c.linear1.weight.dtype))
            c_loss = criterion(predicted_c, c.float())

            # Accumulate x_to_c loss and correct predictions for testing
            running_x_to_c_test_loss += c_loss.item()
            x_to_c_test_correct += ((predicted_c.round() == c).sum(dim=1) == 2).float().sum().item()

            # Forward pass through c_to_y
            predicted_y = c_to_y(predicted_c)
            y_loss = criterion(predicted_y, y.float())

            # Accumulate c_to_y loss and correct predictions for testing
            running_c_to_y_test_loss += y_loss.item()
            c_to_y_test_correct += (predicted_y.round() == y).float().sum().item()
            total_test_samples += len(y)

      x_to_c_test_loss_values.append(running_x_to_c_test_loss / len(test_loader))
      c_to_y_test_loss_values.append(running_c_to_y_test_loss / len(test_loader))
      x_to_c_test_accuracy_values.append(x_to_c_test_correct / total_test_samples)
      c_to_y_test_accuracy_values.append(c_to_y_test_correct / total_test_samples)

    return x_to_c, c_to_y, x_to_c_loss_values, c_to_y_loss_values, x_to_c_predictions, c_to_y_predictions, epochs_count, ground_truth_c, ground_truth_y, x_to_c_accuracy_values, c_to_y_accuracy_values, x_to_c_test_loss_values, c_to_y_test_loss_values, x_to_c_test_accuracy_values, c_to_y_test_accuracy_values

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

def test_models(x_to_c, c_to_y, test_loader):
    criterion = nn.BCELoss()
    
    x_to_c.eval()
    c_to_y.eval()

    x_to_c_test_losses = []
    c_to_y_test_losses = []
    c_to_y_all_predictions = []
    c_to_y_all_ground_truths = []

    with torch.no_grad():
        for x, c, y in test_loader:
            # Testing x_to_c model
            x = x.to(dtype=x_to_c.linear1.weight.dtype)
            predicted_c = x_to_c(x)
            c_loss = criterion(predicted_c, c.float())
            x_to_c_test_losses.append(c_loss.item())

            # Testing c_to_y model
            predicted_y = c_to_y(predicted_c)  # Using the predicted concepts as input
            y_loss = criterion(predicted_y, y.float())
            c_to_y_test_losses.append(y_loss.item())

            # Store predictions and actual values for metrics calculations
            c_to_y_all_predictions.extend(predicted_y.numpy())
            c_to_y_all_ground_truths.extend(y.numpy())

    # Evaluate metrics for c_to_y model
    predictions_binarized = (np.array(c_to_y_all_predictions) > 0.5).astype(int)
    ground_truth_flat = np.array(c_to_y_all_ground_truths)

    accuracy = accuracy_score(ground_truth_flat, predictions_binarized)
    precision = precision_score(ground_truth_flat, predictions_binarized, average='macro', zero_division=1)
    recall = recall_score(ground_truth_flat, predictions_binarized, average='macro')
    f1 = f1_score(ground_truth_flat, predictions_binarized, average='macro')
    mean_loss_x_to_c = np.mean(x_to_c_test_losses)
    mean_loss_c_to_y = np.mean(c_to_y_test_losses)

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "mean_loss_x_to_c": mean_loss_x_to_c,
        "mean_loss_c_to_y": mean_loss_c_to_y
    }

def main():
    # Get data
    x, c, y = datasets.xor(500)

    # Parameters
    x_size = x.shape[1]
    c_size = c.shape[1]
    c_dimension = 10
    y_dimension = 10
    x_to_c_learning_rate = 0.01
    c_to_y_learning_rate = 0.01
    batch_size = 5
    epochs = list(range(400))  # Training for N number of epochs

    # Get data in required format
    train_loader, test_loader = createDataLoader(x, c, y, batch_size)

    # Run the training
    x_to_c, c_to_y, x_to_c_loss_values, c_to_y_loss_values, x_to_c_predictions, c_to_y_predictions, epochs_count, ground_truth_c, ground_truth_y, x_to_c_accuracy_values, c_to_y_accuracy_values, x_to_c_test_loss_values, c_to_y_test_loss_values, x_to_c_test_accuracy_values, c_to_y_test_accuracy_values = train(
    x_size, c_size, c_dimension, y_dimension, x_to_c_learning_rate, c_to_y_learning_rate, epochs, train_loader, test_loader)

    # Visualizing the results
    # Training loss
    plt.figure(figsize=(12, 6))
    plt.plot(epochs_count, x_to_c_loss_values, label='Concept Predictor Loss')
    plt.plot(epochs_count, c_to_y_loss_values, label='Label Predictor Loss')
    plt.title('Training Loss Per Epoch')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Training accuracy 
    plt.figure(figsize=(12, 6))
    plt.plot(epochs_count, x_to_c_accuracy_values, label='Concept Predictor Accuracy')
    plt.plot(epochs_count, c_to_y_accuracy_values, label='Label Predictor Accuracy')
    plt.title('Training Accuracy over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Testing loss
    plt.figure(figsize=(12, 6))
    plt.plot(epochs_count, x_to_c_test_loss_values, label='Concept Predictor Loss')
    plt.plot(epochs_count, c_to_y_test_loss_values, label='Label Predictor Loss')
    plt.title('Testing Loss Per Epoch')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Testing accuracy
    plt.figure(figsize=(12, 6))
    plt.plot(epochs_count, x_to_c_test_accuracy_values, label='Concept Predictor Accuracy')
    plt.plot(epochs_count,c_to_y_test_accuracy_values, label='Label Predictor Accuracy')
    plt.title('Testing Accuracy over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Printing the metrics for training and testing
    training_x_to_c_metrics = evaluate_model_metrics(x_to_c_predictions, ground_truth_c, x_to_c_loss_values)
    print("x_to_c model metrics:", training_x_to_c_metrics)

    training_c_to_y_metrics = evaluate_model_metrics(c_to_y_predictions, ground_truth_y, c_to_y_loss_values)
    print("c_to_y model metrics:", training_c_to_y_metrics)

    test_metrics = test_models(x_to_c, c_to_y, test_loader)
    print("test_metrics:", test_metrics)

if __name__ == "__main__":
    main()

