# AI-Assisted Web Application Penetration Testing Agent - Agent Design

## Agent Lifecycle

### Scan Initiation
The agent begins when a target URL is provided through the GUI or API. The scan controller validates the URL and initializes the scan state with target information, scope parameters, and configuration settings.

### Reconnaissance Phase
The reconnaissance engine performs passive and active discovery of the application:
- Crawls the application to discover endpoints and application structure
- Identifies forms, parameters, and API endpoints
- Detects technologies and frameworks used
- Analyzes JavaScript code for AI interaction patterns
- Collects initial HTTP responses for analysis

### Attack-Surface Construction
The attack-surface model organizes reconnaissance results into structured data:
- Categorizes endpoints by type (API, form, static)
- Analyzes parameters for potential LLM interaction points
- Structures form data with field types and purposes
- Identifies potential AI endpoints based on patterns and parameters

### LLM Planning
The agent planner uses LLM reasoning to:
- Analyze the attack surface data
- Prioritize vulnerabilities based on risk and discovery
- Generate test plans for security testing
- Determine which AI endpoints to target for prompt injection testing

### Test Selection
Based on the LLM-generated plans, the agent selects appropriate tests:
- Prioritizes AI interaction points for prompt injection testing
- Selects appropriate testing techniques for each endpoint
- Determines test parameters and payloads

### Controlled Execution
The agent executor performs tests through controlled tools:
- Executes HTTP requests to endpoints
- Interacts with forms and APIs
- Tests AI endpoints with carefully crafted payloads
- Collects responses and observations

### Evidence Collection
The evidence store captures all test results:
- Stores HTTP requests and responses
- Records test parameters and outcomes
- Maintains logs of all actions and observations
- Indexes evidence for later verification

### Vulnerability Verification
The verification engine validates candidates:
- Cross-references evidence with LLM analysis
- Determines if findings are actual vulnerabilities
- Assigns confidence scores to findings
- Filters out false positives

### Severity/Confidence Assessment
The risk/severity engine assigns ratings:
- Evaluates impact of each vulnerability
- Assigns risk levels (low, medium, high, critical)
- Provides confidence scores for findings
- Prioritizes findings for reporting

### Report Generation
The report generator creates a structured security report:
- Compiles verified findings with evidence
- Formats findings with severity ratings
- Creates professional documentation
- Includes recommendations for remediation

## Agent Loop

The agent operates in a reasoning/action/observation cycle:

### Information Received by LLM
- Current scan state and target information
- Attack surface data and discovered endpoints
- Previous observations and test results
- Scan configuration and constraints
- Evidence database references

### Decisions LLM is Allowed to Make
- Prioritize which endpoints to test next
- Determine test strategies for each endpoint
- Evaluate whether findings are actual vulnerabilities
- Assign risk levels and confidence scores
- Generate test payloads and parameters
- Decide when to stop testing an endpoint

### Actions LLM Can Request
- Execute HTTP requests to specific endpoints
- Test specific parameters or form fields
- Perform browser automation on certain pages
- Request evidence retrieval for analysis
- Generate test payloads for injection
- Modify test parameters based on results

### Action Execution Process
1. LLM generates action request with parameters
2. Action request is validated by deterministic components
3. Tool system executes the requested action
4. Results are captured and stored in evidence database
5. Results are passed back to LLM for analysis

### Result Return to LLM
- Evidence is structured and presented to LLM
- Results are categorized by type (normal, suspicious, vulnerable)
- Context is provided for interpretation
- Previous test results are included for comparison

### Agent Stopping Conditions
The agent stops when:
- All endpoints in scope have been tested
- Maximum test time or iteration limits reached
- No new vulnerabilities are discovered after several iterations
- Critical system errors occur
- User manually terminates the scan

## LLM Responsibilities vs Deterministic Code

### What LLM Should NOT Directly Do
- Execute shell commands or system operations
- Make unrestricted network requests
- Modify files or system resources
- Access credentials or secrets
- Perform uncontrolled exploitation
- Access external APIs without tool system mediation
- Modify scan state directly

### What Deterministic Components Should Handle
- Network request execution (through controlled tools)
- Input/output validation and sanitization
- Security boundary enforcement
- State management and persistence
- Error handling and recovery
- Evidence storage and retrieval
- Configuration management
- Rate limiting and API interaction
- Test result categorization and analysis

## Tool System Design

### Conceptual Tools

#### HTTP Request Tool
- **Purpose**: Execute HTTP requests to target endpoints
- **Input**: URL, method, headers, body, parameters
- **Output**: HTTP response, status code, headers, body
- **Security Restrictions**: Only allowed to request configured endpoints, no arbitrary domains

