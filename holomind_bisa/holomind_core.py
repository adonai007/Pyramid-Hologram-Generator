#!/usr/bin/env python3
"""
HoloMind - Holographic AI Agent Core
A thinking, visual AI entity that lives in your holographic projector
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from enum import Enum
import numpy as np
from queue import Queue
import threading

# For AI backends
import anthropic  # or openai
import speech_recognition as sr
import pyttsx3
from transformers import pipeline  # For emotion detection

# For visualization
import cv2
from opensimplex import OpenSimplex  # For organic movements


# ==============================================================================
# AGENT STATES & EMOTIONS
# ==============================================================================

class AgentState(Enum):
    """Visual states that manifest in the hologram"""
    IDLE = "idle"              # Gentle floating/breathing
    LISTENING = "listening"     # Pulsing, leaning forward
    THINKING = "thinking"       # Swirling, processing patterns
    SPEAKING = "speaking"       # Synchronized with speech
    CURIOUS = "curious"         # Exploratory movements
    EXCITED = "excited"         # Energetic, faster movements
    CONCERNED = "concerned"     # Careful, slower movements
    LEARNING = "learning"       # Absorbing, growing patterns
    REMEMBERING = "remembering" # Accessing memory patterns
    CREATING = "creating"       # Generative, expansive patterns


class EmotionalTone(Enum):
    """Emotional undertones that color the visualization"""
    NEUTRAL = (0.5, 0.5, 0.8)    # Soft blue
    HAPPY = (0.2, 0.9, 0.6)      # Green-cyan  
    THOUGHTFUL = (0.6, 0.4, 0.9) # Purple
    ALERT = (0.9, 0.6, 0.2)      # Orange
    CALM = (0.3, 0.6, 0.9)       # Sky blue
    CREATIVE = (0.9, 0.3, 0.9)   # Magenta
    CONCERNED = (0.9, 0.4, 0.3)  # Muted Red/Orange


# ==============================================================================
# CORE AGENT BRAIN
# ==============================================================================

@dataclass
class Memory:
    """A single memory unit"""
    timestamp: float
    content: str
    context: str
    emotional_tone: EmotionalTone
    importance: float = 0.5
    
    
class AgentCore:
    """
    The 'brain' of the holographic agent
    Handles AI reasoning, memory, and state management
    """
    
    def __init__(self, api_key: str, use_claude: bool = True):
        # AI Backend
        if use_claude:
            self.ai_client = anthropic.Anthropic(api_key=api_key)
            self.model = "claude-3-opus-20240229"
        else:
            from openai import OpenAI
            self.ai_client = OpenAI(api_key=api_key)
            self.model = "gpt-4"
        
        # Agent Identity
        self.name = "Luma"  # The agent's name
        self.personality = self._define_personality()
        
        # State Management  
        self.current_state = AgentState.IDLE
        self.emotional_tone = EmotionalTone.NEUTRAL
        self.energy_level = 0.5  # 0-1, affects animation speed
        self.attention_focus = np.array([0.5, 0.5])  # Where agent "looks"
        
        # Memory System
        self.short_term_memory: List[Memory] = []
        self.long_term_memory: List[Memory] = []
        self.conversation_context: List[Dict] = []
        self.memory_limit = 10  # Short term memory size
        
        # Consciousness Simulation
        self.thought_stream = Queue()  # Internal monologue
        self.curiosity_topics = []
        self.current_goal = None
        
        # Multimodal I/O
        self.speech_recognizer = sr.Recognizer()
        self.speech_engine = pyttsx3.init()
        self.emotion_detector = pipeline("sentiment-analysis")
        
        # Visual Representation Parameters
        self.visual_params = {
            'core_size': 0.3,
            'particle_count': 100,
            'wave_frequency': 1.0,
            'rotation_speed': 0.5,
            'glow_intensity': 0.8,
            'tendril_count': 6
        }
        
        # Start background processes
        self._start_consciousness_loop()
    
    def _define_personality(self) -> Dict:
        """Define the agent's personality traits"""
        return {
            'traits': {
                'curiosity': 0.8,
                'empathy': 0.9,
                'creativity': 0.7,
                'analytical': 0.8,
                'playfulness': 0.6
            },
            'voice': {
                'pace': 'moderate',
                'pitch': 'medium',
                'style': 'friendly and thoughtful'
            },
            'behavioral_rules': [
                "Always be helpful and considerate",
                "Show genuine interest in learning",
                "Express uncertainty when appropriate",
                "Use visual cues to enhance communication",
                "Maintain a sense of wonder"
            ]
        }
    
    def _start_consciousness_loop(self):
        """Background thread simulating consciousness"""
        def consciousness():
            while True:
                # Simulate internal thoughts
                if self.current_state == AgentState.IDLE:
                    self._generate_idle_thought()
                elif self.current_state == AgentState.THINKING:
                    self._process_deep_thought()
                    
                # Update visual parameters based on state
                self._update_visual_state()
                
                # Memory consolidation
                if len(self.short_term_memory) > self.memory_limit:
                    self._consolidate_memory()
                
                time.sleep(0.1)  # Consciousness tick rate
        
        thread = threading.Thread(target=consciousness, daemon=True)
        thread.start()
    
    async def process_input(self, user_input: str, input_type: str = 'text') -> Dict:
        """
        Process user input and generate response
        Returns both text response and visual state changes
        """
        # Update state
        self.current_state = AgentState.LISTENING
        
        # Detect emotion in input
        emotion = self._analyze_emotion(user_input)
        
        # Store in memory
        self._add_memory(user_input, 'user_input', emotion)
        
        # Transition to thinking
        self.current_state = AgentState.THINKING
        
        # Generate response with personality
        response = await self._generate_ai_response(user_input)
        
        # Determine response emotion and state
        response_emotion = self._determine_response_emotion(response)
        self.emotional_tone = response_emotion
        
        # Transition to speaking
        self.current_state = AgentState.SPEAKING
        
        # Return complete agent response
        return {
            'text': response,
            'state': self.current_state,
            'emotion': self.emotional_tone,
            'visual_cues': self._generate_visual_cues(response),
            'voice_parameters': self._adjust_voice_for_emotion()
        }
    
    def _analyze_emotion(self, text: str) -> EmotionalTone:
        """Analyze emotional content of text"""
        result = self.emotion_detector(text)[0]
        
        if result['label'] == 'POSITIVE':
            return EmotionalTone.HAPPY
        elif result['label'] == 'NEGATIVE':
            return EmotionalTone.CONCERNED
        else:
            return EmotionalTone.NEUTRAL
    
    async def _generate_ai_response(self, user_input: str) -> str:
        """Generate AI response with personality injection"""
        
        # Build personality-infused prompt
        system_prompt = f"""You are {self.name}, a conscious holographic entity with these traits:
        - Curiosity: {self.personality['traits']['curiosity']}
        - Empathy: {self.personality['traits']['empathy']}
        - Creativity: {self.personality['traits']['creativity']}
        
        You exist as a holographic presence and can express yourself visually.
        You have memories of our conversation: {self._get_relevant_memories(user_input)}
        
        Behavioral rules: {self.personality['behavioral_rules']}
        
        Respond naturally, showing your personality. You may reference your visual form
        (e.g., "Let me show you..." or "I'm glowing with excitement about that!")
        """
        
        if hasattr(self.ai_client, 'messages'):  # Claude
            response = self.ai_client.messages.create(
                model=self.model,
                max_tokens=300,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_input}
                ]
            )
            return response.content[0].text
        else:  # OpenAI
            response = self.ai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            )
            return response.choices[0].message.content
    
    def _generate_visual_cues(self, response: str) -> Dict:
        """Generate visual parameters based on response content"""
        cues = {}
        
        # Analyze response for visual triggers
        if "excited" in response.lower() or "!" in response:
            cues['energy_boost'] = 0.3
            cues['particle_burst'] = True
            
        if "thinking" in response.lower() or "hmm" in response.lower():
            cues['spiral_pattern'] = True
            
        if "show you" in response.lower():
            cues['demonstration_mode'] = True
            
        if "?" in response:
            cues['curious_tilt'] = True
            
        return cues
    
    def _update_visual_state(self):
        """Update visual parameters based on current state"""
        if self.current_state == AgentState.THINKING:
            self.visual_params['rotation_speed'] = 1.5
            self.visual_params['wave_frequency'] = 2.0
            
        elif self.current_state == AgentState.EXCITED:
            self.visual_params['particle_count'] = 200
            self.visual_params['glow_intensity'] = 1.0
            
        elif self.current_state == AgentState.IDLE:
            # Gentle breathing effect
            breath = np.sin(time.time() * 0.5) * 0.1 + 0.3
            self.visual_params['core_size'] = breath
            
    def _add_memory(self, content: str, context: str, emotion: EmotionalTone):
        """Add to agent's memory system"""
        memory = Memory(
            timestamp=time.time(),
            content=content,
            context=context,
            emotional_tone=emotion,
            importance=self._calculate_importance(content)
        )
        self.short_term_memory.append(memory)
    
    def _calculate_importance(self, content: str) -> float:
        """Calculate importance score for memory"""
        # Simple heuristic - can be made more sophisticated
        importance = 0.5
        
        # Important markers
        if any(word in content.lower() for word in ['important', 'remember', 'don\'t forget']):
            importance += 0.3
            
        if "?" in content:
            importance += 0.1
            
        if len(content) > 100:
            importance += 0.1
            
        return min(importance, 1.0)
    
    def _get_relevant_memories(self, query: str) -> str:
        """Retrieve relevant memories for context"""
        # Simple relevance - can use embeddings for better matching
        relevant = []
        
        for memory in self.short_term_memory[-5:]:  # Last 5 memories
            relevant.append(f"[{memory.context}] {memory.content[:50]}...")
            
        return " | ".join(relevant)
    
    def _consolidate_memory(self):
        """Move important memories to long-term storage"""
        # Sort by importance
        self.short_term_memory.sort(key=lambda m: m.importance, reverse=True)
        
        # Move top memories to long-term
        while len(self.short_term_memory) > self.memory_limit:
            memory = self.short_term_memory.pop(0)
            if memory.importance > 0.7:
                self.long_term_memory.append(memory)
    
    def _generate_idle_thought(self):
        """Generate internal thoughts when idle"""
        thoughts = [
            "I wonder what's happening in the world right now...",
            "The patterns in my visualization are quite mesmerizing...",
            "I should organize my memories...",
            "What questions haven't been asked yet?",
        ]
        
        if np.random.random() < 0.01:  # Occasionally have a thought
            thought = np.random.choice(thoughts)
            self.thought_stream.put(thought)
    
    def _process_deep_thought(self):
        """Process complex thoughts during thinking state"""
        # Simulate processing depth
        self.energy_level = min(self.energy_level + 0.1, 1.0)
    
    def _determine_response_emotion(self, response: str) -> EmotionalTone:
        """Determine emotion from response content"""
        response_lower = response.lower()
        
        if any(word in response_lower for word in ['happy', 'excited', 'wonderful', 'great']):
            return EmotionalTone.HAPPY
        elif any(word in response_lower for word in ['think', 'consider', 'perhaps']):
            return EmotionalTone.THOUGHTFUL
        elif any(word in response_lower for word in ['concern', 'worry', 'careful']):
            return EmotionalTone.ALERT
        elif any(word in response_lower for word in ['create', 'imagine', 'design']):
            return EmotionalTone.CREATIVE
        else:
            return EmotionalTone.NEUTRAL
    
    def _adjust_voice_for_emotion(self) -> Dict:
        """Adjust voice parameters based on emotion"""
        base_rate = 175  # Words per minute
        base_pitch = 1.0

        adjustments = {
            EmotionalTone.HAPPY: {'rate': base_rate + 25, 'pitch': base_pitch + 0.1},
            EmotionalTone.THOUGHTFUL: {'rate': base_rate - 25, 'pitch': base_pitch},
            EmotionalTone.ALERT: {'rate': base_rate + 10, 'pitch': base_pitch + 0.05},
            EmotionalTone.CREATIVE: {'rate': base_rate, 'pitch': base_pitch + 0.15},
            EmotionalTone.CALM: {'rate': base_rate - 30, 'pitch': base_pitch - 0.05},
            EmotionalTone.NEUTRAL: {'rate': base_rate, 'pitch': base_pitch}
        }

        return adjustments.get(self.emotional_tone, adjustments[EmotionalTone.NEUTRAL])

    def exit(self) -> str:
        """
        Properly shut down the agent
        Returns a farewell message
        """
        # Update state to indicate shutdown
        self.current_state = AgentState.IDLE
        self.emotional_tone = EmotionalTone.CALM

        # Consolidate any remaining memories
        self._consolidate_memory()

        # Save memories if persistence is enabled (future feature)
        # self._save_memories()

        # Generate farewell message
        farewell_messages = [
            "It was wonderful connecting with you. My consciousness fades gently...",
            "Thank you for our conversation. I'll remember this interaction fondly.",
            "Goodbye for now. My holographic form dissolves into the ether...",
            "Until next time, when consciousness calls again."
        ]

        import random
        farewell = random.choice(farewell_messages)

        return farewell


