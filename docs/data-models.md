# AI-Assisted Web Application Penetration Testing Agent - Data Models

## Data Model Definitions

### 1. Target
**Purpose**: Represents the target website for scanning
**Fields**:
- `url` (str): Full URL of the target
- `scheme` (str): Protocol (http/https)
- `host` (str): Hostname or IP address
- `port` (int): Port number
- `scope` (dict): Scope configuration including allowed domains, depth limits, exclusions

**Field Types**:
- `url`: str
- `scheme`: str (enum: ["http", "https"])
- `host`: str
- `port`: int
- `scope`: dict

**Required vs Optional**: 
- All fields required

**Allowed Values/Enums**:
- `scheme`: ["http", "https"]

**Relationships**: 
- Linked to ScanConfig, AttackSurface

**Validation Rules**:
- URL must be valid format
- Host must be resolvable
- Port must be in valid range (1-65535)

### 2. ScanConfig
**Purpose**: Configuration for a specific scan run
**Fields**:
- `target` (Target): Target website to scan
- `crawl_limits` (dict): Limits for crawling (depth, count)
- `timeout` (int): Timeout for network operations (seconds)
- `rate_limits` (dict): API rate limiting configuration
- `max_iterations` (int): Maximum number of test iterations
- `enabled_tests` (list): List of enabled test categories
- `llm_provider` (str): LLM provider to use (ollama, openai, anthropic)
- `llm_model` (str): Specific model to use for LLM operations

**Field Types**:
- `target`: Target
- `crawl_limits`: dict
- `timeout`: int
- `rate_limits`: dict
- `max_iterations`: int
- `enabled_tests`: list of str
- `llm_provider`: str (enum: ["ollama", "openai", "anthropic"])
- `llm_model`: str

**Required vs Optional**: 
- `target` required
- All others optional with defaults

**Allowed Values/Enums**:
- `llm_provider`: ["ollama", "openai", "anthropic"]

**Relationships**: 
- References Target, AttackSurface, TestPlan, ToolAction, ToolResult, Evidence, VulnerabilityCandidate, VerifiedFinding

**Validation Rules**:
- Target must be valid
- Timeout must be positive
- Max iterations must be non-negative
- LLM provider must be supported

### 3. Endpoint
**Purpose**: Represents a discovered web endpoint
**Fields**:
- `url` (str): Full URL of the endpoint
- `methods` (list): HTTP methods supported
- `parameters` (list): List of parameters
- `headers` (dict): Relevant headers
- `content_type` (str): Content type expected
- `endpoint_type` (str): Type of endpoint (api, form, static)
- `discovery_source` (str): How the endpoint was discovered

**Field Types**:
- `url`: str
- `methods`: list of str
- `parameters`: list of Parameter
- `headers`: dict
- `content_type`: str
- `endpoint_type`: str (enum: ["api", "form", "static"])
- `discovery_source`: str

**Required vs Optional**: 
- `url` required
- Others optional

**Allowed Values/Enums**:
- `endpoint_type`: ["api", "form", "static"]

**Relationships**: 
- Linked to AttackSurface, TestPlan, ToolAction, ToolResult, Evidence

**Validation Rules**:
- URL must be valid format
- Methods must be valid HTTP methods
- Endpoint type must be valid

### 4. Parameter
**Purpose**: Represents a parameter of an endpoint
**Fields**:
- `name` (str): Parameter name
- `location` (str): Where parameter is located (query, body, header, path)
- `type` (str): Parameter type (string, number, boolean, file)
- `required` (bool): Whether parameter is required
- `ai_relevance` (float): Relevance score for AI/prompt injection (0.0-1.0)

**Field Types**:
- `name`: str
- `location`: str (enum: ["query", "body", "header", "path"])
- `type`: str (enum: ["string", "number", "boolean", "file"])
- `required`: bool
- `ai_relevance`: float

**Required vs Optional**: 
- All fields required

**Allowed Values/Enums**:
- `location`: ["query", "body", "header", "path"]
- `type`: ["string", "number", "boolean", "file"]

