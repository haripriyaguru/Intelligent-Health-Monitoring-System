"""
Quick Start Guide for Training Medical Disease Models
Complete example workflow for training and evaluating CNN models
"""

# ===== STEP 1: PREPARE ENVIRONMENT =====
# Install required packages:
# pip install tensorflow==2.13 keras opencv-python numpy matplotlib scikit-learn


# ===== STEP 2: DATA COLLECTION =====
# Download medical image datasets:
# 
# Eye Disease Dataset:
# - Kaggle: https://www.kaggle.com/datasets/gupta24abhishek/eye-disease-detection
# - EyePACS: http://www.eyepacs.org/ (requires registration)
# - Format: jpg/png images organized in class folders
#
# Tongue Disease Dataset:
# - Kaggle: https://www.kaggle.com/datasets/hastalavista/tongue-disease-detection
# - NIH: https://www.nih.gov/news-events/news-releases
# - Format: jpg/png images organized in class folders
#
# Dataset Structure:
# dataset/
#   eye/
#     train/
#       normal/
#         image1.jpg, image2.jpg, ...
#       infected/
#         image1.jpg, image2.jpg, ...
#       fatigue/
#       strain/
#     test/
#       normal/
#       infected/
#       fatigue/
#       strain/
#   tongue/
#     train/
#       normal/
#       pale/
#       coated/
#       inflamed/
#       fissured/
#       dark/
#       thrush/
#     test/


# ===== STEP 3: VALIDATE DATASET =====
from ml.data_preprocessing import DataPreprocessor

print("=" * 60)
print("VALIDATING EYE DISEASE DATASET")
print("=" * 60)

preprocessor = DataPreprocessor()
try:
    preprocessor.validate_dataset(
        train_dir='dataset/eye/train',
        test_dir='dataset/eye/test'
    )
    print("✓ Eye dataset validation successful\n")
except Exception as e:
    print(f"✗ Eye dataset validation failed: {e}\n")
    print("ACTION: Download more eye images and organize in train/test folders\n")

print("=" * 60)
print("VALIDATING TONGUE DISEASE DATASET")
print("=" * 60)

try:
    preprocessor.validate_dataset(
        train_dir='dataset/tongue/train',
        test_dir='dataset/tongue/test'
    )
    print("✓ Tongue dataset validation successful\n")
except Exception as e:
    print(f"✗ Tongue dataset validation failed: {e}\n")
    print("ACTION: Download more tongue images and organize in train/test folders\n")


# ===== STEP 4: TRAIN EYE DISEASE MODEL =====
from ml.train_cnn_model import CNNModelTrainer

print("=" * 60)
print("TRAINING EYE DISEASE MODEL")
print("=" * 60)
print("This will take 30-60 minutes on GPU (3-4 hours on CPU)\n")

try:
    eye_trainer = CNNModelTrainer(
        model_type='efficientnet',  # Options: efficientnet, resnet50, densenet, mobilenet
        num_classes=4  # normal, infected, fatigue, strain
    )
    
    print("Training eye model...")
    eye_trainer.train(
        train_dir='dataset/eye/train',
        test_dir='dataset/eye/test',
        epochs=10,
        batch_size=32
    )
    
    print("\nEvaluating eye model on test set...")
    eye_metrics = eye_trainer.evaluate('dataset/eye/test')
    print(f"Eye Model Performance:")
    print(f"  Accuracy: {eye_metrics.get('accuracy', 0):.2%}")
    print(f"  Precision: {eye_metrics.get('weighted_precision', 0):.2%}")
    print(f"  Recall: {eye_metrics.get('weighted_recall', 0):.2%}")
    
    print("\nSaving eye model...")
    eye_trainer.save_model('ml/models/eye_disease_model.h5')
    print("✓ Eye model saved to ml/models/eye_disease_model.h5")
    
    print("\nGenerating training history plot...")
    eye_trainer.plot_training_history('eye_training_history.png')
    print("✓ Training plot saved to eye_training_history.png\n")
    
except Exception as e:
    print(f"✗ Eye model training failed: {e}\n")


# ===== STEP 5: TRAIN TONGUE DISEASE MODEL =====
print("=" * 60)
print("TRAINING TONGUE DISEASE MODEL")
print("=" * 60)
print("This will take 30-60 minutes on GPU (3-4 hours on CPU)\n")

try:
    tongue_trainer = CNNModelTrainer(
        model_type='efficientnet',
        num_classes=2  # normal, abnormal
    )
    
    print("Training tongue model...")
    tongue_trainer.train(
        train_dir='dataset/tongue/train',
        test_dir='dataset/tongue/test',
        epochs=15,
        batch_size=32
    )
    
    print("\nEvaluating tongue model on test set...")
    tongue_metrics = tongue_trainer.evaluate('dataset/tongue/test')
    print(f"Tongue Model Performance:")
    print(f"  Accuracy: {tongue_metrics.get('accuracy', 0):.2%}")
    print(f"  Precision: {tongue_metrics.get('weighted_precision', 0):.2%}")
    print(f"  Recall: {tongue_metrics.get('weighted_recall', 0):.2%}")
    
    print("\nSaving tongue model...")
    tongue_trainer.save_model('ml/models/tongue_disease_model.h5')
    print("✓ Tongue model saved to ml/models/tongue_disease_model.h5")
    
    print("\nGenerating training history plot...")
    tongue_trainer.plot_training_history('tongue_training_history.png')
    print("✓ Training plot saved to tongue_training_history.png\n")
    