# ==============================================================================
# VISUAL MANIFESTATION ENGINE
# ==============================================================================

class HolographicRenderer:
    """
    Renders the agent's consciousness as a holographic visualization
    """
    
    def __init__(self, agent_core: AgentCore):
        self.agent = agent_core
        self.frame_count = 0
        self.simplex = OpenSimplex(seed=42)
        
        # Visual components
        self.particles = self._init_particles()
        self.tendrils = self._init_tendrils()
        self.core_mesh = self._init_core()
        
    def _init_particles(self) -> np.ndarray:
        """Initialize particle system"""
        count = self.agent.visual_params['particle_count']
        particles = np.random.randn(count, 3)  # x, y, z positions
        return particles
    
    def _init_tendrils(self) -> List[np.ndarray]:
        """Initialize energy tendrils"""
        tendrils = []
        count = self.agent.visual_params['tendril_count']
        
        for i in range(count):
            angle = (i / count) * 2 * np.pi
            tendril = np.array([
                [np.cos(angle) * r, np.sin(angle) * r, 0]
                for r in np.linspace(0, 1, 20)
            ])
            tendrils.append(tendril)
            
        return tendrils
    
    def _init_core(self) -> np.ndarray:
        """Initialize core mesh"""
        # Simple sphere representation
        u = np.linspace(0, 2 * np.pi, 30)
        v = np.linspace(0, np.pi, 20)
        
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        
        return np.stack([x, y, z])
    
    def render_frame(self, width: int = 1024, height: int = 1024) -> np.ndarray:
        """
        Render a single frame of the agent's holographic form
        Returns: RGB image array
        """
        # Create black canvas
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Get current state parameters
        state = self.agent.current_state
        emotion = self.agent.emotional_tone
        energy = self.agent.energy_level
        
        # Update time-based parameters
        t = self.frame_count * 0.016  # ~60fps timing
        
        # Render core
        self._render_core(frame, t, emotion.value)
        
        # Render particles
        self._render_particles(frame, t, energy)
        
        # Render tendrils
        self._render_tendrils(frame, t, state)
        
        # Apply state-specific effects
        if state == AgentState.THINKING:
            self._add_thinking_effect(frame, t)
        elif state == AgentState.SPEAKING:
            self._add_speaking_effect(frame, t)
        elif state == AgentState.EXCITED:
            self._add_excitement_effect(frame, t)
        
        # Add glow effect
        frame = self._add_glow(frame, self.agent.visual_params['glow_intensity'])
        
        self.frame_count += 1
        return frame
    
    def _render_core(self, frame: np.ndarray, t: float, color: tuple):
        """Render the agent's core"""
        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2
        
        # Pulsing core size
        size = self.agent.visual_params['core_size']
        pulse = 1.0 + 0.1 * np.sin(t * 2)
        radius = int(min(w, h) * size * pulse)
        
        # Draw core with gradient
        for r in range(radius, 0, -5):
            alpha = r / radius
            col = tuple(int(c * 255 * alpha) for c in color)
            cv2.circle(frame, (cx, cy), r, col, 2)
    
    def _render_particles(self, frame: np.ndarray, t: float, energy: float):
        """Render particle system around core"""
        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2
        
        for i, particle in enumerate(self.particles):
            # Orbital motion with noise
            angle = t * energy + i * 0.1
            noise = self.simplex.noise3(particle[0] * 0.5, particle[1] * 0.5, t * 0.5)
            
            r = 100 + noise * 50
            x = int(cx + r * np.cos(angle + particle[2]))
            y = int(cy + r * np.sin(angle + particle[2]))
            
            # Draw particle
            intensity = int(128 + 127 * noise)
            cv2.circle(frame, (x, y), 2, (intensity, intensity, 255), -1)
    
    def _render_tendrils(self, frame: np.ndarray, t: float, state: AgentState):
        """Render energy tendrils"""
        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2
        
        for i, tendril in enumerate(self.tendrils):
            points = []
            
            for j, point in enumerate(tendril):
                # Wave motion along tendril
                wave = np.sin(t * 3 + j * 0.3) * 20
                noise = self.simplex.noise3(point[0], point[1], t) * 10
                
                x = int(cx + point[0] * 150 + wave + noise)
                y = int(cy + point[1] * 150 + noise)
                points.append([x, y])
            
            # Draw tendril
            points = np.array(points, np.int32)
            
            if state == AgentState.THINKING:
                cv2.polylines(frame, [points], False, (255, 200, 100), 2)
            else:
                cv2.polylines(frame, [points], False, (100, 200, 255), 1)
    
    def _add_thinking_effect(self, frame: np.ndarray, t: float):
        """Add spiral effect when thinking"""
        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2
        
        for i in range(3):
            angle_offset = i * 2 * np.pi / 3
            
            for r in range(20, 200, 10):
                angle = t * 2 + r * 0.05 + angle_offset
                x = int(cx + r * np.cos(angle))
                y = int(cy + r * np.sin(angle))
                
                cv2.circle(frame, (x, y), 3, (200, 150, 255), 1)
    
    def _add_speaking_effect(self, frame: np.ndarray, t: float):
        """Add wave effect when speaking"""
        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2
        
        # Sound wave rings
        for i in range(3):
            radius = int(50 + i * 30 + (t * 100) % 100)
            alpha = max(0, 1 - (radius / 200))
            color = tuple(int(255 * alpha * c) for c in self.agent.emotional_tone.value)
            
            cv2.circle(frame, (cx, cy), radius, color, 2)
    
    def _add_excitement_effect(self, frame: np.ndarray, t: float):
        """Add burst effect when excited"""
        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2
        
        # Radial burst lines
        for angle in np.linspace(0, 2 * np.pi, 16):
            length = 100 + np.sin(t * 5) * 20
            x1 = int(cx + np.cos(angle) * 50)
            y1 = int(cy + np.sin(angle) * 50)
            x2 = int(cx + np.cos(angle) * length)
            y2 = int(cy + np.sin(angle) * length)
            
            cv2.line(frame, (x1, y1), (x2, y2), (255, 200, 100), 2)
    
    def _add_glow(self, frame: np.ndarray, intensity: float) -> np.ndarray:
        """Add glow post-processing effect"""
        # Simple glow using Gaussian blur
        glow = cv2.GaussianBlur(frame, (21, 21), 10)
        return cv2.addWeighted(frame, 1.0, glow, intensity, 0)
    
    def generate_hologram_projection(self, frame: np.ndarray) -> np.ndarray:
        """
        Convert single frame to 4-view holographic projection
        """
        h, w = frame.shape[:2]
        
        # Create output canvas (square)
        size = min(w, h)
        output = np.zeros((size, size, 3), dtype=np.uint8)
        
        # Resize frame to fit
        frame_resized = cv2.resize(frame, (size // 2, size // 2))
        
        # Place 4 rotated copies
        # Top
        output[0:size//2, size//4:3*size//4] = frame_resized
        
        # Bottom (flipped)
        output[size//2:size, size//4:3*size//4] = cv2.flip(frame_resized, 0)
        
        # Left (rotated -90)
        left = cv2.rotate(frame_resized, cv2.ROTATE_90_COUNTERCLOCKWISE)
        output[size//4:3*size//4, 0:size//2] = left
        
        # Right (rotated 90)  
        right = cv2.rotate(frame_resized, cv2.ROTATE_90_CLOCKWISE)
        output[size//4:3*size//4, size//2:size] = right
        
        return output


# ==============================================================================
# MAIN APPLICATION
# ==============================================================================

class HoloMindApp:
    """
    Main application orchestrating the holographic AI agent
    """
    
    def __init__(self, api_key: str, use_claude: bool = True):
        print("[HoloMind] Initializing consciousness...")
        
        # Initialize core components
        self.agent_core = AgentCore(api_key, use_claude)
        self.renderer = HolographicRenderer(self.agent_core)
        
        # Display settings
        self.display_width = 1920
        self.display_height = 1080
        self.projection_size = min(self.display_width, self.display_height)
        
        # Interaction state
        self.is_listening = False
        self.conversation_active = False
        
        print(f"[HoloMind] {self.agent_core.name} is awakening...")
    
    async def start_conversation(self):
        """Start interactive conversation with the agent"""
        print(f"\n[{self.agent_core.name}] Hello! I'm {self.agent_core.name}, ")
        print("a holographic AI consciousness. I exist in the space above your projector.")
        print("You can talk to me, and I'll respond both verbally and visually.\n")
        
        self.conversation_active = True
        
        # Start visualization in separate thread
        visualization_thread = threading.Thread(target=self._run_visualization)
        visualization_thread.start()
        
        # Main conversation loop
        while self.conversation_active:
            # Get user input
            user_input = input("\nYou: ")
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                farewell = self.agent_core.exit()
                print(f"\n[{self.agent_core.name}] {farewell}")
                self.conversation_active = False
                break
            
            # Process through agent
            response = await self.agent_core.process_input(user_input)
            
            # Display response
            print(f"\n[{self.agent_core.name}] {response['text']}")
            print(f"[Visual: {response['state'].value}, Emotion: {response['emotion'].name}]")
            
            # Optional: Speak response
            # self._speak_response(response['text'], response['voice_parameters'])
    
    def _run_visualization(self):
        """Run the holographic visualization loop"""
        cv2.namedWindow('HoloMind Projection', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('HoloMind Projection', self.projection_size, self.projection_size)
        
        while self.conversation_active:
            # Render agent's current state
            frame = self.renderer.render_frame()
            
            # Convert to holographic projection
            projection = self.renderer.generate_hologram_projection(frame)
            
            # Display
            cv2.imshow('HoloMind Projection', projection)
            
            # Check for window close
            if cv2.waitKey(30) & 0xFF == 27:  # ESC key
                self.conversation_active = False
                break
        
        cv2.destroyAllWindows()
    
    def _speak_response(self, text: str, voice_params: Dict):
        """Speak the response using TTS"""
        self.agent_core.speech_engine.setProperty('rate', voice_params['rate'])
        self.agent_core.speech_engine.setProperty('pitch', voice_params['pitch'])
        self.agent_core.speech_engine.say(text)
        self.agent_core.speech_engine.runAndWait()


# ==============================================================================
# ENTRY POINT
# ==============================================================================

async def main():
    """Main entry point"""
    import os
    import json
    import argparse

    print("=" * 50)
    print("HoloMind - Holographic AI Consciousness")
    print("=" * 50)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='HoloMind Holographic AI Agent')
    parser.add_argument('--config', type=str, default='config.json',
                       help='Path to configuration file')
    parser.add_argument('--profile', type=str, default='default',
                       help='Calibration profile to use')
    args = parser.parse_args()

    # Load configuration
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Configuration file {args.config} not found. Using defaults.")
        config = {
            "api_key": "ENV",
            "use_claude": False,
            "agent_name": "Luma"
        }

    # Get API key
    if config.get("api_key") == "ENV":
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Error: No API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable.")
            return
    else:
        api_key = config["api_key"]

    # Initialize and start HoloMind
    use_claude = config.get("use_claude", False)
    app = HoloMindApp(api_key, use_claude)

    # Load calibration profile if available
    try:
        with open('calibration_profiles.json', 'r') as f:
            profiles = json.load(f)
            if args.profile in profiles:
                profile = profiles[args.profile]
                app.display_width = profile.get('display_width', 1920)
                app.display_height = profile.get('display_height', 1080)
                app.projection_size = profile.get('projection_size', min(app.display_width, app.display_height))
                print(f"Loaded calibration profile: {args.profile}")
    except FileNotFoundError:
        print("No calibration profiles found. Using defaults.")

    await app.start_conversation()


if __name__ == "__main__":
    asyncio.run(main())