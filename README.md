# Guess Quest - AI Interview Assistant

An interactive interview application powered by CrewAI and local Ollama endpoints. This application conducts progressive difficulty interviews where AI agents ask questions one by one, provide corrections and feedback, and increase complexity based on your performance.

## Features

- 🎯 **Progressive Difficulty**: Questions start easy and adapt based on your answers
- 🤖 **AI-Powered Agents**: Uses CrewAI for intelligent interview management
- 🏠 **Local AI**: Runs entirely on your local Ollama installation for privacy
- 📊 **Real-time Feedback**: Get immediate evaluation and suggestions
- 📚 **Multiple Topics**: Support for programming, ML, system design, and custom topics
- 💬 **Interactive Chat**: Natural conversation flow with the AI interviewer

## Prerequisites

1. **Python 3.8+**
2. **Ollama**: Download and install from [ollama.ai](https://ollama.ai)
3. **A compatible model**: We recommend `llama2`, `mistral`, or `codellama`

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/wickkiey/guess-quest.git
   cd guess-quest
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Ollama:**
   ```bash
   # Install Ollama (if not already installed)
   # Follow instructions at https://ollama.ai
   
   # Pull a model (choose one or more)
   ollama pull llama2        # General purpose
   ollama pull mistral       # Fast and efficient
   ollama pull codellama     # Code-focused
   
   # Start Ollama (usually runs automatically)
   ollama serve
   ```

## Usage

1. **Start the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

2. **Configure the application:**
   - Connect to your local Ollama instance (default: http://localhost:11434)
   - Select an available model
   - Choose an interview topic

3. **Begin your interview:**
   - Click "Start Interview"
   - Answer questions as they're presented
   - Receive real-time feedback and corrections
   - Progress through increasing difficulty levels

## Available Topics

- Python Programming
- JavaScript Development  
- Machine Learning
- Data Science
- Web Development
- System Design
- Database Design
- DevOps
- Cybersecurity
- Custom Topic (specify your own)

## How It Works

The application uses CrewAI to orchestrate two main agents:

1. **Technical Interviewer**: Generates progressive difficulty questions based on the selected topic
2. **Answer Evaluator**: Provides detailed feedback, corrections, and determines when to increase difficulty

The agents communicate with your local Ollama installation to leverage LLM capabilities while keeping everything private and local.

## Troubleshooting

**Ollama Connection Issues:**
- Ensure Ollama is running: `ollama serve`
- Check if models are available: `ollama list`
- Verify the URL (default: http://localhost:11434)

**Performance Issues:**
- Try smaller models like `mistral` for faster responses
- Ensure adequate system resources for the chosen model

**Model Not Available:**
- Pull the desired model: `ollama pull <model-name>`
- Wait for the download to complete before using

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
