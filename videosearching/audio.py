#!usr/bin/env python
import pickle
import operator
import glob
import os

import scipy.signal as sig
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

def save_file(content, file):
    '''
    '''
    np.save(file, content)
    
def analysis_audio(path, save = None, save_path = None):
    '''
    intput: 
        path: path of audio, format: wav
        save: if the results should be saved
        save_path: str, the saved file path and name
    output:
        return the fft results of all chunk of data
    '''
    # data is stereo
    sample_freq, data = wavfile.read(path)
    # Sliding windows to sample from the audio and fft on them
    sliding_rate = sample_freq / 10
    results = []
    for i in range(0, len(data), int(sliding_rate)):
        step = int(sliding_rate)
        left = np.fft.fft(data[i:i+step, 0])
        right = np.fft.fft(data[i:i+step, 1])
        fft_res = np.stack((left, right), axis = -1)
        results.append(fft_res)
    results = np.asarray(results)
    if save is not None:
        save_file(results, save_path)
    return results

freq_range = [40, 80, 120, 180, 300]
def get_index(freq):
    i = 0
    while freq_range[i] < freq:
        i = i + 1
    return i - 1

def voice_print(results, channel):
    '''
        channel: list of voice channels, left or right or both, 0 for left, 1 for right
    '''
    dim = results.shape
    high_scores = np.full((dim[0], len(freq_range) - 1, len(channel)), -np.Inf)
    points = np.zeros((dim[0], len(freq_range) - 1, len(channel)))
    finger_print = []
    for t in range(dim[0]):
        for freq in range(40, 300):
            idx = get_index(freq)
            for c in channel:
                
                mag = np.log(np.abs(results[t][freq][c]) + 1 )
            
                if mag > high_scores[t][idx][c]:
                    high_scores[t][idx][c] = mag
                    points[t][idx][c] = freq
                    
        h = hash_function(points[t])
        finger_print.append((h , (t+1)*0.1))
    return finger_print
    
def get_hash(peaks_val):
    assert len(peaks_val) == 4
    FACTOR = 2
    return int((peaks_val[3] - (peaks_val[3] % FACTOR)) * 1000000 + (peaks_val[2] - (peaks_val[2] % FACTOR))
        * 100000 + (peaks_val[1] - (peaks_val[1] % FACTOR)) * 100
            + (peaks_val[0] - (peaks_val[0] % FACTOR)))
        
def hash_function(content):
    '''
    input: 
        content: list of contents
    output:
        list value of channels
    '''
    res = []
    for c in range(content.shape[1]):
        res.append(get_hash(content[:, c]))
    return res


def load_voiceprint(database_path):
    voiceprint_database = None
    with open(database_path, 'rb') as f:
        voiceprint_database = pickle.load(f)
    return voiceprint_database

def save_voiceprint(voice_path, saved_path, filenames_dict):
    print(saved_path, saved_path)
    file_paths = glob.glob(voice_path)
    voiceprint_database = dict()
    for file_path in file_paths:
        file_name = file_path.split('/')[-2]
        file_index = filenames_dict.get(file_name, -1)
        if file_index == -1: 
            continue
#         print(file_name)
        cur_voice_res = analysis_audio(file_path)
        cur_voiceprint = voice_print(cur_voice_res, [0,1])
        voiceprint_database[file_index] = cur_voiceprint
    
    with open(saved_path, 'wb') as f:
        pickle.dump(voiceprint_database, f)


def audio_interface(query_path, database_path):
    '''
    '''
    voiceprint_database = load_voiceprint(database_path)
    print(query_path)
    query_path = glob.glob(query_path + '/*.wav')[0]
    query_results = analysis_audio(query_path)
    query_print = voice_print(query_results, [0,1])
    
    similarity = list()
    
    for key, value in voiceprint_database.items():
        base_left = set()
        base_right = set()
        for item in value:
            base_left.add(item[0][0])
            base_right.add(item[0][1])
        total_nums = len(query_print) * 2
        similar_nums = 0
        for item in query_print:
            left_key = item[0][0]
            right_key = item[0][1]
            if left_key in base_left:
                similar_nums += 1
            if right_key in base_right:
                similar_nums += 1
        similarity.append((key, similar_nums/total_nums))
    
    # similarity.sort(key = operator.itemgetter(0), reverse = True)
    similarity.sort(key = operator.itemgetter(0))
    return similarity



if __name__ == '__main__':

    voice_path = '../databse_videos/*/*.wav'
    saved_path = '../voice_base/data.pkl'
    filenames_dict = {'flowers': 0, 'interview': 1, 'movie': 2, 'musicvideo': 3, 'sports': 4, 'starcraft': 5, 'traffic': 6}
    if not os.path.exists(saved_path):
        print('executing processing the whole database videos')
        save_voiceprint(voice_path, saved_path, filenames_dict)

    query_path = '/Users/xingwenzhang/work/courses/576/project/new queries/Not From Searching Content/HQ4'
    print('the results for the query are')
    result = audio_interface(query_path, saved_path)
    for item in result:
        print(item)

