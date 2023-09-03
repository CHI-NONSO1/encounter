import numpy as np
import tensorflow as tf
import keras
from keras.layers import TextVectorization
from keras.layers import Normalization
from keras.layers import CenterCrop
from keras.layers import Rescaling

from keras import layers

# Example training data, of dtype `string`.
training_text_data = np.array([["This is the 1st sample."], [
    "And here's the 2nd sample."]])


# Create a TextVectorization layer instance. It can be configured to either
# return integer token indices, or a dense token representation (e.g. multi-hot
# or TF-IDF). The text standardization and text splitting algorithms are fully
# configurable.

vectorizer = TextVectorization(output_mode="int")
labels = [[0], [1]]
# Calling `adapt` on an array or dataset makes the layer generate a vocabulary
# index for the data, which can then be reused when seeing new data.
vectorizer.adapt(training_text_data)


# Asynchronous preprocessing: the text vectorization is part of the tf.data pipeline.
# First, create a dataset
dataset = tf.data.Dataset.from_tensor_slices(
    (training_text_data, labels)).batch(2)
# Apply text vectorization to the samples
dataset = dataset.map(lambda x, y: (vectorizer(x), y))
# Prefetch with a buffer size of 2 batches
dataset = dataset.prefetch(2)

# Our model should expect sequences of integers as inputs
inputs = keras.Input(shape=(None,), dtype="int64")
x = layers.Embedding(input_dim=10, output_dim=32)(inputs)
outputs = layers.Dense(1)(x)
model = keras.Model(inputs, outputs)

model.compile(optimizer="adam", loss="mse", run_eagerly=True)
model.fit(dataset)

# ==========================================================================
# Example image data, with values in the [0, 255] range
training_image_data = np.random.randint(
    0, 256, size=(64, 200, 200, 3)).astype("float32")

normalizer = Normalization(axis=-1)
normalizer.adapt(training_image_data)

normalized_data = normalizer(training_image_data)


cropper = CenterCrop(height=150, width=150)
scaler = Rescaling(scale=1.0 / 255)

output_data = scaler(cropper(training_image_data))


dense = keras.layers.Dense(units=16)
# Let's say we expect our inputs to be RGB images of arbitrary size
inputs = keras.Input(shape=(None, None, 3))

# Center-crop images to 150x150
x = CenterCrop(height=150, width=150)(inputs)
# Rescale images to [0, 1]
x = Rescaling(scale=1.0 / 255)(x)

# Apply some convolution and pooling layers
x = layers.Conv2D(filters=32, kernel_size=(3, 3), activation="relu")(x)
x = layers.MaxPooling2D(pool_size=(3, 3))(x)
x = layers.Conv2D(filters=32, kernel_size=(3, 3), activation="relu")(x)
x = layers.MaxPooling2D(pool_size=(3, 3))(x)
x = layers.Conv2D(filters=32, kernel_size=(3, 3), activation="relu")(x)

# Apply global average pooling to get flat feature vectors
x = layers.GlobalAveragePooling2D()(x)

# Add a dense classifier on top
num_classes = 10
outputs = layers.Dense(num_classes, activation="softmax")(x)
model = keras.Model(inputs=inputs, outputs=outputs)

processed_data = model(training_image_data)

# =======Training models with fit()======
model.compile(optimizer=keras.optimizers.RMSprop(learning_rate=1e-3),
              loss=keras.losses.CategoricalCrossentropy())
# === fitting a model looks like with NumPy data:========
# model.fit(numpy_array_of_samples, numpy_array_of_labels,
# batch_size=32, epochs=10)
# ===fitting a model looks like with a dataset:=====
# model.fit(dataset_of_samples_and_labels, epochs=10)


# ==================Example=====================
# Get the data as Numpy arrays
(x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()


# Build a simple model
inputs = keras.Input(shape=(28, 28))
x = layers.Rescaling(1.0 / 255)(inputs)
x = layers.Flatten()(x)
x = layers.Dense(128, activation="relu")(x)
x = layers.Dense(128, activation="relu")(x)
outputs = layers.Dense(10, activation="softmax")(x)
model = keras.Model(inputs, outputs)
model.summary()

# Compile the model

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=[keras.metrics.SparseCategoricalAccuracy(name="acc")],
)

# Train the model for 1 epoch from Numpy data
batch_size = 64
print("Fit on NumPy data")
history = model.fit(x_train, y_train, batch_size=batch_size, epochs=1)


# Train the model for 1 epoch using a dataset
dataset = tf.data.Dataset.from_tensor_slices(
    (x_train, y_train)).batch(batch_size)
print("Fit on Dataset")
val_dataset = tf.data.Dataset.from_tensor_slices(
    (x_test, y_test)).batch(batch_size)
history = model.fit(dataset, epochs=1, validation_data=val_dataset)
loss, acc = model.evaluate(val_dataset)  # returns loss and metrics
predictions = model.predict(val_dataset)
print(predictions.shape)
print("loss: %.2f" % loss)
print("acc: %.2f" % acc)
print(history.history)
# =======================================


model.summary()

print(processed_data.shape)

print("shape:", output_data.shape)
print("min:", np.min(output_data))
print("max:", np.max(output_data))

print("var: %.4f" % np.var(normalized_data))
print("mean: %.4f" % np.mean(normalized_data))
