import tensorflow as tf
from tensorflow import keras
from keras.layers import Embedding, Flatten, Dense, Input
from keras.models import Model
import numpy as np

# Define hyperparameters
embedding_dim = 32
num_epochs = 10
batch_size = 32

# Assuming you have user and item IDs, and ratings
user_ids = np.array([1, 2, 3])
item_ids = np.array([101, 102, 103])
ratings = np.array([4.5, 3.0, 5.0])

num_users = max(user_ids) + 1
num_items = max(item_ids) + 1

# Define model architecture
user_input = Input(shape=(1,))
item_input = Input(shape=(1,))

user_embedding = Embedding(num_users, embedding_dim, name='user_embedding')(
    user_input)  # Specify the name
item_embedding = Embedding(num_items, embedding_dim, name='item_embedding')(
    item_input)  # Specify the name

user_flatten = Flatten()(user_embedding)
item_flatten = Flatten()(item_embedding)

concat = tf.keras.layers.Concatenate()([user_flatten, item_flatten])

hidden_layer = Dense(128, activation='relu')(concat)
output_layer = Dense(1, activation='linear')(hidden_layer)

model = Model(inputs=[user_input, item_input], outputs=output_layer)

# Compile the model
# Add 'mae' (Mean Absolute Error) as a metric
model.compile(loss='mse', optimizer='adam', metrics=['mae'])

# Split data into training and validation sets
split_idx = int(len(user_ids) * 0.8)
train_user_ids, val_user_ids = user_ids[:split_idx], user_ids[split_idx:]
train_item_ids, val_item_ids = item_ids[:split_idx], item_ids[split_idx:]
train_ratings, val_ratings = ratings[:split_idx], ratings[split_idx:]

# Train the model
history = model.fit([train_user_ids, train_item_ids], train_ratings, epochs=num_epochs,
                    batch_size=batch_size, validation_data=([val_user_ids, val_item_ids], val_ratings))

# Print the history of MAE values
print(history.history['mae'])  # Print training Mean Absolute Error values
# Print validation Mean Absolute Error values
print(history.history['val_mae'])

# Save the trained model
model.save('encounter_model.keras')
