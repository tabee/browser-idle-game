# Browser Idle Game ⚔️

A browser-based idle game inspired by "We Are Warriors!" featuring warriors, battles, and resource management. Built with Python Flask backend and vanilla JavaScript frontend with canvas graphics.

## Features

- 🎮 Idle gameplay with automatic resource generation
- ⚔️ Warrior recruitment and upgrades
- 🌊 Wave-based battle system
- 💰 Resource management (gold, warriors)
- 📈 Progressive difficulty scaling
- 🎨 Simple canvas-based graphics
- 🔄 Real-time updates via WebSocket
- 🐳 Docker-compose setup for easy deployment

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/tabee/browser-idle-game.git
cd browser-idle-game
```

2. Start the game using docker-compose:
```bash
docker-compose up --build
```

3. Open your browser and navigate to:
```
http://localhost:8080
```

The backend API will be running on `http://localhost:5000`

## How to Play

1. **Gather Gold**: Gold is automatically generated over time based on your gold per second rate
2. **Buy Warriors**: Use gold to recruit warriors who will fight for you
3. **Upgrade**: Improve your gold income and warrior strength
4. **Battle**: Send your warriors into battle against increasingly difficult enemy waves
5. **Progress**: Defeat enemies to earn rewards and advance to higher waves

## Game Mechanics

- **Idle Progression**: Resources accumulate even when you're not actively playing (up to 1 hour)
- **Auto-Battle**: Once started, battles continue automatically until victory or defeat
- **Scaling**: Each wave increases enemy health and strength
- **Upgrades**: Warrior cost, gold income, and strength can all be upgraded

## Architecture

- **Backend**: Python Flask with Flask-SocketIO for real-time communication
- **Frontend**: HTML5, CSS3, vanilla JavaScript with Canvas API
- **Communication**: REST API for actions, WebSocket for state updates
- **Deployment**: Docker containers orchestrated with docker-compose

## Development

### Running without Docker

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

**Frontend:**
Serve the frontend directory with any static file server, e.g.:
```bash
cd frontend
python -m http.server 8080
```

### Project Structure

```
browser-idle-game/
├── backend/
│   ├── app.py              # Flask application with game logic
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Backend container config
├── frontend/
│   ├── index.html         # Main HTML page
│   ├── style.css          # Styling
│   ├── game.js            # Game logic and canvas rendering
│   └── Dockerfile         # Frontend container config
├── docker-compose.yml     # Docker orchestration
└── README.md             # This file
```

## API Endpoints

- `GET /api/state` - Get current game state
- `POST /api/buy_warrior` - Purchase a warrior
- `POST /api/upgrade_gold` - Upgrade gold per second
- `POST /api/upgrade_strength` - Upgrade warrior strength
- `POST /api/start_battle` - Begin battle with current wave

## Technologies Used

- **Backend**: Python 3.11, Flask, Flask-SocketIO, Flask-CORS
- **Frontend**: HTML5 Canvas, JavaScript ES6+, Socket.IO client
- **Infrastructure**: Docker, docker-compose, nginx

## License

MIT

## Acknowledgments

Inspired by "We Are Warriors!" by Lessmore UG