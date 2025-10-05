#!/usr/bin/env python3
"""
Quick test for the access fault implementation.
Tests the PMP hole and JALR-based instruction fault mechanism.
"""

import sys
sys.path.insert(0, '.')

from Arrow.Utils.configuration_management import Configuration
from Arrow.Arrow_API import AR
from Arrow.Internal_content.ingredients.exceptions import AccessFaultIngredient

# Set RISC-V architecture 
Configuration.Architecture.riscv = True

def test_access_fault():
    """Test the access fault ingredient with PMP hole."""
    print("Testing AccessFaultIngredient with PMP hole...")
    
    try:
        # Create access fault ingredient
        ingredient = AccessFaultIngredient()
        ingredient.fault_type = None  # Random fault type
        ingredient.fault_count = 3
        ingredient.setup_pmp = True
        
        print("Initializing ingredient...")
        ingredient.init()
        
        print("Getting restricted memory info...")
        memory_info = ingredient.get_restricted_memory_info()
        print(f"Restricted memory: {memory_info}")
        
        print("Getting PMP configuration...")
        pmp_config = ingredient.get_pmp_configuration()
        print(f"PMP configuration: {pmp_config}")
        
        print("AccessFaultIngredient created successfully!")
        
        ingredient.final()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_access_fault()
    if success:
        print("\n✅ Access fault implementation test passed!")
    else:
        print("\n❌ Access fault implementation test failed!")
        sys.exit(1)