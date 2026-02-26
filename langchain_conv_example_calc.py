"""
AI Agent for Number Summation using LangGraph Chat API
This agent can extract two numbers from natural language input and return their sum.
"""

import os
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.runnables import RunnableConfig
#from langchain_oci import ChatOCIGenerativeAI
from langchain_oci.chat_models.oci_generative_ai import ChatOCIGenAI
from langchain_oci.common.auth import OCIAuthType
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import Annotated, TypedDict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class AgentState(TypedDict):
    """State for the number summation agent"""
    messages: Annotated[List[BaseMessage], add_messages]
    extracted_numbers: Optional[Tuple[float, float]]
    sum_result: Optional[float]
    error_message: Optional[str]
    calculation_complete: bool

@dataclass
class NumberExtractionResult:
    """Result of number extraction"""
    success: bool
    numbers: Optional[Tuple[float, float]]
    error_message: Optional[str] = None

class NumberSumAgent:
    """AI Agent for summing two numbers using LangGraph"""

    print("val Service Endpoint\t",os.getenv("OCI_SERVICE_ENDPOINT"))
    print("val API  Key\t",os.getenv("API_KEY") [::-1])
    def __init__(self, model_name: str = "openai.gpt-oss-120b"):
        """Initialize the agent with OCI Generative AI model"""
        self.llm = ChatOCIGenAI(
            model_id=model_name,
            compartment_id="ocid1.compartment.oc1..aaaaaaaamjxynn55q2nddbeur3zwnkzis4yogjtqkd6zzyoaxxx",
            #temperature=0,
            #service_endpoint=os.getenv("OCI_SERVICE_ENDPOINT"),
            #auth_type=os.getenv("OCI_AUTH_TYPE", "API_KEY"),
            #auth_profile=os.getenv("OCI_AUTH_PROFILE", "DEFAULT"),
            auth_type=os.getenv("OCI_AUTH_TYPE", "INSTANCE_PRINCIPAL"),
        )
        self.graph = self._build_graph()
        self.memory = MemorySaver()
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("extract_numbers", self._extract_numbers)
        workflow.add_node("calculate_sum", self._calculate_sum)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("handle_error", self._handle_error)
        
        # Add edges
        workflow.set_entry_point("extract_numbers")
        workflow.add_conditional_edges(
            "extract_numbers",
            self._should_calculate_or_error,
            {
                "calculate": "calculate_sum",
                "error": "handle_error"
            }
        )
        workflow.add_edge("calculate_sum", "generate_response")
        workflow.add_edge("generate_response", END)
        workflow.add_edge("handle_error", END)
        
        return workflow.compile()
    
    def _extract_numbers(self, state: AgentState) -> AgentState:
        """Extract two numbers from the user's message"""
        try:
            last_message = state["messages"][-1]
            user_input = last_message.content
            
            logger.info(f"Extracting numbers from: {user_input}")
            
            # Use LLM to extract numbers more robustly
            extraction_prompt = f"""
            Extract exactly two numbers from the following text and return them as a comma-separated list.
            If you cannot find exactly two numbers, respond with "ERROR: <reason>".
            
            Text: {user_input}
            
            Examples:
            "What is 5 + 3?" -> "5,3"
            "Add 10.5 and 15.2" -> "10.5,15.2"
            "Calculate the sum of 7 and 8" -> "7,8"
            "I want to add twenty and thirty" -> "ERROR: Cannot extract numbers"
            """
            
            response = self.llm.invoke(extraction_prompt)
            extraction_result = response.content.strip()
            
            if extraction_result.startswith("ERROR:"):
                state["error_message"] = extraction_result
                state["extracted_numbers"] = None
                logger.warning(f"Extraction failed: {extraction_result}")
            else:
                # Parse the extracted numbers
                try:
                    numbers_str = extraction_result.split(',')
                    if len(numbers_str) == 2:
                        num1 = float(numbers_str[0].strip())
                        num2 = float(numbers_str[1].strip())
                        state["extracted_numbers"] = (num1, num2)
                        logger.info(f"Successfully extracted numbers: {num1}, {num2}")
                    else:
                        state["error_message"] = "Could not extract exactly two numbers"
                        state["extracted_numbers"] = None
                except ValueError as e:
                    state["error_message"] = f"Invalid number format: {str(e)}"
                    state["extracted_numbers"] = None
            
        except Exception as e:
            logger.error(f"Error in number extraction: {str(e)}")
            state["error_message"] = f"Error extracting numbers: {str(e)}"
            state["extracted_numbers"] = None
        
        return state
    
    def _calculate_sum(self, state: AgentState) -> AgentState:
        """Calculate the sum of extracted numbers"""
        try:
            numbers = state["extracted_numbers"]
            if numbers and len(numbers) == 2:
                num1, num2 = numbers
                sum_result = num1 + num2
                state["sum_result"] = sum_result
                state["calculation_complete"] = True
                logger.info(f"Calculated sum: {num1} + {num2} = {sum_result}")
            else:
                state["error_message"] = "No valid numbers available for calculation"
                state["calculation_complete"] = False
                
        except Exception as e:
            logger.error(f"Error in calculation: {str(e)}")
            state["error_message"] = f"Error calculating sum: {str(e)}"
            state["calculation_complete"] = False
        
        return state
    
    def _generate_response(self, state: AgentState) -> AgentState:
        """Generate a natural language response"""
        try:
            numbers = state["extracted_numbers"]
            sum_result = state["sum_result"]
            
            response_prompt = f"""
            Create a friendly, conversational response for the following calculation:
            Numbers: {numbers[0]} and {numbers[1]}
            Sum: {sum_result}
            
            Make it sound natural and helpful. Show the calculation clearly.
            """
            
            response = self.llm.invoke(response_prompt)
            ai_message = AIMessage(content=response.content)
            state["messages"].append(ai_message)
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            fallback_response = f"The sum of {numbers[0]} and {numbers[1]} is {sum_result}."
            ai_message = AIMessage(content=fallback_response)
            state["messages"].append(ai_message)
        
        return state
    
    def _handle_error(self, state: AgentState) -> AgentState:
        """Handle errors and provide helpful error messages"""
        error_message = state.get("error_message", "An unknown error occurred")
        
        error_response = f"""
        I'm sorry, I couldn't process your request. {error_message}
        
        Please try again with a clear request like:
        - "What is 5 + 3?"
        - "Add 10 and 15"
        - "Calculate the sum of 7 and 8"
        
        Make sure to include exactly two numbers in your request.
        """
        
        ai_message = AIMessage(content=error_response.strip())
        state["messages"].append(ai_message)
        
        return state
    
    def _should_calculate_or_error(self, state: AgentState) -> str:
        """Determine whether to proceed with calculation or handle error"""
        if state.get("extracted_numbers") and state.get("error_message") is None:
            return "calculate"
        else:
            return "error"
    
    def chat(self, message: str, thread_id: str = "default") -> str:
        """Main chat interface"""
        try:
            # Create initial state
            initial_state = {
                "messages": [HumanMessage(content=message)],
                "extracted_numbers": None,
                "sum_result": None,
                "error_message": None,
                "calculation_complete": False
            }
            
            # Run the graph
            config = RunnableConfig(configurable={"thread_id": thread_id})
            result = self.graph.invoke(initial_state, config)
            
            # Return the last AI message
            ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
            if ai_messages:
                return ai_messages[-1].content
            else:
                return "I'm sorry, I couldn't generate a response."
                
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return f"An error occurred: {str(e)}"
    
    def get_conversation_history(self, thread_id: str = "default") -> List[BaseMessage]:
        """Get conversation history for a thread"""
        try:
            config = RunnableConfig(configurable={"thread_id": thread_id})
            # Note: In a real implementation, you'd use the checkpoint saver to get history
            return []
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []

def main():
    """Main function to run the agent interactively"""
    print("🤖 Number Summation AI Agent")
    print("I can help you add two numbers! Just ask me something like:")
    print("- 'What is 5 + 3?'")
    print("- 'Add 10 and 15'")
    print("- 'Calculate the sum of 7 and 8'")
    print("\nType 'quit' to exit.\n")
    
    agent = NumberSumAgent()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye! 👋")
                break
            
            if not user_input:
                continue
            
            response = agent.chat(user_input)
            print(f"Agent: {response}")
            
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()

