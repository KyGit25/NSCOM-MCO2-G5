# 🎧 Real-Time Audio Streaming over IP (NSCOM01 – MCO2)

This project implements a **VoIP (Voice over IP)** system using:
- **SIP over UDP** for call signaling (INVITE, 200 OK, ACK, BYE)  
- **RTP** for audio transmission using audio files  
- **RTCP** for periodic quality feedback  
- **Tkinter GUI** for easy call control by both caller and receiver

---

## 📦 Features

✅ SIP Handshake with custom SDP  
✅ RTP Audio Streaming from audio file  
✅ RTP Playback at receiver  
✅ RTCP Sender Reports (packet, byte stats)  
✅ GUI Interfaces for Caller and Receiver  
✅ Basic error handling (timeouts, format checks)  
✅ Call teardown with proper cleanup  
✅ G.711 (PCM µ-law) audio compatibility  

---

## 📁 File Structure

```
/voip-project/
├── sip_signaling.py       # SIP protocol logic
├── rtp_sender.py          # RTP packet construction + audio streaming
├── rtp_receiver.py        # RTP reception + audio playback
├── rtcp_sender.py         # RTCP sender report generator
├── voip_gui_client1.py    # Caller GUI (sends INVITE and audio)
├── voip_gui_client2.py    # Callee GUI (accepts call, plays audio)
└── README.md              # You're here
```

---

## ⚙️ Requirements

Install Python 3 and the following packages:

```bash
pip install pyaudio
```

> On Linux, install this first if needed:
```bash
sudo apt install portaudio19-dev python3-pyaudio
```

---

## 🚀 How to Run

### ✅ 1. Run Callee (Client 2)
```bash
python voip_gui_client2.py
```
- Listens for INVITE on `127.0.0.1:6060`
- Waits for call, then can **Play**, **Pause**, or **Teardown**

### ✅ 2. Run Caller (Client 1)
```bash
python voip_gui_client1.py
```
- Click “Choose Audio File” to select a valid `.wav` file (must be mono, 8kHz, 16-bit)
- Click **Start Call** to initiate SIP signaling and stream RTP audio

---

## 📞 SIP Flow Overview

1. **Caller** sends `INVITE` with SDP details
2. **Callee** replies with `200 OK`
3. **Caller** sends `ACK` to confirm
4. **RTP** media stream begins (Caller → Callee)
5. **BYE** ends the call session

---

## 🧪 Test Cases

| Test Scenario                        | Expected Behavior                                  |
|-------------------------------------|----------------------------------------------------|
| Caller selects invalid audio file   | GUI shows error message                            |
| Caller clicks “Start Call”          | Logs “INVITE sent”, waits for “200 OK”             |
| Callee accepts call                 | Logs SIP response, enables “Play” button           |
| RTP audio plays on Callee side      | Clear audio received through speakers              |
| Click “End Call” or “Teardown”      | Stops RTP, resets GUI, SIP BYE sent                |
| SIP packet dropped (e.g. BYE lost)  | Call ends after timeout or GUI manual stop         |

---

## 🛠️ Error Handling

- **Audio Format Check:** Only accepts mono, 16-bit, 8kHz WAV files
- **SIP Timeouts:** Automatically logs and resets on unacknowledged calls
- **Exception Catching:** Catches socket/audio errors with fallback messages
- **Safe Teardown:** Cleans up audio, sockets, and GUI threads properly

---

## 📷 Sample Output (Console)

```
[SIP] INVITE sent
[SIP] 200 OK received. Sending ACK.
[RTP] Playing audio stream.
[RTCP] Sent Sender Report.
[RTP] Finished sending audio.
[SIP] BYE sent
```

---

## 🧑‍💻 Authors

**Kyle Maristela & Owen San Luis**  
*NSCOM01 – Term 2 AY 2025-2026*
