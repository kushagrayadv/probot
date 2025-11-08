from mcp.server.fastmcp import FastMCP


def register_pr_report_prompts(mcp: FastMCP):
    """Register PR report prompts with the MCP server."""
    
    @mcp.prompt()
    async def generate_pr_status_report():
        """Generate a comprehensive PR status report including CI/CD results."""
        return """Generate a comprehensive PR status report:

1. Use analyze_file_changes() to understand what changed
2. Use get_workflow_status() to check CI/CD status
3. Use suggest_template() to recommend the appropriate PR template
4. Combine all information into a cohesive report

Create a detailed report with:

## 📋 PR Status Report

### 📝 Code Changes
- *Files Modified*: [Count by type - .py, .js, etc.]
- *Change Type*: [Feature/Bug/Refactor/etc.]
- *Impact Assessment*: [High/Medium/Low with reasoning]
- *Key Changes*: [Bullet points of main modifications]

### 🔄 CI/CD Status
- *All Checks*: [✅ Passing / ❌ Failing / ⏳ Running]
- *Test Results*: [Pass rate, failed tests if any]
- *Build Status*: [Success/Failed with details]
- *Code Quality*: [Linting, coverage if available]

### 📌 Recommendations
- *PR Template*: [Suggested template and why]
- *Next Steps*: [What needs to happen before merge]
- *Reviewers*: [Suggested reviewers based on files changed]

### ⚠️ Risks & Considerations
- [Any deployment risks]
- [Breaking changes]
- [Dependencies affected]"""

