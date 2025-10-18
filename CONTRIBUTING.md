# Contributing to Automated NHL Post-Game Reports

Thank you for your interest in contributing to our NHL post-game reports project! We welcome contributions from the hockey analytics community.

## 🤝 How to Contribute

### Reporting Issues
- Use the [GitHub Issues](https://github.com/yourusername/automated-post-game-reports/issues) page
- Include detailed descriptions of the problem
- Provide steps to reproduce the issue
- Include system information and error messages

### Suggesting Features
- Open a new issue with the "enhancement" label
- Describe the feature and its benefits
- Include mockups or examples if applicable

### Code Contributions
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 🏗️ Development Setup

### Prerequisites
- Python 3.8+
- pip package manager
- Git

### Local Development
```bash
# Clone your fork
git clone https://github.com/yourusername/automated-post-game-reports.git
cd automated-post-game-reports

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r src/requirements.txt

# Install development dependencies
pip install -r src/requirements-dev.txt
```

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src

# Run specific test file
python -m pytest tests/test_comprehensive_report.py
```

## 📝 Code Style Guidelines

### Python Code
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions focused and under 50 lines when possible

### Example Function
```python
def generate_shot_chart(team_data: dict, rink_dimensions: tuple) -> str:
    """
    Generate a professional shot chart for the given team data.
    
    Args:
        team_data: Dictionary containing team shot information
        rink_dimensions: Tuple of (length, width) for rink size
        
    Returns:
        str: Path to the generated chart file
        
    Raises:
        ValueError: If team_data is empty or invalid
    """
    if not team_data:
        raise ValueError("Team data cannot be empty")
    
    # Implementation here
    return chart_file_path
```

### Commit Messages
- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, Remove, etc.)
- Keep the first line under 50 characters
- Add detailed description if needed

**Good examples:**
- `Add realistic shot positioning algorithm`
- `Fix NHL API endpoint URL formatting`
- `Update PDF table styling for better readability`

**Avoid:**
- `Fixed stuff`
- `Updated things`
- `WIP`

## 🧪 Testing Guidelines

### Test Coverage
- Aim for at least 80% test coverage
- Test both success and failure scenarios
- Mock external API calls
- Test edge cases and error conditions

### Test Structure
```python
import pytest
from unittest.mock import patch, MagicMock
from src.comprehensive_report import create_comprehensive_report

class TestComprehensiveReport:
    """Test cases for comprehensive report generation."""
    
    def test_create_report_with_valid_game_id(self):
        """Test report creation with valid game ID."""
        with patch('src.comprehensive_report.get_nhl_game_data') as mock_api:
            mock_api.return_value = {'feed_live': {'game': {'awayTeam': {'abbrev': 'EDM'}}}}
            result = create_comprehensive_report('2024030416')
            assert result is not None
    
    def test_create_report_with_invalid_game_id(self):
        """Test report creation with invalid game ID."""
        with patch('src.comprehensive_report.get_nhl_game_data') as mock_api:
            mock_api.return_value = {}
            result = create_comprehensive_report('invalid_id')
            assert 'sample' in result.lower()
```

## 📚 Documentation

### Code Documentation
- All public functions and classes must have docstrings
- Use Google-style docstring format
- Include examples for complex functions
- Document all parameters and return values

### README Updates
- Update README.md when adding new features
- Include usage examples
- Update installation instructions if dependencies change
- Add screenshots or examples for new visualizations

## 🔒 Security

### API Keys and Credentials
- Never commit API keys or credentials
- Use environment variables for sensitive data
- Add new environment variables to `.env.example`
- Document required environment variables

### Data Handling
- Validate all input data
- Sanitize user inputs
- Handle API rate limits gracefully
- Log errors without exposing sensitive information

## 🚀 Release Process

### Versioning
- Use [Semantic Versioning](https://semver.org/)
- Update version in `__init__.py` and documentation
- Create release notes for each version

### Release Checklist
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Version numbers are updated
- [ ] Release notes are written
- [ ] GitHub release is created
- [ ] PyPI package is updated (if applicable)

## 📞 Getting Help

- **Issues**: Use GitHub Issues for bugs and feature requests
- **Discussions**: Join GitHub Discussions for general questions
- **Wiki**: Check our Wiki for detailed documentation
- **Email**: Contact maintainers for urgent issues

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- GitHub contributors page
- Release notes
- Project documentation

Thank you for contributing to the hockey analytics community! 🏒
