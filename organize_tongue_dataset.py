"""
Organize BioHit Tongue Image Dataset
Download from: https://github.com/BioHit/TongueImageDataset
Extract and run this script to organize into train/test structure with augmentation
"""

import os
import shutil
from pathlib import Path
import random
import numpy as np
import cv2
from PIL import Image

def organize_tongue_dataset():
    """Organize tongue dataset and create augmented versions"""
    
    print("\n" + "="*75)
    print(" "*20 + "ORGANIZING TONGUE DISEASE DATASET")
    print("="*75)
    
    # Try different possible source paths
    source_paths = [
        Path('dataset/TongueImageDataset/dataset'),  # Most likely
        Path('dataset/TongueImageDataset'),
        Path('TongueImageDataset/dataset'),
    ]
    
    source_path = None
    for path in source_paths:
        if path.exists():
            source_path = path
            break
    
    if source_path is None:
        print(f"\n❌ ERROR: Tongue dataset not found")
        print("\n📥 Please download from: https://github.com/BioHit/TongueImageDataset")
        print(f"📁 Extract to: dataset/TongueImageDataset/")
        print(f"\nTried paths:")
        for path in source_paths:
            print(f"   - {path}")
        return False
    
    organized_path = Path('dataset/tongue')
    
    print(f"\n📍 Source: {source_path}")
    print(f"📁 Destination: {organized_path}")
    
    # Create directories
    organized_path.mkdir(parents=True, exist_ok=True)
    (organized_path / 'train/normal').mkdir(parents=True, exist_ok=True)
    (organized_path / 'train/abnormal').mkdir(parents=True, exist_ok=True)
    (organized_path / 'test/normal').mkdir(parents=True, exist_ok=True)
    (organized_path / 'test/abnormal').mkdir(parents=True, exist_ok=True)
    
    # Get all tongue images (include bmp)
    images = (
        list(source_path.glob('*.jpg')) +
        list(source_path.glob('*.png')) +
        list(source_path.glob('*.jpeg')) +
        list(source_path.glob('*.bmp'))
    )
    
    print(f"\n📊 Found {len(images)} tongue images (including BMP)")
    
    if len(images) == 0:
        print(f"❌ No images found at {source_path} - check extensions (bmp/jpg/png)")
        return False
    
    # Since dataset doesn't have labels, split into two groups
    # In production, you would manually label these images
    print("\n⚠️  NOTE: Dataset has no labels. Splitting automatically into normal/abnormal")
    print("          For better accuracy, manually review and re-organize images.")
    
    random.shuffle(images)
    split_point = len(images) // 2
    
    normal_images = images[:split_point]
    abnormal_images = images[split_point:]
    
    print(f"\n📁 Classification (auto-split for demo):")
    print(f"   Normal:    {len(normal_images)} images")
    print(f"   Abnormal:  {len(abnormal_images)} images")
    
    # Split into train/test (80/20)
    train_normal = normal_images[:int(len(normal_images)*0.8)]
    test_normal = normal_images[int(len(normal_images)*0.8):]
    
    train_abnormal = abnormal_images[:int(len(abnormal_images)*0.8)]
    test_abnormal = abnormal_images[int(len(abnormal_images)*0.8):]
    
    print(f"\n📋 Train/Test Split (80/20):")
    print(f"   Train Normal:    {len(train_normal)}")
    print(f"   Test Normal:     {len(test_normal)}")
    print(f"   Train Abnormal:  {len(train_abnormal)}")
    print(f"   Test Abnormal:   {len(test_abnormal)}")
    
    # Copy original images
    print(f"\n📋 Copying images...")
    copied = 0
    
    for img_path in train_normal:
        try:
            shutil.copy2(img_path, organized_path / 'train/normal' / img_path.name)
            copied += 1
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    for img_path in test_normal:
        try:
            shutil.copy2(img_path, organized_path / 'test/normal' / img_path.name)
            copied += 1
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    for img_path in train_abnormal:
        try:
            shutil.copy2(img_path, organized_path / 'train/abnormal' / img_path.name)
            copied += 1
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    for img_path in test_abnormal:
        try:
            shutil.copy2(img_path, organized_path / 'test/abnormal' / img_path.name)
            copied += 1
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"   ✓ Copied {copied} images")
    
    # Create augmented versions for training (since dataset is small)
    print(f"\n🔄 Creating augmented versions (3x expansion for small dataset)...")
    aug_normal = augment_images(organized_path / 'train/normal', multiplier=3)
    aug_abnormal = augment_images(organized_path / 'train/abnormal', multiplier=3)
    
    print(f"   ✓ Normal augmented:    {aug_normal} new images")
    print(f"   ✓ Abnormal augmented:  {aug_abnormal} new images")
    
    print("\n" + "="*75)
    print("✅ Tongue dataset organized successfully!")
    print("="*75)
    
    # Validate
    return validate_tongue_dataset()

