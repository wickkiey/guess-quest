"""
CrewAI agents for conducting interviews with progressive difficulty
"""

from crewai import Agent, Task, Crew
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from typing import Optional, List, Any
from ollama_client import OllamaClient


class OllamaLLM(LLM):
    """Custom LangChain LLM wrapper for Ollama"""
    
    client: OllamaClient = None
    model: str = "llama2"
    
    def __init__(self, client: OllamaClient, model: str = "llama2"):
        super().__init__(client=client, model=model)
        self.client = client
        self.model = model
    
    @property
    def _llm_type(self) -> str:
        return "ollama"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        return self.client.generate(self.model, prompt)


class InterviewCrew:
    """CrewAI setup for conducting interviews"""
    
    def __init__(self, ollama_client: OllamaClient, model: str = "llama2"):
        """
        Initialize interview crew
        
        Args:
            ollama_client: Ollama client instance
            model: Model name to use
        """
        self.llm = OllamaLLM(client=ollama_client, model=model)
        self.difficulty_level = 1
        self.max_difficulty = 5
        self.topic = ""
        self.conversation_history = []
        
    def create_interviewer_agent(self) -> Agent:
        """Create interviewer agent"""
        return Agent(
            role='Technical Interviewer',
            goal=f'Conduct a progressive technical interview on {self.topic} with increasing difficulty',
            backstory=f"""You are an experienced technical interviewer specializing in {self.topic}. 
            You ask questions one by one, starting with basic concepts and gradually increasing complexity.
            You provide constructive feedback and corrections when needed, and you adapt the difficulty
            based on the candidate's responses. You are patient, encouraging, and thorough.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def create_evaluator_agent(self) -> Agent:
        """Create answer evaluator agent"""
        return Agent(
            role='Answer Evaluator',
            goal='Evaluate candidate responses and provide detailed feedback',
            backstory="""You are an expert evaluator who analyzes candidate responses for accuracy,
            completeness, and understanding. You provide specific feedback on what was correct,
            what needs improvement, and suggestions for better answers. You also recommend
            whether to increase difficulty or provide additional clarification.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def generate_question_task(self, interviewer: Agent) -> Task:
        """Create task for generating next question"""
        context = ""
        if self.conversation_history:
            context = f"Previous conversation: {self.conversation_history[-3:]}"  # Last 3 exchanges
            
        return Task(
            description=f"""Generate the next interview question for {self.topic} at difficulty level {self.difficulty_level}/5.
            Current context: {context}
            
            Requirements:
            - Ask ONE specific question appropriate for difficulty level {self.difficulty_level}
            - Build upon previous questions if any
            - Make it progressively challenging
            - Focus on practical understanding
            - Keep questions clear and focused
            
            Return only the question, no additional formatting.""",
            agent=interviewer,
            expected_output="A single, well-crafted interview question"
        )
    
    def evaluate_answer_task(self, evaluator: Agent, question: str, answer: str) -> Task:
        """Create task for evaluating an answer"""
        return Task(
            description=f"""Evaluate this candidate's answer:
            
            Question: {question}
            Answer: {answer}
            Current difficulty level: {self.difficulty_level}/5
            
            Provide:
            1. Score (1-10)
            2. What was correct
            3. What needs improvement
            4. Suggestions for better answer
            5. Whether to increase difficulty (YES/NO)
            
            Format your response as:
            SCORE: X/10
            CORRECT: [what was right]
            IMPROVE: [what needs work]
            SUGGESTION: [how to improve]
            INCREASE_DIFFICULTY: YES/NO""",
            agent=evaluator,
            expected_output="Structured evaluation with score and feedback"
        )
    
    def run_question_generation(self) -> str:
        """Generate next question"""
        interviewer = self.create_interviewer_agent()
        task = self.generate_question_task(interviewer)
        
        crew = Crew(
            agents=[interviewer],
            tasks=[task],
            verbose=False
        )
        
        result = crew.kickoff()
        return str(result).strip()
    
    def run_answer_evaluation(self, question: str, answer: str) -> dict:
        """Evaluate answer and return structured feedback"""
        evaluator = self.create_evaluator_agent()
        task = self.evaluate_answer_task(evaluator, question, answer)
        
        crew = Crew(
            agents=[evaluator],
            tasks=[task],
            verbose=False
        )
        
        result = str(crew.kickoff()).strip()
        
        # Parse the structured response
        feedback = {
            'score': 0,
            'correct': '',
            'improve': '',
            'suggestion': '',
            'increase_difficulty': False
        }
        
        lines = result.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('SCORE:'):
                try:
                    score_text = line.split(':', 1)[1].strip()
                    feedback['score'] = int(score_text.split('/')[0])
                except:
                    feedback['score'] = 5
            elif line.startswith('CORRECT:'):
                feedback['correct'] = line.split(':', 1)[1].strip()
            elif line.startswith('IMPROVE:'):
                feedback['improve'] = line.split(':', 1)[1].strip()
            elif line.startswith('SUGGESTION:'):
                feedback['suggestion'] = line.split(':', 1)[1].strip()
            elif line.startswith('INCREASE_DIFFICULTY:'):
                answer_text = line.split(':', 1)[1].strip().upper()
                feedback['increase_difficulty'] = answer_text == 'YES'
        
        return feedback
    
    def set_topic(self, topic: str):
        """Set interview topic"""
        self.topic = topic
        
    def increase_difficulty(self):
        """Increase difficulty level"""
        if self.difficulty_level < self.max_difficulty:
            self.difficulty_level += 1
            
    def add_to_history(self, question: str, answer: str):
        """Add Q&A to conversation history"""
        self.conversation_history.append({
            'question': question,
            'answer': answer,
            'difficulty': self.difficulty_level
        })
        
    def reset_interview(self):
        """Reset interview state"""
        self.difficulty_level = 1
        self.conversation_history = []