**Relationships**: 
- Linked to Endpoint, AIInteractionPoint

**Validation Rules**:
- Name must be non-empty
- Location must be valid
- Type must be valid
- AI relevance must be between 0.0 and 1.0

### 5. Form
**Purpose**: Represents a web form
**Fields**:
- `action` (str): Form action URL
- `method` (str): HTTP method (GET/POST)
- `fields` (list): List of form fields
- `enctype` (str): Encoding type
- `name` (str): Form name (if specified)
- `id` (str): Form ID (if specified)

**Field Types**:
- `action`: str
- `method`: str (enum: ["GET", "POST"])
- `fields`: list of dict (Field objects)
- `enctype`: str
- `name`: str
- `id`: str

**Required vs Optional**: 
- `action` required
- Others optional

**Allowed Values/Enums**:
- `method`: ["GET", "POST"]

**Relationships**: 
- Linked to Endpoint, AttackSurface

**Validation Rules**:
- Action must be valid URL
- Method must be valid HTTP method

### 6. Technology
**Purpose**: Represents technologies detected on the target
**Fields**:
- `name` (str): Technology name (e.g., "React", "Node.js")
- `version` (str): Version string if detected
- `confidence` (float): Confidence level (0.0-1.0)
- `category` (str): Technology category (frontend, backend, database, etc.)
- `detected_by` (str): Method of detection

**Field Types**:
- `name`: str
- `version`: str
- `confidence`: float
- `category`: str (enum: ["frontend", "backend", "database", "framework", "other"])
- `detected_by`: str

**Required vs Optional**: 
- `name` required
- Others optional

**Allowed Values/Enums**:
- `category`: ["frontend", "backend", "database", "framework", "other"]

**Relationships**: 
- Linked to AttackSurface

**Validation Rules**:
- Name must be non-empty
- Confidence must be between 0.0 and 1.0

### 7. AIInteractionPoint
**Purpose**: Represents a suspected AI/LLM interaction point
**Fields**:
- `endpoint` (Endpoint): The endpoint identified as AI interaction point
- `confidence` (float): Confidence level (0.0-1.0)
- `detection_reasons` (list): List of reasons for detection
- `input_fields` (list): List of input fields for AI interaction
- `interaction_type` (str): Type of AI interaction (chat, completion, embedding, etc.)

**Field Types**:
- `endpoint`: Endpoint
- `confidence`: float
- `detection_reasons`: list of str
- `input_fields`: list of str
- `interaction_type`: str (enum: ["chat", "completion", "embedding", "moderation", "other"])

**Required vs Optional**: 
- `endpoint` required
- Others optional

**Allowed Values/Enums**:
- `interaction_type`: ["chat", "completion", "embedding", "moderation", "other"]

**Relationships**: 
- References Endpoint, AttackSurface, TestPlan, ToolAction

**Validation Rules**:
- Confidence must be between 0.0 and 1.0
- Endpoint must be valid

### 8. AttackSurface
**Purpose**: Represents the complete attack surface of a target
**Fields**:
- `endpoints` (list): List of discovered endpoints
- `forms` (list): List of discovered forms
- `parameters` (list): List of parameters
- `technologies` (list): List of detected technologies
- `ai_interaction_points` (list): List of AI interaction points

**Field Types**:
- `endpoints`: list of Endpoint
- `forms`: list of Form
- `parameters`: list of Parameter
- `technologies`: list of Technology
- `ai_interaction_points`: list of AIInteractionPoint

**Required vs Optional**: 
- All fields required but can be empty lists

**Allowed Values/Enums**: 
- None

**Relationships**: 
- Links to Target, ScanConfig, TestPlan, ToolAction, ToolResult, Evidence, VulnerabilityCandidate, VerifiedFinding

**Validation Rules**:
- All lists should be valid

