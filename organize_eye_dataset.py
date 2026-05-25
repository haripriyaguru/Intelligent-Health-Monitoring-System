"""
Organize Eye Disease Detection Dataset from Kaggle
Download from: https://www.kaggle.com/datasets/gupta24abhishek/eye-disease-detection
Extract and run this script to organize into train/test structure
"""

import os
import shutil
from pathlib import Path
import random

def organize_eye_dataset():
    """Organize downloaded eye disease dataset into train/test structure"""
    
    print("\n" + "="*75)
    print(" "*20 + "ORGANIZING EYE DISEASE DATASET")
    print("="*75)
    
    # Source and destination paths
    downloaded_path = Path('dataset/eye_disease')  # After extracting Kaggle zip
    organized_path = Path('dataset/eye')
    
    # Check if source exists
    if not downloaded_path.exists():
        print(f"\n❌ ERROR: Downloaded dataset not found at {downloaded_path}")
        print("\n📥 Please download from: https://www.kaggle.com/datasets/gupta24abhishek/eye-disease-detection")
        print(f"📁 Extract to: {downloaded_path}")
        return False
    
    # Create directories
    organized_path.mkdir(parents=True, exist_ok=True)
    (organized_path / 'train').mkdir(exist_ok=True)
    (organized_path / 'test').mkdir(exist_ok=True)
    
    # Map Kaggle folders to our class names
    class_mapping = {
        'CNV': 'cnv',
        'DME': 'dme',
        'DRUSEN': 'drusen',
        'NORMAL': 'normal'
    }
    
    train_split = 0.8  # 80% train, 20% test
    total_images = 0
    
    print(f"\n📍 Source: {downloaded_path}")
    print(f"📁 Destination: {organized_path}\n")
    
    for kaggle_class, our_class in class_mapping.items():
        source_dir = downloaded_path / kaggle_class
        
        if not source_dir.exists():
            print(f"⚠️  WARNING: {kaggle_class} folder not found at {source_dir}")
            continue
        
        # Create train/test directories
        train_dir = organized_path / 'train' / our_class
        test_dir = organized_path / 'test' / our_class
        train_dir.mkdir(parents=True, exist_ok=True)
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all images
        images = list(source_dir.glob('*.png')) + list(source_dir.glob('*.jpg')) + list(source_dir.glob('*.jpeg'))
        total_images += len(images)
        
        print(f"📊 Class: {kaggle_class:8} → {our_class:8}")
        print(f"   Total images: {len(images)}")
        
        if len(images) == 0:
            print(f"   ⚠️  No images found!")
            continue
        
        # Shuffle and split
        random.shuffle(images)
        split_index = int(len(images) * train_split)
        train_images = images[:split_index]
        test_images = images[split_index:]
        
        # Copy to train
        for idx, img in enumerate(train_images):
            try:
                shutil.copy2(img, train_dir / img.name)
            except Exception as e:
                print(f"   ❌ Error copying {img.name}: {e}")
        
        # Copy to test
        for img in test_images:
            try:
                shutil.copy2(img, test_dir / img.name)
            except Exception as e:
                print(f"   ❌ Error copying {img.name}: {e}")
        
        print(f"   ✓ Train: {len(train_images)} images")
        print(f"   ✓ Test:  {len(test_images)} images\n")
    
    print(f"✅ Total images organized: {total_images}")
    print("="*75)
    
    # Validate
    return validate_eye_dataset('dataset/eye/train', 'dataset/eye/test')

def validate_eye_dataset(train_dir, test_dir):
    """Verify dataset structure"""
    print("\n" + "="*75)
    print(" "*20 + "EYE DATASET VALIDATION")
    print("="*75)
    
    train_path = Path(train_dir)
    test_path = Path(test_dir)
    
    if not train_path.exists():
        print(f"❌ Training directory not found: {train_path}")
        return False
    
    total_train = 0
    total_test = 0
    min_required = 50  # Minimum images per class
    passed = True
    
    print(f"\n{'Class':<15} {'Train Images':<15} {'Test Images':<15} {'Status':<10}")
    print("─" * 60)
    
    classes = sorted([d.name for d in train_path.iterdir() if d.is_dir()])
    
    for class_name in classes:
        train_count = len(list((train_path / class_name).glob('*')))
        test_count = len(list((test_path / class_name).glob('*')))
        
        total_train += train_count
        total_test += test_count
        
        status = "✓" if train_count >= min_required else "⚠️"
        print(f"{class_name:<15} {train_count:<15} {test_count:<15} {status:<10}")
        
        if train_count < min_required:
            passed = False
    
    print("─" * 60)
    print(f"{'TOTAL':<15} {total_train:<15} {total_test:<15}")
    print("="*75)
    
    if passed and total_train > 0:
        print(f"\n✅ Dataset is valid! Total: {total_train} train + {total_test} test = {total_train + total_test} images")
        return True
    else:
        print(f"\n⚠️  Dataset may need more images (minimum {min_required} per class recommended)")
        return False

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════════════════╗
    ║       EYE DISEASE DATASET ORGANIZATION UTILITY                        ║
    ║                                                                        ║
    ║  This script organizes the Kaggle Eye Disease dataset into a          ║
    ║  train/test directory structure for CNN training.                     ║
    ║                                                                        ║
    ║  Download dataset from:                                               ║
    ║  https://www.kaggle.com/datasets/gupta24abhishek/                    ║
    ║  eye-disease-detection                                                ║
    ║                                                                        ║
    ║  Classes: CNV, DME, DRUSEN, NORMAL                                    ║
    ╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    success = organize_eye_dataset()
    
    if success:
        print("\n🎉 Ready for training!")
        print("\nNext step: Run this command")
        print("  python training_script.py")
    else:
        print("\n⚠️  Please check dataset before training")
