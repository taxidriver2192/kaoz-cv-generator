# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kaoz CV Generator is a Python CLI tool that converts Kaoz.dk JSON profiles into professional CV PDFs using RenderCV. The tool supports 5 professional themes and outputs multiple formats (PDF, Typst, Markdown, HTML, PNG).

## Common Commands

### Installation & Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python generate_cv.py --help
```

### Generate CVs
```bash
# Basic generation with default theme (sb2nov)
python generate_cv.py --input test_data/lukas_profile.json --user-id 123

# With specific theme
python generate_cv.py --input test_data/lukas_profile.json --user-id 123 --theme classic

# Debug mode (keeps temporary YAML file)
python generate_cv.py --input test_data/lukas_profile.json --user-id 123 --debug

# Custom base output directory
python generate_cv.py --input profile.json --user-id 456 --base-output-dir my_cvs

# Generate all themes for a user
for theme in classic sb2nov engineeringresumes moderncv engineeringclassic; do
    python generate_cv.py --input test_data/lukas_profile.json --user-id 123 --theme $theme
done

# Multiple users
python generate_cv.py --input user_123.json --user-id 123 --theme classic
python generate_cv.py --input user_456.json --user-id 456 --theme sb2nov
```

### Testing Converter Standalone
```bash
# Test converter module directly
python converter.py test_data/lukas_profile.json
```

## Architecture

### Two-Module Design

1. **generate_cv.py** - CLI orchestrator
   - Parses command-line arguments (user-id, theme, input file)
   - Validates RenderCV installation
   - Loads JSON input
   - Manages folder structure: `output/{user_id}/{theme}/`
   - Auto-cleanup: Removes old theme versions before generating new ones
   - Manages temporary YAML files
   - Calls RenderCV via subprocess
   - Handles output and error reporting

2. **converter.py** - Core conversion logic
   - `convert_kaoz_to_rendercv()`: Main conversion function that maps Kaoz.dk JSON structure to RenderCV YAML format
   - `parse_date()`: Converts ISO date strings to RenderCV format (YYYY-MM or "present")
   - `split_summary_to_highlights()`: Intelligently breaks long summaries into bullet points
   - `save_as_yaml()`: Exports CV data to YAML file

### Data Flow

```
Kaoz.dk JSON → converter.py → RenderCV YAML → RenderCV CLI → PDF/Typst/MD/HTML/PNG
                                                                 ↓
                                                    output/{user_id}/{theme}/
```

### Folder Structure

The tool organizes output by user and theme for easy integration with Laravel:

```
output/
  {user_id}/           # User identifier (e.g., 123, 456)
    {theme}/           # Theme name (sb2nov, classic, etc.)
      Name_CV.pdf
      Name_CV.typ
      Name_CV.html
      Name_CV.md
      Name_CV_1.png
      Name_CV_2.png
```

**Auto-Cleanup**: When regenerating a CV with the same user_id and theme, the old version is automatically deleted before creating the new one. This ensures users always have the latest version without manual cleanup.

### JSON to YAML Mapping

The converter maps Kaoz.dk profile structure to RenderCV format:
- `profile.name/email/location` → `cv.name/email/location`
- `profile.headline` → `cv.sections.summary`
- `profile.linkedin_url/github_url` → `cv.social_networks`
- `professional_experience[]` → `cv.sections.experience[]`
  - `title` → `position`
  - `company` → `company`
  - `start_date/end_date` → parsed to YYYY-MM format
  - `summary` → split into `highlights[]` (bullet points)
- `education[]` → `cv.sections.education[]`
  - Extracts degree type and area from "Degree in Area" format
  - `school` → `institution`
  - `start_year/end_year` → converted to strings
- `skills.programming_languages/frameworks_libraries/other_skills` → `cv.sections.technologies[]`
  - Groups skills into "Programming Languages", "Frameworks & Libraries", "Tools & Technologies"
  - Limits "other_skills" to top 10 to avoid overcrowding

### Key Design Decisions

**User-Based Folder Structure**: Organizes output as `output/{user_id}/{theme}/` for easy integration with Laravel apps. Each user can have multiple themes, and files are easily accessible by combining user_id and theme.

**Auto-Cleanup**: Before generating a new CV, the tool automatically deletes any existing files in the same `{user_id}/{theme}/` directory using `shutil.rmtree()`. This prevents stale files and ensures users always have the latest version.

**Temporary File Handling**: In non-debug mode, generates a temporary YAML file that's automatically deleted after RenderCV processes it. In debug mode, saves as `output/{user_id}/debug_{theme}_cv_data.yaml` for inspection.

**Date Parsing**: Uses python-dateutil for flexible ISO date parsing. Empty or missing dates become "present" for current positions.

**Summary to Highlights**: Long summaries are intelligently split at sentence boundaries to create readable bullet points (max 150 chars each).

**Phone Number Omission**: Phone numbers are intentionally skipped due to RenderCV's strict phone validation. Users can add manually to the generated CV if needed.

**Skills Limitation**: Only top 10 "other_skills" are included to prevent overcrowding the CV.

## Available Themes

- **sb2nov** (default) - Modern, clean design recommended for tech roles
- **classic** - Traditional academic style
- **engineeringresumes** - Optimized for engineers/developers
- **moderncv** - Modern corporate style
- **engineeringclassic** - Classic engineering style

## Dependencies

- `rendercv[full]>=2.3` - Core CV generation engine (includes TinyTeX for PDF)
- `pyyaml>=6.0` - YAML file handling
- `python-dateutil>=2.8` - Flexible date parsing

## Output Files

All generated in `output/{user_id}/{theme}/`:
- `{Name}_CV.pdf` - Main CV in PDF format
- `{Name}_CV.typ` - Typst source code
- `{Name}_CV.md` - Markdown version
- `{Name}_CV.html` - HTML version
- `{Name}_CV_1.png`, `{Name}_CV_2.png` - PNG preview images (one per page)

### Laravel Integration

The folder structure makes it easy to access CV files from Laravel:
```php
// Get PDF path for a user and theme
$pdfPath = storage_path("app/cv-output/{$userId}/{$theme}/{$name}_CV.pdf");

// List all themes for a user
$themes = Storage::directories("cv-output/{$userId}");

// Check if a CV exists
$exists = Storage::exists("cv-output/{$userId}/{$theme}/{$name}_CV.pdf");
```

## Testing

Test data is in `test_data/lukas_profile.json` - a complete example Kaoz.dk profile with:
- Professional experience entries
- Education history
- Skills categorized by type
- Social network URLs

## Language & Internationalization

The codebase is written in English but designed to handle Danish text:
- All files use UTF-8 encoding
- Supports Danish special characters (æ, ø, å)
- CLI output messages are in Danish with emoji indicators
- Sample data and README are in Danish

## Error Handling

The CLI provides clear error messages:
- Missing RenderCV installation
- Invalid JSON format
- File not found
- RenderCV processing errors

All errors include emoji prefixes (❌) and actionable guidance.
