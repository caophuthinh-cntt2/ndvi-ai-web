#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert GeoTIFF to Cloud Optimized GeoTIFF (COG)
Usage: python convert_to_cog.py <input.tif> <output_cog.tif>
"""
import os
import sys
import subprocess
from pathlib import Path

def convert_to_cog(
    input_path: str,
    output_path: str,
    compression: str = 'LZW',
    blocksize: int = 256,
    overview_resampling: str = 'AVERAGE',
    add_overviews: bool = True
):
    """
    Convert a GeoTIFF to Cloud Optimized GeoTIFF format
    
    Args:
        input_path: Path to input GeoTIFF
        output_path: Path to output COG file
        compression: Compression method (LZW, DEFLATE, JPEG, etc.)
        blocksize: Internal tile size (default 256)
        overview_resampling: Resampling method for overviews
        add_overviews: Whether to add overview levels
    """
    
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    # Validate input
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Converting: {input_path.name}")
    print(f"Output: {output_path}")
    
    # Build gdal_translate command
    cmd = [
        'gdal_translate',
        '-of', 'COG',
        '-co', f'COMPRESS={compression}',
        '-co', f'BLOCKSIZE={blocksize}',
        '-co', f'OVERVIEW_RESAMPLING={overview_resampling}',
    ]
    
    if add_overviews:
        cmd.extend(['-co', 'OVERVIEWS=AUTO'])
    
    cmd.extend([str(input_path), str(output_path)])
    
    # Execute conversion
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        
        print(f"✓ Successfully converted to COG")
        
        # Print file sizes
        input_size = input_path.stat().st_size / (1024 * 1024)
        output_size = output_path.stat().st_size / (1024 * 1024)
        print(f"  Input size: {input_size:.2f} MB")
        print(f"  Output size: {output_size:.2f} MB")
        
        return str(output_path)
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error during conversion:")
        print(e.stderr)
        raise
    except FileNotFoundError:
        print("✗ Error: gdal_translate not found. Please install GDAL.")
        print("  Windows: https://www.gisinternals.com/release.php")
        raise

def main():
    if len(sys.argv) < 3:
        print("Usage: python convert_to_cog.py <input.tif> <output_cog.tif>")
        print("\nOptions:")
        print("  --compression TYPE    Compression method (default: LZW)")
        print("  --blocksize SIZE      Block size (default: 256)")
        print("  --no-overviews        Skip overview generation")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Parse options
    compression = 'LZW'
    blocksize = 256
    add_overviews = True
    
    for i, arg in enumerate(sys.argv[3:]):
        if arg == '--compression' and i + 4 < len(sys.argv):
            compression = sys.argv[i + 4]
        elif arg == '--blocksize' and i + 4 < len(sys.argv):
            blocksize = int(sys.argv[i + 4])
        elif arg == '--no-overviews':
            add_overviews = False
    
    try:
        convert_to_cog(
            input_file,
            output_file,
            compression=compression,
            blocksize=blocksize,
            add_overviews=add_overviews
        )
    except Exception as e:
        print(f"\n✗ Conversion failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
