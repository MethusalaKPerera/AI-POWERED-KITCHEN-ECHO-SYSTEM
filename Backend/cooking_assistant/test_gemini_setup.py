"""
Quick Test Script for Gemini API Integration
Run this to verify your setup is working
"""

import os
import sys

def test_gemini_setup():
    """Test if Gemini API is properly configured"""
    
    print("=" * 60)
    print("🧪 Testing Gemini API Setup for Kitchen Echo System")
    print("=" * 60)
    print()
    
    # Step 1: Check if Gemini package is installed
    print("1️⃣ Checking if google-generativeai is installed...")
    try:
        import google.generativeai as genai
        print("   ✅ google-generativeai is installed!")
    except ImportError:
        print("   ❌ google-generativeai is NOT installed")
        print("   📦 Run: pip install google-generativeai")
        return False
    
    # Step 2: Check for API key
    print("\n2️⃣ Checking for Gemini API key...")
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("   ❌ GEMINI_API_KEY not found in environment")
        print("   🔑 Please set it:")
        print("   - Option 1: Add to .env file: GEMINI_API_KEY=your_key_here")
        print("   - Option 2: Run: set GEMINI_API_KEY=your_key_here")
        print()
        print("   Get your FREE API key at: https://aistudio.google.com/app/apikey")
        return False
    elif api_key == "your_api_key_here" or api_key == "YOUR_KEY_HERE":
        print("   ⚠️  Found placeholder API key")
        print("   🔑 Replace with your actual Gemini API key")
        print("   Get it at: https://aistudio.google.com/app/apikey")
        return False
    else:
        print(f"   ✅ API key found: {api_key[:10]}...{api_key[-5:]}")
    
    # Step 3: Test API connection
    print("\n3️⃣ Testing API connection...")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Simple test prompt
        response = model.generate_content("Say 'API is working!' in exactly 3 words.")
        
        if response and response.text:
            print("   ✅ Successfully connected to Gemini API!")
            print(f"   📝 Response: {response.text.strip()}")
        else:
            print("   ⚠️  Connected but received empty response")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to connect: {str(e)}")
        if "API_KEY_INVALID" in str(e) or "invalid" in str(e).lower():
            print("   🔑 Your API key appears to be invalid")
            print("   Get a new one at: https://aistudio.google.com/app/apikey")
        return False
    
    # Step 4: Test ingredient detector
    print("\n4️⃣ Testing GeminiIngredientDetector...")
    try:
        from gemini_ingredient_detector import GeminiIngredientDetector
        
        detector = GeminiIngredientDetector(api_key=api_key)
        print("   ✅ GeminiIngredientDetector initialized successfully!")
        
    except ImportError:
        print("   ❌ Cannot import GeminiIngredientDetector")
        print("   📁 Make sure gemini_ingredient_detector.py is in the same folder")
        return False
    except Exception as e:
        print(f"   ❌ Error initializing detector: {str(e)}")
        return False
    
    # Step 5: Check PIL/Pillow
    print("\n5️⃣ Checking image processing library...")
    try:
        from PIL import Image
        print("   ✅ PIL/Pillow is installed!")
    except ImportError:
        print("   ❌ PIL/Pillow is NOT installed")
        print("   📦 Run: pip install Pillow")
        return False
    
    # All tests passed!
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED! Your setup is ready!")
    print("=" * 60)
    print()
    print("📋 Next Steps:")
    print("   1. Update your .env file with GEMINI_API_KEY")
    print("   2. Replace Google Vision code with Gemini code")
    print("   3. Test with a real food image")
    print("   4. Run your Flask app!")
    print()
    print("📖 See MIGRATION_GUIDE.md for detailed instructions")
    print()
    
    return True


def test_with_sample_text():
    """Test basic text generation"""
    print("\n" + "=" * 60)
    print("🧪 BONUS TEST: Testing ingredient recognition capability")
    print("=" * 60)
    print()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key in ["your_api_key_here", "YOUR_KEY_HERE"]:
        print("⚠️  Skipping - API key not configured")
        return
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        test_prompt = """
List 5 common Sri Lankan ingredients used in curry dishes.
Format: just the ingredient names, one per line.
"""
        
        print("Testing ingredient knowledge...")
        response = model.generate_content(test_prompt)
        
        print("✅ Response received:")
        print()
        print(response.text)
        print()
        print("💡 Gemini knows about Sri Lankan cuisine!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


if __name__ == "__main__":
    print()
    
    # Check if running from correct directory
    if not os.path.exists('gemini_ingredient_detector.py'):
        print("⚠️  Warning: gemini_ingredient_detector.py not found")
        print("📁 Make sure you're in the correct directory")
        print()
    
    # Run main tests
    success = test_gemini_setup()
    
    if success:
        # Run bonus test
        test_with_sample_text()
    
    print()
    print("=" * 60)
    
    if success:
        print("✅ SETUP COMPLETE - You're ready to go!")
    else:
        print("❌ SETUP INCOMPLETE - Please fix the issues above")
    
    print("=" * 60)
    print()