// Game state
let gameState = null;
let socket = null;

// Backend URL configuration
const BACKEND_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : `http://${window.location.hostname}:5000`;

// Canvas setup
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Animation state
let warriors = [];
let enemy = null;
let particles = [];

// Connect to backend
function connectToBackend() {
    socket = io(BACKEND_URL);
    
    socket.on('connect', () => {
        console.log('Connected to game server');
        fetchGameState();
    });
    
    socket.on('game_state', (state) => {
        updateGameState(state);
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from game server');
    });
}

// Fetch initial game state
async function fetchGameState() {
    try {
        const response = await fetch(`${BACKEND_URL}/api/state`);
        const state = await response.json();
        updateGameState(state);
    } catch (error) {
        console.error('Failed to fetch game state:', error);
    }
}

// Update game state
function updateGameState(state) {
    gameState = state;
    updateUI();
    updateWarriorPositions();
    updateEnemy();
}

// Update UI elements
function updateUI() {
    if (!gameState) return;
    
    document.getElementById('gold').textContent = Math.floor(gameState.resources.gold);
    document.getElementById('warriors').textContent = Math.floor(gameState.resources.warriors);
    document.getElementById('gold-per-sec').textContent = gameState.upgrades.gold_per_second.toFixed(1);
    document.getElementById('warrior-cost').textContent = gameState.upgrades.warrior_cost;
    document.getElementById('wave').textContent = gameState.battle.wave;
    document.getElementById('strength').textContent = gameState.upgrades.warrior_strength.toFixed(1);
    
    // Update upgrade costs
    const goldUpgradeCost = Math.floor(100 * Math.pow(1.5, gameState.upgrades.gold_per_second));
    const strengthUpgradeCost = Math.floor(200 * Math.pow(1.5, gameState.upgrades.warrior_strength));
    document.getElementById('gold-upgrade-cost').textContent = goldUpgradeCost;
    document.getElementById('strength-upgrade-cost').textContent = strengthUpgradeCost;
    
    // Update button states
    document.getElementById('buy-warrior').disabled = gameState.resources.gold < gameState.upgrades.warrior_cost;
    document.getElementById('upgrade-gold').disabled = gameState.resources.gold < goldUpgradeCost;
    document.getElementById('upgrade-strength').disabled = gameState.resources.gold < strengthUpgradeCost;
    document.getElementById('start-battle').disabled = gameState.resources.warriors < 1 || gameState.battle.in_combat;
    
    // Update battle status
    const battleStatus = document.getElementById('battle-status');
    if (gameState.battle.in_combat) {
        const healthPercent = (gameState.battle.enemy_health / gameState.battle.enemy_max_health * 100).toFixed(0);
        battleStatus.textContent = `⚔️ Fighting! Enemy: ${Math.floor(gameState.battle.enemy_health)}/${gameState.battle.enemy_max_health} (${healthPercent}%)`;
        battleStatus.style.color = '#f5576c';
    } else {
        battleStatus.textContent = '✅ Ready for battle';
        battleStatus.style.color = '#4caf50';
    }
}

// Update warrior positions for animation
function updateWarriorPositions() {
    if (!gameState) return;
    
    const targetCount = Math.floor(gameState.resources.warriors);
    
    // Add new warriors
    while (warriors.length < targetCount) {
        warriors.push({
            x: 50 + Math.random() * 200,
            y: 200 + Math.random() * 200,
            targetX: 50 + Math.random() * 200,
            targetY: 200 + Math.random() * 200,
            color: `hsl(${Math.random() * 60 + 200}, 70%, 50%)`,
            size: 15 + Math.random() * 5
        });
    }
    
    // Remove excess warriors
    while (warriors.length > targetCount) {
        warriors.pop();
    }
}

// Update enemy
function updateEnemy() {
    if (!gameState) return;
    
    if (!enemy || !gameState.battle.in_combat) {
        enemy = {
            x: 450,
            y: 250,
            size: 30,
            color: '#f5576c',
            health: gameState.battle.enemy_health,
            maxHealth: gameState.battle.enemy_max_health
        };
    } else {
        enemy.health = gameState.battle.enemy_health;
        enemy.maxHealth = gameState.battle.enemy_max_health;
    }
}

// Create particle effect
function createParticle(x, y, color) {
    particles.push({
        x: x,
        y: y,
        vx: (Math.random() - 0.5) * 4,
        vy: (Math.random() - 0.5) * 4,
        life: 30,
        color: color,
        size: 3 + Math.random() * 3
    });
}

