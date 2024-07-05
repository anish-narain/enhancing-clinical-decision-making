import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from torch.utils.data import Dataset, DataLoader

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt


# DATA LOADING AND PRE-PROCESSING
# Class for pre-processing the data
# Class for pre-processing the data
class MIMICDataProcessor:
    def __init__(self, file_path, batch_size=64, test_size=0.33):
        self.file_path = file_path
        self.batch_size = batch_size
        self.test_size = test_size
        self.scaler = StandardScaler()

        # Load and preprocess the data
        self.df = pd.read_csv(file_path)
        # Replace all missing values with 0
        self.df.fillna(0, inplace=True)

        # Features
        self.X = self.df[['aniongap_max', 'albumin_max', 'albumin_min', 'rsp_pao2fio2_vent_min', 'rsp_pao2fio2_novent_min',
                          'cgn_platelet_min', 'lvr_bilirubin_max', 'cdv_mbp_min', 'cdv_rate_dopamine', 'cdv_rate_dobutamine',
                          'cdv_rate_epinephrine', 'cdv_rate_norepinephrine', 'gcs_min', 'rfl_urineoutput', 'rfl_creatinine_max']]

        # Concepts
        self.C = self.df[['rsp_fail_moderate', 'rsp_fail_severe', 'cgn_fail_moderate', 'cgn_fail_severe', 'lvr_fail_moderate',
                          'lvr_fail_severe', 'cdv_fail_moderate', 'cdv_fail_severe', 'gcs_fail_moderate', 'gcs_fail_severe',
                          'rfl_fail_moderate', 'rfl_fail_severe', 'SSH', 'ARD', 'HES', 'COD', 'MOD', 'CRF', 'LCF',
                          'flag_high_aniongap', 'flag_low_albumin', 'flag_high_albumin', 'flag_high_bilirubin']]

        # Label
        self.Y = self.df['mortality_year']

        # Convert to tensors
        self.X_tensor = torch.tensor(self.X.values, dtype=torch.float32)
        self.C_tensor = torch.tensor(self.C.values, dtype=torch.float32)
        self.Y_tensor = torch.tensor(self.Y.values, dtype=torch.float32)

        # Normalise the features
        self.X_scaled = self.scaler.fit_transform(self.X)
        self.X_tensor_scaled = torch.tensor(self.X_scaled, dtype=torch.float32)

    def get_features(self):
        return self.X.columns.tolist()  
    
    def get_concepts(self):
        return self.C.columns.tolist()
    
    def get_labels(self):
        return self.Y.columns.tolist()

    # Dataset class needed to provide the __getitem__ method for DataLoader
    class MIMICDataset(Dataset):
        def __init__(self, x, c, y):
            self.x = x
            self.c = c
            self.y = y

        def __len__(self):
            return len(self.y)

        def __getitem__(self, idx):
            return self.x[idx], self.c[idx], self.y[idx]

    def create_dataloaders(self):
        x_train, x_test, c_train, c_test, y_train, y_test = train_test_split(
            self.X_tensor_scaled, self.C_tensor, self.Y_tensor, test_size=self.test_size, random_state=42)

        train_dataset = self.MIMICDataset(x_train, c_train, y_train)
        test_dataset = self.MIMICDataset(x_test, c_test, y_test)

        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=self.batch_size, shuffle=False)

        return train_loader, test_loader
    

# MODEL
class MultiOutputNN(nn.Module):
    def __init__(self, num_features, num_outputs):
        super(MultiOutputNN, self).__init__()
        self.layer1 = nn.Linear(num_features, 64)
        self.layer2 = nn.Linear(64, 128)
        self.layer3 = nn.Linear(128, 64)
        self.output_layer = nn.Linear(64, num_outputs)

    def forward(self, x):
        x = torch.relu(self.layer1(x))
        x = torch.relu(self.layer2(x))
        x = torch.relu(self.layer3(x))
        x = self.output_layer(x)  # No activation function
        return x

