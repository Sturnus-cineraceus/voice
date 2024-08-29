from pathlib import Path

import sys, os
import hashlib
import re
from datetime import date
import simpleaudio
import argparse

core = None
# core = VoicevoxCore(open_jtalk_dict_dir=Path("./open_jtalk_dic_utf_8-1.11"))
speaker_id = 1

wavepath = "./wav/"
script_txt = "./script.txt"
play_list = []
dayuntil_pattern = r'\{days_until \d{4}-\d{2}-\d{2}\}'



def load_script():
    with open(script_txt) as f:
        lst = f.readlines()
        lst = [s.replace('\n','') for s in lst if not s.startswith("#") ]
        lst = [s for s in lst if len(s) != 0]
        return lst

#動的にセリフを変えるやつ
def convert_clause(clause):
    findlist = re.findall(dayuntil_pattern, clause)
    if len(findlist) > 0:
        for du in findlist:
            datestr = du.replace('{days_until ','').replace('}','')
            udate = date.fromisoformat(datestr)
            today = date.today()
            days = (udate - today).days
            daystr = str(days)
            if udate < today :
                daystr = "マイナス" + daystr
            clause = clause.replace(du,daystr)
        
    return clause


def make_voice(clause):
    clause = convert_clause(clause)
    hash = hashlib.md5(clause.encode(encoding='utf-8')).hexdigest()
    name = hash + ".wav"
    filepath = wavepath + name
    play_list.append(name)
    if os.path.exists(filepath):
        return
    global core
    if core is None:
        from voicevox_core import VoicevoxCore, METAS
        core = VoicevoxCore(open_jtalk_dict_dir=Path("./open_jtalk_dic_utf_8-1.11"))
    if not core.is_model_loaded(speaker_id):
        core.load_model(speaker_id)
        
    wave_bytes = core.tts(clause, speaker_id)
    with open(filepath,"wb") as f:
            f.write(wave_bytes)

def play_voice():
    for wav in play_list:
        try:     
            # pygame.mixer.music.load(wavepath + wav)
            # pygame.mixer.music.play()
            # while pygame.mixer.music.get_busy():
            #     pass
            wav_obj = simpleaudio.WaveObject.from_wave_file(wavepath + wav)
            play_obj = wav_obj.play()
            play_obj.wait_done()
        except Exception as e:
            print(e)
            
def sweep_file():
    file_names = os.listdir(wavepath)
    target_files = set(file_names) - set(play_list)
    for file in target_files:
        os.remove(wavepath + file)


def main():
    parser = argparse.ArgumentParser(description="-m オプションがあります")
    parser.add_argument('-m', action='store_true', help="これをセットすると、音声を作るだけで再生はしません")

    args = parser.parse_args()
    
    #セリフをロードする
    voice_list = load_script()
    for v in voice_list:
        make_voice(v)
    #再生
    if not args.m:
        play_voice()
    #使わないファイルは削除
    sweep_file()
    
    
if __name__ == '__main__':
    main()
    