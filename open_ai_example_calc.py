#!/usr/bin/env python3
"""
AI Math Agent
An intelligent agent that uses OpenAI's Responses API for mathematical operations
with advanced reasoning, conversation memory, and adaptive learning.
"""

import os
import re
import json
import sys
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import colorama
from colorama import Fore, Style
from dotenv import load_dotenv
import openai
from openai import OpenAI
from oci_openai import OciOpenAI, OciSessionAuth, OciInstancePrincipalAuth, OciUserPrincipalAuth, OciResourcePrincipalAuth


# Initialize colorama for colored output
colorama.init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_math_agent.log'),
        #logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent operational states."""
    IDLE = "idle"
    PROCESSING = "processing"
    REASONING = "reasoning"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ConversationMessage:
    """Represents a conversation message."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CalculationResult:
    """Represents a calculation result with metadata."""
    expression: str
    result: float
    reasoning: str
    confidence: float
    verification_passed: bool
    timestamp: datetime
    tokens_used: int


class ConversationManager:
    """Manages conversation memory and context."""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.messages: List[ConversationMessage] = []
        self.context_variables: Dict[str, Any] = {}
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a message to conversation history."""
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata
        )
        self.messages.append(message)
        
        # Trim history if needed
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
    
    def get_context(self) -> List[Dict[str, str]]:
        """Get conversation context for API calls."""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages
        ]
    
    def set_context_variable(self, key: str, value: Any):
        """Set a context variable."""
        self.context_variables[key] = value
    
    def get_context_variable(self, key: str, default: Any = None) -> Any:
        """Get a context variable."""
        return self.context_variables.get(key, default)


class MathematicalEngine:
    """Handles mathematical reasoning and verification."""
    
    @staticmethod
    def extract_numbers_from_text(text: str) -> List[float]:
        """Extract all numbers from text."""
        pattern = r'-?\d+\.?\d*'
        matches = re.findall(pattern, text)
        return [float(match) for match in matches]
    
    @staticmethod
    def parse_math_expression(expression: str) -> Tuple[str, List[float]]:
        """Parse a mathematical expression and extract operation and numbers."""
        expression = expression.lower().strip()
        
        # Identify the operation
        operations = {
            'add': '+', 'plus': '+', 'sum': '+', 'addition': '+',
            'subtract': '-', 'minus': '-', 'difference': '-',
            'multiply': '*', 'times': '*', 'product': '*', 'multiplication': '*',
            'divide': '/', 'divided by': '/', 'division': '/'
        }
        
        operation = None
        for word, op in operations.items():
            if word in expression:
                operation = op
                break
        
        # Extract numbers
        numbers = MathematicalEngine.extract_numbers_from_text(expression)
        
        if operation and len(numbers) >= 2:
            # Create a simple expression
            result_expr = f"{numbers[0]} {operation} {numbers[1]}"
            return result_expr, numbers[:2]
        
        return expression, numbers
    
    @staticmethod
    def calculate_locally(expression: str) -> Optional[float]:
        """Calculate expression locally for verification."""
        try:
            # Simple and safe evaluation for basic operations
            if '+' in expression:
                parts = expression.split('+')
                return float(parts[0].strip()) + float(parts[1].strip())
            elif '-' in expression:
                parts = expression.split('-')
                return float(parts[0].strip()) - float(parts[1].strip())
            elif '*' in expression:
                parts = expression.split('*')
                return float(parts[0].strip()) * float(parts[1].strip())
            elif '/' in expression:
                parts = expression.split('/')
                denominator = float(parts[1].strip())
                if denominator == 0:
                    return None
                return float(parts[0].strip()) / denominator
        except Exception:
            pass
        return None


