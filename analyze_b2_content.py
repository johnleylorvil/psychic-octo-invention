#!/usr/bin/env python3
"""
analyze_b2_content.py
Enhanced B2 bucket content analyzer for Afèpanou marketplace
Organizes images by category and provides detailed statistics
"""

import os
import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

def load_images_data():
    """Load images data from JSON file"""
    try:
        with open('images_list.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: images_list.json not found. Please run analyze_b2_bucket.py first.")
        return None

def analyze_content_structure(images_data):
    """Analyze and organize B2 bucket content"""
    
    # Organization by folder structure
    folders = defaultdict(list)
    categories = defaultdict(list)
    file_types = Counter()
    size_stats = {"total": 0, "count": 0, "largest": 0, "smallest": float('inf')}
    
    # B2 Configuration
    B2_BUCKET_NAME = os.getenv('B2_BUCKET_NAME', 'afepanou')
    B2_ENDPOINT_URL = os.getenv('B2_ENDPOINT_URL', 'https://s3.us-east-005.backblazeb2.com')
    B2_BASE_URL = f"{B2_ENDPOINT_URL}/{B2_BUCKET_NAME}"
    
    print("🔍 Analyzing B2 bucket content structure...\n")
    
    for image in images_data:
        file_path = image["file_name"]
        size_bytes = image["size_bytes"]
        
        # Update size statistics
        size_stats["total"] += size_bytes
        size_stats["count"] += 1
        size_stats["largest"] = max(size_stats["largest"], size_bytes)
        size_stats["smallest"] = min(size_stats["smallest"], size_bytes)
        
        # File type analysis
        file_ext = Path(file_path).suffix.lower()
        file_types[file_ext] += 1
        
        # Organize by folder structure
        if '/' in file_path:
            folder = file_path.split('/')[0]
            folders[folder].append({
                "name": file_path,
                "size": size_bytes,
                "url": f"{B2_BASE_URL}/{file_path}"
            })
        else:
            folders["root"].append({
                "name": file_path,
                "size": size_bytes,
                "url": f"{B2_BASE_URL}/{file_path}"
            })
        
        # Categorize by content type
        if "Store Produits de Première Nécessité" in file_path or "produits/premiere-necessite" in file_path:
            categories["premiere-necessite"].append(image)
        elif "Store Produits Locaux" in file_path or "produits/locaux" in file_path:
            categories["locaux"].append(image)
        elif "Store Produits Patriotiques" in file_path or "produits/patriotiques" in file_path:
            categories["patriotiques"].append(image)
        elif "Store Produits Électroniques" in file_path:
            categories["electroniques"].append(image)
        elif "Store Services Divers" in file_path or "services/" in file_path:
            categories["services"].append(image)
        elif "banners/" in file_path or "banner" in file_path.lower():
            categories["banners"].append(image)
        elif "featured/" in file_path:
            categories["featured"].append(image)
        elif "bestproduct/" in file_path:
            categories["bestproduct"].append(image)
        else:
            categories["autres"].append(image)
    
    return {
        "folders": dict(folders),
        "categories": dict(categories),
        "file_types": dict(file_types),
        "size_stats": size_stats,
        "base_url": B2_BASE_URL
    }

def format_size(size_bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def print_analysis_report(analysis):
    """Print detailed analysis report"""
    
    print("📊 B2 BUCKET CONTENT ANALYSIS REPORT")
    print("=" * 50)
    
    # Overall Statistics
    print(f"\n📈 OVERALL STATISTICS:")
    print(f"   Total Images: {analysis['size_stats']['count']}")
    print(f"   Total Size: {format_size(analysis['size_stats']['total'])}")
    print(f"   Average Size: {format_size(analysis['size_stats']['total'] / analysis['size_stats']['count'])}")
    print(f"   Largest File: {format_size(analysis['size_stats']['largest'])}")
    print(f"   Smallest File: {format_size(analysis['size_stats']['smallest'])}")
    print(f"   Base URL: {analysis['base_url']}")
    
    # File Types
    print(f"\n📁 FILE TYPES:")
    for ext, count in sorted(analysis['file_types'].items()):
        print(f"   {ext}: {count} files")
    
    # Folder Structure
    print(f"\n🗂️  FOLDER STRUCTURE:")
    for folder, files in sorted(analysis['folders'].items()):
        total_size = sum(f['size'] for f in files)
        print(f"   📂 {folder}/: {len(files)} files ({format_size(total_size)})")
        
        # Show first few files in each folder
        for i, file_info in enumerate(sorted(files, key=lambda x: x['size'], reverse=True)[:3]):
            filename = Path(file_info['name']).name
            print(f"      • {filename} ({format_size(file_info['size'])})")
        
        if len(files) > 3:
            print(f"      ... and {len(files) - 3} more files")
    
    # Categories for Products
    print(f"\n🏷️  CONTENT CATEGORIES:")
    for category, images in sorted(analysis['categories'].items()):
        if images:
            total_size = sum(img['size_bytes'] for img in images)
            print(f"   🏪 {category}: {len(images)} images ({format_size(total_size)})")
    
    # Usable Images for Product Population
    print(f"\n🛍️  PRODUCT IMAGES AVAILABLE:")
    product_categories = ['premiere-necessite', 'locaux', 'patriotiques', 'electroniques', 'services']
    total_product_images = 0
    
    for cat in product_categories:
        if cat in analysis['categories']:
            count = len(analysis['categories'][cat])
            total_product_images += count
            print(f"   • {cat.title()}: {count} images")
    
    print(f"   📊 Total Product Images: {total_product_images}")
    
    # Banner Images Available
    banner_count = len(analysis['categories'].get('banners', [])) + len(analysis['categories'].get('featured', []))
    print(f"   🎨 Banner Images: {banner_count}")

def save_organized_data(analysis):
    """Save organized data to JSON files"""
    
    # Save organized structure
    with open('b2_content_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n💾 Detailed analysis saved to: b2_content_analysis.json")
    
    # Create a simplified product mapping
    product_mapping = {}
    for category, images in analysis['categories'].items():
        if category in ['premiere-necessite', 'locaux', 'patriotiques', 'electroniques', 'services']:
            product_mapping[category] = [
                {
                    "file_name": img["file_name"],
                    "url": f"{analysis['base_url']}/{img['file_name']}",
                    "size": format_size(img["size_bytes"])
                }
                for img in images
            ]
    
    with open('product_images_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(product_mapping, f, ensure_ascii=False, indent=2)
    print(f"💾 Product images mapping saved to: product_images_mapping.json")

def main():
    """Main analysis function"""
    images_data = load_images_data()
    
    if not images_data:
        sys.exit(1)
    
    # Perform analysis
    analysis = analyze_content_structure(images_data)
    
    # Print report
    print_analysis_report(analysis)
    
    # Save organized data
    save_organized_data(analysis)
    
    print(f"\n✅ Analysis complete! Ready for database population.")
    print(f"📝 Next step: Run 'python populate_db_with_b2_images.py' to populate the database.")

if __name__ == "__main__":
    main()