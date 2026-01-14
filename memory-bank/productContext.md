# Product Context: Jira Reporting System

## Purpose
The Jira Reporting System exists to automate the extraction and processing of project management data from Jira for reporting and analysis purposes. It bridges the gap between raw Jira data and actionable business insights.

## Problems Solved
1. **Manual Data Extraction**: Eliminates the need for manual exporting of Jira issues and time tracking data
2. **Data Processing Automation**: Automatically converts time estimates and tracked time into standardized formats
3. **Report Generation**: Creates structured reports suitable for further analysis and stakeholder reporting
4. **Consistent Data Format**: Ensures consistent data structure across different reporting periods
5. **Time Calculation Standardization**: Applies uniform rounding rules for time estimation reporting

## How It Works
1. **Data Extraction**: Connects to Jira API using authentication tokens and executes configured JQL queries
2. **Data Processing**: Extracts relevant fields including issue details, time estimates, and custom fields
3. **Time Conversion**: Converts seconds-based time tracking data to hours with configurable rounding
4. **Report Generation**: Creates JSON storage files and detailed CSV analysis reports
5. **File Organization**: Separates input and output files for clean data workflow

## User Experience Goals
- **Reliability**: Consistent and error-free data processing
- **Transparency**: Clear console output showing processing status and results
- **Configurability**: Easy customization through environment variables
- **Maintainability**: Well-structured code that's easy to extend and modify
- **Performance**: Efficient data processing with minimal resource usage
