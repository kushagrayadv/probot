import json
import os
import subprocess
from typing import Optional, Dict, Any

from mcp.server.fastmcp import FastMCP

from pr_agent.config.settings import BASE_DIR
from pr_agent.utils.logger import get_logger

logger = get_logger(__name__)


def register_git_analysis_tools(mcp: FastMCP) -> None:
    """Register git analysis tools with the MCP server.
    
    Args:
        mcp: FastMCP server instance to register tools with
    """
    
    @mcp.tool()
    async def analyze_file_changes(
        base_branch: str = "main",
        include_diff: bool = True,
        max_diff_lines: int = 500,
        working_directory: Optional[str] = None
    ) -> str:
        """Get the full diff and list of changed files in the current git repository.
        
        Args:
            base_branch: Base branch to compare against (default: main)
            include_diff: Include the full diff content (default: true)
            max_diff_lines: Maximum number of diff lines to include (default: 500)
            working_directory: Directory to run git commands in (default: current directory)
        """
        try:
            logger.debug(
                "Analyzing file changes",
                base_branch=base_branch,
                include_diff=include_diff,
                max_diff_lines=max_diff_lines,
                working_directory=working_directory
            )
            
            # Try to get working directory from roots first
            if working_directory is None:
                try:
                    context = mcp.get_context()
                    roots_result = await context.session.list_roots()
                    # Get the first root - Claude Code sets this to the CWD
                    root = roots_result.roots[0]
                    # FileUrl object has a .path property that gives us the path directly
                    working_directory = root.uri.path
                    logger.debug("Got working directory from MCP context", working_directory=working_directory)
                except Exception as e:
                    # If we can't get roots, fall back to current directory
                    logger.debug("Could not get working directory from MCP context, using current directory", error=str(e))
                    pass
            
            # Use provided working directory or current directory
            cwd = working_directory if working_directory else os.getcwd()
            logger.debug("Using working directory", cwd=cwd)
            # Get list of changed files
            files_result = subprocess.run(
                ["git", "diff", "--name-status", f"{base_branch}...HEAD"],
                capture_output=True,
                text=True,
                check=True,
                cwd=cwd
            )
            
            # Get diff statistics
            stat_result = subprocess.run(
                ["git", "diff", "--stat", f"{base_branch}...HEAD"],
                capture_output=True,
                text=True,
                check=True,
                cwd=cwd
            )
            
            # Get the actual diff if requested
            diff_content = ""
            truncated = False
            diff_lines = []
            if include_diff:
                diff_result = subprocess.run(
                    ["git", "diff", f"{base_branch}...HEAD"],
                    capture_output=True,
                    text=True,
                    cwd=cwd
                )
                diff_lines = diff_result.stdout.split('\n')
                
                # Check if we need to truncate
                if len(diff_lines) > max_diff_lines:
                    diff_content = '\n'.join(diff_lines[:max_diff_lines])
                    diff_content += f"\n\n... Output truncated. Showing {max_diff_lines} of {len(diff_lines)} lines ..."
                    diff_content += "\n... Use max_diff_lines parameter to see more ..."
                    truncated = True
                else:
                    diff_content = diff_result.stdout
            
            # Get commit messages for context
            commits_result = subprocess.run(
                ["git", "log", "--oneline", f"{base_branch}..HEAD"],
                capture_output=True,
                text=True,
                check=True,
                cwd=cwd
            )
            
            analysis: Dict[str, Any] = {
                "base_branch": base_branch,
                "files_changed": files_result.stdout,
                "statistics": stat_result.stdout,
                "commits": commits_result.stdout,
                "diff": diff_content if include_diff else "Diff not included (set include_diff=true to see full diff)",
                "truncated": truncated,
                "total_diff_lines": len(diff_lines) if include_diff else 0
            }
            
            logger.info(
                "File changes analyzed successfully",
                base_branch=base_branch,
                files_changed_count=len(files_result.stdout.split('\n')) if files_result.stdout else 0,
                diff_truncated=truncated,
                total_diff_lines=len(diff_lines) if include_diff else 0
            )
            
            return json.dumps(analysis, indent=2)
            
        except subprocess.CalledProcessError as e:
            logger.error(
                "Git command failed",
                base_branch=base_branch,
                command_error=e.stderr,
                return_code=e.returncode
            )
            return json.dumps({"error": f"Git error: {e.stderr}"})
        except Exception as e:
            logger.exception(
                "Unexpected error analyzing file changes",
                base_branch=base_branch,
                error=str(e)
            )
            return json.dumps({"error": str(e)})

