🛡️ Ransomware Honeypot Demo

📌 Overview

This project is a simple ransomware honeypot system that detects, isolates, and recovers from ransomware-like attacks in a controlled environment.

⚙️ How It Works

1. Run honeypot_setup.py
   
   Creates honeypot (decoy) files
   
   Creates backup of original files
3. Run monitor.py

   Continuously monitors file activity

   Detects suspicious behavior
5. Run attacker_simulator.py (for demo)

   Simulates ransomware attack

   Encrypts/changes files like real malware
7. Detection & Response

   Monitor detects abnormal activity

   isolator.py isolates the attacking process

   Encrypted files are removed

   Files are restored from backup

▶️ Running Order

Step 1: Setup honeypot
  
  python honeypot_setup.py

Step 2: Start monitoring
  
  python monitor.py

Step 3: Simulate attack (demo)
  
  python attacker_simulator.py

📂 Files

->  honeypot_setup.py → Setup honeypot & backup

->  monitor.py → Monitor and detect attacks

->  attacker_simulator.py → Simulate ransomware

->  isolator.py → Stop attacker & recover files

⚠️ Disclaimer

For educational purposes only.
