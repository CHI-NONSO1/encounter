import numpy as np
import tensorflow as tf
from sklearn.metrics import mean_squared_error

# Mock data
lenders = [
    {"lender_id": 1, "name": "Lender A"},
    {"lender_id": 2, "name": "Lender B"},
    {"lender_id": 3, "name": "Lender C"},
]

borrowers = [
    {"borrower_id": 101, "name": "Borrower X"},
    {"borrower_id": 102, "name": "Borrower Y"},
    {"borrower_id": 103, "name": "Borrower Z"},
]

loan_history = [
    {"lender_id": 1, "borrower_id": 101, "rating": 4.5},
    {"lender_id": 2, "borrower_id": 101, "rating": 3.0},
    {"lender_id": 1, "borrower_id": 102, "rating": 5.0},
    {"lender_id": 3, "borrower_id": 103, "rating": 4.2},
    {"lender_id": 2, "borrower_id": 103, "rating": 3.8},
]

# Create user and item dictionaries
user_dict = {user["borrower_id"]: i for i, user in enumerate(borrowers)}
item_dict = {item["lender_id"]: i for i, item in enumerate(lenders)}

# Create rating matrix
num_users = len(borrowers)
num_items = len(lenders)

ratings_matrix = np.zeros((num_users, num_items))

for rating in loan_history:
    user_idx = user_dict[rating["borrower_id"]]
    item_idx = item_dict[rating["lender_id"]]
    ratings_matrix[user_idx, item_idx] = rating["rating"]

# Perform Singular Value Decomposition
U, S, Vt = np.linalg.svd(ratings_matrix)


# Choose the number of latent factors
num_latent_factors = 2


# Build recommendation matrix
U_reduced = U[:, :num_latent_factors]
S_reduced = np.diag(S[:num_latent_factors])
Vt_reduced = Vt[:num_latent_factors, :]

recommendations = np.dot(np.dot(U_reduced, S_reduced), Vt_reduced)


# Choose a user to make recommendations for (Borrower X in this case)
user_id_to_recommend = 102
user_index = user_dict[user_id_to_recommend]

# Get recommended lenders and their scores
user_recommendations = recommendations[user_index]
recommended_lender_indices = np.argsort(user_recommendations)[::-1]

# Print top recommended lenders
num_recommendations = 2
print(f"Recommended lenders for Borrower {user_id_to_recommend}:")
for i in range(num_recommendations):
    lender_index = recommended_lender_indices[i]
    recommended_lender = lenders[lender_index]["name"]
    recommendation_score = user_recommendations[lender_index]
    print(f"{recommended_lender}: {recommendation_score:.2f}")

# Split data into training and validation sets
train_ratio = 0.8
train_mask = np.random.rand(*ratings_matrix.shape) < train_ratio
train_data = ratings_matrix * train_mask
validation_data = ratings_matrix * (~train_mask)

# Create a model for saving

model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(num_items,)),
    tf.keras.layers.Dense(num_latent_factors),
    tf.keras.layers.Dense(num_items, activation='linear')
])

# Compile the model (you can customize the optimizer and loss function)
model.compile(optimizer='adam', loss='mean_squared_error')

# Prepare the data using tf.data.Dataset
train_dataset = tf.data.Dataset.from_tensor_slices(
    (train_data, train_data)).batch(1)

# Train the model
model.fit(train_dataset, epochs=10, verbose=1)

# Calculate validation error (mean squared error)
validation_mask = ~train_mask
predicted_ratings = model.predict(validation_data)
mse = mean_squared_error(
    validation_data[validation_mask], predicted_ratings[validation_mask])

print(f"Validation Mean Squared Error: {mse:.2f}")

model.save('lender_borrower.keras')
