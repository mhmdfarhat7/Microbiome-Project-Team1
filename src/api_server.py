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

from backend_lib import get_environments, get_phylum_composition, get_composition, get_data_by_location, clear_composition_cache, get_cache_stats

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
    """Get taxonomic composition for a specific environment and level."""
    try:
        # Get query parameters
        top = request.args.get('top', type=int, default=50)
        level = request.args.get('level', default='phylum')
        
        # Get composition data
        result = get_composition(
            env=env, 
            level=level,
            top=top, 
            as_dataframe=False
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        # Environment not found or invalid level
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


@app.route('/api/geographic-locations', methods=['GET'])
def api_geographic_locations():
    """Get list of available geographic locations from the dedicated unique file."""
    try:
        import pandas as pd
        import os
        from flask import jsonify
        
        # Path to the dedicated unique file
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "data", "processed", "geo_loc_name_unique.csv.gz"
        )
        
        # Load the unique values directly
        df = pd.read_csv(data_path)
        
        # Convert to list and sort (in case not sorted already)
        geo_locations = df['geo_loc_name'].dropna().sort_values().tolist()
        
        return jsonify({
            'success': True,
            'geo_locations': geo_locations,
            'count': len(geo_locations)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/location/<location>', methods=['GET'])
def api_location_data(location):
    """Get microbiome data filtered by geographic location."""
    try:
        # Decode URL-encoded location name
        import urllib.parse
        decoded_location = urllib.parse.unquote(location)
        
        # Get query parameters
        top = request.args.get('top', type=int, default=50)
        level = request.args.get('level', default='phylum')
        
        result = get_data_by_location(decoded_location, level=level, top=top)
        
        if result.get('success', False):
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/cache/clear', methods=['POST'])
def api_clear_cache():
    """Clear all cached composition data."""
    try:
        clear_composition_cache()
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/cache/stats', methods=['GET'])
def api_cache_stats():
    """Get cache statistics."""
    try:
        stats = get_cache_stats()
        return jsonify({
            'success': True,
            'stats': stats
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
    print("    Query params: top=N, level=phylum|class|order|family|genus")
    print("  GET /api/stats           - Get data statistics")
    print("  GET /api/geographic-locations - List available geographic locations")
    print("  GET /api/location/<location> - Get data filtered by geographic location")
    print("    Query params: top=N, level=phylum|class|order|family|genus")
    print("  POST /api/cache/clear    - Clear composition cache")
    print("  GET /api/cache/stats     - Get cache statistics")
    print("=" * 60)
    
    # Run the server
    app.run(
        host='0.0.0.0',  # Allow external connections
        port=5001,       # Use port 5001 to avoid macOS AirPlay conflict
        debug=True       # Enable debug mode for development
    )
