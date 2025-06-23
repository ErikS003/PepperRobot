**Setting up server/HTTP tunnel**
1. Set up ngrok:\
      1.1 Create an ngrok account and locate an authtoken\
      1.2 Run (in cmd) ngrok authtoken YOUR_AUTHTOKEN on the machine you wish to host the server (personal or garage pc) \
      1.3 Run python stt_Flask.py \
      1.4 Run ngrok http --scheme=http --host-header=localhost:5000 5000 \
2. Ensure that your script on pepper that sends audio to your server \
   (e.g test_send.py) has the correct ngrok url (shown when you run the above commands) \
3. You should now be able to send audio (or other data) from pepper to the server and recieve answers (or other data) back to pepper.
