"""
waste_tracker.py — Stub file
Real implementation will be added by teammate when ready.
"""
from flask import Blueprint, jsonify

waste_bp = Blueprint('waste', __name__)

@waste_bp.route('/status', methods=['GET'])
def waste_status():
    return jsonify({'status': 'Waste tracker stub — pending teammate implementation'}), 200
