# 🎧 Real-Time Audio Streaming over IP (NSCOM01 – MCO2)

This project implements a **VoIP (Voice over IP)** system in Python using:
- SIP over UDP for session setup and teardown
- RTP for real-time audio streaming (from file or microphone)
- RTCP for simple quality statistics
- A Tkinter GUI for control and interaction

---

## 📦 Features

✅ SIP Handshake  
✅ SDP Negotiation (with codec/port)  
✅ RTP Audio Streaming (from mic)  
✅ RTP Audio Playback (real-time)  
✅ RTCP Reporting  
✅ GUI-based Call Control  
✅ Two-Way Voice Communication (mic-to-mic)  
✅ Error Handling and Cleanup

---

## 📁 File Structure

```
/NSCOM-MCO2-G5/
├── code/
│   ├── run_voip.py             # Entry point     
│   ├── Server.py               # Server
│   ├── Client.py               # Client
│   ├── AudioStream.py          # RTP audio stream 
│   ├── audio.wav               # Audio test file
│   ├── ServerWorker.py         # Server Worker
│   └── RtpPacket.py            # RTP packet creation/decoding
└── README.md               # You're here
```

---

## ⚙️ Requirements

Install these Python packages first:
```bash
pip install pyaudio
```

> 🔐 On Linux, you may also need:
```bash
sudo apt install portaudio19-dev python3-pyaudio
```

---

## 🚀 How to Run

### ✅ Launch Server
```bash
python Server.py 6060
```

### ✅ Launch Client 1 (Caller)
- On another terminal/PC (same LAN), also run:
```bash
python run_voip.py caller 127.0.0.1 5060 127.0.0.1 6060 5004 audio.wav
```

### ✅ Launch Client 2 (Callee)
- On another terminal/PC (same LAN), also run:
```bash
python run_voip.py callee 127.0.0.1 6060 127.0.0.1 5060 5006
```

### 📞 Making a Call
1. In the first window, enter the **remote IP** (e.g., `127.0.0.1` if local)
2. Click **Call**
3. Speak into your mic and listen on the other side
4. Click **Hang Up** to end the session

---

## 💡 Implemented SIP Flow

- `INVITE` ➝ sent to initiate call
- `200 OK` ➝ received with SDP info
- `ACK` ➝ confirms setup
- `BYE` ➝ sent to end call

---

## 🧪 Test Cases

| Test Description                 | Expected Result                                      |
|----------------------------------|------------------------------------------------------|
| Call established (INVITE → OK)   | "Call Started", GUI shows `Status: In Call`         |
| Speak into mic                   | Remote client plays voice via speakers              |
| End call (BYE sent)              | Status updates to `Call Ended`, resources released  |
| SIP Error (invalid address)      | Logs 4xx/5xx and GUI shows failed connection        |

---

## 🛠️ Error Handling

- Gracefully handles:
  - SIP errors (4xx, 5xx)
  - Socket timeouts
  - Microphone access failure
- Proper teardown on GUI close or Hang Up

---

## 📷 Sample Output (Terminal)

```
[SIP] INVITE sent
[SIP] 200 OK received
[SIP] ACK sent
[RTP] Microphone streaming started.
[RTP] Listening on port 5004...
[RTP] Received Seq=20 Len=160
...
[SIP] BYE sent
[RTP] Microphone streaming stopped.
[RTP] Receiver stopped.
```

---

## 👨‍💻 Authors

*Maristela, Kyle and San Luis, Owen*  
*NSCOM01 – Term 2 AY 2025-2026*  
