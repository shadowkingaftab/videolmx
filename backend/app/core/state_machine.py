"""State machine implementation."""

from typing import Dict, Any, Set, List, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class Transition:
    """State transition definition."""
    from_state: str
    to_state: str
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    action: Optional[Callable[[Dict[str, Any]], None]] = None


class StateMachine:
    """State machine for managing state transitions."""
    
    def __init__(self, initial_state: str):
        self.initial_state = initial_state
        self.current_state = initial_state
        self.states: Set[str] = {initial_state}
        self.transitions: List[Transition] = []
        self.entry_actions: Dict[str, List[Callable]] = {}
        self.exit_actions: Dict[str, List[Callable]] = {}
        self._context: Dict[str, Any] = {}
    
    def add_state(self, state: str) -> "StateMachine":
        """Add a state."""
        self.states.add(state)
        return self
    
    def add_transition(
        self,
        from_state: str,
        to_state: str,
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
        action: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> "StateMachine":
        """Add a transition."""
        if from_state not in self.states:
            self.states.add(from_state)
        if to_state not in self.states:
            self.states.add(to_state)
        
        self.transitions.append(Transition(from_state, to_state, condition, action))
        return self
    
    def add_entry_action(self, state: str, action: Callable) -> "StateMachine":
        """Add entry action for a state."""
        if state not in self.entry_actions:
            self.entry_actions[state] = []
        self.entry_actions[state].append(action)
        return self
    
    def add_exit_action(self, state: str, action: Callable) -> "StateMachine":
        """Add exit action for a state."""
        if state not in self.exit_actions:
            self.exit_actions[state] = []
        self.exit_actions[state].append(action)
        return self
    
    def set_context(self, context: Dict[str, Any]) -> None:
        """Set context for state machine."""
        self._context = context
    
    async def transition(self, to_state: str) -> bool:
        """Transition to a new state."""
        # Find matching transition
        for transition in self.transitions:
            if (
                transition.from_state == self.current_state and
                transition.to_state == to_state
            ):
                # Check condition
                if transition.condition:
                    if not transition.condition(self._context):
                        return False
                
                # Execute exit actions
                for action in self.exit_actions.get(self.current_state, []):
                    await action(self._context)
                
                # Execute transition action
                if transition.action:
                    await transition.action(self._context)
                
                # Update state
                self.current_state = to_state
                
                # Execute entry actions
                for action in self.entry_actions.get(to_state, []):
                    await action(self._context)
                
                return True
        
        return False
    
    def get_current_state(self) -> str:
        """Get current state."""
        return self.current_state
    
    def can_transition(self, to_state: str) -> bool:
        """Check if transition is possible."""
        for transition in self.transitions:
            if (
                transition.from_state == self.current_state and
                transition.to_state == to_state
            ):
                return True
        return False
    
    def get_available_transitions(self) -> List[str]:
        """Get available transitions from current state."""
        transitions = []
        for transition in self.transitions:
            if transition.from_state == self.current_state:
                if not transition.condition or transition.condition(self._context):
                    transitions.append(transition.to_state)
        return transitions
    
    def reset(self) -> None:
        """Reset state machine to initial state."""
        self.current_state = self.initial_state
        self._context = {}