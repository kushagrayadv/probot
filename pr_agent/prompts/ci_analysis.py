from mcp.server.fastmcp import FastMCP


def register_ci_analysis_prompts(mcp: FastMCP) -> None:
    """Register CI/CD analysis prompts with the MCP server.
    
    Args:
        mcp: FastMCP server instance to register prompts with
    """
    
    @mcp.prompt()
    async def analyze_ci_results() -> str:
        """Analyze recent CI/CD results and provide insights.
        
        Returns:
            Prompt template string for analyzing CI results
        """
        return """Please analyze the recent CI/CD results from GitHub Actions:

1. First, call get_recent_actions_events() to fetch the latest CI/CD events
2. Then call get_workflow_status() to check current workflow states
3. Identify any failures or issues that need attention
4. Provide actionable next steps based on the results

Format your response as:
## CI/CD Status Summary
- *Overall Health*: [Good/Warning/Critical]
- *Failed Workflows*: [List any failures with links]
- *Successful Workflows*: [List recent successes]
- *Recommendations*: [Specific actions to take]
- *Trends*: [Any patterns you notice]"""
    
    
    @mcp.prompt()
    async def troubleshoot_workflow_failure() -> str:
        """Help troubleshoot a failing GitHub Actions workflow.
        
        Returns:
            Prompt template string for troubleshooting workflow failures
        """
        return """Help troubleshoot failing GitHub Actions workflows:

1. Use get_recent_actions_events() to find recent failures
2. Use get_workflow_status() to see which workflows are failing
3. Analyze the failure patterns and timing
4. Provide systematic troubleshooting steps

Structure your response as:

## 🔧 Workflow Troubleshooting Guide

### ❌ Failed Workflow Details
- *Workflow Name*: [Name of failing workflow]
- *Failure Type*: [Test/Build/Deploy/Lint]
- *First Failed*: [When did it start failing]
- *Failure Rate*: [Intermittent or consistent]

### 🔍 Diagnostic Information
- *Error Patterns*: [Common error messages or symptoms]
- *Recent Changes*: [What changed before failures started]
- *Dependencies*: [External services or resources involved]

### 💡 Possible Causes (ordered by likelihood)
1. *[Most Likely]*: [Description and why]
2. *[Likely]*: [Description and why]
3. *[Possible]*: [Description and why]

### ✅ Suggested Fixes
**Immediate Actions:**
- [ ] [Quick fix to try first]
- [ ] [Second quick fix]

**Investigation Steps:**
- [ ] [How to gather more info]
- [ ] [Logs or data to check]

**Long-term Solutions:**
- [ ] [Preventive measure]
- [ ] [Process improvement]

### 📚 Resources
- [Relevant documentation links]
- [Similar issues or solutions]"""