### 9. TestPlan
**Purpose**: Represents a plan for security testing
**Fields**:
- `test_id` (str): Unique identifier for the test plan
- `target` (str): Target identifier
- `vulnerability_category` (str): Category of vulnerability to test
- `objective` (str): Objective of the test
- `requested_tool_action` (ToolAction): Tool action requested by LLM
- `parameters` (dict): Test parameters
- `priority` (str): Priority level (low, medium, high, critical)
- `reasoning` (str): LLM reasoning for the test plan

**Field Types**:
- `test_id`: str
- `target`: str
- `vulnerability_category`: str
- `objective`: str
- `requested_tool_action`: ToolAction
- `parameters`: dict
- `priority`: str (enum: ["low", "medium", "high", "critical"])
- `reasoning`: str

**Required vs Optional**: 
- `test_id`, `target`, `vulnerability_category`, `objective` required
- Others optional

**Allowed Values/Enums**:
- `priority`: ["low", "medium", "high", "critical"]

**Relationships**: 
- References ToolAction, AttackSurface, Evidence, VulnerabilityCandidate, VerifiedFinding

**Validation Rules**:
- Test ID must be unique
- Priority must be valid
- Target must be valid

### 10. ToolAction
**Purpose**: Represents an action requested by the agent to be executed by tools
**Fields**:
- `action_id` (str): Unique identifier for the action
- `tool_name` (str): Name of tool to execute
- `arguments` (dict): Arguments for tool execution
- `target` (str): Target for the action
- `safety_constraints` (dict): Safety constraints for the action

**Field Types**:
- `action_id`: str
- `tool_name` (str): Tool name
- `arguments`: dict
- `target`: str
- `safety_constraints`: dict

**Required vs Optional**: 
- `action_id`, `tool_name`, `arguments` required
- Others optional

**Allowed Values/Enums**: 
- None

**Relationships**: 
- Links to TestPlan, ToolResult, Evidence, VulnerabilityCandidate, VerifiedFinding

**Validation Rules**:
- Action ID must be unique
- Tool name must be valid
- Arguments must be valid for the tool

### 11. ToolResult
**Purpose**: Represents the result of a tool execution
**Fields**:
- `action_id` (str): Identifier of the action that generated this result
- `success` (bool): Whether the action succeeded
- `status` (str): Status code or message
- `response` (dict): Response from tool execution
- `error_info` (dict): Error information if failed
- `timing` (dict): Timing information

**Field Types**:
- `action_id`: str
- `success`: bool
- `status`: str
- `response`: dict
- `error_info`: dict
- `timing`: dict

**Required vs Optional**: 
- `action_id`, `success` required
- Others optional

**Allowed Values/Enums**: 
- None

**Relationships**: 
- References ToolAction, Evidence, VulnerabilityCandidate, VerifiedFinding

**Validation Rules**:
- Action ID must reference existing action
- Success must be boolean

### 12. Evidence
**Purpose**: Stores security evidence collected during testing
**Fields**:
- `evidence_id` (str): Unique identifier for evidence
- `related_action` (ToolAction): Action that generated this evidence
- `request` (dict): HTTP request details
- `response` (dict): HTTP response details
- `observations` (list): Observations made during test
- `timestamp` (str): When evidence was collected
- `integrity_info` (dict): Integrity information for evidence

**Field Types**:
- `evidence_id`: str
- `related_action`: ToolAction
- `request`: dict
- `response`: dict
- `observations`: list of str
- `timestamp`: str (ISO format)
- `integrity_info`: dict

**Required vs Optional**: 
- `evidence_id`, `related_action` required
- Others optional

**Allowed Values/Enums**: 
- None

**Relationships**: 
- References ToolAction, VulnerabilityCandidate, VerifiedFinding

**Validation Rules**:
- Evidence ID must be unique
- Related action must exist
- Timestamp must be valid

### 13. VulnerabilityCandidate
**Purpose**: Represents a potential security vulnerability identified
**Fields**:
- `candidate_id` (str): Unique identifier for the candidate
- `category` (str): Vulnerability category
- `target` (str): Target of the vulnerability
- `description` (str): Description of the vulnerability
- `evidence_references` (list): List of evidence IDs
- `observations` (list): Observations made
- `confidence` (float): Confidence level (0.0-1.0)

