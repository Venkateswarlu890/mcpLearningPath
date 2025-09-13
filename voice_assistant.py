"""
Voice-Based Virtual Assistant for Mock Interviews
Implements the three-stage process: pre-processing, classification, and feature extraction
"""

import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
import re
import json
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
import os

class VoiceCommandType(Enum):
    """Types of voice commands the assistant can recognize"""
    START_INTERVIEW = "start_interview"
    NEXT_QUESTION = "next_question"
    REPEAT_QUESTION = "repeat_question"
    EVALUATE_ANSWER = "evaluate_answer"
    END_INTERVIEW = "end_interview"
    HELP = "help"
    PREPARE_QUESTIONS = "prepare_questions"
    UNKNOWN = "unknown"

@dataclass
class VoiceCommand:
    """Represents a recognized voice command"""
    command_type: VoiceCommandType
    confidence: float
    raw_text: str
    parameters: Dict[str, Any] = None

class VoicePreprocessor:
    """Stage 1: Pre-processing - Clean and normalize voice input"""
    
    def __init__(self):
        self.noise_patterns = [
            r'\b(um|uh|er|ah)\b',  # Filler words
            r'\b(like|you know|basically|actually)\b',  # Common filler phrases
            r'\s+',  # Multiple spaces
            r'[^\w\s]',  # Special characters except spaces
        ]
        
    def preprocess_text(self, text: str) -> str:
        """Clean and normalize the input text"""
        if not text:
            return ""
            
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove filler words and phrases
        for pattern in self.noise_patterns:
            text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from the text"""
        # Simple keyword extraction - in production, use more sophisticated NLP
        keywords = []
        
        # Interview-related keywords
        interview_keywords = [
            'start', 'begin', 'interview', 'question', 'next', 'repeat',
            'evaluate', 'answer', 'end', 'finish', 'help', 'assistance'
        ]
        
        # Technical keywords
        technical_keywords = [
            'python', 'java', 'javascript', 'react', 'node', 'database',
            'algorithm', 'data structure', 'machine learning', 'ai'
        ]
        
        words = text.split()
        for word in words:
            if word in interview_keywords or word in technical_keywords:
                keywords.append(word)
        
        return keywords

class VoiceClassifier:
    """Stage 2: Classification - Classify voice commands into categories"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.classifier = MultinomialNB()
        self.is_trained = False
        
        # Training data for command classification
        self.training_data = {
            VoiceCommandType.START_INTERVIEW: [
                "start interview", "begin interview", "let's start", "start the interview",
                "begin the interview", "ready to start", "start now"
            ],
            VoiceCommandType.NEXT_QUESTION: [
                "next question", "next", "continue", "move to next", "next please",
                "ask next question", "proceed to next"
            ],
            VoiceCommandType.REPEAT_QUESTION: [
                "repeat question", "repeat", "say again", "can you repeat",
                "repeat the question", "what was the question"
            ],
            VoiceCommandType.EVALUATE_ANSWER: [
                "evaluate my answer", "how did I do", "rate my answer", "feedback",
                "evaluate answer", "assess my response"
            ],
            VoiceCommandType.END_INTERVIEW: [
                "end interview", "finish interview", "stop interview", "end now",
                "conclude interview", "finish up"
            ],
            VoiceCommandType.HELP: [
                "help", "what can you do", "commands", "assistance", "guide me",
                "how to use", "what are the options"
            ],
            VoiceCommandType.PREPARE_QUESTIONS: [
                "prepare questions on python", "create interview questions about data science",
                "ask questions for frontend", "generate questions for machine learning",
                "prepare questions on algorithms", "make some interview questions about sql",
                "give me questions on react"
            ]
        }
        
        self._train_classifier()
    
    def _train_classifier(self):
        """Train the classifier with predefined command patterns"""
        texts = []
        labels = []
        
        for command_type, examples in self.training_data.items():
            for example in examples:
                texts.append(example)
                labels.append(command_type.value)
        
        # Add some negative examples
        negative_examples = [
            "hello", "good morning", "thank you", "yes", "no", "maybe",
            "I think", "probably", "definitely", "absolutely"
        ]
        
        for example in negative_examples:
            texts.append(example)
            labels.append(VoiceCommandType.UNKNOWN.value)
        
        # Train the classifier
        X = self.vectorizer.fit_transform(texts)
        self.classifier.fit(X, labels)
        self.is_trained = True
    
    def classify_command(self, text: str) -> VoiceCommand:
        """Classify the input text into a voice command"""
        if not self.is_trained:
            return VoiceCommand(VoiceCommandType.UNKNOWN, 0.0, text)
        
        # Preprocess the text
        preprocessor = VoicePreprocessor()
        cleaned_text = preprocessor.preprocess_text(text)
        
        if not cleaned_text:
            return VoiceCommand(VoiceCommandType.UNKNOWN, 0.0, text)
        
        # Vectorize and classify
        X = self.vectorizer.transform([cleaned_text])
        prediction = self.classifier.predict(X)[0]
        confidence = max(self.classifier.predict_proba(X)[0])
        
        try:
            command_type = VoiceCommandType(prediction)
        except ValueError:
            command_type = VoiceCommandType.UNKNOWN
        
        return VoiceCommand(
            command_type=command_type,
            confidence=confidence,
            raw_text=text,
            parameters=self._extract_parameters(cleaned_text, command_type)
        )
    
    def _extract_parameters(self, text: str, command_type: VoiceCommandType) -> Dict[str, Any]:
        """Extract parameters from the command text"""
        parameters = {}
        
        if command_type == VoiceCommandType.START_INTERVIEW:
            # Extract interview type or role if mentioned
            if 'technical' in text:
                parameters['type'] = 'technical'
            elif 'behavioral' in text:
                parameters['type'] = 'behavioral'
        elif command_type == VoiceCommandType.PREPARE_QUESTIONS:
            # Attempt to extract topic/role after keywords like on/about/for/in
            m = re.search(r"(?:on|about|for|in)\s+([a-zA-Z0-9_\-\s]+)$", text)
            if m:
                parameters['topic'] = m.group(1).strip()
        
        return parameters

