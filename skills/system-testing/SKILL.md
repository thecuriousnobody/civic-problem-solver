# System Testing & Validation Skill

## Description
A comprehensive testing framework for civic resource systems that validates every component before claiming completion. Tests APIs, URLs, search functionality, and end-to-end user workflows systematically.

## Capabilities
- **API Endpoint Testing**: Validate all backend endpoints respond correctly
- **URL Verification**: Check that all resource URLs are real and accessible
- **Search Tool Validation**: Verify external APIs (Serper) are actually being called
- **End-to-End Workflow Testing**: Test complete user journeys from frontend to backend
- **Resource Data Integrity**: Validate phone numbers, addresses, and contact information
- **Performance Monitoring**: Measure actual response times and bottlenecks
- **Log Analysis**: Parse and analyze system logs for errors and issues

## When to Use
- Before claiming any feature is "complete"
- When debugging slow performance or missing functionality
- After making changes to search, API, or resource systems
- When adding new resources to verify they're legitimate
- For systematic troubleshooting of complex issues

## Validation Levels
1. **Atomic Testing**: Test individual components in isolation
2. **Integration Testing**: Test how components work together
3. **End-to-End Testing**: Test complete user workflows
4. **Data Validation**: Verify all external data (URLs, phones, addresses)
5. **Performance Testing**: Measure and validate response times

## Tools Required
- curl for API testing
- Python requests for advanced validation
- Log parsing utilities
- URL validation tools
- Performance measurement scripts