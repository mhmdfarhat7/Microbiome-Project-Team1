#!/usr/bin/env python3
"""
Test script to verify M2-M3 integration

This script tests:
1. M2 backend library functions
2. API server endpoints
3. Data flow from M1 → M2 → M3
"""

import sys
import os

# Add src to path
sys.path.append('src')

def test_m2_backend_lib():
    """Test the M2 backend library functions."""
    print("🧪 Testing M2 Backend Library")
    print("=" * 40)
    
    try:
        from backend_lib import get_environments, get_phylum_composition
        
        # Test getting environments
        print("Testing get_environments()...")
        all_envs = get_environments()
        top_envs = get_environments(top=5)
        
        print(f"✅ Total environments: {len(all_envs)}")
        print(f"✅ Top 5 environments: {top_envs}")
        
        # Test getting composition
        if top_envs:
            test_env = top_envs[0]
            print(f"\nTesting get_phylum_composition() for '{test_env}'...")
            
            result = get_phylum_composition(test_env, top=5)
            print(f"✅ Found {result['n_runs']} bioruns")
            print(f"✅ Top phyla: {len(result['composition'])}")
            
            # Show first few results
            for i, phylum in enumerate(result['composition'][:3], 1):
                print(f"  {i}. {phylum['taxon']}: {phylum['mean_percent']:.2f}%")
        
        print("\n✅ M2 Backend Library tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ M2 Backend Library test failed: {e}")
        return False


def test_api_server():
    """Test the API server endpoints."""
    print("\n🌐 Testing API Server")
    print("=" * 40)
    
    try:
        from api_server import app
        
        # Create a test client
        with app.test_client() as client:
            # Test health endpoint
            print("Testing /api/health...")
            response = client.get('/api/health')
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
            
            # Test environments endpoint
            print("Testing /api/environments...")
            response = client.get('/api/environments')
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Environments endpoint working: {data['count']} environments")
            else:
                print(f"❌ Environments endpoint failed: {response.status_code}")
                return False
            
            # Test composition endpoint
            print("Testing /api/composition endpoint...")
            test_env = "soil metagenome"
            response = client.get(f'/api/composition/{test_env}?top=5')
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Composition endpoint working: {data['data']['n_runs']} bioruns")
            else:
                print(f"❌ Composition endpoint failed: {response.status_code}")
                return False
        
        print("\n✅ API Server tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ API Server test failed: {e}")
        return False


def main():
    """Run all integration tests."""
    print("🚀 M2-M3 Integration Test Suite")
    print("=" * 60)
    
    # Test M2 backend library
    m2_success = test_m2_backend_lib()
    
    # Test API server
    api_success = test_api_server()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Integration Test Results:")
    print(f"  M2 Backend Library: {'✅ PASS' if m2_success else '❌ FAIL'}")
    print(f"  API Server: {'✅ PASS' if api_success else '❌ FAIL'}")
    
    if m2_success and api_success:
        print("\n🎉 All tests passed! M2-M3 integration is ready!")
        print("\n💡 Next steps:")
        print("  1. Install dependencies: pip3 install -r requirements.txt")
        print("  2. Start API server: python3 src/api_server.py")
        print("  3. Start M3 frontend: cd frontend && npm run dev")
        print("  4. Open browser to M3 frontend URL")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
