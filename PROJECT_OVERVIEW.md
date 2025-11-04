# Project Overview: Classroom Temperature Monitoring System

## Quick Links

- **For End Users (Teachers)**: See [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)
- **For Developers**: See [ARCHITECTURE.md](ARCHITECTURE.md) and [docs/classroom_temp_spec.md](docs/classroom_temp_spec.md)
- **Quick Start**: See [README.md](README.md)
- **Usage Examples**: See [USAGE.md](USAGE.md)

## What is This?

A complete temperature monitoring system for classrooms using BBC micro:bit hardware. Teachers can:
- Track classroom temperature trends over time
- Share data publicly via secure links
- Export data for analysis
- View historical patterns

## System Components

### 1. Hardware
- **BBC micro:bit**: Temperature sensor (any version)
- **USB Cable**: For power and data connection
- **Computer**: Running the host script (Windows/Mac/Linux)

### 2. Software
- **micro:bit Code** (`microbit/main.py`): MicroPython script for temperature reading
- **Host Script** (`src/host_script.py`): Python 3.7+ application for data collection and upload
- **Anvil Web App**: Cloud-hosted dashboard (not in this repo)

### 3. Data Flow

```
micro:bit → USB Serial → Host Script → Internet → Anvil Web App → Dashboard
  (30s)      (115200)     (20min avg)   (HTTPS)    (Database)     (Charts)
```

## Repository Structure

```
.
├── src/                      # Host application source
│   ├── host_script.py        # Main Python script
│   ├── config.txt            # Configuration template
│   └── README.md
├── microbit/                 # micro:bit firmware
│   ├── main.py               # MicroPython code
│   └── README.md
├── docs/                     # Documentation
│   ├── classroom_temp_spec.md   # Complete technical specification
│   ├── SETUP_GUIDE.md           # User setup instructions
│   └── README.md
├── vendor/                   # Bundled Python dependencies
│   ├── serial/               # pyserial for USB communication
│   ├── requests/             # HTTP client
│   └── ...
├── .github/
│   ├── workflows/build.yml   # CI/CD automation
│   └── copilot/              # GitHub Copilot instructions
├── build.py                  # Build script for distribution
├── vendor_dependencies.py    # Dependency management
├── requirements.txt          # Python dependencies list
├── README.md                 # Main project documentation
├── ARCHITECTURE.md           # System architecture details
└── USAGE.md                  # Usage examples and troubleshooting
```

## Key Features

### For Users
- ✅ **Simple Setup**: Extract ZIP, edit config, run script
- ✅ **No Installation**: All dependencies bundled (pure Python)
- ✅ **Cross-Platform**: Works on Windows, macOS, Linux
- ✅ **Automatic Recovery**: Retries failed uploads, caches offline data
- ✅ **Calibration**: Adjustable temperature offset for accuracy

### For Developers
- ✅ **Pure Python**: No compiled modules, easy deployment
- ✅ **Automated Builds**: GitHub Actions creates distribution ZIPs
- ✅ **Validated**: CI ensures no compiled dependencies
- ✅ **Well Documented**: Comprehensive technical specification
- ✅ **Modular Design**: Clear separation of concerns

## Technology Stack

### micro:bit
- **Language**: MicroPython
- **IDE**: MakeCode, Thonny, or mu editor
- **Communication**: USB Serial (115200 baud)

### Host Script
- **Language**: Python 3.7+
- **Dependencies**: pyserial, requests (vendored)
- **Platform**: Cross-platform (Windows/Mac/Linux)

### Web Application
- **Platform**: Anvil (Python-based web framework)
- **Database**: Anvil Data Tables
- **API**: RESTful HTTP endpoints
- **Frontend**: Plotly charts, responsive design

## Development Workflow

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/h-arnold/Itstoogoddamcoldinmyclassroom.co.uk.git
cd Itstoogoddamcoldinmyclassroom.co.uk

# Install dependencies
python3 vendor_dependencies.py

# Build distribution
python3 build.py
```

### Making Changes

1. **Edit source files** in `src/` or `microbit/`
2. **Test locally** with a connected micro:bit
3. **Update documentation** as needed
4. **Run build** to verify no compiled modules
5. **Commit and push** - CI will validate automatically

### Release Process

1. **Tag release**: `git tag v1.0.0`
2. **Push tag**: `git push origin v1.0.0`
3. **GitHub Actions** automatically builds and creates release
4. **Download artifact** from Actions page
5. **Distribute** ZIP to users

## Security

- ✅ API keys stored locally, never in repository
- ✅ HTTPS for all web communication
- ✅ Rate limiting on server side
- ✅ No personal data collected
- ✅ Share links use UUID tokens (122-bit entropy)

## Support and Contributing

### Getting Help
- Check [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) troubleshooting section
- Review [USAGE.md](USAGE.md) for examples
- Open an issue on GitHub
- Check existing issues for solutions

### Contributing
- Read the technical specification
- Follow existing code style
- Test thoroughly before submitting
- Update documentation with changes
- Ensure CI passes (no compiled modules)

## License

MIT License - See LICENSE file for details

## Project Status

🟢 **Active Development**

Current Version: 1.0.0 (Initial Release)

### Completed
- ✅ Core host script functionality
- ✅ micro:bit MicroPython code
- ✅ Build system and vendoring
- ✅ GitHub Actions CI/CD
- ✅ Comprehensive documentation
- ✅ Cross-platform support

### Planned
- 🔄 Anvil web application deployment
- 🔄 Teacher accounts and dashboard
- 🔄 Data visualization and export
- 🔄 Share link functionality
- 🔄 Mobile-responsive interface

## Contact

- **Repository**: [github.com/h-arnold/Itstoogoddamcoldinmyclassroom.co.uk](https://github.com/h-arnold/Itstoogoddamcoldinmyclassroom.co.uk)
- **Issues**: [GitHub Issues](https://github.com/h-arnold/Itstoogoddamcoldinmyclassroom.co.uk/issues)
- **Website**: itstoodamncoldinmyclassroom.co.uk (pending deployment)

---

**Last Updated**: 2025-11-04  
**Documentation Version**: 1.0