// Render game
function render() {
    // Clear canvas
    ctx.fillStyle = '#34495e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    if (!gameState) {
        ctx.fillStyle = 'white';
        ctx.font = '20px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Connecting to server...', canvas.width / 2, canvas.height / 2);
        return;
    }
    
    // Draw ground
    ctx.fillStyle = '#2c3e50';
    ctx.fillRect(0, 400, canvas.width, 100);
    
    // Draw warriors
    warriors.forEach((warrior, index) => {
        // Animate movement
        warrior.x += (warrior.targetX - warrior.x) * 0.05;
        warrior.y += (warrior.targetY - warrior.y) * 0.05;
        
        // Change target occasionally
        if (Math.random() < 0.01) {
            warrior.targetX = 50 + Math.random() * 200;
            warrior.targetY = 200 + Math.random() * 200;
        }
        
        // Attack animation in combat
        if (gameState.battle.in_combat && Math.random() < 0.1) {
            warrior.targetX = 350 + Math.random() * 50;
            warrior.targetY = 220 + Math.random() * 60;
            
            if (Math.random() < 0.05) {
                createParticle(warrior.x, warrior.y, warrior.color);
            }
        }
        
        // Draw warrior (simple stick figure)
        ctx.fillStyle = warrior.color;
        ctx.beginPath();
        // Head
        ctx.arc(warrior.x, warrior.y, warrior.size * 0.4, 0, Math.PI * 2);
        ctx.fill();
        // Body
        ctx.fillRect(warrior.x - 2, warrior.y + warrior.size * 0.4, 4, warrior.size * 0.6);
        // Arms
        ctx.fillRect(warrior.x - warrior.size * 0.4, warrior.y + warrior.size * 0.5, warrior.size * 0.8, 3);
        // Legs
        ctx.fillRect(warrior.x - 5, warrior.y + warrior.size, 4, warrior.size * 0.5);
        ctx.fillRect(warrior.x + 1, warrior.y + warrior.size, 4, warrior.size * 0.5);
    });
    
    // Draw enemy
    if (enemy && gameState.battle.enemy_health > 0) {
        // Enemy body (larger monster)
        ctx.fillStyle = enemy.color;
        ctx.beginPath();
        ctx.arc(enemy.x, enemy.y, enemy.size, 0, Math.PI * 2);
        ctx.fill();
        
        // Enemy eyes
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.arc(enemy.x - 10, enemy.y - 5, 5, 0, Math.PI * 2);
        ctx.arc(enemy.x + 10, enemy.y - 5, 5, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.fillStyle = 'black';
        ctx.beginPath();
        ctx.arc(enemy.x - 10, enemy.y - 5, 2, 0, Math.PI * 2);
        ctx.arc(enemy.x + 10, enemy.y - 5, 2, 0, Math.PI * 2);
        ctx.fill();
        
        // Health bar
        const barWidth = 80;
        const barHeight = 8;
        const healthPercent = enemy.health / enemy.maxHealth;
        
        ctx.fillStyle = '#333';
        ctx.fillRect(enemy.x - barWidth / 2, enemy.y - enemy.size - 20, barWidth, barHeight);
        
        ctx.fillStyle = healthPercent > 0.5 ? '#4caf50' : healthPercent > 0.25 ? '#ff9800' : '#f44336';
        ctx.fillRect(enemy.x - barWidth / 2, enemy.y - enemy.size - 20, barWidth * healthPercent, barHeight);
        
        // Damage effect
        if (gameState.battle.in_combat && Math.random() < 0.2) {
            createParticle(enemy.x + (Math.random() - 0.5) * 40, enemy.y + (Math.random() - 0.5) * 40, '#ff6b6b');
        }
    }
    
    // Draw and update particles
    particles = particles.filter(p => {
        p.x += p.vx;
        p.y += p.vy;
        p.life--;
        
        ctx.fillStyle = p.color;
        ctx.globalAlpha = p.life / 30;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1;
        
        return p.life > 0;
    });
    
    // Draw info text
    ctx.fillStyle = 'white';
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'left';
    ctx.fillText(`Warriors: ${Math.floor(gameState.resources.warriors)}`, 10, 25);
    ctx.fillText(`Wave: ${gameState.battle.wave}`, 10, 50);
    
    requestAnimationFrame(render);
}

// API calls
async function makeAPICall(endpoint) {
    try {
        const response = await fetch(`${BACKEND_URL}/api/${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateGameState(data.state);
        } else {
            console.error('API error:', data.error);
        }
    } catch (error) {
        console.error('Failed to make API call:', error);
    }
}

// Event listeners
document.getElementById('buy-warrior').addEventListener('click', () => {
    makeAPICall('buy_warrior');
});

document.getElementById('upgrade-gold').addEventListener('click', () => {
    makeAPICall('upgrade_gold');
});

document.getElementById('upgrade-strength').addEventListener('click', () => {
    makeAPICall('upgrade_strength');
});

document.getElementById('start-battle').addEventListener('click', () => {
    makeAPICall('start_battle');
});

// Initialize
connectToBackend();
render();
