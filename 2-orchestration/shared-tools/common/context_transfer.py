"""
Context Transfer Utilities

Helper functions for preserving context when transferring between agents.

Reference: Pattern #7 - Handoff Orchestration
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json


@dataclass
class ContextPackage:
    """
    Structured context package for agent handoffs.

    Preserves all relevant information when transferring a task from one agent to another.
    """

    # Source and destination
    source_agent: str
    target_agent: str
    handoff_reason: str

    # Core context
    original_request: str
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    current_state: Dict[str, Any] = field(default_factory=dict)

    # Customer information
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_tier: Optional[str] = None  # "standard", "premium", "vip"

    # Issue tracking
    issue_summary: str = ""
    issue_category: Optional[str] = None
    priority: str = "medium"  # "low", "medium", "high", "urgent"

    # Resolution attempts
    previous_attempts: List[str] = field(default_factory=list)
    actions_taken: List[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert context package to dictionary."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data

    def to_json(self) -> str:
        """Serialize context package to JSON."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextPackage':
        """Create context package from dictionary."""
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)

    def add_conversation_turn(self, speaker: str, message: str):
        """Add a conversation turn to the history."""
        self.conversation_history.append({
            "speaker": speaker,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })

    def add_attempt(self, description: str):
        """Record a resolution attempt."""
        self.previous_attempts.append(description)

    def add_action(self, action: str):
        """Record an action taken."""
        self.actions_taken.append(action)

    def get_summary(self) -> str:
        """Get a human-readable summary of the context."""
        summary_lines = [
            f"Handoff from {self.source_agent} to {self.target_agent}",
            f"Reason: {self.handoff_reason}",
            f"Priority: {self.priority}",
            ""
        ]

        if self.customer_name:
            summary_lines.append(f"Customer: {self.customer_name}")
            if self.customer_tier:
                summary_lines.append(f"Tier: {self.customer_tier}")
            summary_lines.append("")

        summary_lines.append(f"Issue: {self.issue_summary}")

        if self.previous_attempts:
            summary_lines.append(f"\nPrevious attempts ({len(self.previous_attempts)}):")
            for attempt in self.previous_attempts:
                summary_lines.append(f"  - {attempt}")

        if self.actions_taken:
            summary_lines.append(f"\nActions taken ({len(self.actions_taken)}):")
            for action in self.actions_taken:
                summary_lines.append(f"  - {action}")

        return "\n".join(summary_lines)


def preserve_context(
    source_agent: str,
    target_agent: str,
    request: str,
    reason: str,
    **kwargs
) -> ContextPackage:
    """
    Create a context package for agent handoff.

    Args:
        source_agent: Name of the agent initiating the handoff
        target_agent: Name of the receiving agent
        request: Original user request
        reason: Reason for the handoff
        **kwargs: Additional context data

    Returns:
        ContextPackage ready for transfer

    Example:
        >>> context = preserve_context(
        ...     source_agent="L1Support",
        ...     target_agent="FinancialSpecialist",
        ...     request="I need a refund for order #12345",
        ...     reason="Financial transaction requires specialist approval",
        ...     customer_name="John Doe",
        ...     priority="high"
        ... )
    """
    return ContextPackage(
        source_agent=source_agent,
        target_agent=target_agent,
        original_request=request,
        handoff_reason=reason,
        customer_name=kwargs.get('customer_name'),
        customer_email=kwargs.get('customer_email'),
        customer_id=kwargs.get('customer_id'),
        customer_tier=kwargs.get('customer_tier'),
        issue_summary=kwargs.get('issue_summary', request[:200]),
        issue_category=kwargs.get('issue_category'),
        priority=kwargs.get('priority', 'medium'),
        conversation_history=kwargs.get('conversation_history', []),
        current_state=kwargs.get('current_state', {}),
        previous_attempts=kwargs.get('previous_attempts', []),
        actions_taken=kwargs.get('actions_taken', []),
        metadata=kwargs.get('metadata', {})
    )


def restore_context(context_data: Dict[str, Any]) -> ContextPackage:
    """
    Restore a context package from serialized data.

    Args:
        context_data: Dictionary containing context data

    Returns:
        Reconstructed ContextPackage

    Example:
        >>> context_dict = {...}
        >>> context = restore_context(context_dict)
    """
    return ContextPackage.from_dict(context_data)


def merge_contexts(contexts: List[ContextPackage]) -> ContextPackage:
    """
    Merge multiple context packages (e.g., from multiple handoffs).

    Args:
        contexts: List of context packages to merge

    Returns:
        Merged context package
    """
    if not contexts:
        raise ValueError("At least one context required")

    if len(contexts) == 1:
        return contexts[0]

    # Use the most recent context as base
    merged = contexts[-1]

    # Merge conversation history from all contexts
    all_conversations = []
    for ctx in contexts:
        all_conversations.extend(ctx.conversation_history)
    merged.conversation_history = sorted(
        all_conversations,
        key=lambda x: x.get('timestamp', '')
    )

    # Merge attempts and actions
    all_attempts = []
    all_actions = []
    for ctx in contexts:
        all_attempts.extend(ctx.previous_attempts)
        all_actions.extend(ctx.actions_taken)

    merged.previous_attempts = all_attempts
    merged.actions_taken = all_actions

    # Add metadata about the merge
    merged.metadata['merged_from'] = [ctx.source_agent for ctx in contexts]
    merged.metadata['merge_count'] = len(contexts)

    return merged


def extract_key_points(context: ContextPackage) -> List[str]:
    """
    Extract key points from a context package for quick review.

    Args:
        context: Context package to analyze

    Returns:
        List of key points
    """
    key_points = []

    # Customer tier
    if context.customer_tier in ["premium", "vip"]:
        key_points.append(f"⭐ {context.customer_tier.upper()} customer")

    # Priority
    if context.priority in ["high", "urgent"]:
        key_points.append(f"🔴 {context.priority.upper()} priority")

    # Issue category
    if context.issue_category:
        key_points.append(f"📁 Category: {context.issue_category}")

    # Attempt count
    if context.previous_attempts:
        key_points.append(f"🔄 {len(context.previous_attempts)} previous attempt(s)")

    # Escalation chain
    if len(context.conversation_history) > 5:
        key_points.append(f"💬 Extended conversation ({len(context.conversation_history)} turns)")

    return key_points
