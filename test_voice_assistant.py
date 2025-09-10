"""
Test script for the Voice-Based Virtual Assistant
Demonstrates the three-stage process: pre-processing, classification, and feature extraction
"""

from voice_assistant import VoiceAssistant, VoicePreprocessor, VoiceClassifier, VoiceFeatureExtractor, VoiceCommandType
import time

def test_preprocessing():
    """Test Stage 1: Pre-processing"""
    print("=" * 50)
    print("Testing Stage 1: Pre-processing")
    print("=" * 50)
    
    preprocessor = VoicePreprocessor()
    
    test_inputs = [
        "um, start interview please",
        "uh, next question, you know",
        "repeat the question, basically",
        "evaluate my answer, like, how did I do?",
        "end interview now"
    ]
    
    for text in test_inputs:
        cleaned = preprocessor.preprocess_text(text)
        keywords = preprocessor.extract_keywords(text)
        print(f"Original: '{text}'")
        print(f"Cleaned:  '{cleaned}'")
        print(f"Keywords: {keywords}")
        print("-" * 30)

def test_classification():
    """Test Stage 2: Classification"""
    print("=" * 50)
    print("Testing Stage 2: Classification")
    print("=" * 50)
    
    classifier = VoiceClassifier()
    
    test_commands = [
        "start interview",
        "next question please",
        "repeat the question",
        "evaluate my answer",
        "end interview",
        "help me",
        "hello there",  # Should be classified as unknown
        "what's the weather"  # Should be classified as unknown
    ]
    
    for command_text in test_commands:
        command = classifier.classify_command(command_text)
        print(f"Input: '{command_text}'")
        print(f"Classified as: {command.command_type.value}")
        print(f"Confidence: {command.confidence:.2f}")
        print(f"Parameters: {command.parameters}")
        print("-" * 30)

def test_feature_extraction():
    """Test Stage 3: Feature Extraction"""
    print("=" * 50)
    print("Testing Stage 3: Feature Extraction")
    print("=" * 50)
    
    feature_extractor = VoiceFeatureExtractor()
    
    test_texts = [
        "start interview",
        "I think this is a very complex technical question about machine learning algorithms",
        "good answer",
        "what is the difference between lists and tuples in Python?",
        "bad terrible awful"
    ]
    
    for text in test_texts:
        features = feature_extractor.extract_features(text)
        print(f"Text: '{text}'")
        print(f"Features:")
        for key, value in features.items():
            if key != 'timestamp':
                print(f"  {key}: {value}")
        print("-" * 30)

def test_voice_assistant():
    """Test the complete Voice Assistant"""
    print("=" * 50)
    print("Testing Complete Voice Assistant")
    print("=" * 50)
    
    # Create voice assistant (without mock interview for testing)
    assistant = VoiceAssistant()
    
    test_commands = [
        "start interview",
        "next question",
        "repeat question",
        "evaluate answer",
        "end interview",
        "help",
        "unknown command"
    ]
    
    for command_text in test_commands:
        print(f"Testing command: '{command_text}'")
        
        # Process through three-stage pipeline
        command = assistant.process_voice_input(command_text)
        response = assistant.execute_command(command)
        
        print(f"Command Type: {command.command_type.value}")
        print(f"Confidence: {command.confidence:.2f}")
        print(f"Response: {response}")
        print("-" * 30)

def test_voice_commands():
    """Test specific voice command handling"""
    print("=" * 50)
    print("Testing Voice Command Handling")
    print("=" * 50)
    
    assistant = VoiceAssistant()
    
    # Test different variations of the same command
    start_commands = [
        "start interview",
        "begin interview",
        "let's start",
        "start the interview",
        "ready to start"
    ]
    
    print("Testing 'start interview' variations:")
    for cmd in start_commands:
        command = assistant.process_voice_input(cmd)
        print(f"'{cmd}' -> {command.command_type.value} (confidence: {command.confidence:.2f})")
    
    print("\nTesting 'next question' variations:")
    next_commands = [
        "next question",
        "next",
        "continue",
        "move to next",
        "ask next question"
    ]
    
    for cmd in next_commands:
        command = assistant.process_voice_input(cmd)
        print(f"'{cmd}' -> {command.command_type.value} (confidence: {command.confidence:.2f})")

def demonstrate_three_stage_process():
    """Demonstrate the complete three-stage process"""
    print("=" * 60)
    print("Demonstrating Complete Three-Stage Process")
    print("=" * 60)
    
    # Sample voice input
    voice_input = "um, next question please, you know"
    
    print(f"Original Voice Input: '{voice_input}'")
    print()
    
    # Stage 1: Pre-processing
    preprocessor = VoicePreprocessor()
    cleaned_text = preprocessor.preprocess_text(voice_input)
    keywords = preprocessor.extract_keywords(voice_input)
    
    print("Stage 1 - Pre-processing:")
    print(f"  Cleaned Text: '{cleaned_text}'")
    print(f"  Keywords: {keywords}")
    print()
    
    # Stage 2: Classification
    classifier = VoiceClassifier()
    command = classifier.classify_command(cleaned_text)
    
    print("Stage 2 - Classification:")
    print(f"  Command Type: {command.command_type.value}")
    print(f"  Confidence: {command.confidence:.2f}")
    print(f"  Parameters: {command.parameters}")
    print()
    
    # Stage 3: Feature Extraction
    feature_extractor = VoiceFeatureExtractor()
    features = feature_extractor.extract_features(cleaned_text)
    
    print("Stage 3 - Feature Extraction:")
    for key, value in features.items():
        if key != 'timestamp':
            print(f"  {key}: {value}")
    print()
    
    # Execute command
    assistant = VoiceAssistant()
    response = assistant.execute_command(command)
    
    print("Command Execution:")
    print(f"  Response: {response}")

if __name__ == "__main__":
    print("Voice-Based Virtual Assistant Test Suite")
    print("Testing the three-stage process: Pre-processing, Classification, Feature Extraction")
    print()
    
    # Run all tests
    test_preprocessing()
    test_classification()
    test_feature_extraction()
    test_voice_assistant()
    test_voice_commands()
    demonstrate_three_stage_process()
    
    print("=" * 60)
    print("All tests completed successfully!")
    print("The voice assistant is ready for integration with the mock interview system.")
    print("=" * 60)
