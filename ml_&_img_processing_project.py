# -*- coding: utf-8 -*-
"""ML & Img Processing Project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18v8EA3MStDapEZbnmvj-WJL9uYm4pbzN
"""

!pip install -q opendatasets

import opendatasets as od

dataset_url = 'https://www.kaggle.com/datasets/xhlulu/140k-real-and-fake-faces'
od.download(dataset_url)

train_dir="/content/140k-real-and-fake-faces/real_vs_fake/real-vs-fake/train"
test_dir="/content/140k-real-and-fake-faces/real_vs_fake/real-vs-fake/test"

print(len(train_dir))
print(len(test_dir))

import os
def walk_through_dir(dir_path):
  """
  Walks through dir_path returning its contents.
  Args:
    dir_path (str or pathlib.Path): target directory

  Returns:
    A print out of:
      number of subdiretories in dir_path
      number of images (files) in each subdirectory
      name of each subdirectory
  """
  for dirpath, dirnames, filenames in os.walk(dir_path):
    print(f"There are {len(dirnames)} directories and {len(filenames)} images in '{dirpath}'.")

walk_through_dir(train_dir)

import pandas as pd

df_train = pd.read_csv('/content/140k-real-and-fake-faces/train.csv')
df_test = pd.read_csv('/content/140k-real-and-fake-faces/test.csv')

df_train['full_path'] = '/content/140k-real-and-fake-faces/real_vs_fake/real-vs-fake/' + df_train['path']
df_test['full_path'] = '/content/140k-real-and-fake-faces/real_vs_fake/real-vs-fake/' + df_test['path']

print("Training samples:", len(df_train))
print("Testing samples:", len(df_test))

import matplotlib.pyplot as plt
from PIL import Image

def show_sample_images(df, num_samples=5):
    plt.figure(figsize=(15, 5))
    for i in range(num_samples):
        # Real
        real_img = df[df['label'] == 1].sample(1)
        img_real = Image.open(real_img['full_path'].values[0])
        plt.subplot(2, num_samples, i+1)
        plt.imshow(img_real)
        plt.title('Real')
        plt.axis('off')

        # Fake
        fake_img = df[df['label'] == 0].sample(1)
        img_fake = Image.open(fake_img['full_path'].values[0])
        plt.subplot(2, num_samples, i+1+num_samples)
        plt.imshow(img_fake)
        plt.title('Fake')
        plt.axis('off')
    plt.tight_layout()
    plt.show()

show_sample_images(df_train)

show_sample_images(df_test)

"""# **Preprocessing**"""

import numpy as np

def preprocess_image(image_path, target_size=(224, 224), stretch_contrast=True):
    img = Image.open(image_path).convert('RGB')
    img = img.resize(target_size)
    img_array = np.array(img, dtype=np.float32) / 255.0

    if stretch_contrast:
        current_max = img_array.max()
        if current_max > 0:
            img_array /= current_max

    return img_array

def process_in_batches(df, batch_size=1000, target_size=(224, 224), stretch_contrast=True):
    num_samples = len(df)
    num_batches = (num_samples + batch_size - 1) // batch_size

    X = np.zeros((num_samples, *target_size, 3), dtype=np.float32)
    y = np.zeros(num_samples, dtype=np.int8)

    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, num_samples)

        batch_df = df.iloc[start_idx:end_idx]
        for j, (_, row) in enumerate(batch_df.iterrows()):
            try:
                X[start_idx + j] = preprocess_image(row['full_path'], target_size, stretch_contrast)
                y[start_idx + j] = row['label']
            except Exception as e:
                print(f"Error processing {row['full_path']}: {e}")
                X[start_idx + j] = np.zeros((*target_size, 3))
                y[start_idx + j] = -1

    valid_mask = y != -1
    return X[valid_mask], y[valid_mask]

sample_size = 2000
df_sample = df_train.sample(sample_size, random_state=42)

X_sample, y_sample = process_in_batches(df_sample)

print("\nSample dataset processed:")
print("Images shape:", X_sample.shape)
print("Labels shape:", y_sample.shape)
print("Pixel value range:", X_sample.min(), "-", X_sample.max())