#### Endpoint Crawling/Discovery Tool
- **Purpose**: Discover new endpoints and application structure
- **Input**: Base URL, crawl configuration, scope limits
- **Output**: List of discovered endpoints, parameters, form data
- **Security Restrictions**: Limited to target domain, respects robots.txt

#### Response Inspection Tool
- **Purpose**: Analyze HTTP responses for patterns and vulnerabilities
- **Input**: HTTP response data, analysis parameters
- **Output**: Analysis results, identified patterns, potential vulnerabilities
- **Security Restrictions**: No modification of data, only analysis

#### Form Interaction Tool
- **Purpose**: Fill and submit web forms
- **Input**: Form data, target URL, form fields
- **Output**: Form submission results, response data
- **Security Restrictions**: Only interacts with forms on target domain

#### AI Endpoint Interaction Tool
- **Purpose**: Test AI application endpoints specifically
- **Input**: AI endpoint URL, payload, context, parameters
- **Output**: AI responses, behavior patterns, potential vulnerabilities
- **Security Restrictions**: Limited to identified AI endpoints, controlled payloads

#### Evidence Storage/Retrieval Tool
- **Purpose**: Manage security evidence database
- **Input**: Evidence data, query parameters
- **Output**: Stored evidence, retrieved evidence, database status
- **Security Restrictions**: Controlled access, no direct LLM modification

## Agent State

The agent maintains structured state during scans:

### Core State Elements
- **Target**: URL and scan scope configuration
- **Scope**: Allowed domains, depth limits, exclusions
- **Discovered Endpoints**: List of identified URLs and endpoints
- **Parameters**: Endpoint parameters and their types
- **Forms**: Form structures and field information
- **Technologies**: Detected frameworks, libraries, and tools
- **Suspected AI Endpoints**: Identified AI interaction points
- **Test Plans**: LLM-generated test strategies
- **Executed Actions**: History of performed tests
- **Observations**: Collected data and results
- **Evidence**: Stored requests, responses, and test data
- **Vulnerability Candidates**: Potential security issues identified
- **Verified Findings**: Confirmed security issues with evidence

## LLM Provider Abstraction

### Provider Interface Design
The LLM provider abstraction layer implements a common interface:
- **Common Methods**: `generate_response(prompt, model, temperature)`, `get_model_list()`, `validate_provider()`
- **Configuration**: Provider selection through configuration file/environment variables
- **Error Handling**: Standardized error responses across providers
- **Rate Limiting**: Provider-agnostic rate limiting implementation

### Provider-Specific Implementation
- **Ollama**: Direct API calls to local Ollama instance
- **OpenAI**: API calls through OpenAI SDK with API key
- **Anthropic**: API calls through Anthropic SDK with API key

### Provider Independence
- No provider-specific logic in core agent components
- Configuration-driven provider selection
- Standardized response formats regardless of provider
- Shared prompt templates and structures

## Prompt-Injection Testing Agent Behavior

### AI Endpoint Discovery Process
1. **Pattern Recognition**: Analyze discovered endpoints for AI-like patterns
2. **Parameter Analysis**: Look for parameters that accept prompts or instructions
3. **JavaScript Analysis**: Examine client-side code for AI service calls
4. **Response Pattern Matching**: Identify endpoints that return AI-like responses
5. **Contextual Analysis**: Determine if endpoint is likely an AI service

### Test Decision Process
When identifying an AI endpoint, the agent:
- **Direct Prompt Injection**: Tests direct input injection in prompt parameters
- **Indirect Prompt Injection**: Tests through related parameters and context
- **Instruction Override**: Tests for instruction parameter manipulation
- **System Prompt Disclosure**: Looks for system prompt exposure in responses
- **Sensitive Information Disclosure**: Tests for data leakage in AI responses
- **Jailbreak Resistance**: Tests for bypass techniques and escaping
- **Multi-turn Manipulation**: Tests conversation context and history manipulation

### Controlled Testing Approach
- All tests use pre-defined, safe payloads
- Tests are limited to known AI endpoints
- Results are carefully analyzed for actual vulnerability vs. normal behavior
- No exploitation beyond controlled testing

## Verification Process

### Distinguishing Behaviors
The agent distinguishes:
- **Normal Application Behavior**: Expected responses for valid inputs
- **Suspicious Behavior**: Unusual or unexpected responses
- **Likely Vulnerability**: Patterns that suggest a vulnerability
- **Verified Vulnerability**: Confirmed security issues with evidence

### Evidence-Based Validation
- Cross-reference findings with stored evidence
- Compare responses to baseline behavior
- Apply LLM analysis to determine if behavior is normal or suspicious
- Use multiple tests to confirm vulnerability
- Filter out false positives through validation

## Agent Stopping Conditions

### Continue Testing
- New endpoints discovered and not yet tested
- No clear indication of vulnerability at current endpoint
- Scan time limit not reached
- Maximum iteration count not exceeded

