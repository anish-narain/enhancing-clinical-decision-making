# Notes on CBM for PyTorch Explain Tutorial 
(For `train.py`)

https://github.com/pietrobarbiero/pytorch_explain?tab=readme-ov-file
https://pypi.org/project/torch-explain/

Steps:
1. **Import**. Using torch_explain which really simplifies some of the parts of the CBM
2. **Load dataset** (didn't need preprocessing in this case)
3. **Split the data**
4. **Define concept encoder**. A concept encoder learns to map the input features x to an intermediate concept representation c. It takes in the training x values and produces two types of concepts `c_emb` and `c_pred`. `c_emb` (embeddings of concepts) is fed into the task predictor to product `y_pred`. `c_pred` (predicted concept labels) is compared against `c_train` to optimise for the concept prediction part of the model.
5. **Define task predictor**. Takes in `c_emb` to make the final prediction for output `y_pred`.
6. **Train both concept prediction and task prediction simultaneously**. Both concept predictor and task predictor is are optimised together. The loss function tries to minimise `c_pred` against `c_train` and `y_pred` against `y_train`.


## Concept Encoder
Has three main components:
* Linear layer = takes the input vector from the dataset (x_train) and linearly transforms it to a higher or different dimension. In this model, it transforms the input to a 10-dimensional space.
* LeakyReLU activation = It introduces non-linearity to the encoding process, which is essential because it allows the model to learn more complex patterns in the data.
* Concept Embedding layer = The concept embedding layer is where the actual 'conceptualization' of the data occurs. Each dimension of the output from this layer represents a concept in an embedded form. 

## Task Predictor

## Training

`model = torch.nn.Sequential(concept_encoder, task_predictor)`
The torch.nn.Sequential container allows you to stack different modules in a sequence, where the output of one module becomes the input to the next. In this case, the concept_encoder processes the input data to produce concept embeddings, which are then used by the task_predictor to make the final task predictions.

`optimizer = torch.optim.AdamW(model.parameters(), lr=0.01)`

This line sets up the optimizer for the training process, which is responsible for updating the model parameters based on the gradients computed during backpropagation. AdamW is a variant of the Adam optimizer that includes corrections for weight decay, improving training stability and performance.

**Training Loop**
1. Epoch - represents a complete pass over the entire training dataset. So we iteratre through 501 epochs in this case
2. `optimizer.zero_grad()` - Before the model can update its weights, the gradients need to be zeroed out. This is because gradients accumulate by default, and failing to reset them would lead to incorrect weight updates.
3. Generate Concept and Task Predictions
4. Compute Loss
5. Backpropagation and Optimizer Step - `loss.backward()` computes the gradient of the loss function with respect to the model parameters, effectively telling the model how to change its parameters to reduce loss. `optimizer.step()` updates the model parameters according to the optimization strategy and the gradients calculated by backward().


## Testing

`c_emb, c_pred = concept_encoder.forward(x_test)`

`y_pred = task_predictor(c_emb.reshape(len(c_emb), -1))`

This part of the code generates predictions using the test dataset (x_test). The outputs are used for evaluating the model's ability to generalize to new data using: 

`task_accuracy = accuracy_score(y_test, y_pred > 0)`

`concept_accuracy = accuracy_score(c_test, c_pred > 0.5)`