def show_processed_images_with_stats(X, y, num_samples=5):
    plt.figure(figsize=(20, 5))
    stats = []

    for i in range(min(num_samples, len(X))):
        plt.subplot(1, num_samples, i+1)
        plt.imshow(X[i])

        img_stats = {
            'min': X[i].min(),
            'max': X[i].max(),
            'mean': X[i].mean(),
            'white_px': np.sum(X[i] >= 0.99),
            'size': f"{X[i].shape[0]}x{X[i].shape[1]}"
        }
        stats.append(img_stats)

        title = [
            f"{'Real' if y[i] == 1 else 'Fake'}",
            f"Size: {img_stats['size']}",
            f"Range: {img_stats['min']:.2f}-{img_stats['max']:.2f}",
            f"White px: {img_stats['white_px']}"
        ]
        plt.title("\n".join(title), fontsize=9)
        plt.axis('off')

    plt.tight_layout()
    plt.show()

    print("\nVerification Table (All values should be 0 ≤ x ≤ 1)")
    print("-"*65)
    print(f"{'Sample':<6} {'Min':<8} {'Max':<8} {'Mean':<8} {'White Pixels':<12} {'Size':<10}")
    print("-"*65)
    for i, s in enumerate(stats):
        print(f"{i+1:<6} {s['min']:<8.4f} {s['max']:<8.4f} {s['mean']:<8.4f} {s['white_px']:<12} {s['size']:<10}")

show_processed_images_with_stats(X_sample, y_sample)

# 9. Full Dataset Processing (False right now)
full_dataset = False

if full_dataset:
    print("\nProcessing full training dataset...")
    X_train, y_train = process_in_batches(df_train)

    print("\nProcessing test dataset...")
    X_test, y_test = process_in_batches(df_test)

    print("\nFull dataset processed:")
    print("Training shape:", X_train.shape)
    print("Test shape:", X_test.shape)
else:
    print("\nSkipping full dataset processing to avoid memory issues")
    print("To process full dataset, set full_dataset=True")

"""# **MODEL BUILDING - CNN**"""

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from sklearn.model_selection import train_test_split

X_train, X_val, y_train, y_val = train_test_split(X_sample, y_sample, test_size=0.2, random_state=42, stratify=y_sample)

print("Train size:", X_train.shape)
print("Validation size:", X_val.shape)

model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=(224,224,3)),
    MaxPooling2D(2,2),

    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D(2,2),

    Conv2D(128, (3,3), activation='relu'),
    MaxPooling2D(2,2),

    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(1, activation='sigmoid')  # for binary classification
])

model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])

model.summary()

history = model.fit(X_train, y_train,
                    validation_data=(X_val, y_val),
                    epochs=10,
                    batch_size=32)

"""# **Making it more interactive**"""

def predict_single_image(model, image_path, true_label=None, target_size=(224, 224)):
    """
    Predict if a given image is real or fake, and compare with true label if provided.

    Args:
        model: Trained Keras model
        image_path: Path to the image
        true_label: Actual label (0=fake, 1=real), optional
        target_size: Resize target (default 224x224)

    Returns:
        prediction_label: "Real" or "Fake"
        confidence: prediction probability
    """
    img = Image.open(image_path).convert('RGB')
    img = img.resize(target_size)
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    pred_prob = model.predict(img_array, verbose=0)[0][0]
    prediction_label = "Real" if pred_prob >= 0.5 else "Fake"
    confidence = pred_prob if pred_prob >= 0.5 else 1 - pred_prob

    plt.imshow(img)
    title_text = f"Predicted: {prediction_label} ({confidence*100:.2f}%)"
    if true_label is not None:
        true_text = "Real" if true_label == 1 else "Fake"
        title_text += f"\nTrue Label: {true_text}"
    plt.title(title_text)
    plt.axis('off')
    plt.show()

    return prediction_label, confidence