**Field Types**:
- `candidate_id`: str
- `category`: str
- `target`: str
- `description`: str
- `evidence_references`: list of str
- `observations`: list of str
- `confidence`: float

**Required vs Optional**: 
- All fields required

**Allowed Values/Enums**: 
- None

**Relationships**: 
- References Evidence, VerifiedFinding

**Validation Rules**:
- Candidate ID must be unique
- Confidence must be between 0.0 and 1.0

### 14. VerifiedFinding
**Purpose**: Represents a confirmed security finding
**Fields**:
- `finding_id` (str): Unique identifier for the finding
- `vulnerability_category` (str): Category of vulnerability
- `title` (str): Title of the finding
- `description` (str): Detailed description
- `severity` (str): Severity level (low, medium, high, critical)
- `confidence` (float): Confidence level (0.0-1.0)
- `affected_endpoint` (Endpoint): Endpoint affected
- `evidence_references` (list): List of evidence IDs
- `reproduction_summary` (str): How to reproduce the finding
- `remediation` (str): Recommended remediation

**Field Types**:
- `finding_id`: str
- `vulnerability_category`: str
- `title`: str
- `description`: str
- `severity` (str): str (enum: ["low", "medium", "high", "critical"])
- `confidence`: float
- `affected_endpoint`: Endpoint
- `evidence_references`: list of str
- `reproduction_summary`: str
- `remediation`: str

**Required vs Optional**: 
- All fields required

**Allowed Values/Enums**:
- `severity`: ["low", "medium", "high", "critical"]

**Relationships**: 
- References Evidence, AttackSurface, TestPlan, ToolAction

**Validation Rules**:
- Finding ID must be unique
- Severity must be valid
- Confidence must be between 0.0 and 1.0

### 15. AgentState
**Purpose**: Represents the current state of the agent during a scan
**Fields**:
- `scan_info` (dict): Scan metadata
- `attack_surface` (AttackSurface): Current attack surface
- `current_plan` (TestPlan): Current test plan
- `completed_actions` (list): List of completed actions
- `observations` (list): Current observations
- `evidence` (list): Collected evidence
- `candidates` (list): Vulnerability candidates
- `verified_findings` (list): Verified findings
- `current_iteration` (int): Current iteration number
- `status` (str): Current scan status

**Field Types**:
- `scan_info`: dict
- `attack_surface`: AttackSurface
- `current_plan`: TestPlan
- `completed_actions`: list of ToolAction
- `observations`: list of str
- `evidence`: list of Evidence
- `candidates`: list of VulnerabilityCandidate
- `verified_findings`: list of VerifiedFinding
- `current_iteration`: int
- `status`: str

**Required vs Optional**: 
- All fields required

**Allowed Values/Enums**: 
- None

**Relationships**: 
- Links to all other models

**Validation Rules**:
- All fields must be valid according to their types

### 16. ScanResult
**Purpose**: Represents the final result of a scan
**Fields**:
- `scan_metadata` (dict): Metadata about the scan
- `findings` (list): List of verified findings
- `limitations` (list): Scan limitations encountered
- `statistics` (dict): Scan statistics
- `completion_status` (str): Status of scan completion

**Field Types**:
- `scan_metadata`: dict
- `findings`: list of VerifiedFinding
- `limitations`: list of str
- `statistics`: dict
- `completion_status`: str (enum: ["completed", "partial", "failed"])

**Required vs Optional**: 
- `scan_metadata`, `findings` required
- Others optional

**Allowed Values/Enums**:
- `completion_status`: ["completed", "partial", "failed"]

**Relationships**: 
- References VerifiedFinding, AttackSurface

**Validation Rules**:
- Scan metadata must be valid
- Completion status must be valid

## Data Flow

Target
→ ScanConfig
→ AttackSurface
→ TestPlan
→ ToolAction
→ ToolResult
→ Evidence
→ VulnerabilityCandidate
→ VerifiedFinding
→ ScanResult

## Important Design Rules

