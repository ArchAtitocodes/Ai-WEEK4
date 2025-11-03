# ==============================================================================
# PEERBOT CORE - Intelligent Code Review Assistant
#
# This script converts the simulated LLM calls into REAL API calls to the
# Gemini API, including structured output and robust error handling.
# ==============================================================================
import json
import requests
import time
from typing import Dict, List, Any

# --- Configuration Constants ---
LLM_MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
API_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{LLM_MODEL_NAME}:generateContent"
API_KEY = "" # The API key will be provided at runtime by the environment.

# --- Robustness Settings ---
MAX_RETRIES = 5
INITIAL_DELAY = 1.0 # seconds

# --- Structured Output Schema (Mandatory for machine-readable review) ---
# The LLM will be instructed to return an array of issues, each detailing the problem.
ISSUE_SCHEMA = {
    "type": "ARRAY",
    "items": {
        "type": "OBJECT",
        "properties": {
            "severity": {"type": "STRING", "description": "HIGH, MEDIUM, or TRIVIAL."},
            "issueType": {"type": "STRING", "description": "e.g., 'Security Flag', 'Policy Enforcement', 'Complexity Check'"},
            "description": {"type": "STRING", "description": "Detailed explanation of the violation."},
            "suggestedFix": {"type": "STRING", "description": "A concise, runnable code suggestion or refactoring hint."}
        },
        "required": ["severity", "issueType", "description", "suggestedFix"]
    }
}


def load_configuration(filepath: str = 'config.json') -> Dict[str, Any]:
    """Loads model settings and custom policies from the configuration file."""
    try:
        # In a real system, we might need a dynamic way to find config.json
        with open(filepath, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file '{filepath}' not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{filepath}'.")
        return {}


def _call_llm_for_review(prompt: str, policy_context: List[str]) -> List[Dict[str, str]]:
    """
    REAL implementation of the API call with exponential backoff and structured output.
    Returns a list of structured review issues (dictionaries).
    """
    system_prompt = (
        "You are PeerBot, an AI code review specialist. Your task is to analyze the "
        "provided code diff against the team's custom policies and standard best practices. "
        "Strictly adhere to the output JSON schema. Do not include any text outside the JSON block. "
        "Focus on security, complexity, and custom policy violations defined here: "
        f"{', '.join(policy_context)}"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": ISSUE_SCHEMA
        }
    }

    headers = {'Content-Type': 'application/json'}
    # In a real deployment, the API key would be passed securely in the URL or headers
    url = f"{API_ENDPOINT}?key={API_KEY}" 
    
    for attempt in range(MAX_RETRIES):
        try:
            print(f"Attempting API call (Retry {attempt + 1}/{MAX_RETRIES})...")
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)

            result = response.json()
            
            # Extract and parse the JSON string from the response
            json_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            if not json_text:
                raise ValueError("LLM response content was empty or malformed.")

            # The response is a JSON string, which we must parse into a list of dictionaries
            issues_list = json.loads(json_text)
            return issues_list
        
        except (requests.exceptions.RequestException, ValueError, json.JSONDecodeError) as e:
            print(f"API Error on attempt {attempt + 1}: {e}")
            if attempt + 1 == MAX_RETRIES:
                print("Max retries reached. Failing.")
                raise
            
            # Exponential backoff
            delay = INITIAL_DELAY * (2 ** attempt)
            print(f"Waiting for {delay:.2f} seconds before retrying...")
            time.sleep(delay)
            
    return [] # Should not be reached if max retries fails


def summarize_pull_request(pr_title: str, pr_description: str, changes_diff: str) -> str:
    """
    Generates a concise, actionable summary of the PR for the human reviewer.
    (Kept simple and non-LLM based for separation of concerns, focusing LLM on issues)
    """
    # Simple keyword-based extraction simulation
    keywords = set()
    for word in ["auth", "database", "login", "payment", "refactor", "ui", "bugfix"]:
        if word in changes_diff.lower() or word in pr_description.lower():
            keywords.add(word)

    summary_text = (
        f"**PeerBot PR Summary (AI-Generated)**\n"
        f"**Core Action:** {pr_title}\n"
        f"**Purpose:** {pr_description[:80]}...\n"
        f"**System Impact:** Affects {', '.join(keywords) if keywords else 'minor utility'} components.\n"
        f"**Recommended Focus:** Logic flaws and security vulnerabilities. Style issues are pre-vetted."
    )
    return summary_text


