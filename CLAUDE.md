# Claude Code Instructions for Arrow Development

## Project Overview
This is the nue-core project containing Arrow, an architecture-agnostic random instruction test (RIT) generator for x86, ARM, and RISC-V. Arrow is maintained as a private fork of an open source tool, with Ahead Computing's primary focus on RISC-V CPU development.

## Arrow Project Structure
- **Main package**: `Arrow/` containing the core framework
- **Key directories**:
  - `Arrow/Tool/` - Core generation logic, memory/register management
  - `Arrow/Internal_content/` - Company-specific test ingredients/scenarios
  - `Arrow/Externals/` - Binary generation, database management, UI
  - `Submodules/arrow_content/` - Additional test content repository

## Architecture Guidelines
1. **Multi-architecture support**: Always ensure new features work across x86, ARM, and RISC-V
2. **Architecture-agnostic design**: Use architecture detection patterns like `if Configuration.Architecture.riscv:`
3. **Graceful degradation**: Provide meaningful error messages when x86/ARM tests try to use RISC-V-only features
4. **No breaking changes**: Maintain backward compatibility with existing x86/ARM functionality

## Key Components
- **MemoryManager**: Handles memory allocation, segments, and blocks
- **RegisterManager**: Manages register allocation and reservations  
- **AR.generate()**: Primary instruction generation with database queries
- **Ingredients**: Reusable test components with init/body/final methods
- **Scenarios**: Top-level test orchestration flows
- **Templates**: Overall test structure and configuration

## Development Patterns
- Use `AR.generate()` with query parameters for instruction selection
- Guard architecture-specific code with `if Configuration.Architecture.{arch}:`
- Implement ingredients as classes with `@AR.ingredient_decorator`
- Use `yield` in ingredient body methods for proper state management
- Always use `RegisterManager.get_and_reserve()` / `RegisterManager.free()` pairs

## Testing

### Arrow MCP Server
- **MCP Integration**: Arrow testing is provided via MCP server located in `tfm/nhtsa/arrow_agent/`
- **Available through Claude Code**: Use MCP tools `arrow_run_test`, `arrow_run_smoke_tests`, `arrow_analyze_failure`
- **Environment Validation**: Use `arrow_validate_env` MCP tool to check prerequisites

### Test Execution
- **Smoke test command**: `ahc_regress --dut whisper --keep -l val/common/testlists/arrow_smoke_examples.yaml --local --no_compress`
- **Specific test**: Add `--test <test_name>` (e.g., `--test arrow_direct`)
- **Available smoke tests**: arrow_random, arrow_direct, arrow_branch, arrow_cfg, arrow_mode_switch
- **Test iterations**: Use 1 for smoke tests, 5-10 for full regression testing

### Prerequisites
- **Virtual environment**: Must be activated (`$GIT_ROOT/.venv`)
- **Whisper simulator**: Required at `$GIT_ROOT/cores/nue-core/build/releases/whisper/whisper`
- **Build if needed** (usually not required):
  ```bash
  cmake $GIT_ROOT --fresh -B $GIT_ROOT/cores/nue-core/build
  cmake --build $GIT_ROOT/cores/nue-core/build --target download_whisper
  ```

### Test Results
- **Result location**: `$GIT_ROOT/cores/nue-core/regression/nue_whisper_cfg/small/`
- **Status reports**: Check `report.yaml` files for PASS/FAIL status
- **Execution logs**: `ahc_exec.log` for main logs, `arrow/debug.log` for Arrow-specific output
- **Generated assembly**: `arrow/*.s` files in test directories

### Template Development
- **Template location**: `../../val/common/tests/arrow/`
- **Reference templates**: `direct_template.py`, `random_template.py`, `branch_template.py`, `cfg_template.py`, `msu_template.py`
- **For new templates**: Use Arrow Agent's template creation features or modify existing templates
- **Test list updates**: Modify YAML files in `val/common/testlists/` to add new test entries

