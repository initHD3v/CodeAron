#!/usr/bin/env python3
"""
Test script untuk prompt template optimization.
"""

import sys
sys.path.insert(0, '/Users/initialh/Projects/CodeAron')

from src.core.prompt_templates import PromptTemplateManager, ModelFamily, ARON_SYSTEM_PROMPT

def test_system_prompt():
    """Test bahwa system prompt ada dan benar."""
    print("=" * 60)
    print("TEST 1: System Prompt Check")
    print("=" * 60)
    
    assert ARON_SYSTEM_PROMPT is not None, "ARON_SYSTEM_PROMPT should not be None"
    assert len(ARON_SYSTEM_PROMPT) > 100, "ARON_SYSTEM_PROMPT should be detailed"
    assert "OBSERVE FIRST" in ARON_SYSTEM_PROMPT, "Should have OBSERVE FIRST principle"
    assert "NO HALLUCINATION" in ARON_SYSTEM_PROMPT, "Should have NO HALLUCINATION principle"
    assert "ACTION ORIENTED" in ARON_SYSTEM_PROMPT, "Should have ACTION ORIENTED principle"
    
    print("✅ System prompt loaded correctly")
    print(f"   Length: {len(ARON_SYSTEM_PROMPT)} characters")
    print()

def test_qwen_prompt_building():
    """Test building prompt untuk Qwen model."""
    print("=" * 60)
    print("TEST 2: Qwen Prompt Building")
    print("=" * 60)
    
    messages = [
        {"role": "user", "content": "Halo, siapa kamu?"},
    ]
    
    # Test dengan default system prompt
    prompt = PromptTemplateManager.build_prompt(
        messages=messages,
        model_family=ModelFamily.QWEN,
        system_prompt=None
    )
    
    assert "[INST]" in prompt, "Qwen prompt should have [INST] token"
    assert "[/INST]" in prompt, "Qwen prompt should have [/INST] token"
    assert "OBSERVE FIRST" in prompt, "Prompt should contain ARON_SYSTEM_PROMPT"
    
    print("✅ Qwen prompt built correctly")
    print(f"   Prompt length: {len(prompt)} characters")
    print(f"   Preview: {prompt[:200]}...")
    print()

def test_custom_system_prompt():
    """Test menggunakan custom system prompt."""
    print("=" * 60)
    print("TEST 3: Custom System Prompt")
    print("=" * 60)
    
    custom_prompt = "Kamu adalah assistant yang helpful."
    messages = [
        {"role": "user", "content": "Test"},
    ]
    
    prompt = PromptTemplateManager.build_prompt(
        messages=messages,
        model_family=ModelFamily.QWEN,
        system_prompt=custom_prompt
    )
    
    assert "Kamu adalah assistant yang helpful." in prompt, "Should use custom system prompt"
    
    print("✅ Custom system prompt works")
    print()

def test_model_family_detection():
    """Test deteksi model family."""
    print("=" * 60)
    print("TEST 4: Model Family Detection")
    print("=" * 60)
    
    assert PromptTemplateManager.detect_model_family("Qwen2.5-Coder-7B") == ModelFamily.QWEN
    assert PromptTemplateManager.detect_model_family("llama-3-8b") == ModelFamily.LLAMA
    assert PromptTemplateManager.detect_model_family("unknown-model") == ModelFamily.CHATML
    
    print("✅ Model family detection works")
    print()

def test_llama_prompt():
    """Test building prompt untuk Llama model."""
    print("=" * 60)
    print("TEST 5: Llama Prompt Building")
    print("=" * 60)
    
    messages = [
        {"role": "user", "content": "Test"},
    ]
    
    prompt = PromptTemplateManager.build_prompt(
        messages=messages,
        model_family=ModelFamily.LLAMA,
        system_prompt=None
    )
    
    assert "<|begin_of_text|>" in prompt, "Llama prompt should have begin token"
    assert "<|start_header_id|>" in prompt, "Llama prompt should have header tags"
    
    print("✅ Llama prompt built correctly")
    print()

def test_chatml_prompt():
    """Test building prompt untuk ChatML format."""
    print("=" * 60)
    print("TEST 6: ChatML Prompt Building")
    print("=" * 60)
    
    messages = [
        {"role": "user", "content": "Test"},
    ]
    
    prompt = PromptTemplateManager.build_prompt(
        messages=messages,
        model_family=ModelFamily.CHATML,
        system_prompt=None
    )
    
    assert "user: Test" in prompt, "ChatML prompt should have user: prefix"
    
    print("✅ ChatML prompt built correctly")
    print()

def main():
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "PROMPT TEMPLATE OPTIMIZATION TEST" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    try:
        test_system_prompt()
        test_qwen_prompt_building()
        test_custom_system_prompt()
        test_model_family_detection()
        test_llama_prompt()
        test_chatml_prompt()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("Summary:")
        print("  - System prompt loaded with strong Aron persona")
        print("  - Qwen prompt template working correctly")
        print("  - Custom system prompt override supported")
        print("  - Model family detection working")
        print("  - Llama and ChatML fallbacks working")
        print()
        
    except AssertionError as e:
        print("=" * 60)
        print("❌ TEST FAILED!")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print("=" * 60)
        print("❌ UNEXPECTED ERROR!")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
