# Building Blender on macOS (ARM64)

## System Information
- Architecture: ARM64 (Apple Silicon M1/M2/M3)
- OS: macOS
- CMake Version: 3.31.4 ✓

## Prerequisites ✓
- [x] Xcode Command Line Tools
- [x] CMake (via Homebrew)
- [x] Python 3

## Build Process

### Step 1: Download Dependencies
Blender needs pre-built libraries (Python, Boost, OpenImageIO, FFmpeg, etc.)

```bash
# Download both Blender updates and pre-built libraries
make update

# Or run the Python script directly:
python3 build_files/utils/make_update.py

# To only download libraries (if code is already up to date):
python3 build_files/utils/make_update.py --no-blender
```

**What this does:**
- Updates the git repository
- Downloads pre-built libraries to `lib/macos_arm64/`
- Sets up Git LFS for large files

**Time:** 5-15 minutes depending on internet speed

---

### Step 2: Build Blender

#### Option A: Quick Build (Recommended for first time)
```bash
make lite
```
- Minimal features
- Faster compilation (~20-40 mins)
- Good for testing if everything works

#### Option B: Full Development Build
```bash
make developer
```
- Includes tests and debugging tools
- Faster incremental builds
- Recommended for actual development

#### Option C: Full Feature Build
```bash
make full
```
- All features enabled
- Longer build time
- Most complete build

#### Option D: Release Build
```bash
make release
```
- Matches official Blender releases
- Includes CUDA, OptiX (if available)
- Production-quality build

### Speed Optimization
Combine these flags for faster builds:

```bash
# Fastest possible build for development
make lite developer ninja ccache

# Full featured but optimized for speed
make developer ninja ccache
```

**Build time estimates:**
- lite: 20-40 minutes (first build)
- full: 60-90 minutes (first build)
- Incremental builds: 1-5 minutes with ccache

---

### Step 3: Run Blender

After building, the binary is located at:
```
../build_darwin/bin/Blender.app/Contents/MacOS/Blender
```

Run it with:
```bash
# From the source directory
../build_darwin/bin/Blender.app/Contents/MacOS/Blender

# Or open the app bundle
open ../build_darwin/bin/Blender.app
```

---

## Build Directory Structure

```
gamedev/
├── blender/                    # Source code (this directory)
│   ├── source/
│   ├── scripts/
│   ├── lib/
│   │   └── macos_arm64/       # Pre-built libraries (after 'make update')
│   └── GNUmakefile
└── build_darwin/              # Build output (created automatically)
    ├── bin/
    │   └── Blender.app        # Built application
    ├── CMakeCache.txt
    └── [build artifacts]
```

You can override the build directory:
```bash
make BUILD_DIR=/path/to/custom/build
```

---

## Makefile Targets Cheat Sheet

### Building
```bash
make                # Basic build
make lite           # Minimal features
make full           # All features
make release        # Production build
make debug          # Debug build
make developer      # Developer build with tests
make bpy            # Build as Python module
make headless       # No GUI (server/render farm)
make cycles         # Cycles standalone only
```

### Build Tools
```bash
make ninja          # Use Ninja build system (faster)
make ccache         # Enable ccache (faster rebuilds)
```

### Utilities
```bash
make update         # Update code and libraries
make update_code    # Update only code (not libraries)
make clean          # Clean build directory
make config         # Open cmake configuration GUI
make test           # Run automated tests
make format         # Format code (clang-format, autopep8)
```

### Documentation
```bash
make doc_py         # Generate Python API docs
make doc_doxy       # Generate C/C++ docs (Doxygen)
make doc_man        # Generate man page
```

### Code Checking
```bash
make check_pep8           # Python style check
make check_spelling_c     # C/C++ spell check
make check_spelling_py    # Python spell check
```

---

## Troubleshooting

### Issue: "No libraries found"
**Solution:** Run `make update` to download dependencies

### Issue: Build fails with "command not found"
**Solution:** Install Xcode Command Line Tools:
```bash
xcode-select --install
```

### Issue: Out of disk space
**Solution:** Build directories can be large (20-50 GB). Clean old builds:
```bash
rm -rf ../build_darwin*
```

### Issue: Slow build
**Solution:** Use ninja and ccache:
```bash
brew install ninja ccache
make lite ninja ccache
```

### Issue: CMake errors
**Solution:** Delete CMake cache and reconfigure:
```bash
rm -rf ../build_darwin/CMakeCache.txt
make
```

---

## Next Steps After Building

1. **Run your build** - Test that everything works
2. **Make a small change** - Edit a UI string, rebuild, see your change
3. **Study the code** - Explore `source/blender/` 
4. **Build with tests** - `make developer test`
5. **Generate docs** - `make doc_py doc_doxy`

---

## Resources

- [Official Build Instructions](https://developer.blender.org/docs/handbook/building_blender/)
- [Developer Portal](https://developer.blender.org/docs/)
- [Code Review](https://projects.blender.org)
- [Dev Forum](https://devtalk.blender.org)

---

## Build Log

### First Build Attempt
- Date: October 5, 2025
- Command: `make developer ninja`
- Status: ✅ **SUCCESS**
- Build Type: Developer mode with Ninja
- Notes: 
  - Required manual clone of lib-macos_arm64 repository (~973 MB)
  - Needed to restore Git LFS files with `git checkout HEAD -- release/datafiles/`
  - Build configuration automatically detected ARM64 architecture
  - Total configuration time: ~9 seconds
  - Binary location: `../build_darwin/bin/Blender.app`
  - Successfully launches and runs!

### Troubleshooting Steps Taken
1. **Missing Ninja**: Installed via `brew install ninja`
2. **Missing dependencies**: Manually cloned lib-macos_arm64 submodule
3. **Missing LFS files**: Restored release datafiles with git checkout

### Quick Rebuild Commands
After making code changes:
```bash
# Incremental build (only changed files)
make developer ninja

# Clean build (if needed)
rm -rf ../build_darwin
make developer ninja
```

