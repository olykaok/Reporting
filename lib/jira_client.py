import requests
import logging
from typing import Dict, Any, Optional, List
from requests.auth import AuthBase
from urllib.parse import urljoin
from dotenv import load_dotenv
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BearerAuth(AuthBase):
    """Custom authentication class for Bearer token."""
    
    def __init__(self, token: str):
        self.token = token
        
    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        r.headers['Authorization'] = f'Bearer {self.token}'
        return r

class JiraClient:
    """Client for interacting with Jira API."""
    
    def __init__(self, base_url: str, auth_token: str, max_results_per_page: int = 100):
        self.base_url = base_url.rstrip('/')
        self.auth = BearerAuth(auth_token)
        self.session = requests.Session()
        self.issue_cache: Dict[str, Dict[str, Any]] = {}
        self.max_results_per_page = max_results_per_page
        
    def get_issue(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """
        Get the full data structure of a Jira issue.
        
        Args:
            issue_key: Jira issue key (e.g., "GRA-444")
            
        Returns:
            Full issue data structure or None if not found
        """
        if issue_key in self.issue_cache:
            return self.issue_cache[issue_key]
            
        url = f'{self.base_url}/rest/api/2/issue/{issue_key}'
        
        try:
            response = self.session.get(url, auth=self.auth, timeout=10)
            response.raise_for_status()
            
            issue_data = response.json()
            summary = issue_data.get('fields', {}).get('summary')
            if summary:
                self.issue_cache[issue_key] = issue_data
                return issue_data
                
            logger.error('Issue %s found, but has no summary field', issue_key)
            return None
            
        except requests.exceptions.RequestException as re:
            logger.error('Failed to fetch issue %s. Error: %s', issue_key, str(re))
            return None
            
    def get_issue_summary(self, issue_key: str) -> Optional[str]:
        """
        Get the summary of a Jira issue.
        
        Args:
            issue_key: Jira issue key (e.g., "GRA-444")
            
        Returns:
            Summary of the issue or None if not found
        """
        issue_data = self.get_issue(issue_key)
        if issue_data:
            return issue_data.get('fields', {}).get('summary')
        return None
            
    def create_worklog(self, issue_key: str, work_data: Dict[str, Any]) -> bool:
        """
        Create a worklog entry for a Jira issue.
        
        Args:
            issue_key: Jira issue key
            work_data: Dictionary with timeSpent and started fields
            
        Returns:
            True if worklog was created, False otherwise
        """
        url = f'{self.base_url}/rest/api/2/issue/{issue_key}/worklog'
        response = None
        
        try:
            print(issue_key, work_data)
            response = self.session.post(url, auth=self.auth, json=work_data, timeout=10)
            response.raise_for_status()
            # time.sleep(2)
            return True
            
        except requests.exceptions.RequestException as re:
            logger.error('Failed to create worklog for %s. Error: %s %s', 
                        issue_key, str(re), response.text if response is not None and hasattr(response, 'text') else '')
            return False
            
    def search_issues_by_jql(self, jql_query: str, max_results_per_page: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for issues using JQL query with pagination.
        
        Args:
            jql_query: JQL query string
            max_results_per_page: Override default max results per page (optional)
            
        Returns:
            List of all issues matching the JQL query
        """
        start_at = 0
        max_results = max_results_per_page or self.max_results_per_page
        all_issues = []
        total_issues = 0
        
        while True:
            params = {
                'jql': jql_query,
                'startAt': start_at,
                'maxResults': max_results
            }
            
            try:
                url = f'{self.base_url}/rest/api/2/search'
                response = self.session.get(url, auth=self.auth, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                issues = data.get('issues', [])
                
                # Get total count on first iteration
                if total_issues == 0:
                    total_issues = data.get('total', 0)
                    if total_issues == 0:
                        print("Найдено 0 задач")
                        break
                
                if not issues:
                    break
                    
                all_issues.extend(issues)
                
                # Display progress
                current_end = start_at + len(issues)
                print(f"Обработка задач Jira: {start_at + 1}-{current_end} из {total_issues}", end='\r')
                time.sleep(2)

                # Check if there are more issues
                if current_end >= total_issues:
                    break
                    
                start_at += len(issues)
                
            except requests.exceptions.RequestException as e:
                logger.error('Failed to search issues. JQL: %s, Error: %s', jql_query, str(e))
                break
        
        if total_issues > 0:
            print(f"Завершено: обработано {len(all_issues)} задач")
                
        return all_issues