def execute_peerbot_review(pr_data: Dict[str, str], config: Dict[str, Any]) -> Dict[str, Any]:
    """Orchestrates the full PeerBot review process."""
    if not config:
        return {"error": "Failed to load configuration. Review halted."}

    pr_title = pr_data['title']
    pr_description = pr_data['description']
    changes_diff = pr_data['diff']
    custom_policies = config.get('custom_policies', [])

    print("\n[STEP 1/3] Generating PR Summary...")
    summary = summarize_pull_request(pr_title, pr_description, changes_diff)

    print("\n[STEP 2/3] Calling REAL LLM API for Structured Review...")
    prompt = (
        f"Analyze the following code changes (diff) against the provided team policies. "
        f"Identify all issues related to security, complexity, and custom style violations. "
        f"Diff:\n---\n{changes_diff}"
    )
    
    review_issues: List[Dict[str, str]] = []
    try:
        review_issues = _call_llm_for_review(prompt, custom_policies)
    except Exception as e:
        print(f"Critical error during LLM review: {e}")
        return {"error": f"LLM Review Failed: {e}", "summary": summary, "status": "Partial Review"}

    print("\n[STEP 3/3] Finalizing Review Report...")
    
    # Analyze the structured issues to determine severity ranking
    severity_ranking = {
        "HIGH": sum(1 for issue in review_issues if issue.get('severity') == 'HIGH'),
        "MEDIUM": sum(1 for issue in review_issues if issue.get('severity') == 'MEDIUM'),
        "TRIVIAL": sum(1 for issue in review_issues if issue.get('severity') == 'TRIVIAL'),
        "TOTAL": len(review_issues)
    }

    return {
        "summary": summary,
        "review_issues": review_issues, # Now a list of dictionaries, not a single string
        "severity_ranking": severity_ranking,
        "status": "Review Complete"
    }


if __name__ == '__main__':
    # --- Mock PR Data for Demonstration ---
    mock_pr_data = {
        "title": "Feature: Implement new user authentication service",
        "description": "This PR adds a new service for user authentication, including login and registration handlers.",
        "diff": """
            // file: services/auth.js
            +const user_id = req.body.user_id; // Simulates a policy violation (snake_case)
            +localStorage.setItem('auth_token', token); // Simulates a security violation
            -function old_login(user) { ... } // Old function removed
            +function handle_auth(user) {
            +  if (user.is_admin) {
            +    if (user.status === 'ACTIVE') {
            +      // Complex logic block here
            +    } else {
            +      // more complex logic
            +    }
            +  } else if (user.is_guest) {
            +    // more nested logic (Simulates Complexity Check)
            +  }
            +  return true;
            +}
        """
    }

    # Load config and run the simulation
    peerbot_config = load_configuration()
    if peerbot_config:
        print(f"Loaded {len(peerbot_config.get('custom_policies', []))} custom policies.")
        review_report = execute_peerbot_review(mock_pr_data, peerbot_config)

        print("\n=============================================")
        print("          PEERBOT FINAL REVIEW REPORT        ")
        print("=============================================")

        if 'error' in review_report:
            print(f"!!! CRITICAL ERROR: {review_report['error']}")
        
        print(review_report['summary'])

        print("\n--- DETAILED COMMENTS (Structured, for PR Thread Insertion) ---")
        if review_report.get('review_issues'):
            for i, issue in enumerate(review_report['review_issues']):
                print(f"\n[ISSUE {i+1} / {issue.get('severity', 'UNKNOWN')}] ({issue.get('issueType', 'N/A')})")
                print(f"Description: {issue.get('description', 'No description provided.')}")
                print(f"Suggested Fix: {issue.get('suggestedFix', 'N/A')}")
        else:
            print("No structured issues found (either review failed or code is clean).")


        print("\n--- SEVERITY RANKING (For Human Reviewer Prioritization) ---")
        for severity, count in review_report['severity_ranking'].items():
            print(f"- {severity}: {count} critical items")

        print("=============================================")
        print(f"Review Status: {review_report['status']}")
    else:
        print("\nPeerBot execution failed due to configuration error.")