def augment_images(image_dir, multiplier=3):
    """Create augmented versions of images"""
    
    images = list(image_dir.glob('*'))
    images = [f for f in images if f.suffix.lower() in ['.jpg', '.png', '.jpeg']]
    
    aug_count = 0
    
    for idx, img_path in enumerate(images):
        if not img_path.is_file():
            continue
        
        try:
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            
            # Create augmented versions
            for aug_idx in range(1, multiplier):
                aug_img = img.copy()
                
                # Random rotation (-10 to +10 degrees)
                angle = random.randint(-10, 10)
                rows, cols = aug_img.shape[:2]
                M = cv2.getRotationMatrix2D((cols/2, rows/2), angle, 1)
                aug_img = cv2.warpAffine(aug_img, M, (cols, rows))
                
                # Random brightness adjustment (0.8x to 1.2x)
                brightness = random.uniform(0.8, 1.2)
                aug_img = cv2.convertScaleAbs(aug_img, alpha=brightness, beta=0)
                
                # Random horizontal flip (50% chance)
                if random.random() > 0.5:
                    aug_img = cv2.flip(aug_img, 1)
                
                # Save augmented image
                new_name = img_path.stem + f'_aug{aug_idx}' + img_path.suffix
                cv2.imwrite(str(image_dir / new_name), aug_img)
                aug_count += 1
        
        except Exception as e:
            pass  # Skip problematic images
    
    return aug_count

def validate_tongue_dataset():
    """Verify tongue dataset"""
    print("\n" + "="*75)
    print(" "*20 + "TONGUE DATASET VALIDATION")
    print("="*75)
    
    base_path = Path('dataset/tongue')
    
    if not base_path.exists():
        print(f"❌ Dataset directory not found: {base_path}")
        return False
    
    total_images = 0
    min_required = 50
    passed = True
    
    for split in ['train', 'test']:
        print(f"\n{split.upper()}:")
        split_total = 0
        
        for class_name in ['normal', 'abnormal']:
            class_path = base_path / split / class_name
            count = len(list(class_path.glob('*')))
            split_total += count
            total_images += count
            
            status = "✓" if count >= min_required else "⚠️"
            print(f"  {class_name:12}: {count:4} images {status}")
            
            if count < min_required and split == 'train':
                passed = False
        
        print(f"  {split:12}  TOTAL: {split_total}")
    
    print("\n" + "="*75)
    print(f"✅ Total images: {total_images}")
    
    if passed and total_images > 0:
        print(f"✓ Dataset is ready for training!")
        return True
    else:
        print(f"⚠️  Dataset sizes are small. Consider:")
        print(f"   - Collecting more real tongue images")
        print(f"   - Using more aggressive data augmentation")
        print(f"   - Training with fewer epochs")
        return False

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════════════════╗
    ║       TONGUE IMAGE DATASET ORGANIZATION UTILITY                       ║
    ║                                                                        ║
    ║  This script organizes the BioHit tongue dataset into a train/test    ║
    ║  directory structure with data augmentation for CNN training.         ║
    ║                                                                        ║
    ║  Download dataset from:                                               ║
    ║  https://github.com/BioHit/TongueImageDataset                        ║
    ║                                                                        ║
    ║  Note: Dataset will be auto-split into normal/abnormal               ║
    ║        For better results, manually label your own images             ║
    ╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    success = organize_tongue_dataset()
    
    if success:
        print("\n🎉 Tongue dataset ready for training!")
        print("\nNext step: Run this command")
        print("  python training_script.py")
    else:
        print("\n⚠️  Please resolve issues before training")
