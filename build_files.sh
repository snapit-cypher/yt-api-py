echo "BUILD START"
python3.9 -m pip install -r requirements.txt
apt-get update && apt-get install -y ffmpeg
echo "BUILD END"