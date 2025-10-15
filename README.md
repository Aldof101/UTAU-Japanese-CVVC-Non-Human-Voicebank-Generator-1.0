Automated Tool for Creating Japanese CVVC Voicebanks Without a Human Voice Provider (Non-human Voicebank) Version 1.0

Before using the script, please ensure you have a Python environment installed. To use it, open ajpncvvc.py with Notepad or a text editor. Change the paths at the beginning:
consonant_path = r"this\is\a\PATH"
vowel_path = r"this\is\a\PATH"
output_path = r"this\is\a\PATH"
These represent the consonant path (you can use the Japanese consonant path included in this file, or change it to your own consonant folder), the vowel path (please ensure you have six mono, 44100Hz, 16-bit audio files: a.wav, i.wav, u.wav, e.wav, o.wav, and n.wav), and the output path (where the concatenated phonemes will be saved). Then run the script.

After using MoreSampler to automatically generate the CVVC oto.ini, missing sounds may occur due to labeling issues. To fix this, change the path at the end of the script cvvcotofixer.py: oto_file_path = r"this\is\YOUR\oto.ini" to the corresponding path of your oto.ini (usually located in the folder with the concatenated phonemes). Save the script and run it. To prevent incorrect operation, the script will create a backup oto.ini.bak in the same directory, which you can delete.

This script is open source and intended solely for the creation and learning reference of Non-human Voicebanks. It is prohibited for commercial and illegal use. By Aldof
