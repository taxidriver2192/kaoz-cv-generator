# 🚀 Kaoz CV Generator

Konverter din Kaoz.dk JSON profil til professionelt CV i PDF format via RenderCV.

## Features

- ✅ Konverter Kaoz.dk JSON profil automatisk til CV
- ✅ 5 professionelle temaer (sb2nov, classic, engineeringresumes, moderncv, engineeringclassic)
- ✅ Genererer PDF + Typst + Markdown + HTML + PNG
- ✅ CLI interface - let at bruge
- ✅ Supports dansk tekst og special characters

## Installation

### Prerequisites
- Python 3.10 eller nyere
- pip

### Setup

```bash
# Clone repo
git clone https://github.com/taxidriver2192/kaoz-cv-generator.git
cd kaoz-cv-generator

# Install dependencies
pip install -r requirements.txt

# Verify installation
python generate_cv.py --help
```

## Brug

### Basic Usage

```bash
# Simpel generering med default tema (sb2nov)
python generate_cv.py --input test_data/lukas_profile.json --user-id 123

# Med specifikt tema
python generate_cv.py --input profile.json --user-id 123 --theme classic
```

### Advanced Usage

```bash
# Generer flere forskellige temaer for samme bruger
python generate_cv.py --input profile.json --user-id 456 --theme sb2nov
python generate_cv.py --input profile.json --user-id 456 --theme classic

# Custom base output directory
python generate_cv.py --input profile.json --user-id 789 --base-output-dir my_cvs

# Debug mode (behold temp YAML fil)
python generate_cv.py --input profile.json --user-id 123 --debug
```

### Folder Struktur

CVs gemmes i følgende struktur:
```
output/
  {user_id}/
    {theme}/
      Navn_Navnesen_CV.pdf
      Navn_Navnesen_CV.typ
      Navn_Navnesen_CV.html
      Navn_Navnesen_CV.md
      Navn_Navnesen_CV_1.png
      Navn_Navnesen_CV_2.png
```

Eksempel: `output/123/sb2nov/Lukas_Schmidt_CV.pdf`

**Vigtig:** Når du genererer samme tema igen for en bruger, slettes den gamle version automatisk.

### Tilgængelige Temaer

- **sb2nov** - Modern, clean design (anbefalet til tech)
- **classic** - Klassisk akademisk stil
- **engineeringresumes** - Optimeret til ingeniører/developers
- **moderncv** - Moderne corporate stil
- **engineeringclassic** - Klassisk engineering stil

## Input Format

Scriptet forventer en JSON fil med følgende struktur fra Kaoz.dk:

```json
{
  "profile": {
    "name": "Navn Navnesen",
    "email": "email@example.com",
    "headline": "Job titel / beskrivelse",
    "location": "By"
  },
  "professional_experience": [
    {
      "title": "Job titel",
      "company": "Firma navn",
      "summary": "Beskrivelse af arbejde",
      "location": "By, Land",
      "start_date": "2023-01-01T00:00:00.000Z",
      "end_date": "",
      "skills": []
    }
  ],
  "education": [
    {
      "school": "Skole navn",
      "degree": "Uddannelse",
      "summary": "Beskrivelse",
      "start_year": 2019,
      "end_year": 2021
    }
  ],
  "skills": {
    "programming_languages": ["PHP", "JavaScript", "Python"],
    "frameworks_libraries": ["Laravel", "Vue", "React"],
    "other_skills": ["Docker", "AWS", "Git"]
  }
}
```

## Output

Genererer følgende filer i `output/{user_id}/{theme}/` mappen:

- `Navn_Navnesen_CV.pdf` - Din CV i PDF format
- `Navn_Navnesen_CV.typ` - Typst source code
- `Navn_Navnesen_CV.md` - Markdown version
- `Navn_Navnesen_CV.html` - HTML version
- `Navn_Navnesen_CV_1.png` - PNG preview af første side
- `Navn_Navnesen_CV_2.png` - PNG preview af anden side (hvis CV er >1 side)

## CLI Options

```
--input, -i          Path til JSON profil fil (required)
--user-id, -u        User ID for at organisere output per bruger (required)
--theme, -t          CV tema (default: sb2nov)
--base-output-dir    Base output directory (default: output)
--debug, -d          Debug mode - behold temp YAML fil
--help, -h           Vis hjælp
```

## Examples

```bash
# Test med sample data
python generate_cv.py --input test_data/lukas_profile.json --user-id 123

# Generer alle temaer for en bruger
for theme in classic sb2nov engineeringresumes moderncv engineeringclassic; do
    python generate_cv.py --input test_data/lukas_profile.json --user-id 123 --theme $theme
done

# Debug - se genereret YAML
python generate_cv.py --input test_data/lukas_profile.json --user-id 123 --theme sb2nov --debug
cat output/123/debug_sb2nov_cv_data.yaml

# Multiple brugere
python generate_cv.py --input user_123.json --user-id 123 --theme classic
python generate_cv.py --input user_456.json --user-id 456 --theme sb2nov
```

## Troubleshooting

### RenderCV ikke fundet
```bash
# Geninstaller dependencies
pip install -r requirements.txt --force-reinstall
```

### PDF generation fejler
```bash
# Check at TinyTeX er installeret (required for PDF)
rendercv new "Test"
rendercv render Test_CV.yaml
```

### Encoding errors med danske tegn
- Sørg for at JSON filen er UTF-8 encoded
- Check at Python 3.10+ bruges

## Contributing

Pull requests er velkomne! For større ændringer, åbn venligst et issue først.

## License

MIT

## Credits

Bygget med [RenderCV](https://github.com/rendercv/rendercv) - Version-control CVs as source code.
