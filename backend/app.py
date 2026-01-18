from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import time
import threading
import math

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Game balance constants
INITIAL_ENEMY_HEALTH = 100
ENEMY_HEALTH_MULTIPLIER = 1.2
INITIAL_ENEMY_STRENGTH = 5
ENEMY_STRENGTH_MULTIPLIER = 1.15

# Game state
game_state = {
    'resources': {
        'gold': 100,
        'warriors': 5
    },
    'upgrades': {
        'warrior_cost': 10,
        'gold_per_second': 1.0,
        'warriors_per_second': 0.1,
        'warrior_strength': 1.0
    },
    'battle': {
        'enemy_health': 100,
        'enemy_max_health': 100,
        'enemy_strength': 5,
        'wave': 1,
        'in_combat': False
    },
    'last_update': time.time()
}

def calculate_idle_progress():
    """Calculate resources gained while idle"""
    current_time = time.time()
    elapsed = current_time - game_state['last_update']
    
    # Cap at 1 hour of idle time
    elapsed = min(elapsed, 3600)
    
    # Calculate gold gained
    gold_gained = game_state['upgrades']['gold_per_second'] * elapsed
    game_state['resources']['gold'] += gold_gained
    
    # Update timestamp
    game_state['last_update'] = current_time
    
    return gold_gained

def game_loop():
    """Main game loop that runs every second"""
    while True:
        time.sleep(1)
        
        # Generate passive resources
        game_state['resources']['gold'] += game_state['upgrades']['gold_per_second']
        
        # Auto-battle if in combat
        if game_state['battle']['in_combat']:
            # Warriors attack enemy
            damage = game_state['resources']['warriors'] * game_state['upgrades']['warrior_strength']
            game_state['battle']['enemy_health'] -= damage
            
            # Enemy attacks back
            warrior_loss = game_state['battle']['enemy_strength'] / 10.0
            game_state['resources']['warriors'] = max(0, game_state['resources']['warriors'] - warrior_loss)
            
            # Check if enemy defeated
            if game_state['battle']['enemy_health'] <= 0:
                # Victory! Give rewards and spawn new enemy
                wave = game_state['battle']['wave']
                game_state['resources']['gold'] += 50 * wave
                game_state['battle']['wave'] += 1
                
                # Scale enemy difficulty
                game_state['battle']['enemy_max_health'] = int(INITIAL_ENEMY_HEALTH * math.pow(ENEMY_HEALTH_MULTIPLIER, wave))
                game_state['battle']['enemy_health'] = game_state['battle']['enemy_max_health']
                game_state['battle']['enemy_strength'] = int(INITIAL_ENEMY_STRENGTH * math.pow(ENEMY_STRENGTH_MULTIPLIER, wave))
                game_state['battle']['in_combat'] = False
            
            # Check if all warriors dead
            elif game_state['resources']['warriors'] <= 0:
                game_state['battle']['in_combat'] = False
        
        game_state['last_update'] = time.time()
        
        # Broadcast state to all connected clients
        socketio.emit('game_state', game_state, broadcast=True)

@app.route('/')
def index():
    return jsonify({'status': 'ok', 'message': 'Idle Game API'})

@app.route('/api/state', methods=['GET'])
def get_state():
    """Get current game state"""
    calculate_idle_progress()
    return jsonify(game_state)

@app.route('/api/buy_warrior', methods=['POST'])
def buy_warrior():
    """Buy a new warrior"""
    cost = game_state['upgrades']['warrior_cost']
    
    if game_state['resources']['gold'] >= cost:
        game_state['resources']['gold'] -= cost
        game_state['resources']['warriors'] += 1
        # Increase cost for next warrior
        game_state['upgrades']['warrior_cost'] = int(cost * 1.15)
        return jsonify({'success': True, 'state': game_state})
    else:
        return jsonify({'success': False, 'error': 'Not enough gold'}), 400

@app.route('/api/upgrade_gold', methods=['POST'])
def upgrade_gold():
    """Upgrade gold per second"""
    cost = int(100 * math.pow(1.5, game_state['upgrades']['gold_per_second']))
    
    if game_state['resources']['gold'] >= cost:
        game_state['resources']['gold'] -= cost
        game_state['upgrades']['gold_per_second'] += 0.5
        return jsonify({'success': True, 'state': game_state})
    else:
        return jsonify({'success': False, 'error': 'Not enough gold'}), 400

@app.route('/api/upgrade_strength', methods=['POST'])
def upgrade_strength():
    """Upgrade warrior strength"""
    cost = int(200 * math.pow(1.5, game_state['upgrades']['warrior_strength']))
    
    if game_state['resources']['gold'] >= cost:
        game_state['resources']['gold'] -= cost
        game_state['upgrades']['warrior_strength'] += 0.5
        return jsonify({'success': True, 'state': game_state})
    else:
        return jsonify({'success': False, 'error': 'Not enough gold'}), 400

@app.route('/api/start_battle', methods=['POST'])
def start_battle():
    """Start a battle with current enemy"""
    if game_state['resources']['warriors'] > 0:
        game_state['battle']['in_combat'] = True
        return jsonify({'success': True, 'state': game_state})
    else:
        return jsonify({'success': False, 'error': 'Need at least 1 warrior'}), 400

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('game_state', game_state)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnect"""
    print('Client disconnected')

if __name__ == '__main__':
    # Start game loop in background thread
    game_thread = threading.Thread(target=game_loop, daemon=True)
    game_thread.start()
    
    # Run Flask-SocketIO server
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