def batch_predict_and_visualize(model, df, num_samples=10, target_size=(224, 224)):
    """
    Predict multiple random images and visualize results with true labels.

    Args:
        model: Trained model
        df: DataFrame containing 'full_path' and 'label'
        num_samples: How many images to predict
        target_size: Resize target
    """
    # getting random rows
    sample_df = df.sample(num_samples, random_state=42)

    plt.figure(figsize=(20, 8))

    for idx, (_, row) in enumerate(sample_df.iterrows()):

        img = Image.open(row['full_path']).convert('RGB')
        img_resized = img.resize(target_size)
        img_array = np.array(img_resized, dtype=np.float32) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        pred_prob = model.predict(img_array, verbose=0)[0][0]
        pred_label = "Real" if pred_prob >= 0.5 else "Fake"
        confidence = pred_prob if pred_prob >= 0.5 else 1 - pred_prob

        true_label = "Real" if row['label'] == 1 else "Fake"

        plt.subplot(2, (num_samples+1)//2, idx+1)
        plt.imshow(img)
        title_color = 'green' if pred_label == true_label else 'red'
        plt.title(f"Pred: {pred_label}\nTrue: {true_label}\n({confidence*100:.1f}%)", color=title_color, fontsize=9)
        plt.axis('off')

    plt.tight_layout()
    plt.show()

# Predict a single random image
random_row = df_test.sample(1).iloc[0]
predict_single_image(model, random_row['full_path'], true_label=random_row['label'])

# Predicting a batch of 10 random images
batch_predict_and_visualize(model, df_test, num_samples=10)

"""# **User is uploading the image**"""

from google.colab import files
from PIL import Image
import io

def upload_and_predict(model, target_size=(224, 224)):
    """
    Upload an image from local machine and predict Real/Fake.
    Args:
        model: Trained Keras model
        target_size: Tuple (height, width) for resizing the uploaded image
    """
    uploaded = files.upload()

    for filename in uploaded.keys():
        print(f"Processing file: {filename}")
        image_data = uploaded[filename]
        img = Image.open(io.BytesIO(image_data)).convert('RGB')
        img_resized = img.resize(target_size)
        img_array = np.array(img_resized, dtype=np.float32) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        pred_prob = model.predict(img_array, verbose=0)[0][0]
        prediction = "Real" if pred_prob >= 0.5 else "Fake"
        confidence = pred_prob if pred_prob >= 0.5 else 1 - pred_prob

        plt.imshow(img)
        plt.title(f"Prediction: {prediction} ({confidence*100:.2f}%)")
        plt.axis('off')
        plt.show()

        print(f"Prediction: {prediction}")
        print(f"Confidence: {confidence*100:.2f}%")

upload_and_predict(model)

import tensorflow as tf
from tensorflow.keras import layers, Sequential
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from sklearn.model_selection import train_test_split

"""# **Simple CNN**"""

def simple_cnn(input_shape=(224,224,3)):
    model = Sequential([
        Conv2D(32, (3,3), activation='relu', input_shape=input_shape),
        MaxPooling2D(2,2),

        Conv2D(64, (3,3), activation='relu'),
        MaxPooling2D(2,2),

        Conv2D(128, (3,3), activation='relu'),
        MaxPooling2D(2,2),

        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid')  # for binary classification
    ])
    return model

"""# **Using DeepCNN**"""

def build_deep_cnn(input_shape=(224,224,3)):
    model = Sequential([
        layers.Conv2D(32, (3,3), activation='relu', input_shape=input_shape),
        layers.Conv2D(32, (3,3), activation='relu'),
        layers.MaxPooling2D(2,2),

        layers.Conv2D(64, (3,3), activation='relu'),
        layers.Conv2D(64, (3,3), activation='relu'),
        layers.MaxPooling2D(2,2),

        layers.Conv2D(128, (3,3), activation='relu'),
        layers.Conv2D(128, (3,3), activation='relu'),
        layers.MaxPooling2D(2,2),

        layers.Flatten(),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid')
    ])
    return model

"""# **Using Transfer Learning -> ResNet50 and MobileNetV2**"""

def build_transfer_model(base_model_name='ResNet50', input_shape=(224,224,3)):
    if base_model_name.lower() == 'resnet50':
        base_model = tf.keras.applications.ResNet50(weights='imagenet', include_top=False, input_shape=input_shape)
    elif base_model_name.lower() == 'mobilenetv2':
        base_model = tf.keras.applications.MobileNetV2(weights='imagenet', include_top=False, input_shape=input_shape)
    else:
        raise ValueError("Unsupported model name. Choose 'ResNet50' or 'MobileNetV2'.")

    base_model.trainable = False  # Freeze base layer
    model = Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid')
    ])
    return model

def train_models(model, model_name, epochs=10, batch_size=32):
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    print(f"\nTraining {model_name}...\n")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        verbose=2
    )

"""# **Prinitng model architectures**"""

models_to_train = {
    "Simple CNN": simple_cnn(),
    "Deep CNN": build_deep_cnn(),
    "ResNet50": build_transfer_model('resnet50'),
    "MobileNetV2": build_transfer_model('mobilenetv2')
}

for model_name, model in models_to_train.items():
    print(f"\n===== {model_name} Architecture =====\n")
    model.summary()
    print("\n" + "="*60 + "\n")

"""# **Understanding params for each model**"""

