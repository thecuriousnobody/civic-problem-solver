# Contributing to Civic Problem Solver

Thank you for your interest in contributing to Civic Problem Solver! This project aims to make civic resources accessible through AI-powered assistance. We welcome contributions from developers, civic technologists, community organizers, and anyone passionate about helping people access local resources.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Ways to Contribute](#ways-to-contribute)
- [Development Setup](#development-setup)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Community](#community)

## Code of Conduct

This project serves vulnerable populations seeking help. We maintain a welcoming, inclusive, and respectful environment for all contributors. Please be kind, patient, and constructive in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/civic-problem-solver.git
   cd civic-problem-solver
   ```
3. **Set up the development environment** (see [Development Setup](#development-setup))
4. **Look for good first issues** labeled `good-first-issue` or `help-wanted`

## Ways to Contribute

### 🐛 Bug Reports
Found something broken? Help us fix it:
- Search existing issues first
- Include steps to reproduce
- Provide system information (OS, Python/Node versions)
- Include error messages and logs

### ✨ Feature Requests
Have an idea for improvement?
- Check if it's already been suggested
- Describe the problem it solves
- Consider community impact and scalability
- Provide implementation ideas if possible

### 📖 Documentation
Help others understand and use the system:
- Fix typos or unclear instructions
- Add examples or tutorials
- Translate documentation
- Improve setup guides

### 🌍 Localization
Adapt the system for your community:
- Add local resource databases
- Update geographic boundaries
- Translate user-facing text
- Share deployment guides

### 🧪 Testing
Ensure quality across environments:
- Write unit tests for new features
- Test on different operating systems
- Validate with real civic resource scenarios
- Performance testing and optimization

## Development Setup

### Prerequisites
- Python 3.8+ with pip
- Node.js 18+ with npm
- Git

### Backend Setup
```bash
cd api
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env with your API keys
python civic_api_v2.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Running Tests
```bash
# Backend tests
cd api
python -m pytest

# Frontend tests
cd frontend
npm test

# System integration tests
python quick_domain_test.py
```

## Submitting Changes

### Pull Request Process

1. **Create a feature branch** from main:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** with clear, focused commits:
   ```bash
   git commit -m "feat: add housing resource validation
   
   - Implement URL validation for housing resources
   - Add error handling for broken links
   - Include unit tests for validation logic"
   ```

3. **Test thoroughly**:
   - Run all existing tests
   - Add tests for new functionality
   - Test manually with realistic scenarios

4. **Push to your fork** and create a pull request:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Describe your changes** in the PR:
   - What problem does this solve?
   - How did you test it?
   - Any breaking changes?
   - Screenshots for UI changes

### Review Process

- All PRs require review from maintainers
- We may request changes or improvements
- Once approved, maintainers will merge your PR
- Large changes benefit from discussion in issues first

## Coding Standards

### Python (Backend)
- Follow PEP 8 style guidelines
- Use type hints for function parameters and returns
- Include docstrings for modules, classes, and functions
- Write unit tests for new functionality
- Use meaningful variable and function names

```python
def validate_resource_url(url: str) -> bool:
    """Validate that a civic resource URL is accessible.
    
    Args:
        url: The URL to validate
        
    Returns:
        True if URL is accessible, False otherwise
    """
    # Implementation here
```

### TypeScript/React (Frontend)
- Use TypeScript strict mode
- Follow React best practices and hooks patterns
- Use meaningful component and variable names
- Include JSDoc comments for complex logic
- Write unit tests for components and utilities

```typescript
interface Resource {
  name: string;
  category: string;
  url?: string;
  contact?: string;
}

/**
 * Validates civic resource data integrity
 */
const validateResource = (resource: Resource): boolean => {
  // Implementation here
};
```

### AI Agent Development
- Document agent roles and capabilities clearly
- Include reasoning for prompt design choices
- Test with diverse, realistic user inputs
- Consider edge cases and error handling

## Community

### Live Development Sessions
We build in public during Peoria AI Collective meetings:
- **When**: First Wednesday of each month, 6 PM CT
- **Where**: Join our [Slack workspace](https://the-aicollective.slack.com)
- **What**: Live coding, design discussions, community feedback

### Communication Channels
- **GitHub Issues**: Bug reports, feature requests, technical discussion
- **GitHub Discussions**: General questions, ideas, community showcase
- **Slack**: Real-time chat, coordination, community building

### Recognition

Contributors will be:
- Listed in our README acknowledgments
- Credited in release notes for significant contributions
- Invited to join our community calls and planning sessions

## Questions?

- Check our [README](README.md) for basic information
- Search [existing issues](https://github.com/thecuriousnobody/civic-problem-solver/issues)
- Join our [Slack workspace](https://the-aicollective.slack.com)
- Attend a community meeting

---

**Remember**: This is civic infrastructure, not a startup. We optimize for community benefit, accessibility, and replicability. Every contribution helps people in your community and communities around the world access the help they need.

Thank you for contributing! 🌟