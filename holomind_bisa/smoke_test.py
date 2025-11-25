#!/usr/bin/env python3
"""
HoloMind Smoke Test
Quick end-to-end validation of core functionality
"""

import asyncio
import os
import sys

async def smoke_test():
    """Run comprehensive smoke test"""
    print("Starting HoloMind smoke test...")

    # Check environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OPENAI_API_KEY environment variable found")
        return False

    print("API key found")

    try:
        # Test imports
        from holomind_core import AgentCore, HolographicRenderer, HoloMindApp
        print("Core imports successful")

        # Test agent initialization
        print("Initializing agent core...")
        agent = AgentCore(api_key, use_claude=False)
        print("Agent core initialized")

        # Test renderer
        print("Initializing renderer...")
        renderer = HolographicRenderer(agent)
        print("Renderer initialized")

        # Test frame generation
        print("Testing frame rendering...")
        frame = renderer.render_frame(512, 512)
        print(f"Frame rendered: {frame.shape}")

        # Test hologram projection
        projection = renderer.generate_hologram_projection(frame)
        print(f"Projection generated: {projection.shape}")

        # Test agent processing (simple input)
        print("Testing agent processing...")
        test_input = "Hello, can you show me a simple visualization?"
        response = await agent.process_input(test_input)

        print(f"Agent response: {response['text'][:100]}...")
        print(f"State: {response['state'].value}")
        print(f"Emotion: {response['emotion'].name}")

        # Test app initialization
        print("Testing full app initialization...")
        app = HoloMindApp(api_key, use_claude=False)
        print("Full app initialized")

        print("\nAll smoke tests passed! HoloMind is ready.")
        return True

    except Exception as e:
        print(f"❌ Smoke test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    print("=" * 50)
    print("HoloMind Smoke Test")
    print("=" * 50)

    # Run async test
    success = asyncio.run(smoke_test())

    print("=" * 50)
    if success:
        print("Smoke test completed successfully!")
        print("\nNext steps:")
        print("1. Run calibration: python calibrate.py")
        print("2. Start full conversation: python holomind-core.py")
    else:
        print("Smoke test failed. Check errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()