class ResponseProcessor:
    """Processes and validates OpenAI responses."""
    
    @staticmethod
    def extract_result_from_response(response_text: str) -> Optional[float]:
        """Extract numerical result from AI response."""
        # Look for patterns like "result is X", "answer: X", etc.
        patterns = [
            r'(?:result|answer|equals?|is)\s*:?\s*(-?\d+\.?\d*)',
            r'(-?\d+\.?\d*)\s*(?:is the result|is the answer)',
            r'final answer\s*:?\s*(-?\d+\.?\d*)',
            r'(-?\d+\.?\d*)$'  # Last number in response
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        # Fallback: extract any numbers
        numbers = MathematicalEngine.extract_numbers_from_text(response_text)
        if numbers:
            return numbers[-1]  # Return the last number found
        
        return None
    
    @staticmethod
    def extract_reasoning(response_text: str) -> str:
        """Extract reasoning steps from AI response."""
        # Look for reasoning patterns
        reasoning_patterns = [
            r'(?:step|reasoning|explanation|because|since)[^:]*:\s*(.*?)(?:\n|$)',
            r'(?:i think|i believe|i calculate)[^:]*:\s*(.*?)(?:\n|$)'
        ]
        
        for pattern in reasoning_patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return response_text.strip()


class ErrorHandler:
    """Handles errors and recovery strategies."""
    
    @staticmethod
    def handle_api_error(error: Exception) -> str:
        """Handle OpenAI API errors."""
        if isinstance(error, openai.RateLimitError):
            return "Rate limit exceeded. Please wait a moment and try again."
        elif isinstance(error, openai.AuthenticationError):
            return "Authentication failed. Please check your API key."
        elif isinstance(error, openai.APIError):
            return f"API error occurred: {error}"
        else:
            return f"Unexpected error: {error}"
    
    @staticmethod
    def calculate_confidence(ai_result: float, local_result: float, tolerance: float = 0.0001) -> float:
        """Calculate confidence score based on verification."""
        if local_result is None:
            return 0.5  # Medium confidence when no verification possible
        
        diff = abs(ai_result - local_result)
        if diff <= tolerance:
            return 1.0  # High confidence
        elif diff <= tolerance * 10:
            return 0.7  # Medium-high confidence
        elif diff <= tolerance * 100:
            return 0.4  # Low-medium confidence
        else:
            return 0.1  # Low confidence


class AIMathAgent:
    """Intelligent AI agent for mathematical operations."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the AI Math Agent."""
        self.state = AgentState.IDLE
        self.conversation_manager = ConversationManager()
        self.math_engine = MathematicalEngine()
        self.response_processor = ResponseProcessor()
        self.error_handler = ErrorHandler()
        
        demo_mode=os.getenv('DEMO_MODE')
        print(f"{Fore.GREEN}Demo Mode for Authentication is: {demo_mode}{Style.RESET_ALL}")
        if (demo_mode == 'API'):
          # Initialize OpenAI client
          if api_key is None:
              load_dotenv()
              api_key = os.getenv('OPENAI_API_KEY')
      
              if not api_key:
                raise ValueError("OpenAI API key is required")

              INF_URL="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/20231130/actions/v1"
              print(f"{Fore.GREEN}API Key is : {api_key}{Style.RESET_ALL}")
              print(f"{Fore.GREEN}Inference URL is : {api_key}{Style.RESET_ALL}")
              self.client = OpenAI(api_key=api_key,base_url=INF_URL)
        elif (demo_mode == 'IP'):

          self.client = OciOpenAI(
                     region="us-chicago-1",
                     auth=OciInstancePrincipalAuth(),
                     compartment_id="ocid1.compartment.oc1..aaaaaaaamjxynn55q2nddbeur3zwnkzis4yogjtqkd6zzyxxx",
                  )
        elif (demo_mode == 'SP'):

          self.client = OciOpenAI(
                     region="us-chicago-1",
                     auth=OciSessionAuth(profile_name="gendemo"),
                     compartment_id="ocid1.compartment.oc1..aaaaaaaamjxynn55q2nddbeur3zwnkzis4yogjtqkd6zzyxxx",
                  )
        else:

          self.client = OciOpenAI(
                     region="us-chicago-1",
                     auth=OciUserPrincipalAuth(profile_name="DEFAULT"),
                     compartment_id="ocid1.compartment.oc1..aaaaaaaamjxynn55q2nddbeur3zwnkzis4yogjtqkd6zzyxxx",
                  )

        print(f"{Fore.GREEN}End of Auth Details Display{Style.RESET_ALL}")
        print(self.client)
        self.total_tokens_used = 0
        self.calculation_history: List[CalculationResult] = []
        
        logger.info("AI Math Agent initialized successfully")
    
    async def process_request(self, user_input: str) -> CalculationResult:
        """Process a user request for mathematical operation."""
        self.state = AgentState.PROCESSING
        logger.info(f"Processing request: {user_input}")
        
        try:
            # Add user message to conversation
            self.conversation_manager.add_message("user", user_input)
            
            # Parse the mathematical expression
            expression, numbers = self.math_engine.parse_math_expression(user_input)
            #print("SD: ",expression)
            #print("SD Numbers: ",numbers)
            
            if len(numbers) < 2:
                raise ValueError("Please provide at least two numbers for calculation")
            
            # Get AI reasoning and calculation
            self.state = AgentState.REASONING
            ai_response = await self._get_ai_calculation(expression, numbers)
            
            # Extract result and reasoning
            result = self.response_processor.extract_result_from_response(ai_response)
            reasoning = self.response_processor.extract_reasoning(ai_response)
            
            if result is None:
                raise ValueError("Could not extract result from AI response")
            
            # Verify result locally
            self.state = AgentState.VERIFYING
            local_result = self.math_engine.calculate_locally(expression)
            verification_passed = local_result is not None and abs(result - local_result) < 0.0001
            
            # Calculate confidence
            confidence = self.error_handler.calculate_confidence(result, local_result)
            
            # Create result object
            calculation_result = CalculationResult(
                expression=expression,
                result=result,
                reasoning=reasoning,
                confidence=confidence,
                verification_passed=verification_passed,
                timestamp=datetime.now(),
                tokens_used=self._estimate_tokens_used(ai_response)
            )
            
            # Add to history
            self.calculation_history.append(calculation_result)
            
            # Add assistant response to conversation
            response_text = self._format_response(calculation_result, local_result)
            self.conversation_manager.add_message("assistant", response_text)
            
            self.state = AgentState.COMPLETED
            logger.info(f"Calculation completed: {expression} = {result}")
            
            return calculation_result
            
        except Exception as e:
            self.state = AgentState.ERROR
            error_msg = self.error_handler.handle_api_error(e)
            logger.error(f"Error processing request: {error_msg}")
            raise ValueError(error_msg)
    
    async def _get_ai_calculation(self, expression: str, numbers: List[float]) -> str:
        """Get calculation from OpenAI with reasoning."""
        context = self.conversation_manager.get_context()
        
        system_prompt = """You are a mathematical AI assistant specialized in arithmetic operations. 
        When given a mathematical expression, you must:
        1. Show step-by-step reasoning
        2. Perform the calculation accurately
        3. Provide the final numerical result clearly
        4. Be concise but thorough in your explanation
        
        Format your response to include the reasoning process and end with the numerical result."""
        
        user_prompt = f"""Please calculate this expression and show your reasoning: {expression}
        
        Numbers involved: {numbers}
        
        Provide step-by-step reasoning and give the final result."""
        
        # Build messages for API call
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(context[-5:])  # Include last 5 messages for context
        messages.append({"role": "user", "content": user_prompt})
        
        response = self.client.responses.create(
            model="openai.gpt-oss-120b",
            input=messages,
            #max_tokens=300,
            #temperature=0.1  # Low temperature for consistent math
            stream=False,
            store=False,
        )
        #print(response.output_text.strip())
        
        #return response.choices[0].message.content
        return response.output_text
    
    def _format_response(self, result: CalculationResult, local_result: Optional[float]) -> str:
        """Format the response for display."""
        response = f"I calculated {result.expression} = {result.result}\n\n"
        response += f"Reasoning: {result.reasoning}\n\n"
        response += f"Confidence: {result.confidence:.1%}"
        
        if local_result is not None:
            response += f"\nVerification: ✅ Passed" if result.verification_passed else f"\nVerification: ⚠️  Local result: {local_result}"
        
        return response
    
    def _estimate_tokens_used(self, response_text: str) -> int:
        """Estimate tokens used in response."""
        # Rough estimation: ~4 characters per token
        return len(response_text) // 4
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        return {
            "total_calculations": len(self.calculation_history),
            "total_tokens_used": sum(r.tokens_used for r in self.calculation_history),
            "average_confidence": sum(r.confidence for r in self.calculation_history) / len(self.calculation_history) if self.calculation_history else 0,
            "verification_rate": sum(1 for r in self.calculation_history if r.verification_passed) / len(self.calculation_history) if self.calculation_history else 0,
            "current_state": self.state.value
        }
    
    def export_history(self, filename: str):
        """Export calculation history to file."""
        history_data = [asdict(result) for result in self.calculation_history]
        # Convert datetime objects to strings for JSON serialization
        for item in history_data:
            item['timestamp'] = item['timestamp'].isoformat()
        
        with open(filename, 'w') as f:
            json.dump(history_data, f, indent=2)
        
        logger.info(f"History exported to {filename}")


class InteractiveInterface:
    """Interactive command-line interface for the AI Math Agent."""
    
    def __init__(self, agent: AIMathAgent):
        self.agent = agent
        self.running = True
    
    def display_welcome(self):
        """Display welcome message."""
        print(f"\n{Fore.CYAN}🤖 AI Math Agent - Advanced Mathematical Assistant{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}I can help you with mathematical operations using AI reasoning!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Commands: 'stats', 'history', 'export', 'help', 'quit'{Style.RESET_ALL}")
        print("-" * 60)
    
    def display_help(self):
        """Display help information."""
        help_text = f"""
{Fore.CYAN}AI Math Agent Help:{Style.RESET_ALL}

{Fore.YELLOW}Usage Examples:{Style.RESET_ALL}
• "add 5 and 3"
• "what's 10 plus 15?"
• "multiply 7 by 6"
• "divide 20 by 4"

{Fore.YELLOW}Commands:{Style.RESET_ALL}
• stats - Show session statistics
• history - Show calculation history
• export <filename> - Export history to file
• help - Show this help
• quit - Exit the agent

{Fore.YELLOW}Features:{Style.RESET_ALL}
• Step-by-step reasoning
• Result verification
• Conversation memory
• Confidence scoring
"""
        print(help_text)
    
    async def run(self):
        """Run the interactive interface."""
        self.display_welcome()
        
        while self.running:
            try:
                # Get user input
                user_input = input(f"\n{Fore.BLUE}You:{Style.RESET_ALL} ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    self.running = False
                    break
                elif user_input.lower() == 'help':
                    self.display_help()
                    continue
                elif user_input.lower() == 'stats':
                    self.display_stats()
                    continue
                elif user_input.lower() == 'history':
                    self.display_history()
                    continue
                elif user_input.lower().startswith('export'):
                    parts = user_input.split(maxsplit=1)
                    filename = parts[1] if len(parts) > 1 else f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    self.agent.export_history(filename)
                    print(f"{Fore.GREEN}✅ History exported to {filename}{Style.RESET_ALL}")
                    continue
                
                # Process mathematical request
                print(f"{Fore.YELLOW}🤔 Processing...{Style.RESET_ALL}")
                
                try:
                    result = await self.agent.process_request(user_input)
                    self.display_result(result)
                    
                except ValueError as e:
                    print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
                self.running = False
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
                logger.error(f"Unexpected error in interface: {e}")
    
    def display_result(self, result: CalculationResult):
        """Display calculation result with formatting."""
        print(f"\n{Fore.CYAN}🧮 Calculation Result:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Expression: {result.expression}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Result: {result.result}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Reasoning: {result.reasoning}{Style.RESET_ALL}")
        
        # Confidence indicator
        confidence_color = Fore.GREEN if result.confidence >= 0.8 else Fore.YELLOW if result.confidence >= 0.5 else Fore.RED
        print(f"{confidence_color}Confidence: {result.confidence:.1%}{Style.RESET_ALL}")
        
        # Verification status
        if result.verification_passed:
            print(f"{Fore.GREEN}✅ Verification: Passed{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}⚠️  Verification: Failed{Style.RESET_ALL}")
    
    def display_stats(self):
        """Display session statistics."""
        stats = self.agent.get_session_stats()
        print(f"\n{Fore.CYAN}📊 Session Statistics:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Total Calculations: {stats['total_calculations']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Total Tokens Used: {stats['total_tokens_used']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Average Confidence: {stats['average_confidence']:.1%}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Verification Rate: {stats['verification_rate']:.1%}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Current State: {stats['current_state']}{Style.RESET_ALL}")
    
    def display_history(self):
        """Display calculation history."""
        if not self.agent.calculation_history:
            print(f"{Fore.YELLOW}No calculation history yet.{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}📜 Calculation History:{Style.RESET_ALL}")
        for i, result in enumerate(self.agent.calculation_history[-5:], 1):  # Show last 5
            print(f"{Fore.GREEN}{i}. {result.expression} = {result.result}{Style.RESET_ALL}")
            print(f"   {Fore.YELLOW}Confidence: {result.confidence:.1%} | Verified: {'✅' if result.verification_passed else '❌'}{Style.RESET_ALL}")


async def main():
    """Main function to run the AI Math Agent."""
    try:
        # Initialize agent
        agent = AIMathAgent()
        
        # Run interactive interface
        interface = InteractiveInterface(agent)
        await interface.run()
        
    #except ValueError as e:
    #    print(f"{Fore.RED}❌ Configuration Error: {e}{Style.RESET_ALL}")
    #    print(f"{Fore.YELLOW}Please ensure your OPENAI_API_KEY is set in the .env file{Style.RESET_ALL}")
    #    sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        logger.error(f"Fatal error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

