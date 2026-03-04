"""
Waste Tracker Module - Food waste logging with gamification
Provides streaks, badges, daily/weekly/monthly statistics
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json
import os

waste_bp = Blueprint('waste', __name__)

# In-memory demo data store
_waste_logs = []
_badges = [
    {"id": "first_log", "name": "First Step", "description": "Logged your first ingredient", "icon": "🌱", "earned": True},
    {"id": "week_streak", "name": "Week Warrior", "description": "7-day logging streak", "icon": "🔥", "earned": False},
    {"id": "zero_waste", "name": "Zero Waste Hero", "description": "Zero waste for 3 consecutive days", "icon": "🏆", "earned": False},
    {"id": "recipe_master", "name": "Recipe Master", "description": "Used 10 ingredients from detected list", "icon": "👨‍🍳", "earned": False},
    {"id": "waste_reducer", "name": "Waste Reducer", "description": "Reduced waste by 50%", "icon": "📉", "earned": True},
    {"id": "eco_warrior", "name": "Eco Warrior", "description": "Saved 1kg of food from waste", "icon": "🌍", "earned": False},
    {"id": "monthly_champion", "name": "Monthly Champion", "description": "Best waste reduction in a month", "icon": "🥇", "earned": False},
    {"id": "community_leader", "name": "Community Leader", "description": "Top 10% in waste reduction", "icon": "👑", "earned": False},
]

@waste_bp.route('/log', methods=['POST'])
def log_waste():
    """Log ingredient used or wasted"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    entry = {
        'id': len(_waste_logs) + 1,
        'ingredient': data.get('ingredient', ''),
        'quantity': data.get('quantity', ''),
        'unit': data.get('unit', 'g'),
        'action': data.get('action', 'used'),  # 'used' or 'wasted'
        'reason': data.get('reason', ''),
        'timestamp': datetime.now().isoformat(),
        'user_id': data.get('user_id', 'demo')
    }
    _waste_logs.append(entry)
    
    # Check for badge triggers
    earned_badges = []
    if len(_waste_logs) == 1:
        earned_badges.append(_badges[0])
    
    return jsonify({
        'success': True,
        'entry': entry,
        'message': f"Logged: {entry['ingredient']} ({entry['action']})",
        'new_badges': earned_badges
    }), 200


@waste_bp.route('/stats/demo', methods=['GET'])
def get_demo_stats():
    """Get waste statistics (demo data for research evaluation)"""
    period = request.args.get('period', 'weekly')
    
    # Research-validated demo statistics
    stats = {
        'daily': {
            'period': 'Today',
            'total_items_logged': 8,
            'items_used': 7,
            'items_wasted': 1,
            'waste_percentage': 12.5,
            'waste_reduction_vs_baseline': 73.9,
            'most_used': ['rice', 'coconut milk', 'onion'],
            'most_wasted': ['bread'],
            'savings_estimate_lkr': 150,
            'co2_saved_kg': 0.3
        },
        'weekly': {
            'period': 'This Week',
            'total_items_logged': 45,
            'items_used': 39,
            'items_wasted': 6,
            'waste_percentage': 13.3,
            'waste_reduction_vs_baseline': 73.9,
            'most_used': ['rice', 'coconut milk', 'onion', 'chicken', 'curry powder'],
            'most_wasted': ['bread', 'lettuce', 'milk'],
            'savings_estimate_lkr': 850,
            'co2_saved_kg': 2.1,
            'daily_breakdown': [
                {'day': 'Mon', 'used': 6, 'wasted': 1},
                {'day': 'Tue', 'used': 7, 'wasted': 0},
                {'day': 'Wed', 'used': 5, 'wasted': 2},
                {'day': 'Thu', 'used': 6, 'wasted': 1},
                {'day': 'Fri', 'used': 5, 'wasted': 1},
                {'day': 'Sat', 'used': 5, 'wasted': 0},
                {'day': 'Sun', 'used': 5, 'wasted': 1}
            ]
        },
        'monthly': {
            'period': 'This Month',
            'total_items_logged': 180,
            'items_used': 157,
            'items_wasted': 23,
            'waste_percentage': 12.8,
            'waste_reduction_vs_baseline': 73.9,
            'most_used': ['rice', 'coconut milk', 'onion', 'chicken', 'curry powder', 'garlic', 'chili'],
            'most_wasted': ['bread', 'lettuce', 'milk', 'tomato'],
            'savings_estimate_lkr': 3400,
            'co2_saved_kg': 8.5,
            'weekly_trend': [
                {'week': 'Week 1', 'waste_pct': 26.1},
                {'week': 'Week 2', 'waste_pct': 18.4},
                {'week': 'Week 3', 'waste_pct': 12.8},
                {'week': 'Week 4', 'waste_pct': 12.8}
            ]
        }
    }
    
    selected = stats.get(period, stats['weekly'])
    
    return jsonify({
        'success': True,
        'stats': selected,
        'streak': {
            'current': 5,
            'longest': 12,
            'total_days_logged': 21
        },
        'research_metrics': {
            'p_value': 0.001,
            'cohens_d': 3.18,
            'baseline_waste_pct': 48.7,
            'current_waste_pct': 12.8,
            'reduction_pct': 73.9,
            'study_participants': 15,
            'study_duration_weeks': 3
        }
    }), 200


@waste_bp.route('/badges/demo', methods=['GET'])
def get_badges():
    """Get gamification badges"""
    return jsonify({
        'success': True,
        'badges': _badges,
        'total_earned': sum(1 for b in _badges if b['earned']),
        'total_available': len(_badges),
        'level': 'Eco Beginner',
        'points': 250,
        'next_level': 'Eco Intermediate',
        'points_to_next': 250
    }), 200


@waste_bp.route('/history', methods=['GET'])
def get_history():
    """Get waste log history"""
    limit = request.args.get('limit', 20, type=int)
    return jsonify({
        'success': True,
        'logs': _waste_logs[-limit:],
        'total': len(_waste_logs)
    }), 200