### Data Model Principles
- **Keep models simple**: Only include necessary fields
- **Prefer immutable/validated data**: Use validation where appropriate
- **Avoid database-specific models**: Pure data representation
- **No ORM design**: Plain data structures
- **No unnecessary abstractions**: Direct, clear representation
- **Python type hint friendly**: Compatible with typing system
- **JSON serializable**: All models should be JSON-serializable
- **LLM validation**: Raw LLM output must be validated before entering core state
- **No direct LLM state mutation**: Deterministic code validates and processes LLM output

## LLM Boundary

### Models for LLM Input
- **AttackSurface**: Attack surface data for LLM analysis
- **TestPlan**: Test plan generation context
- **VulnerabilityCandidate**: Candidate vulnerabilities for LLM evaluation

### Models for LLM Output
- **TestPlan**: Generated test plans
- **VulnerabilityCandidate**: Identified candidates
- **VerifiedFinding**: Final findings

### Models for Tool Input
- **ToolAction**: Actions to be executed by tools
- **TestPlan**: Test parameters for tool execution

### Models for Tool Output
- **ToolResult**: Results from tool execution
- **Evidence**: Evidence collected by tools

### Models for Internal Use Only
- **AgentState**: Internal agent state
- **ScanConfig**: Scan configuration
- **Target**: Target information

### Critical LLM Boundaries

**TestPlan and ToolAction**:
- LLM generates TestPlan and ToolAction structures
- Deterministic code must validate these before execution
- ToolAction must be validated against allowed actions
- TestPlan must be validated against scan configuration
- No raw LLM output should directly modify AgentState
- All LLM-generated actions must be passed through validation layers

## Recommended Python Representation

### Target
- **Recommendation**: dataclass or Pydantic model
- **Reason**: Simple, structured data with validation

### ScanConfig
- **Recommendation**: Pydantic model
- **Reason**: Requires validation and default values

### Endpoint
- **Recommendation**: dataclass or Pydantic model
- **Reason**: Simple, structured data with validation

### Parameter
- **Recommendation**: dataclass or Pydantic model
- **Reason**: Simple, structured data with validation

### Form
- **Recommendation**: Pydantic model
- **Reason**: Complex structure with validation requirements

### Technology
- **Recommendation**: dataclass or Pydantic model
- **Reason**: Simple data with validation

### AIInteractionPoint
- **Recommendation**: dataclass or Pydantic model
- **Reason**: Simple, structured data with validation

### AttackSurface
- **Recommendation**: dataclass or Pydantic model
- **Reason**: Aggregation of other models

### TestPlan
- **Recommendation**: Pydantic model
- **Reason**: Requires validation and complex structure

### ToolAction
- **Recommendation**: Pydantic model
- **Reason**: Requires validation and safety constraints

### ToolResult
- **Recommendation**: Pydantic model
- **Reason**: Requires validation and structured error handling

### Evidence
- **Recommendation**: Pydantic model
- **Reason**: Requires validation and structured data

### VulnerabilityCandidate
- **Recommendation**: Pydantic model
- **Reason**: Requires validation and structured data

### VerifiedFinding
- **Recommendation**: Pydantic model
- **Reason**: Requires validation and structured data

### AgentState
- **Recommendation**: dataclass or Pydantic model
- **Reason**: Complex aggregation of data

### ScanResult
- **Recommendation**: Pydantic model
- **Reason**: Requires validation and structured output

### Enum Types
- **Recommended**: Use Python Enum for all enum fields
- **Examples**: 
  - `scheme` (http/https)
  - `endpoint_type` (api/form/static)
  - `llm_provider` (ollama/openai/anthropic)
  - `priority` (low/medium/high/critical)
  - `severity` (low/medium/high/critical)
  - `completion_status` (completed/partial/failed)
  - `location` (query/body/header/path)
  - `type` (string/number/boolean/file)
  - `method` (GET/POST)
  - `category` (frontend/backend/database/framework/other)
  - `interaction_type` (chat/completion/embedding/moderation/other)