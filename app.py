from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import json
import psutil
import os
import signal
from threading import Thread
import time

app = Flask(__name__)
CORS(app)  # អនុញ្ញាតឱ្យ Telegram ទាក់ទងមក

# អគ្គិសនី mining process
mining_process = None
mining_stats = {
    "running": False,
    "hashrate": "0 H/s",
    "shares": {"accepted": 0, "rejected": 0},
    "uptime": 0
}

def load_config():
    """អានការកំណត់រចនាសម្ព័ន្ធ mining"""
    try:
        with open('../config/config.json', 'r') as f:
            return json.load(f)
    except:
        # ការកំណត់រចនាសម្ព័ន្ធលំនាំដើម
        return {
            "pools": [{
                "name": "US-VIPOR",
                "url": "stratum+tcp://eu.luckpool.net:3960",
                "user": "RJsJZEayCndArTCLd816mmeCWmoK2XcTSY.Cyraxmod",
                "algo": "verus"
            }]
        }

config = load_config()

def check_mining_status():
    """ពិនិត្យមើលថាតើការជីកកំពុងដំណើរការឬទេ"""
    global mining_process
    if mining_process and mining_process.poll() is None:
        return True
    return False

@app.route('/api/start', methods=['POST'])
def start_mining():
    """ចាប់ផ្តើមការជីកគ្រីបតូ"""
    global mining_process
    
    if check_mining_status():
        return jsonify({"success": False, "message": "Mining already running"})
    
    try:
        # បង្កើត script ជីកគ្រីបតូ
        start_script = '''#!/bin/bash
cd /tmp
./ccminer -c config.json
'''
        
        # រក្សាទុក script
        with open('/tmp/start_mining.sh', 'w') as f:
            f.write(start_script)
        
        os.chmod('/tmp/start_mining.sh', 0o755)
        
        # ចាប់ផ្តើមដំណើរការ
        mining_process = subprocess.Popen(
            ['/tmp/start_mining.sh'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            preexec_fn=os.setsid
        )
        
        mining_stats["running"] = True
        mining_stats["start_time"] = time.time()
        
        return jsonify({
            "success": True,
            "message": "Mining started",
            "pid": mining_process.pid
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/stop', methods=['POST'])
def stop_mining():
    """បញ្ឈប់ការជីកគ្រីបតូ"""
    global mining_process
    
    try:
        if mining_process:
            # បញ្ឈប់ដំណើរការ និងកូនរបស់វា
            os.killpg(os.getpgid(mining_process.pid), signal.SIGTERM)
            mining_process.wait()
            mining_process = None
        
        mining_stats["running"] = False
        mining_stats["uptime"] = 0
        
        return jsonify({"success": True, "message": "Mining stopped"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/status', methods=['GET'])
def get_status():
    """ទទួលស្ថានភាពបច្ចុប្បន្ន"""
    global mining_stats
    
    if check_mining_status():
        mining_stats["running"] = True
        if "start_time" in mining_stats:
            mining_stats["uptime"] = int(time.time() - mining_stats["start_time"])
    else:
        mining_stats["running"] = False
    
    return jsonify({
        "mining": mining_stats,
        "config": {
            "wallet": config.get("pools", [{}])[0].get("user", ""),
            "pool": config.get("pools", [{}])[0].get("name", ""),
            "algorithm": config.get("algo", "verus")
        }
    })

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """គ្រប់គ្រងការកំណត់រចនាសម្ព័ន្ធ"""
    global config
    
    if request.method == 'POST':
        new_config = request.json
        with open('../config/config.json', 'w') as f:
            json.dump(new_config, f, indent=2)
        config = new_config
        return jsonify({"success": True, "message": "Config updated"})
    
    return jsonify(config)

@app.route('/api/system', methods=['GET'])
def system_info():
    """ទទួលព័ត៌មានប្រព័ន្ធ"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    return jsonify({
        "cpu": {
            "percent": cpu_percent,
            "cores": psutil.cpu_count()
        },
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent
        },
        "disk": {
            "total": psutil.disk_usage('/').total,
            "free": psutil.disk_usage('/').free
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """ពិនិត្យសុខភាព server"""
    return jsonify({"status": "healthy", "service": "mining-controller"})

if __name__ == '__main__':
    print("Starting Mining Controller API...")
    print("API available at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