# TRAINING
def train(x_size, c_size, y_size, x_to_c_learning_rate, c_to_y_learning_rate, epochs, train_loader, test_loader):
    torch.manual_seed(25)

    x_to_c = MultiOutputNN(num_features=x_size, num_outputs=c_size) # concept predictor
    c_to_y = MultiOutputNN(num_features=c_size, num_outputs=y_size) # label predictor

    criterion = nn.MSELoss() # Mean Squared Error Loss for regression
    x_to_c_optimizer = torch.optim.Adam(x_to_c.parameters(), lr=x_to_c_learning_rate)
    c_to_y_optimizer = torch.optim.Adam(c_to_y.parameters(), lr=c_to_y_learning_rate)

    # Initialising useful lists
    epochs_count = []
    x_to_c_loss_values, c_to_y_loss_values = [], []
    x_to_c_predictions, c_to_y_predictions = [], []
    x_to_c_test_loss_values, c_to_y_test_loss_values = [], []
    x_to_c_test_predictions, c_to_y_test_predictions = [], []
    ground_truth_test_c, ground_truth_test_y = [], []

    for epoch in range(epochs):
        print(f"Epoch {epoch+1}/{epochs}")  # Print current epoch
        epochs_count.append(epoch)

        # Training Loop ==========================================================
        x_to_c.train()
        c_to_y.train()

        running_x_to_c_loss, running_c_to_y_loss = 0.0, 0.0
        x_to_c_correct, c_to_y_correct, total_samples = 0, 0, 0

        for i, batch in enumerate(train_loader):
            x, c, y = batch

            # Forward pass through x_to_c
            x = x.to(x_to_c.layer1.weight.dtype)  # ensures data type of input tensor x matches data type of weights of the first linear layer
            predicted_c = x_to_c(x)
            x_to_c_predictions.append(predicted_c.detach().numpy())
            c_loss = criterion(predicted_c, c.float())

            # Forward pass through c_to_y
            predicted_y = c_to_y(predicted_c)
            c_to_y_predictions.append(predicted_y.detach().numpy())
            y_loss = criterion(predicted_y, y.unsqueeze(1).float())

            # Combined loss
            total_loss = c_loss + y_loss

            # Zero gradients for both optimizers
            x_to_c_optimizer.zero_grad()
            c_to_y_optimizer.zero_grad()

            # Backward pass and optimization for combined loss
            total_loss.backward()
            x_to_c_optimizer.step()
            c_to_y_optimizer.step()

            # Accumulate loss values
            running_x_to_c_loss += c_loss.item()
            running_c_to_y_loss += y_loss.item()

            total_samples += len(y)

        x_to_c_loss_values.append(running_x_to_c_loss / len(train_loader))
        c_to_y_loss_values.append(running_c_to_y_loss / len(train_loader))

        # Testing Loop ===========================================================
        x_to_c.eval()
        c_to_y.eval()

        running_x_to_c_test_loss, running_c_to_y_test_loss = 0.0, 0.0
        total_test_samples = 0

        with torch.no_grad():
            for x, c, y in test_loader:
                # Add ground truths from the dataset
                ground_truth_test_c.append(c)
                ground_truth_test_y.append(y)

                # Forward pass through x_to_c
                predicted_c = x_to_c(x.to(dtype=x_to_c.layer1.weight.dtype))
                x_to_c_test_predictions.append(predicted_c.detach().numpy())
                c_loss = criterion(predicted_c, c.float())

                # Accumulate x_to_c loss for testing
                running_x_to_c_test_loss += c_loss.item()

                # Forward pass through c_to_y
                predicted_y = c_to_y(predicted_c)
                c_to_y_test_predictions.append(predicted_y.detach().numpy())
                y_loss = criterion(predicted_y, y.unsqueeze(1).float())

                # Accumulate c_to_y loss for testing
                running_c_to_y_test_loss += y_loss.item()
                total_test_samples += len(y)

        x_to_c_test_loss_values.append(running_x_to_c_test_loss / len(test_loader))
        c_to_y_test_loss_values.append(running_c_to_y_test_loss / len(test_loader))

    return (x_to_c, c_to_y, epochs_count, x_to_c_loss_values, c_to_y_loss_values, x_to_c_predictions, c_to_y_predictions, x_to_c_test_loss_values, c_to_y_test_loss_values, x_to_c_test_predictions, c_to_y_test_predictions, ground_truth_test_c, ground_truth_test_y)

