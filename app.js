// Telegram Web App initialization
const tg = window.Telegram.WebApp;
tg.expand();
tg.MainButton.setText('Mining Dashboard').show();

// API endpoint (change to your server URL)
const API_BASE = 'http://localhost:5000/api'; // For development
// const API_BASE = 'https://your-server.com/api'; // For production

let miningStatus = {
    running: false,
    hashrate: '0 H/s',
    uptime: 0
};

// DOM Elements
const statusBadge = document.getElementById('statusBadge');
const hashrateEl = document.getElementById('hashrate');
const uptimeEl = document.getElementById('uptime');
const walletEl = document.getElementById('walletAddress');
const poolEl = document.getElementById('poolName');
const cpuUsageEl = document.getElementById('cpuUsage');
const memoryUsageEl = document.getElementById('memoryUsage');
const cpuCoresEl = document.getElementById('cpuCores');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const loadingEl = document.getElementById('loading');
const statsInfoEl = document.getElementById('statsInfo');
const activityLogEl = document.getElementById('activityLog');

// Add log entry
function addLog(message) {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement('div');
    logEntry.textContent = `[${timestamp}] ${message}`;
    logEntry.className = 'mb-1';
    activityLogEl.prepend(logEntry);
    
    // Keep only last 5 logs
    if (activityLogEl.children.length > 5) {
        activityLogEl.removeChild(activityLogEl.lastChild);
    }
}

// Format time
function formatTime(seconds) {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
}

// Load mining status
async function loadData() {
    try {
        loadingEl.classList.remove('hidden');
        statsInfoEl.classList.add('hidden');
        
        const [statusRes, systemRes] = await Promise.all([
            fetch(`${API_BASE}/status`),
            fetch(`${API_BASE}/system`)
        ]);
        
        if (!statusRes.ok || !systemRes.ok) {
            throw new Error('API error');
        }
        
        const statusData = await statusRes.json();
        const systemData = await systemRes.json();
        
        // Update mining status
        miningStatus = statusData.mining;
        
        // Update UI
        statusBadge.textContent = miningStatus.running ? '🟢 Running' : '🔴 Stopped';
        statusBadge.className = `badge ${miningStatus.running ? 'bg-success' : 'bg-danger'}`;
        
        hashrateEl.textContent = miningStatus.hashrate;
        uptimeEl.textContent = formatTime(miningStatus.uptime);
        
        walletEl.textContent = statusData.config.wallet || 'Not set';
        poolEl.textContent = statusData.config.pool || 'Not connected';
        
        // Update system info
        cpuUsageEl.textContent = `${systemData.cpu.percent.toFixed(1)}%`;
        memoryUsageEl.textContent = `${systemData.memory.percent.toFixed(1)}%`;
        cpuCoresEl.textContent = systemData.cpu.cores;
        
        // Update buttons
        startBtn.disabled = miningStatus.running;
        stopBtn.disabled = !miningStatus.running;
        
        loadingEl.classList.add('hidden');
        statsInfoEl.classList.remove('hidden');
        
        addLog('Status refreshed');
        
    } catch (error) {
        console.error('Error loading data:', error);
        addLog('Error: Failed to load data');
        
        // Show error state
        statusBadge.textContent = '❌ Error';
        statusBadge.className = 'badge bg-warning';
        
        loadingEl.classList.add('hidden');
        statsInfoEl.classList.remove('hidden');
    }
}

// Start mining
async function startMining() {
    try {
        addLog('Starting mining...');
        startBtn.disabled = true;
        
        const response = await fetch(`${API_BASE}/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            tg.showPopup({
                title: '✅ Started',
                message: 'Mining has been started successfully'
            });
            addLog('Mining started');
            setTimeout(loadData, 2000); // Reload after 2 seconds
        } else {
            tg.showPopup({
                title: '❌ Error',
                message: data.message || 'Failed to start mining'
            });
            addLog(`Start failed: ${data.message}`);
        }
        
    } catch (error) {
        console.error('Error starting mining:', error);
        tg.showPopup({
            title: '❌ Error',
            message: 'Connection failed'
        });
        addLog('Connection error');
    } finally {
        startBtn.disabled = false;
    }
}

// Stop mining
async function stopMining() {
    try {
        addLog('Stopping mining...');
        stopBtn.disabled = true;
        
        const response = await fetch(`${API_BASE}/stop`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            tg.showPopup({
                title: '⏹ Stopped',
                message: 'Mining has been stopped'
            });
            addLog('Mining stopped');
            setTimeout(loadData, 2000); // Reload after 2 seconds
        } else {
            tg.showPopup({
                title: '❌ Error',
                message: data.message || 'Failed to stop mining'
            });
            addLog(`Stop failed: ${data.message}`);
        }
        
    } catch (error) {
        console.error('Error stopping mining:', error);
        tg.showPopup({
            title: '❌ Error',
            message: 'Connection failed'
        });
        addLog('Connection error');
    } finally {
        stopBtn.disabled = false;
    }
}

// Telegram event handlers
tg.onEvent('viewportChanged', () => {
    tg.expand();
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Set theme based on Telegram
    document.body.style.backgroundColor = tg.themeParams.bg_color || '#212121';
    document.body.style.color = tg.themeParams.text_color || '#ffffff';
    
    // Load initial data
    loadData();
    
    // Auto-refresh every 10 seconds
    setInterval(loadData, 10000);
    
    addLog('Mining controller initialized');
});
