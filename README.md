# 🛡️ **RANSOMWARE HONEYPOT DEMO**

---

## 📌 Overview

This project is a simple ransomware honeypot system that detects, isolates, and recovers from ransomware-like attacks in a controlled environment.

---

## ⚙️ How It Works

### 1️⃣ Setup Phase

Run:

```
python honeypot_setup.py
```

* Creates honeypot (decoy) files
* Creates backup of original files

---

### 2️⃣ Monitoring Phase

Run:

```
python monitor.py
```

* Continuously monitors file activity
* Detects suspicious behavior

---

### 3️⃣ Attack Simulation (Demo)

Run:

```
python attacker_simulator.py
```

* Simulates ransomware attack
* Encrypts/changes files like real malware

---

### 🛡️ Detection & Response

* Monitor detects abnormal activity
* `isolator.py` isolates the attacking process
* Encrypted files are removed
* Files are restored from backup

---

## ▶️ Running Order

```
Step 1: python honeypot_setup.py
Step 2: python monitor.py
Step 3: python attacker_simulator.py
```

---

## 📂 Files

* `honeypot_setup.py` → Setup honeypot & backup
* `monitor.py` → Monitor and detect attacks
* `attacker_simulator.py` → Simulate ransomware
* `isolator.py` → Stop attacker & recover files

---

## ⚠️ Disclaimer

This project is for **educational purposes only**.
