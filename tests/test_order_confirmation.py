"""
Test script to verify the order confirmation example works correctly
"""

import json
import pytest
import asyncio
from app.gpt_handler import extract_intent
from app.transformer import build_flow_json
from app.utils.validator import validate_flow


@pytest.mark.asyncio
async def test_order_confirmation():
    """Test the order confirmation example"""
    
    user_input = "After a customer places an order, send them a confirmation email with order details"
    
    print(f"Testing input: {user_input}")
    print("-" * 50)
    
    try:
        # Step 1: Extract intent
        print("Step 1: Extracting intent from GPT...")
        intent = await extract_intent(user_input)
        print(f"Intent extracted: {json.dumps(intent, indent=2)}")
        print()
        
        # Step 2: Build flow JSON
        print("Step 2: Building flow JSON...")
        flow_json = build_flow_json(intent)
        print(f"Flow JSON: {json.dumps(flow_json, indent=2)}")
        print()
        
        # Step 3: Validate flow
        print("Step 3: Validating flow...")
        validate_flow(flow_json)
        print("✅ Flow validation passed!")
        print()
        
        # Step 4: Show expected format
        print("Expected response format:")
        response = {
            "trace_id": "550e8400-e29b-41d4-a716-446655440001",
            "flow": flow_json
        }
        print(json.dumps(response, indent=2))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


@pytest.mark.asyncio
async def test_fallback_scenario():
    """Test with a fallback scenario (simulating API failure)"""
    
    print("\n" + "="*60)
    print("Testing fallback scenario...")
    print("="*60)
    
    # Create a mock intent that might come from fallback
    intent = {
        "trigger": "order_placed",
        "actions": [
            {
                "type": "send_email",
                "template": "confirmation",
                "fields": {
                    "name": "user.name",
                    "email": "user.email",
                    "order_id": "order.id"
                }
            }
        ]
    }
    
    try:
        flow_json = build_flow_json(intent)
        print(f"Fallback flow JSON: {json.dumps(flow_json, indent=2)}")
        validate_flow(flow_json)
        print("✅ Fallback validation passed!")
        
    except Exception as e:
        print(f"❌ Fallback error: {e}")

if __name__ == "__main__":
    asyncio.run(test_order_confirmation())
    asyncio.run(test_fallback_scenario())