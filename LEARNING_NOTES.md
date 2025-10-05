# Blender Learning Notes

Personal documentation for learning Blender's internals.

## Build Instructions for Mac

### Quick Start
```bash
# Simple build (in the blender directory)
make

# Build with specific configurations
make lite          # Minimal build, faster
make full          # All features enabled
make release       # Production build (like official releases)
make developer     # Recommended for development (faster builds, tests)
make ninja         # Use ninja instead of make (faster)
make ccache        # Use ccache for faster rebuilds

# Combine options (processed right to left)
make lite ninja ccache   # Fast, minimal build with caching
```

### Build Output
- **Build Directory**: `../build_darwin` (one level up from source)
- **Binary Location**: `../build_darwin/bin/Blender.app/Contents/MacOS/Blender`
- **Architecture**: Automatically detects (arm64 for M1/M2, x64 for Intel)

### Prerequisites
You'll need to install:
- **Xcode Command Line Tools**: `xcode-select --install`
- **CMake**: `brew install cmake`
- **Dependencies**: Blender expects pre-built libraries in `lib/macos_arm64` or `lib/macos_x64`

### Official Documentation
- [Build Instructions](https://developer.blender.org/docs/handbook/building_blender/)
- [Developer Docs](https://developer.blender.org/docs/)
- [Code Review & Bugs](https://projects.blender.org)

---

## Project Structure

```
blender/
├── source/          # Main C/C++ source code
│   ├── blender/     # Core Blender code
│   │   ├── blenkernel/    # Kernel functions
│   │   ├── blenlib/       # Utility library
│   │   ├── editors/       # UI editors
│   │   ├── render/        # Rendering engine
│   │   └── ...
│   └── creator/     # Application entry point
├── intern/          # Internal libraries
│   ├── cycles/      # Cycles render engine
│   ├── ghost/       # Platform abstraction layer
│   └── ...
├── extern/          # External dependencies
├── scripts/         # Python scripts
├── release/         # Release files, icons, etc.
├── build_files/     # Build configuration
└── doc/             # Official documentation
```

---

## Learning Path

### Phase 1: Building & Running ✓
- [x] Install prerequisites (CMake, Ninja)
- [x] Download/verify dependencies (lib/macos_arm64)
- [x] Build Blender (`make developer ninja`)
- [x] Run the built binary
- [x] Verify it works ✨

### Phase 2: Code Exploration
- [ ] Understand the startup flow (source/creator)
- [ ] Explore blenkernel (core data structures)
- [ ] Study the RNA/DNA system (Blender's reflection system)
- [ ] Look at how operators work

### Phase 3: Making Changes
- [ ] Make a trivial UI change
- [ ] Add a simple operator
- [ ] Modify render settings
- [ ] Build with tests (`make developer`)

### Phase 4: Advanced Topics
- [ ] Cycles rendering internals
- [ ] Node system architecture
- [ ] Python integration (bpy module)
- [ ] Platform-specific code (GHOST)

---

## Key Concepts to Learn

### DNA/RNA System
- **DNA**: Blender's serialization system (file format)
- **RNA**: Runtime API & reflection system
- Located in: `source/blender/makesdna` and `source/blender/makesrna`

### Operators
- Main way users interact with Blender
- Located in: `source/blender/editors/*/`

### Data System
- BKE (Blender Kernel) manages core data structures
- Located in: `source/blender/blenkernel`

---

## Build Notes

### First Build ✅
- Date: October 5, 2025
- Command: `make developer ninja`
- Status: **SUCCESS!**
- Build Time: Initial build completed
- Binary Size: Check with `du -sh ../build_darwin/bin/Blender.app`

### Build Issues & Solutions
1. **Missing Ninja build tool**
   - Solution: `brew install ninja`
   
2. **Empty lib/macos_arm64 directory**
   - Solution: Manually cloned the precompiled libraries repository
   - Command: `git clone --depth=1 https://projects.blender.org/blender/lib-macos_arm64.git lib/macos_arm64`
   
3. **Missing Git LFS files (preview.blend)**
   - Solution: Restored release datafiles
   - Command: `git checkout HEAD -- release/datafiles/`

### What I Learned
- Blender uses CMake with a convenient Makefile wrapper
- Pre-compiled libraries are ~973 MB for macOS ARM64
- Developer mode enables faster incremental builds and includes testing tools
- The build system automatically detects architecture (ARM64 vs x64)
- Ninja is much faster than traditional Make for large projects

---

## Code Snippets & Examples
(Add interesting code snippets as you explore)

---

## Resources
- [Blender Developer Wiki](https://developer.blender.org)
- [Source Code Documentation (Doxygen)](https://developer.blender.org/docs/api/)
- [Blender Stack Exchange](https://blender.stackexchange.com)
- [#blendercoders on IRC/Discord](https://devtalk.blender.org)

---

## Questions & TODOs
- How does Blender handle undo/redo?
- What's the event system architecture?
- How does Python integration work?

