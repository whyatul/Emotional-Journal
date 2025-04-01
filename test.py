import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array

# Load Trained Model
model = tf.keras.models.load_model("emotion_model.h5")

# Image Dimensions & Paths
img_size = (48, 48)
test_dir = "dataset/test"  # Ensure this directory contains test images

# Data Preprocessing for Testing
test_datagen = ImageDataGenerator(rescale=1./255)
test_generator = test_datagen.flow_from_directory(
    test_dir, target_size=img_size, batch_size=32, class_mode='categorical', shuffle=False
)

# Evaluate Model
loss, accuracy = model.evaluate(test_generator)
print(f"✅ Model Evaluation: Loss = {loss:.4f}, Accuracy = {accuracy:.4%}")

# Predict on a Few Sample Images
emotion_classes = list(test_generator.class_indices.keys())  # Get class labels

def predict_emotion(image_path):
    """Loads an image, preprocesses it, and predicts the emotion."""
    img = load_img(image_path, target_size=img_size)
    img_array = img_to_array(img) / 255.0  # Normalize
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    
    prediction = model.predict(img_array)
    predicted_class = emotion_classes[np.argmax(prediction)]
    
    # Show Image & Prediction
    plt.imshow(img)
    plt.title(f"Predicted Emotion: {predicted_class}")
    plt.axis("off")
    plt.show()python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

# Test on Sample Images (Change filenames as needed)
sample_images = ["data\frame_0_00_1.jpg,data\frame_0_00_10.jpg,data\frame_0_00_3.jpg,data\frame_0_00_13.jpg"]

for img_path in sample_images:
    predict_emotion(img_path)