## File Organization
- Never create new files without explicit need
- Prefer editing existing files over creating new ones
- Internal AHC content goes in `Arrow/Internal_content/`
- External/upstream changes go in appropriate `Arrow/` subdirectories

## Development Environment
- **Package manager**: This project uses `uv` (install with `pip install uv` or see https://github.com/astral-sh/uv)
- **Virtual environment**: `../../.venv/` (already set up with uv)
- **Install dependencies**: `cd ../../ && uv sync` (installs all workspace packages including Arrow)
- **Install Arrow in dev mode**: Already included in workspace - use `uv sync`
- **Run Arrow**: `uv run python Arrow/main.py <template>` or activate venv first
- **Repository paths**:
  - `REPO_ROOT`: Repository root (find with `git rev-parse --show-toplevel`)
  - `CORE_ROOT`: Assumed to be `$REPO_ROOT/cores/nue-core`

## Common Commands
- **Sync all dependencies**: `cd ../../ && uv sync`
- **Run Arrow**: `uv run python -m Arrow.main <template>`
- **Run tests**: `uv run pytest`
- **Code formatting**: `uv run black .`
- **Linting**: `uv run flake8`
- **Development mode**: Use PyCharm with provided configurations

## Important Notes
- Arrow generates assembly tests, not malicious code - this is defensive security tooling
- Focus on RISC-V but maintain x86/ARM compatibility
- Performance-critical sections may need C++/Rust implementations
- All generated tests must be deterministic and terminate correctly
- Memory allocation must avoid collisions and maintain safety

## Architecture-Specific Features
- **RISC-V**: Full privileged mode support (M/S/U), virtual memory, exceptions
- **x86/ARM**: Maintain existing functionality, provide meaningful errors for unsupported RISC-V features
- Use external tools like `pagegen` for low-level memory management

## Arrow MCP Server Integration
Arrow testing and development support is provided through an MCP (Model Context Protocol) server located in `tfm/nhtsa/arrow_agent/` in the main repo.

### Available MCP Tools
- **`arrow_validate_env`**: Validate Arrow development environment prerequisites
- **`arrow_run_test`**: Run a specific Arrow test
- **`arrow_run_smoke_tests`**: Run all Arrow smoke tests
- **`arrow_analyze_failure`**: Analyze test failures with detailed diagnostics including GCC/assembler errors

### Key Features
- **Test Execution**: Automated smoke test and specific test execution via MCP
- **Enhanced Failure Analysis**: Automatic GCC/assembler diagnostic capture for build failures
- **Environment Validation**: Prerequisite checking and setup guidance
- **Direct Claude Code Integration**: No command-line interface needed - all functionality available through MCP tools

### MCP Server development
- CRITICAL NEVER work around an issue with an agent or MCP that is run locally (we have control over the source code). It is IMPERATIVE that we fix the root issue to improve the quality and usefulness of the agent/MCP server.
- The user must be prompted to restart the server after a change is made is made to the server source code.
- never grep the logs, use an MCP agent to get the necessary info. fix/enhance the agent if necessary

The MCP server handles all the complexity and provides detailed results directly in the Claude Code interface.

### MCP Server Location
- **Path**: `tfm/nhtsa/arrow_agent/mcp_server.py`
- **Configuration**: Automatically loaded when Claude Code starts with MCP support
- **No manual setup required**: The server is integrated into the Claude Code environment

## Key Files to Understand
- `Arrow/main.py` - Entry point
- `Arrow/Tool/generation_management/generate*.py` - Architecture-specific generation
- `Arrow/Utils/configuration_management/` - Configuration and knobs
- `Arrow/Tool/memory_management/memory_manager.py` - Memory allocation
- `Arrow/Tool/register_management/register_manager.py` - Register management
- `arrow_agent/` - Arrow Development Agent (isolated directory)
- Always output analysis report files to the test run directory, not the source directory.