### Retry Conditions
- Tool execution timeout
- LLM response parsing errors
- Network connectivity issues
- Configuration changes required

### Strategy Changes
- No new vulnerabilities discovered in several iterations
- Critical endpoint found with high risk
- Scan scope changes detected

### Inconclusive Results
- Ambiguous responses with no clear pattern
- Insufficient evidence to determine vulnerability
- Tests that produced inconsistent results

### Endpoint Testing Stop
- All parameters tested for current endpoint
- No new vulnerabilities found
- Time or resource limits reached
- Endpoint identified as non-AI or non-vulnerable

### Scan Completion
- All endpoints in scope tested
- Maximum scan time reached
- User termination request
- Critical system error occurs

## Failure Handling

### Target Unreachable
- Log error and notify user
- Skip endpoint and continue with others
- Attempt connection retry with exponential backoff
- Record as scan limitation

### Endpoint Timeout
- Retry with increased timeout
- Mark endpoint as unresponsive
- Continue with other endpoints
- Log timeout for reporting

### LLM Request Failure
- Retry with exponential backoff
- Fall back to default model if configured
- Log error and continue scan
- Attempt to recover by using cached responses

### Tool Failure
- Retry failed tool execution
- Log error and continue scan
- Mark endpoint as failed
- Attempt to use alternative tools

### Malformed LLM Output
- Parse error handling with retry
- Validate response structure
- Log malformed output for debugging
- Continue with alternative approaches

### Test/Time Limit Exceeded
- Stop current test and move to next
- Log timeout for reporting
- Continue with remaining endpoints
- Inform user of time limitations

### Ambiguous Results
- Attempt additional tests on same endpoint
- Use LLM to analyze ambiguity
- Mark as inconclusive with evidence
- Continue scan with other endpoints

## Minimal MVP Architecture

### Core Modules
1. **Scan Controller**: Orchestrates the scanning process
2. **Reconnaissance Engine**: Discovers attack surface
3. **Attack-Surface Model**: Structured representation of findings
4. **Agent Planner**: LLM-based test planning
5. **Agent Executor**: Controlled tool execution
6. **Tool System**: Interface for security testing tools
7. **Evidence Store**: Security evidence management
8. **Verification Engine**: Vulnerability validation
9. **Risk Engine**: Severity and confidence assignment
10. **Report Generator**: Security report creation
11. **LLM Provider Abstraction**: Unified interface for LLM providers

### Interface Design
- Strong, well-defined interfaces between modules
- Minimal dependencies between components
- Configuration-driven behavior
- Standardized data formats
- Clear separation of LLM reasoning and deterministic execution

### Local Execution
- All components run locally
- No external services required
- Works with Qwen3-Coder 30B through Ollama
- Minimal resource requirements
- No database dependencies

## Concrete Example Flow

### Example Scan Flow
1. **Target URL**: `https://example.com/ai-chat`
2. **Discovery**: Agent discovers `/ai-chat/api`, `/ai-chat/form`, `/ai-chat/endpoint`
3. **AI Endpoint Identification**: Agent identifies `/ai-chat/api` as likely AI endpoint
4. **Prompt Injection Test Plan**: LLM determines to test for direct prompt injection
5. **Controlled Test Execution**: Agent sends injection payload to `/ai-chat/api`
6. **Response Inspection**: Agent analyzes response for AI behavior
7. **Evidence Collection**: Agent stores request and response data
8. **Finding Verification**: LLM analyzes evidence to determine if injection was successful
9. **Finding Production**: Agent assigns severity and creates report entry

## Explicit Boundaries

### Planner vs Executor
- **Planner**: LLM reasoning, test strategy generation
- **Executor**: Tool execution, action implementation

### Tools vs State
- **Tools**: Execute specific actions, return results
- **State**: Maintain scan context and data

### Evidence vs Verification
- **Evidence**: Raw data collection and storage
- **Verification**: Analysis and validation of findings

### Report Generation vs Other Components
- **Report**: Output generation from verified findings
- **Others**: Data processing and analysis leading to findings

## Implementation Order

1. **Tool System** - Core interface for security testing tools
2. **Reconnaissance Engine** - Basic application discovery
3. **Attack-Surface Model** - Structured data representation
4. **LLM Provider Abstraction** - Unified LLM interface
5. **Agent Planner** - LLM-based test planning
6. **Agent Executor** - Controlled tool execution
7. **Evidence Store** - Security evidence management
8. **Verification Engine** - Vulnerability validation
9. **Risk Engine** - Severity and confidence assignment
10. **Report Generator** - Security report creation
11. **Scan Controller** - Overall scan orchestration
12. **Configuration System** - Scan parameter management