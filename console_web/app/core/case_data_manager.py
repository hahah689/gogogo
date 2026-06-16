import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

# Directory to store user sessions data
USER_DATA_DIR = "./case_data"

def initialize_case_data_dir():
    """Initialize the user data directory if it doesn't exist."""
    if not os.path.exists(USER_DATA_DIR):
        os.makedirs(USER_DATA_DIR)

def get_case_data_file(session_id: str) -> str:
    """Get the file path for a specific user's data."""
    return os.path.join(USER_DATA_DIR, f"{session_id}.json")

def load_case_data(session_id: str) -> Dict[str, Any]:
    """Load user data from the individual JSON file."""
    initialize_case_data_dir()
    user_file = get_case_data_file(session_id)
    
    if not os.path.exists(user_file):
        return {}
    
    try:
        with open(user_file, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_case_data(session_id: str, data: Dict[str, Any]):
    """Save user data to the individual JSON file."""
    user_file = get_case_data_file(session_id)
    with open(user_file, "w") as f:
        json.dump(data, f, indent=2)

def get_user_session(session_id: str) -> Dict[str, Any]:
    """Get a user session by session ID, creating a new one if it doesn't exist."""
    case_data = load_case_data(session_id)
    
    if not case_data:
        # Initialize a new session with default values
        case_data = {
            "session_id": session_id,
            "chat_history": [],
            "pending_action": None,
            "user_decision": None,
            "operation_log": [],  # Add operation log storage
            "created_at": datetime.now().isoformat()
        }
        save_case_data(session_id, case_data)
    
    return case_data

def update_user_chat_history(session_id: str, user_message: str, ai_response: str):
    """Update the chat history for a user session."""
    case_data = load_case_data(session_id)
    
    if not case_data:
        case_data = {
            "session_id": session_id,
            "chat_history": [],
            "pending_action": None,
            "user_decision": None,
            "operation_log": [],  # Add operation log storage
            "created_at": datetime.now().isoformat()
        }
    
    # Add the new message pair to the chat history
    case_data["chat_history"].append({
        "timestamp": datetime.now().isoformat(),
        "user_message": user_message,
        "ai_response": ai_response
    })
    
    save_case_data(session_id, case_data)

def set_pending_action(session_id: str, action_details: Dict[str, Any]):
    """Set a pending action for a user session."""
    case_data = load_case_data(session_id)
    
    if not case_data:
        case_data = {
            "session_id": session_id,
            "chat_history": [],
            "pending_action": None,
            "user_decision": None,
            "operation_log": [],  # Add operation log storage
            "created_at": datetime.now().isoformat()
        }
    
    case_data["pending_action"] = action_details
    save_case_data(session_id, case_data)

def get_pending_action(session_id: str) -> Optional[Dict[str, Any]]:
    """Get the pending action for a user session."""
    session_data = get_user_session(session_id)
    return session_data.get("pending_action")

def clear_pending_action(session_id: str):
    """Clear the pending action for a user session."""
    case_data = load_case_data(session_id)
    if case_data:
        case_data["pending_action"] = None
        save_case_data(session_id, case_data)

def set_user_decision(session_id: str, decision: str):
    """Set the user decision for a pending action."""
    case_data = load_case_data(session_id)
    
    if not case_data:
        case_data = {
            "session_id": session_id,
            "chat_history": [],
            "pending_action": None,
            "user_decision": None,
            "operation_log": [],  # Add operation log storage
            "created_at": datetime.now().isoformat()
        }
    
    case_data["user_decision"] = decision
    save_case_data(session_id, case_data)

def get_user_decision(session_id: str) -> Optional[str]:
    """Get the user decision for a pending action."""
    session_data = get_user_session(session_id)
    return session_data.get("user_decision")

def clear_user_decision(session_id: str):
    """Clear the user decision for a pending action."""
    case_data = load_case_data(session_id)
    if case_data:
        case_data["user_decision"] = None
        save_case_data(session_id, case_data)

def add_operation_log(session_id: str, log_entry: Dict[str, Any]):
    """Add an operation log entry to a user session."""
    case_data = load_case_data(session_id)
    
    if not case_data:
        case_data = {
            "session_id": session_id,
            "chat_history": [],
            "pending_action": None,
            "user_decision": None,
            "operation_log": [],  # Add operation log storage
            "created_at": datetime.now().isoformat()
        }
    
    # Add timestamp if not provided
    if "timestamp" not in log_entry:
        log_entry["timestamp"] = datetime.now().isoformat()
    
    case_data["operation_log"].append(log_entry)
    save_case_data(session_id, case_data)

def get_operation_log(session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get the operation log for a user session, with optional limit."""
    session_data = get_user_session(session_id)
    log = session_data.get("operation_log", [])
    
    # Return the most recent entries up to the limit
    if limit > 0 and len(log) > limit:
        return log[-limit:]
    return log

def clear_operation_log(session_id: str):
    """Clear the operation log for a user session."""
    case_data = load_case_data(session_id)
    if case_data:
        case_data["operation_log"] = []
        save_case_data(session_id, case_data)