# MODEL Evaluation
# Concept Predictor Evaluation
def evaluate_concept_predictor(ground_truth_test_c, x_to_c_test_predictions, concept_labels):
    results = []
    for i, label in enumerate(concept_labels):
        true_values = np.concatenate([c[:, i].numpy() for c in ground_truth_test_c])
        predicted_values = np.concatenate([c[:, i] for c in x_to_c_test_predictions])
        
        mse = mean_squared_error(true_values, predicted_values)
        mae = mean_absolute_error(true_values, predicted_values)
        r2 = r2_score(true_values, predicted_values)
        
        results.append({
            "Label": label,
            "MSE": mse,
            "MAE": mae,
            "R2": r2
        })
    return pd.DataFrame(results)

# Label Predictor Evaluation
def evaluate_label_predictor(ground_truth_test_y, c_to_y_test_predictions):
    # Ensure all elements are tensors
    ground_truth_test_y = [torch.tensor(gy) if not isinstance(gy, torch.Tensor) else gy for gy in ground_truth_test_y]
    c_to_y_test_predictions = [torch.tensor(py) if not isinstance(py, torch.Tensor) else py for py in c_to_y_test_predictions]

    true_values = torch.cat(ground_truth_test_y).numpy()
    predicted_values = torch.cat(c_to_y_test_predictions).squeeze().numpy()

    mse = mean_squared_error(true_values, predicted_values)
    mae = mean_absolute_error(true_values, predicted_values)
    r2 = r2_score(true_values, predicted_values)

    results = {"MSE": mse,
        "MAE": mae,
        "R2": r2}

    index = pd.Index(["Metrics"])
    return pd.DataFrame(results, index=index)



# Specify Parameters
x_size = 15
c_size = 23
y_size = 1
x_to_c_learning_rate = 0.01
c_to_y_learning_rate = 0.01
epochs = 10

# Load Data
file_path = '/Users/anishnarain/Documents/FYP-Files/git/mimic-scripts/pre-processing/csv-files/cohorta_trial1_data.csv'
data_processor = MIMICDataProcessor(file_path, batch_size=64)
train_loader, test_loader = data_processor.create_dataloaders()

x_to_c, c_to_y, epochs_count, x_to_c_loss_values, c_to_y_loss_values, x_to_c_predictions, c_to_y_predictions, x_to_c_test_loss_values, c_to_y_test_loss_values, x_to_c_test_predictions, c_to_y_test_predictions, ground_truth_test_c, ground_truth_test_y = train(x_size, c_size, y_size, x_to_c_learning_rate, c_to_y_learning_rate, epochs, train_loader, test_loader)

# PLOTTING
# Training loss
plt.figure(figsize=(12, 6))
plt.plot(epochs_count, x_to_c_loss_values, label='Concept Model Loss')
plt.plot(epochs_count, c_to_y_loss_values, label='Label Model Loss')
plt.title('Training Loss Per Epoch')
plt.xlabel('Epoch')
plt.ylabel('Loss')
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

# Get concept labels from the data processor
concept_labels = data_processor.get_concepts()

# Evaluation
concept_predictor_results = evaluate_concept_predictor(ground_truth_test_c, x_to_c_test_predictions, concept_labels)
print("Concept Predictor Results:")
print(concept_predictor_results)

# Evaluation
label_predictor_results = evaluate_label_predictor(ground_truth_test_y, c_to_y_test_predictions)
print(label_predictor_results)