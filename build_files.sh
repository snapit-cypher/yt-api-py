echo "BUILD START"
python3.9 -m pip install -r requirements.txt
apt-get update && apt-get install -y ffmpeg
chmod 755 /app && sudo chmod 777 /app/downloads/output
echo "BUILD END"