import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator # pyright: ignore[reportMissingImports]
from tensorflow.keras.models import Sequential # pyright: ignore[reportMissingImports]
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout # pyright: ignore[reportMissingImports]

# Define dataset path
dataset_path = 'C:\\Users\\sansk\\Downloads\\archive (3)'  # Replace with the path to your dataset

# Define data directories
train_dir = os.path.join(dataset_path, 'dataset', 'train')
test_dir = os.path.join(dataset_path, 'dataset', 'test')

# Data augmentation
train_datagen = ImageDataGenerator(rescale=1./255,
                                    shear_range=0.2,
                                    zoom_range=0.2,
                                    horizontal_flip=True)

test_datagen = ImageDataGenerator(rescale=1./255)

# Load training and testing data
train_generator = train_datagen.flow_from_directory(train_dir,
                                                    target_size=(224, 224),
                                                    batch_size=32,
                                                    class_mode='categorical')

test_generator = test_datagen.flow_from_directory(test_dir,
                                                  target_size=(224, 224),
                                                  batch_size=32,
                                                  class_mode='categorical')

# Model definition
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.2),
    Dense(len(train_generator.class_indices), activation='softmax')
])

# Compile model
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Train model
history = model.fit(train_generator,
                    epochs=10,
                    validation_data=test_generator)

# Evaluate model
loss, accuracy = model.evaluate(test_generator)
print(f'Test accuracy: {accuracy:.2f}')

# Save model
model.save('trashnet_model.h5')

import json

# Save model
model.save('trashnet_model.h5')

# Save label mapping
with open('labels.json', 'w') as f:
    json.dump(train_generator.class_indices, f)  # {"cardboard":0, "glass":1, ...}
