"""
Data Preprocessing Module
Handles image loading, normalization, and augmentation
"""

import cv2
import numpy as np
from pathlib import Path
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array


class DataPreprocessor:
    """Preprocess medical images for CNN training"""
    
    def __init__(self, img_size=(224, 224)):
        self.img_size = img_size
    
    def load_and_preprocess_image(self, image_path):
        """Load and preprocess single image"""
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                return None
            
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Resize
            image = cv2.resize(image, self.img_size)
            
            # Normalize to 0-1
            image = image.astype('float32') / 255.0
            
            return image
        except Exception as e:
            print(f"Error loading {image_path}: {e}")
            return None
    
    def get_augmentation_pipeline(self):
        """Return data augmentation pipeline"""
        return ImageDataGenerator(
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.15,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest',
            brightness_range=[0.8, 1.2],
            channel_shift_range=15.0
        )
    
    def create_dataset_generators(self, train_dir, test_dir, batch_size=32):
        """Create train and test generators from directory structure"""
        
        if not Path(train_dir).exists() or not Path(test_dir).exists():
            raise ValueError(f"Directory not found: train={train_dir}, test={test_dir}")
        
        # Training data generator (with augmentation)
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=25,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.15,
            zoom_range=0.2,
            horizontal_flip=True,
            brightness_range=[0.8, 1.2],
            channel_shift_range=20,
            fill_mode='nearest'
        )
        
        # Test data generator (no augmentation, only rescaling)
        test_datagen = ImageDataGenerator(rescale=1./255)
        
        # Load training images
        train_generator = train_datagen.flow_from_directory(
            train_dir,
            target_size=self.img_size,
            batch_size=batch_size,
            class_mode='categorical',
            shuffle=True
        )
        
        # Load test images
        test_generator = test_datagen.flow_from_directory(
            test_dir,
            target_size=self.img_size,
            batch_size=batch_size,
            class_mode='categorical',
            shuffle=False
        )
        
        return train_generator, test_generator
    
    def count_images_in_directory(self, base_dir):
        """Count images in directory structure"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        counts = {}
        
        for class_dir in Path(base_dir).iterdir():
            if class_dir.is_dir():
                count = sum(1 for f in class_dir.glob('*') 
                           if f.suffix.lower() in image_extensions)
                counts[class_dir.name] = count
        
        return counts
    
    def validate_dataset(self, train_dir, test_dir, min_per_class=50):
        """Validate that dataset meets minimum requirements"""
        train_counts = self.count_images_in_directory(train_dir)
        test_counts = self.count_images_in_directory(test_dir)
        
        print("\n=== TRAINING SET ===")
        for class_name, count in train_counts.items():
            status = "✓" if count >= min_per_class else "✗"
            print(f"{status} {class_name}: {count} images")
        
        print("\n=== TEST SET ===")
        for class_name, count in test_counts.items():
            status = "✓" if count >= 10 else "✗"
            print(f"{status} {class_name}: {count} images")
        
        total_train = sum(train_counts.values())
        total_test = sum(test_counts.values())
        
        print(f"\nTotal training images: {total_train}")
        print(f"Total test images: {total_test}")
        
        if total_train < 200:
            print("\n⚠️  WARNING: Less than 200 training images. Model may overfit.")
        
        return train_counts, test_counts
