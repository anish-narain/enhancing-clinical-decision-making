import torch
import torch_explain as te
from torch_explain import datasets
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# Load xor datasets
x, c, y = datasets.xor(500)

# Just for viewing the dataset
print("Sample x values:", x[:5])
print("Sample c values:", c[:5])
print("Sample y values:", y[:5])

# Train and test split
x_train, x_test, c_train, c_test, y_train, y_test = train_test_split(x, c, y, test_size=0.33, random_state=42)

# Initialise concept encoder
embedding_size = 8
concept_encoder = torch.nn.Sequential(
    torch.nn.Linear(x.shape[1], 10),
    torch.nn.LeakyReLU(),
    te.nn.ConceptEmbedding(10, c.shape[1], embedding_size),
)

# Initialise task predictor
task_predictor = torch.nn.Sequential(
    torch.nn.Linear(c.shape[1]*embedding_size, 1),
)
model = torch.nn.Sequential(concept_encoder, task_predictor)

# Optimiser updates model parameters during backpropagation
optimizer = torch.optim.AdamW(model.parameters(), lr=0.01)
# Loss function measures how weel the model is performing during training
loss_form_c = torch.nn.BCELoss()
loss_form_y = torch.nn.BCEWithLogitsLoss()
model.train()

# Training
for epoch in range(501):
    optimizer.zero_grad()

    # generate concept and task predictions
    c_emb, c_pred = concept_encoder(x_train)
    y_pred = task_predictor(c_emb.reshape(len(c_emb), -1))

    # compute loss
    concept_loss = loss_form_c(c_pred, c_train)
    task_loss = loss_form_y(y_pred, y_train)
    loss = concept_loss + 0.5*task_loss

    loss.backward()
    optimizer.step()

c_emb, c_pred = concept_encoder.forward(x_test)
y_pred = task_predictor(c_emb.reshape(len(c_emb), -1))

task_accuracy = accuracy_score(y_test, y_pred > 0)
concept_accuracy = accuracy_score(c_test, c_pred > 0.5)

print(task_accuracy)
print(concept_accuracy)