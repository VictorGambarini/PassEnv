# PassEnv

Load environment variables from [pass](https://www.passwordstore.org/) entries seamlessly in your shell.

## Features

- **Secure**: Leverages the existing `pass` password manager
- **Simple**: Load/unload environment variables with a single command
- **Stateful**: Tracks what's loaded and prevents conflicts
- **Auto-completion**: Tab completion for pass entries
- **Shell Integration**: Works with bash, zsh, fish, and more

## Installation

### Prerequisites

- [pass](https://www.passwordstore.org/) must be installed and initialized
- Python 3.10 or higher

### Install from PyPI

```bash
pip install passenv
```

### Or install with pipx to have it globally accessible

```bash
pipx install passenv
```

### Set up shell integration

After installation, run the setup command:

```bash
passenv install
```

This will add the necessary shell function and completion to your `~/.bashrc`, `~/.zshrc`, or specific shell rc file.

## Usage

### Basic Commands

```bash
# Load environment variables from a pass entry at database/envs
passenv load database/envs

# Check what's currently loaded
passenv status

# List available pass entries
passenv list

# Unload current environment
passenv unload

# Export as .env format (default)
passenv export database/envs
```

### Pass Entry Format

Store your environment variables in pass entries using the `KEY=VALUE` format:

```bash
# Create a pass entry
pass edit database/envs
```

Example entry content:
```
DATABASE_URL=postgres://user:pass@localhost/mydb
API_KEY=secret123
DEBUG=false
# This is a comment
LOG_LEVEL=info
```

### Advanced Usage

#### Environment Isolation

PassEnv automatically handles environment isolation:

- Loading a new set of environment variables automatically unloads the previous ones
- Tracks which variables were loaded to prevent conflicts
- Provides clear status information

## Examples

### Development Workflow

```bash
# Load development environment
passenv load myapp/development

# Run your application
python manage.py runserver

# Switch to staging environment
passenv load myapp/staging

# Deploy to staging
./deploy.sh

# Clean up
passenv unload
```

### Basic Export Usage

```bash
# Export as .env format (default)
passenv export database/envs

# Export to different formats
passenv export database/envs --format yaml
passenv export database/envs --format json
passenv export database/envs --format csv
passenv export database/envs --format docker

# Save to file
passenv export database/envs --output .env
passenv export database/envs --format yaml --output config.yaml
```

### Export Formats

#### .env format (default)
```bash
passenv export myapp/production
```
Output:
```
DATABASE_URL=postgres://user:pass@localhost/mydb
API_KEY=secret123
DEBUG=false
LOG_LEVEL=info
```

#### YAML format
```bash
passenv export myapp/production --format yaml
```
Output:
```yaml
DATABASE_URL: postgres://user:pass@localhost/mydb
API_KEY: secret123
DEBUG: "false"
LOG_LEVEL: info
```

#### JSON format
```bash
passenv export myapp/production --format json
```
Output:
```json
{
  "DATABASE_URL": "postgres://user:pass@localhost/mydb",
  "API_KEY": "secret123", 
  "DEBUG": "false",
  "LOG_LEVEL": "info"
}
```

#### CSV format
```bash
passenv export myapp/production --format csv
```
Output:
```csv
KEY,VALUE
DATABASE_URL,postgres://user:pass@localhost/mydb
API_KEY,secret123
DEBUG,false
LOG_LEVEL,info
```

#### Docker format
```bash
passenv export myapp/production --format docker
```
Output:
```
-e DATABASE_URL="postgres://user:pass@localhost/mydb" -e API_KEY="secret123" -e DEBUG="false" -e LOG_LEVEL="info"
```

### Docker Integration Examples

```bash
# Export and use directly with docker run
docker run $(passenv export myapp/production --format docker) my-app:latest

# Save to file and use with docker-compose
passenv export myapp/production --output .env
docker-compose up

# Use with Kubernetes ConfigMap
passenv export myapp/production --format yaml --output configmap.yaml
kubectl create configmap app-config --from-file=configmap.yaml
```

### Pass Entry Organization Suggestion

Organize your pass entries logically:

```
myapp/
├── development
├── staging
└── production

database/
├── local
├── staging
└── production
```

### Environment Variable Format

- **Comments**: Lines starting with `#` are ignored
- **Empty lines**: Skipped automatically
- **Format**: `KEY=VALUE` (spaces around `=` are stripped)
- **Quotes**: Optional quotes around values are removed
- **Variable names**: Must be valid shell variable names (`[A-Za-z_][A-Za-z0-9_]*`)

## Troubleshooting

### Common Issues

**Pass not found**
```
Error: 'pass' command not found. Please install pass.
```
Install pass using your package manager:
```bash
# Ubuntu/Debian
sudo apt install pass

# macOS
brew install pass

# Arch Linux
sudo pacman -S pass
```

**Pass not initialized**
```
Error: Pass store not initialized.
```
Initialize your pass store:
```bash
pass init your-gpg-key-id
```

**Entry not found**
```
Error: Pass entry 'myapp/staging' not found.
```
Create the entry:
```bash
pass edit myapp/staging
```

**Invalid variable format**
```
Error: Invalid line 'malformed-line' in pass entry.
```
Check your pass entry format. Each line should be `KEY=VALUE` or a comment.

### Getting Help

```bash
# Show help
passenv --help

# Show command-specific help
passenv load --help
```

## Development

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/passenv.git
cd passenv

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=passenv

# Run specific test file
pytest tests/test_parser.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Related Projects

- [pass](https://www.passwordstore.org/) - The password manager this tool integrates with