class VoiceFeatureExtractor:
    """Stage 3: Feature Extraction - Extract meaningful features from voice input"""
    
    def __init__(self):
        self.feature_history = []
    
    def extract_features(self, text: str, audio_data: Optional[bytes] = None) -> Dict[str, Any]:
        """Extract features from voice input"""
        features = {
            'text_length': len(text),
            'word_count': len(text.split()),
            'has_question_words': self._has_question_words(text),
            'sentiment': self._analyze_sentiment(text),
            'complexity': self._analyze_complexity(text),
            'keywords': VoicePreprocessor().extract_keywords(text),
            'timestamp': time.time()
        }
        
        # Add audio features if available
        if audio_data:
            features.update(self._extract_audio_features(audio_data))
        
        self.feature_history.append(features)
        return features
    
    def _has_question_words(self, text: str) -> bool:
        """Check if text contains question words"""
        question_words = ['what', 'how', 'why', 'when', 'where', 'which', 'who']
        return any(word in text.lower() for word in question_words)
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'perfect']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'wrong', 'incorrect']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _analyze_complexity(self, text: str) -> str:
        """Analyze text complexity"""
        word_count = len(text.split())
        avg_word_length = sum(len(word) for word in text.split()) / word_count if word_count > 0 else 0
        
        if word_count < 5 or avg_word_length < 4:
            return 'simple'
        elif word_count < 15 and avg_word_length < 6:
            return 'moderate'
        else:
            return 'complex'
    
    def _extract_audio_features(self, audio_data: bytes) -> Dict[str, Any]:
        """Extract features from audio data (placeholder implementation)"""
        # In a real implementation, you would analyze audio properties
        # like pitch, volume, speaking rate, etc.
        return {
            'audio_length': len(audio_data),
            'has_audio': True
        }

