#!/usr/bin/env python3
"""
Flask API Server for M3 Frontend Integration

This server provides REST endpoints that M3 can call to:
1. GET /api/environments - List available environments
2. GET /api/composition/<env> - Get phylum composition for environment

The server uses backend_lib.py to get data from M2 backend.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend_lib import get_environments, get_phylum_composition

app = Flask(__name__)
CORS(app)  # Allow M3 frontend to call this API


@app.route('/api/environments', methods=['GET'])
def api_environments():
    """Get list of available environments for M3 dropdown."""
    try:
        # Get top parameter from query string
        top = request.args.get('top', type=int)
        
        # Get environments
        envs = get_environments(top=top)
        
        return jsonify({
            'success': True,
            'environments': envs,
            'count': len(envs)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/composition/<env>', methods=['GET'])
def api_composition(env):
    """Get phylum composition for a specific environment."""
    try:
        # Get query parameters
        top = request.args.get('top', type=int, default=50)
        group_others = request.args.get('group_others', type=str, default='true').lower() == 'true'
        others_threshold = request.args.get('others_threshold', type=float, default=0.5)
        
        # Get composition data
        result = get_phylum_composition(
            env=env, 
            top=top, 
            as_dataframe=False,
            group_others=group_others,
            others_threshold=others_threshold
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        # Environment not found
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def api_health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'M2 Backend API',
        'version': '1.0.0'
    })


@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Get basic statistics about available data."""
    try:
        from backend_lib import get_environment_stats
        
        stats = get_environment_stats()
        total_runs = sum(stats.values())
        
        return jsonify({
            'success': True,
            'stats': {
                'total_environments': len(stats),
                'total_bioruns': total_runs,
                'top_environments': dict(list(stats.items())[:10])
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("🚀 Starting M2 Backend API Server for M3 Frontend")
    print("=" * 60)
    print("Available endpoints:")
    print("  GET /api/health          - Health check")
    print("  GET /api/environments    - List environments")
    print("  GET /api/composition/<env> - Get composition data")
    print("    Query params: top=N, group_others=true/false, others_threshold=0.5")
    print("  GET /api/stats           - Get data statistics")
    print("=" * 60)
    
    # Run the server
    app.run(
        host='0.0.0.0',  # Allow external connections
        port=5001,       # Use port 5001 to avoid macOS AirPlay conflict
        debug=True       # Enable debug mode for development
    )
