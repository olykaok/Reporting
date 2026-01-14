# System Patterns: Jira Reporting System

## System Architecture
The Jira Reporting System follows a modular, linear processing architecture:

1. **Configuration Layer**: Environment variables and .env file configuration
2. **Data Extraction Layer**: Jira API client and JSON data handling
3. **Data Processing Layer**: Time conversion and business logic processing
4. **Report Generation Layer**: CSV file creation and output management
5. **File Organization Layer**: Input/output directory separation

## Key Technical Decisions
- **Directory Separation**: `data/in` for input files, `data/out` for generated reports
- **Modular Function Design**: Separate functions for JSON fetching, JSON processing, and main orchestration
- **Environment-Based Configuration**: All configurable parameters stored in `.env` file
- **Automatic Directory Creation**: Runtime creation of required directories to prevent file errors
- **Comprehensive Error Handling**: Try/catch blocks with detailed error messages for all operations

## Design Patterns in Use
- **Separation of Concerns**: Different functions handle distinct responsibilities (fetching, processing, output)
- **Configuration Pattern**: Centralized configuration management through environment variables
- **File Processing Pipeline**: Linear workflow from data extraction to report generation
- **Defensive Programming**: Extensive error checking and validation at each step
- **Path Abstraction**: Consistent path handling using `os.path` utilities

## Component Relationships
- **Main Function** ↔ **Jira Client**: Main orchestrates data fetching through the client
- **Jira Client** → **JSON Output**: Client provides data that gets saved to JSON
- **JSON Files** ↔ **CSV Generator**: Processed JSON data converted to detailed reports
- **Environment Config** → **All Components**: Configuration settings flow to all system parts
- **File System** ↔ **All I/O Operations**: Directory and file operations throughout the system

## Critical Implementation Paths
1. **Jira API Integration Path**: Authentication → Query execution → Data retrieval → JSON storage
2. **File Processing Path**: Input JSON detection → Data parsing → CSV generation → Output storage
3. **Directory Management Path**: Path validation → Directory existence checking → Automatic creation → File placement
4. **Error Handling Path**: Exception detection → Error logging → User notification → Graceful continuation

## Path Handling Strategy
- **Input Files**: Located in `data/in` directory, processed but not modified
- **Output Files**: Generated in `data/out` directory with timestamp-based naming
- **Configuration Files**: `.env` file in root directory
- **Library Files**: `lib/` directory containing client and logging utilities
- **Memory Bank**: `memory-bank/` directory for project documentation