class VoiceAssistant:
    """Main Voice Assistant class that orchestrates the three-stage process"""
    
    def __init__(self, mock_interview_system=None):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.mock_interview = mock_interview_system
        
        # Initialize the three-stage pipeline
        self.preprocessor = VoicePreprocessor()
        self.classifier = VoiceClassifier()
        self.feature_extractor = VoiceFeatureExtractor()
        
        # Voice settings
        self.setup_voice_settings()
        
        # Command queue for processing
        self.command_queue = queue.Queue()
        self.is_listening = False
        self.callbacks = {}
        
        # Calibrate microphone
        self._calibrate_microphone()
    
    def setup_voice_settings(self):
        """Configure text-to-speech settings"""
        voices = self.tts_engine.getProperty('voices')
        if voices:
            # Try to use a female voice if available
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
        
        # Set speech rate and volume
        self.tts_engine.setProperty('rate', 180)  # Speed of speech
        self.tts_engine.setProperty('volume', 0.9)  # Volume level
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
    
    def speak(self, text: str):
        """Convert text to speech"""
        def speak_thread():
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        
        thread = threading.Thread(target=speak_thread)
        thread.daemon = True
        thread.start()
    
    def listen(self, timeout: int = 5, phrase_time_limit: int = 5) -> Optional[str]:
        """Listen for voice input and return transcribed text"""
        try:
            with self.microphone as source:
                # Listen for audio with timeout
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
            # Recognize speech using Google's service
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Could not request results from speech recognition service; {e}")
            return None
    
    def process_voice_input(self, text: str) -> VoiceCommand:
        """Process voice input through the three-stage pipeline"""
        # Stage 1: Pre-processing
        cleaned_text = self.preprocessor.preprocess_text(text)
        
        # Stage 2: Classification
        command = self.classifier.classify_command(cleaned_text)
        
        # Stage 3: Feature Extraction
        features = self.feature_extractor.extract_features(cleaned_text)
        command.features = features
        
        return command
    
    def execute_command(self, command: VoiceCommand) -> str:
        """Execute the recognized voice command"""
        if command.command_type == VoiceCommandType.START_INTERVIEW:
            return self._handle_start_interview(command)
        elif command.command_type == VoiceCommandType.NEXT_QUESTION:
            return self._handle_next_question(command)
        elif command.command_type == VoiceCommandType.REPEAT_QUESTION:
            return self._handle_repeat_question(command)
        elif command.command_type == VoiceCommandType.EVALUATE_ANSWER:
            return self._handle_evaluate_answer(command)
        elif command.command_type == VoiceCommandType.END_INTERVIEW:
            return self._handle_end_interview(command)
        elif command.command_type == VoiceCommandType.HELP:
            return self._handle_help(command)
        elif command.command_type == VoiceCommandType.PREPARE_QUESTIONS:
            return self._handle_prepare_questions(command)
        else:
            return "I didn't understand that command. Please try again or say 'help' for available commands."
    
    def _handle_start_interview(self, command: VoiceCommand) -> str:
        """Handle start interview command"""
        if not self.mock_interview:
            return "Mock interview system not available. Please initialize it first."
        
        response = "Starting the interview. Please wait while I prepare your first question."
        self.speak(response)
        return response
    
    def _handle_next_question(self, command: VoiceCommand) -> str:
        """Handle next question command"""
        if not self.mock_interview:
            return "Mock interview system not available."
        
        # Get next question from mock interview system
        question_data = self.mock_interview.get_next_question()
        response = f"Here's your next question: {question_data['question']}"
        self.speak(response)
        return response
    
    def _handle_repeat_question(self, command: VoiceCommand) -> str:
        """Handle repeat question command"""
        if not self.mock_interview:
            return "Mock interview system not available."
        
        # Get current question and repeat it
        if hasattr(self.mock_interview, 'current_question') and self.mock_interview.current_question:
            response = f"Let me repeat the question: {self.mock_interview.current_question['question']}"
        else:
            response = "No current question available. Please start the interview first."
        
        self.speak(response)
        return response
    
    def _handle_evaluate_answer(self, command: VoiceCommand) -> str:
        """Handle evaluate answer command"""
        if not self.mock_interview:
            return "Mock interview system not available."
        
        response = "Please provide your answer first, then I can evaluate it for you."
        self.speak(response)
        return response
    
    def _handle_end_interview(self, command: VoiceCommand) -> str:
        """Handle end interview command"""
        if not self.mock_interview:
            return "Mock interview system not available."
        
        response = "Ending the interview. Generating your final report now."
        self.speak(response)
        return response

    def _handle_prepare_questions(self, command: VoiceCommand) -> str:
        """Generate interview questions based on user's requested topic via voice."""
        if not self.mock_interview:
            return "Mock interview system not available."
        topic = (command.parameters or {}).get('topic') or command.raw_text
        try:
            questions = self.mock_interview.generate_questions_from_topic(topic=topic, num_questions=5)
            if not questions:
                return "I couldn't generate questions right now. Please try again."
            # Speak the first question and return the list
            self.speak(f"First question: {questions[0]}")
            formatted = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
            return f"Prepared questions for '{topic}':\n{formatted}"
        except Exception as e:
            return f"Error preparing questions: {str(e)}"
    
    def _handle_help(self, command: VoiceCommand) -> str:
        """Handle help command"""
        help_text = """
        Available voice commands:
        - Say 'start interview' to begin a new interview
        - Say 'next question' to get the next question
        - Say 'repeat question' to hear the current question again
        - Say 'evaluate answer' to get feedback on your answer
        - Say 'end interview' to finish and get your report
        - Say 'help' to hear this list again
        """
        self.speak(help_text)
        return help_text
    
    def start_continuous_listening(self, callback: Optional[Callable] = None):
        """Start continuous voice listening"""
        self.is_listening = True
        
        def listen_loop():
            while self.is_listening:
                try:
                    text = self.listen(timeout=1)
                    if text:
                        command = self.process_voice_input(text)
                        response = self.execute_command(command)
                        
                        if callback:
                            callback(command, response)
                        else:
                            print(f"Command: {command.command_type.value}")
                            print(f"Response: {response}")
                
                except Exception as e:
                    print(f"Error in voice processing: {e}")
                    time.sleep(1)
        
        thread = threading.Thread(target=listen_loop)
        thread.daemon = True
        thread.start()
    
    def stop_continuous_listening(self):
        """Stop continuous voice listening"""
        self.is_listening = False
    
    def set_mock_interview_system(self, mock_interview_system):
        """Set the mock interview system for integration"""
        self.mock_interview = mock_interview_system

# Example usage and testing
if __name__ == "__main__":
    # Create voice assistant
    assistant = VoiceAssistant()
    
    print("Voice Assistant initialized. Say 'help' to see available commands.")
    
    # Test the three-stage process
    test_commands = [
        "start interview",
        "next question please",
        "repeat the question",
        "evaluate my answer",
        "end interview",
        "help me"
    ]
    
    for test_command in test_commands:
        print(f"\nTesting: '{test_command}'")
        command = assistant.process_voice_input(test_command)
        print(f"Classified as: {command.command_type.value}")
        print(f"Confidence: {command.confidence:.2f}")
        print(f"Features: {command.features}")
        response = assistant.execute_command(command)
        print(f"Response: {response}")
