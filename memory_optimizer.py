#!/usr/bin/env python3
"""
Memory Management and Optimization Tool for Ollama on macOS
"""

import subprocess
import sys
import os
import psutil
import time

def check_system_memory():
    """Check available system memory."""
    print("🔍 System Memory Analysis")
    print("-" * 30)
    
    # Get memory info using psutil
    memory = psutil.virtual_memory()
    
    print(f"Total RAM: {memory.total / (1024**3):.1f} GB")
    print(f"Available RAM: {memory.available / (1024**3):.1f} GB")
    print(f"Used RAM: {memory.used / (1024**3):.1f} GB ({memory.percent:.1f}%)")
    print(f"Free RAM: {memory.free / (1024**3):.1f} GB")
    
    # Check if we have enough memory for gpt-oss:20b
    available_gb = memory.available / (1024**3)
    
    print(f"\n💡 Model Compatibility:")
    if available_gb >= 14:
        print(f"✅ gpt-oss:20b: Recommended (14+ GB available)")
    elif available_gb >= 10:
        print(f"⚠️  gpt-oss:20b: Possible but risky ({available_gb:.1f} GB available)")
    else:
        print(f"❌ gpt-oss:20b: Not recommended ({available_gb:.1f} GB available)")
    
    if available_gb >= 6:
        print(f"✅ llama3.1:8b: Recommended")
    else:
        print(f"⚠️  llama3.1:8b: May struggle")
    
    print(f"✅ phi3:mini: Always compatible (2GB required)")
    
    return available_gb

def check_ollama_processes():
    """Check Ollama processes and their memory usage."""
    print(f"\n🔍 Ollama Process Analysis")
    print("-" * 30)
    
    ollama_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
        try:
            if 'ollama' in proc.info['name'].lower():
                ollama_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if ollama_processes:
        total_memory = 0
        for proc in ollama_processes:
            memory_mb = proc.info['memory_info'].rss / (1024**2)
            total_memory += memory_mb
            print(f"PID {proc.info['pid']}: {proc.info['name']} - {memory_mb:.0f} MB")
        
        print(f"Total Ollama Memory Usage: {total_memory:.0f} MB ({total_memory/1024:.1f} GB)")
        return total_memory
    else:
        print("No Ollama processes found")
        return 0

def optimize_macos_memory():
    """Optimize macOS memory for better Ollama performance."""
    print(f"\n🔧 macOS Memory Optimization")
    print("-" * 30)
    
    recommendations = [
        "1. Close unnecessary applications (Chrome tabs, etc.)",
        "2. Restart Ollama service: pkill ollama && ollama serve",
        "3. Increase swap space if needed",
        "4. Monitor Activity Monitor for memory pressure",
        "5. Use smaller chunk sizes in the web scraper",
        "6. Process fewer chunks simultaneously"
    ]
    
    for rec in recommendations:
        print(f"💡 {rec}")
    
    return recommendations

def restart_ollama_optimized():
    """Restart Ollama with optimized settings."""
    print(f"\n🔄 Restarting Ollama with Optimization")
    print("-" * 40)
    
    try:
        # Stop existing Ollama processes
        print("🛑 Stopping Ollama processes...")
        subprocess.run(['pkill', '-f', 'ollama'], check=False)
        time.sleep(3)
        
        # Set environment variables for optimization
        env = os.environ.copy()
        env.update({
            'OLLAMA_MAX_LOADED_MODELS': '1',
            'OLLAMA_MAX_QUEUE': '1', 
            'OLLAMA_NUM_PARALLEL': '1',
            'OLLAMA_FLASH_ATTENTION': '1',
            'OLLAMA_HOST': '127.0.0.1:11434'
        })
        
        print("🚀 Starting optimized Ollama service...")
        
        # Start Ollama in background
        process = subprocess.Popen(['ollama', 'serve'], env=env)
        
        print(f"✅ Ollama started with PID: {process.pid}")
        print("⏳ Waiting for service to be ready...")
        time.sleep(5)
        
        # Test if Ollama is responding
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            if result.returncode == 0:
                print("✅ Ollama service is responding")
                return True
            else:
                print("❌ Ollama service not responding properly")
                return False
        except subprocess.TimeoutExpired:
            print("⚠️  Ollama service startup timeout")
            return False
            
    except Exception as e:
        print(f"❌ Error restarting Ollama: {e}")
        return False

def install_efficient_models():
    """Install memory-efficient models as fallbacks."""
    print(f"\n📥 Installing Memory-Efficient Models")
    print("-" * 40)
    
    efficient_models = [
        ("llama3.1:8b", "8B parameter model - good balance of performance/memory"),
        ("phi3:mini", "Mini model - very memory efficient")
    ]
    
    for model_name, description in efficient_models:
        print(f"📦 Installing {model_name}: {description}")
        try:
            result = subprocess.run(['ollama', 'pull', model_name],
                                  capture_output=True,
                                  text=True,
                                  timeout=300)
            if result.returncode == 0:
                print(f"✅ {model_name} installed successfully")
            else:
                print(f"❌ Failed to install {model_name}: {result.stderr}")
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout installing {model_name}")
        except Exception as e:
            print(f"❌ Error installing {model_name}: {e}")

def main():
    """Main memory optimization function."""
    print("🧠 Ollama Memory Optimization Tool for macOS")
    print("=" * 50)
    
    # Check system memory
    available_memory = check_system_memory()
    
    # Check Ollama processes
    ollama_memory = check_ollama_processes()
    
    # Provide optimization recommendations
    optimize_macos_memory()
    
    # Ask user for actions
    print(f"\n🎯 Recommended Actions:")
    
    if available_memory < 10:
        print("❗ Low memory detected - strongly recommend using llama3.1:8b instead of gpt-oss:20b")
        install_models = input("Install memory-efficient models? (y/n): ").lower().strip()
        if install_models == 'y':
            install_efficient_models()
    
    if ollama_memory > 5000:  # More than 5GB
        restart = input("High Ollama memory usage detected. Restart with optimization? (y/n): ").lower().strip()
        if restart == 'y':
            restart_ollama_optimized()
    
    print(f"\n✨ Optimization complete!")
    print(f"💡 For best results with gpt-oss:20b:")
    print(f"   - Use chunk sizes of 2000-3000 characters")
    print(f"   - Process one chunk at a time")
    print(f"   - Monitor memory usage in Activity Monitor")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n👋 Optimization cancelled by user")
    except Exception as e:
        print(f"\n❌ Error during optimization: {e}")
        sys.exit(1)
