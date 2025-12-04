#!/usr/bin/env python3
"""
Kaoz CV Generator - CLI Tool

Converts Kaoz.dk JSON profiles to professional CV PDFs using RenderCV.
"""

import argparse
import json
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
from converter import convert_kaoz_to_rendercv, save_as_yaml


def load_json(file_path):
    """
    Load JSON profile data from file

    Args:
        file_path: Path to JSON file

    Returns:
        Dictionary with profile data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)


def check_rendercv_installed():
    """Check if RenderCV is installed and accessible"""
    try:
        result = subprocess.run(
            ['rendercv', '--version'],
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def cleanup_old_theme_version(theme_dir):
    """
    Remove old CV files for a specific theme before generating new ones

    Args:
        theme_dir: Path to theme directory to clean up
    """
    if theme_dir.exists():
        print(f"🧹 Cleaning up old {theme_dir.name} version...")
        try:
            shutil.rmtree(theme_dir)
            print(f"✅ Old version removed")
        except Exception as e:
            print(f"⚠️  Warning: Could not remove old files: {e}")


def generate_cv_with_rendercv(yaml_path, output_dir):
    """
    Call RenderCV CLI to generate CV from YAML

    Args:
        yaml_path: Path to YAML input file
        output_dir: Directory for output files

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"🔨 Generating CV with RenderCV...")

        result = subprocess.run(
            [
                'rendercv',
                'render',
                str(yaml_path),
                '--output-folder-name',
                str(output_dir)
            ],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            return True
        else:
            print(f"❌ RenderCV Error:\n{result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error calling RenderCV: {e}")
        return False


def main():
    """Main CLI entry point"""

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="🚀 Convert Kaoz.dk JSON profile to professional CV (PDF)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_cv.py --input profile.json --user-id 123
  python generate_cv.py --input profile.json --user-id 123 --theme classic
  python generate_cv.py --input profile.json --user-id 456 --theme sb2nov --debug

Available themes:
  - sb2nov (default, modern & clean)
  - classic
  - engineeringresumes
  - moderncv
  - engineeringclassic

Folder structure:
  output/{user_id}/{theme}/
  Example: output/123/sb2nov/Lukas_Schmidt_CV.pdf
        """
    )

    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Path to Kaoz.dk JSON profile file'
    )

    parser.add_argument(
        '--user-id', '-u',
        required=True,
        help='User ID (for organizing output by user)'
    )

    parser.add_argument(
        '--theme', '-t',
        default='sb2nov',
        choices=['classic', 'sb2nov', 'engineeringresumes', 'moderncv', 'engineeringclassic'],
        help='CV theme (default: sb2nov)'
    )

    parser.add_argument(
        '--base-output-dir',
        default='output',
        help='Base output directory (default: output)'
    )

    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Debug mode - keep temporary YAML file'
    )

    args = parser.parse_args()

    # Check RenderCV installation
    print("🔍 Checking RenderCV installation...")
    if not check_rendercv_installed():
        print("❌ Error: RenderCV is not installed or not in PATH")
        print("📦 Install with: pip install 'rendercv[full]'")
        sys.exit(1)
    print("✅ RenderCV found")

    # Load JSON
    print(f"📂 Loading JSON file: {args.input}")
    kaoz_json = load_json(args.input)

    # Convert to RenderCV format
    print(f"🔄 Converting to RenderCV format...")
    cv_data = convert_kaoz_to_rendercv(kaoz_json, theme=args.theme)

    print(f"   📝 Name: {cv_data['cv']['name']}")
    print(f"   📧 Email: {cv_data['cv']['email']}")
    print(f"   👤 User ID: {args.user_id}")
    print(f"   🎨 Theme: {args.theme}")

    # Build output directory structure: base_output_dir/user_id/theme/
    base_dir = Path(args.base_output_dir)
    user_dir = base_dir / str(args.user_id)
    theme_dir = user_dir / args.theme

    # Clean up old theme version if it exists
    cleanup_old_theme_version(theme_dir)

    # Create output directory structure
    theme_dir.mkdir(parents=True, exist_ok=True)

    # Save as temporary YAML or debug YAML
    if args.debug:
        yaml_path = user_dir / f"debug_{args.theme}_cv_data.yaml"
        save_as_yaml(cv_data, yaml_path)
        print(f"🐛 Debug: YAML saved to {yaml_path}")
        temp_file = None
    else:
        # Create temp file that will be auto-deleted
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.yaml',
            delete=False,
            encoding='utf-8'
        )
        yaml_path = Path(temp_file.name)
        save_as_yaml(cv_data, yaml_path)
        temp_file.close()

    # Generate CV with RenderCV
    success = generate_cv_with_rendercv(yaml_path, theme_dir)

    # Cleanup temp file if not in debug mode
    if not args.debug and temp_file:
        try:
            yaml_path.unlink()
        except Exception:
            pass

    # Report results
    if success:
        cv_filename = cv_data['cv']['name'].replace(' ', '_')
        print(f"\n🎉 Success! Your CV has been generated:")
        print(f"   📁 Location: {theme_dir.absolute()}")
        print(f"   👤 User: {args.user_id}")
        print(f"   🎨 Theme: {args.theme}")
        print(f"\n   Files generated:")
        print(f"   📄 PDF: {cv_filename}_CV.pdf")
        print(f"   📝 Typst: {cv_filename}_CV.typ")
        print(f"   🌐 HTML: {cv_filename}_CV.html")
        print(f"   📊 Markdown: {cv_filename}_CV.md")
        print(f"   🖼️  PNG: {cv_filename}_CV_1.png, {cv_filename}_CV_2.png")
        sys.exit(0)
    else:
        print(f"\n❌ CV generation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