for model_name, model in models_to_train.items():
    total_params = model.count_params()
    trainable_params = np.sum([np.prod(v.shape) for v in model.trainable_weights])
    non_trainable_params = total_params - trainable_params

    print(f"\nModel: {model_name}")
    print(f"Total Parameters: {total_params}")
    print(f"Trainable Parameters: {trainable_params}")
    print(f"Non-Trainable Parameters: {non_trainable_params}\n")

"""# **Junk Code -> not needed**

Another way using tensorflow (assuming that brightness should be same)
"""

from PIL import Image
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def preprocess_face(image):
    """Rescale image so the brightest pixel becomes white (255) before normalization"""
    img_array = np.array(image)
    current_max = img_array.max()
    if current_max > 0:
        img_array = (img_array / current_max) * 255  # Stretch to full dynamic range
    return img_array  # Return as numpy array (required by ImageDataGenerator)

#training dataset
train_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_face,  # Stretch contrast first
    rescale=1./255,                         # Then normalize to [0,1]
    rotation_range=20,                      # Augmentation
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True
)

target_size = (224, 224)  # resized to 224x224 pixels
batch_size = 32    # 32 images per batch

df_train['label'] = df_train['label'].astype(str)

train_generator = train_datagen.flow_from_dataframe(
    dataframe=df_train,
    x_col='full_path',
    y_col='label',
    target_size=target_size,
    batch_size=batch_size,
    class_mode='binary'
    # No subset parameter
)

#check
import matplotlib.pyplot as plt

# Get a batch
batch_images, batch_labels = next(train_generator)

# Display first 4 images with their pixel ranges
plt.figure(figsize=(15, 5))
for i in range(4):
    plt.subplot(1, 4, i+1)
    plt.imshow(batch_images[i])
    plt.title(f"Label: {batch_labels[i]}\n"
              f"Min: {batch_images[i].min():.2f}\n"
              f"Max: {batch_images[i].max():.2f}")
    plt.axis('off')
plt.tight_layout()
plt.show()

#testing data
test_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_face,  # Stretch contrast first
    rescale=1./255,                         # Then normalize to [0,1]
    rotation_range=20,                      # Augmentation
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True
)

target_size = (224, 224)  # resized to 224x224 pixels
batch_size = 32    # 32 images per batch

df_test['label'] = df_test['label'].astype(str)

test_generator = test_datagen.flow_from_dataframe(
    dataframe=df_test,
    x_col='full_path',
    y_col='label',
    target_size=target_size,
    batch_size=batch_size,
    class_mode='binary'
    # No subset parameter
)

#check
import matplotlib.pyplot as plt

# Get a batch
batch_images, batch_labels = next(test_generator)

# Display first 4 images with their pixel ranges
plt.figure(figsize=(15, 5))
for i in range(4):
    plt.subplot(1, 4, i+1)
    plt.imshow(batch_images[i])
    plt.title(f"Label: {batch_labels[i]}\n"
              f"Min: {batch_images[i].min():.2f}\n"
              f"Max: {batch_images[i].max():.2f}")
    plt.axis('off')
plt.tight_layout()
plt.show()

"""Using tensorflow but preserving relative brightness differences"""

from PIL import Image
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def preprocess_face(image):
    """Better contrast stretching preserving relative brightness"""
    img_array = np.array(image, dtype=np.float32)
    p2, p98 = np.percentile(img_array, (2, 98))  # Adjust percentiles if needed
    if p98 > p2:
        img_array = np.clip((img_array - p2) / (p98 - p2), 0, 1)
    return img_array

train_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_face,  # Handles normalization + smart contrast
    rotation_range=20,                      # Augmentation
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True
)

train_generator = train_datagen.flow_from_dataframe(
    dataframe=df_train,
    x_col='full_path',
    y_col='label',
    target_size=(224, 224),
    batch_size=32,
    class_mode='binary'  # Or 'categorical' for multi-class
)

#check
import matplotlib.pyplot as plt

# Get a batch
batch_images, batch_labels = next(train_generator)

# Display first 4 images with their pixel ranges
plt.figure(figsize=(15, 5))
for i in range(4):
    plt.subplot(1, 4, i+1)
    plt.imshow(batch_images[i])
    plt.title(f"Label: {batch_labels[i]}\n"
              f"Min: {batch_images[i].min():.2f}\n"
              f"Max: {batch_images[i].max():.2f}")
    plt.axis('off')
plt.tight_layout()
plt.show()