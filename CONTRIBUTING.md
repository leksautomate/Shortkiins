# Contributing to Video Generator Pipeline

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. Fork and clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Project Structure

```
Shortkiins/
├── main.py              # Main pipeline orchestrator
├── config.py            # Configuration management
├── modules/             # Core modules
│   ├── tts.py          # Text-to-speech
│   ├── subtitles.py    # Subtitle generation
│   ├── scene_division.py # Script segmentation
│   ├── image_gen.py    # Image generation
│   ├── video_effects.py # Video effects
│   └── assembler.py    # Final assembly
└── examples/           # Example scripts
```

## Adding New Features

### Adding a New Image Provider

1. Create a new class in `modules/image_gen.py` that inherits from `ImageGenerator`
2. Implement the `generate()` method
3. Add configuration options in `config.py`
4. Update the README with usage instructions

Example:
```python
class NewProviderGenerator(ImageGenerator):
    def generate(self, prompt: str, output_path: Path) -> Path:
        # Implementation here
        pass
```

### Adding New Video Effects

1. Add effect function in `modules/video_effects.py`
2. Update `create_video_clip()` to support the new effect
3. Add documentation

Example:
```python
def new_effect(get_frame, t):
    """Create a new effect."""
    # Implementation here
    pass
```

## Code Style

- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Add docstrings for all public functions and classes
- Keep functions focused and modular

## Testing

Before submitting a pull request:

1. Test with the sample script:
   ```bash
   bash examples/quickstart.sh
   ```

2. Test with different providers and settings

3. Ensure no errors in logs

## Pull Request Process

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "Add: description of your changes"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Open a pull request with:
   - Clear description of changes
   - Screenshots/videos if applicable
   - Any breaking changes noted

## Reporting Bugs

Open an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error logs if applicable

## Feature Requests

Open an issue with:
- Clear description of the feature
- Use case / motivation
- Proposed implementation (if any)

## Questions?

Feel free to open an issue for any questions about contributing!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