except Exception as e:
    print(f"✗ Tongue model training failed: {e}\n")


# ===== STEP 6: TEST MODELS ON SAMPLE IMAGES =====
from ml.cnn_eye_model import EyeDiseaseDetectorCNN
from ml.cnn_tongue_model import TongueDiseaseDetectorCNN
from pathlib import Path

print("=" * 60)
print("TESTING TRAINED MODELS")
print("=" * 60)

# Test eye model
print("\nTesting Eye Disease Model:")
print("-" * 40)
eye_detector = EyeDiseaseDetectorCNN('ml/models/eye_disease_model.h5')

test_eye_image = Path('dataset/eye/test').glob('*/image_*.jpg')
test_eye_images = list(test_eye_image)[:3]  # Test on 3 random images

for img_path in test_eye_images:
    result = eye_detector.analyze_eye_image(str(img_path))
    print(f"\nImage: {img_path.name}")
    print(f"  Status: {result['status']}")
    print(f"  Score: {result['score']}/100")
    print(f"  Confidence: {result['confidence']:.1%}")
    print(f"  Issues: {', '.join(result['issues'][:2])}")

# Test tongue model
print("\n\nTesting Tongue Disease Model:")
print("-" * 40)
tongue_detector = TongueDiseaseDetectorCNN('ml/models/tongue_disease_model.h5')

test_tongue_image = Path('dataset/tongue/test').glob('*/image_*.jpg')
test_tongue_images = list(test_tongue_image)[:3]  # Test on 3 random images

for img_path in test_tongue_images:
    result = tongue_detector.analyze_tongue_image(str(img_path))
    print(f"\nImage: {img_path.name}")
    print(f"  Status: {result['status']}")
    print(f"  Score: {result['score']}/100")
    print(f"  Confidence: {result['confidence']:.1%}")
    print(f"  Issues: {', '.join(result['issues'][:2])}")


# ===== STEP 7: INTEGRATE WITH FLASK APP =====
print("\n\n" + "=" * 60)
print("INTEGRATION WITH FLASK APP")
print("=" * 60)
print("""
To integrate trained models with your Flask app:

1. Replace eye detection in app.py:
   FROM: from models.eye_detection import EyeDetector
   TO:   from ml.cnn_eye_model import EyeDiseaseDetectorCNN

2. Replace tongue detection in app.py:
   FROM: from models.tongue_analysis import TongueAnalyzer
   TO:   from ml.cnn_tongue_model import TongueDiseaseDetectorCNN

3. Initialize models in app.py __init__:
   eye_detector = EyeDiseaseDetectorCNN('ml/models/eye_disease_model.h5')
   tongue_detector = TongueDiseaseDetectorCNN('ml/models/tongue_disease_model.h5')

4. Use in run_analysis():
   eye_result = eye_detector.analyze_eye_image(eye_image_path)
   tongue_result = tongue_detector.analyze_tongue_image(tongue_image_path)

5. Test with real medical images in the web app

✓ Models will now use deep learning instead of rule-based analysis
✓ Accuracy should improve significantly with sufficient training data
✓ Fallback to basic analysis if models not available
""")


# ===== TROUBLESHOOTING =====
print("\n\n" + "=" * 60)
print("TROUBLESHOOTING TIPS")
print("=" * 60)
print("""
ISSUE: "Model not found" error
SOLUTION: Ensure models are saved to ml/models/ directory with correct names

ISSUE: Low accuracy (<75%)
SOLUTION: 
  - Collect more training data (minimum 200-300 images per class)
  - Check data labeling for errors
  - Try different model architecture (ResNet50, DenseNet)
  - Increase epochs to 100

ISSUE: Overfitting (train loss decreases, val loss increases)
SOLUTION:
  - Increase dropout rates (currently 0.5→0.4→0.3)
  - Use more aggressive data augmentation
  - Reduce learning rate (try 1e-5)
  - Add L2 regularization

ISSUE: Out of memory during training
SOLUTION:
  - Reduce batch size from 32 to 16
  - Use lighter model (MobileNetV3 instead of EfficientNet)
  - Reduce image size from 224 to 192

ISSUE: Very slow training on CPU
SOLUTION:
  - This is normal - CPU training of CNN takes 3-4 hours
  - Use GPU if available: check CUDA installation
  - Or use smaller dataset (100 images per class) for testing

ISSUE: Model predictions wrong on new images
SOLUTION:
  - Test set may not be representative
  - Model needs more data or better augmentation
  - Check image preprocessing (color space, normalization)
  - Verify image quality and labeling
""")

print("\n" + "=" * 60)
print("TRAINING COMPLETE!")
print("=" * 60)
