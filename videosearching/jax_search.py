# coding: utf-8
#!/usr/bin/env python
import os
from flask import Flask, request, render_template, jsonify, json
from flask_cors import CORS, cross_origin
import audio
import color
import motion
import subprocess
import matplotlib.pyplot as plt
import pickle
import operator
import numpy as np


query_fixed_path = "./static/data/query"
# [f.name for f in os.scandir(query_path) if f.is_dir()]
voice_path = "./static/data/database/*/*.wav"
voice_cache_path = "./static/data/cache/audio/data.pkl"


app = Flask(__name__)
CORS(app)
#db = SQLAlchemy(app,use_native_unicode="utf8")
 
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:cacti@localhost/web12306'

 
@app.route('/suggest', methods=['GET'])
def suggest():
    data = [f.name for f in os.scandir(query_fixed_path) if f.is_dir()]
    return json.dumps(data)

 
@app.route('/search', methods=['GET', 'POST'])
def search():
    query_name = str(request.form['query'])
    # print(query_name)
    query_path = query_fixed_path + '/' + query_name
    # query(query_path, query_name)
    query_video_path, result_video_name, result_video_path, result_img_path = query(query_path, query_name) # qutality, location of videos
    # result_video_name = ['music', 'flowers']
    # query_video_path = '/static/video/movieVid.mp4'
    # result_video_path = ['/static/video/musicvideoVid.mp4', '/static/video/flowersVid.mp4']
    # result_img_path = ['/static/img/logo2.png', '/static/img/logo2.png']
    res = {'query':query_name, 'name':result_video_name, 'query_video_path':query_video_path, 'result_video_path':result_video_path, 'result_img_path':result_img_path}
    return render_template('./result.html', result = res)
             
@app.route('/')
def index():
    return render_template('./index.html')
 

def query(query_path, query_name):
    print('start executing')
    color_res = color.return_info(query_path)
    # for line in color_res:
    #     print(line[:2])


    filenames_dict = {'flowers': 0, 'interview': 1, 'movie': 2, 'musicvideo': 3, 'sports': 4, 'starcraft': 5, 'traffic': 6}
    index_to_name = {0:'flowers', 1:'interview', 2: 'movie', 3: 'musicvideo', 4: 'sports', 5: 'starcraft', 6: 'traffic'}
    index_to_loc = {0: '/static/data/database/flowers',
    1: './static/data/database/interview',
    2: './static/data/database/movie',
    3: './static/data/database/musicvideo',
    4: './static/data/database/sports',
    5: './static/data/database/starcraft',
    6: './static/data/database/traffic'}
    if not os.path.exists(voice_cache_path):
        # print('executing processing the whole database videos')
        audio.save_voiceprint(voice_path, voice_cache_path, filenames_dict)

    audio_res = audio.audio_interface(query_path, voice_cache_path)
    # for item in audio_res:
    #     print(item)
    

    # '''motion part'''
    MOTION_NORM = 258402*149

    MSDtest=motion.test_video(query_path+'/*.rgb',0,149)
    # I have total 7 database, the path of the database also need to be changed to "/path/flowersMSD.pkl", the same as the following 6 database.
    pickle_flowers=open("./static/data/cache/motion/flowersMSD.pkl","rb") 
    flowersMSD=pickle.load(pickle_flowers)
    #print(flowersMSD)
    pickle_interview=open("./static/data/cache/motion/interviewMSD.pkl","rb")
    interviewMSD=pickle.load(pickle_interview)
    # print(interviewMSD)
    pickle_movie=open("./static/data/cache/motion/movieMSD.pkl","rb")
    movieMSD=pickle.load(pickle_movie)
    # print(movieMSD)
    pickle_musicvideo=open("./static/data/cache/motion/musicvideoMSD.pkl","rb")
    musicvideoMSD=pickle.load(pickle_musicvideo)
    # print(musicvideoMSD)
    pickle_sports=open("./static/data/cache/motion/sportsMSD.pkl","rb")
    sportsMSD=pickle.load(pickle_sports)
    # print(sportsMSD)
    pickle_starcraft=open("./static/data/cache/motion/starcraftMSD.pkl","rb")
    starcraftMSD=pickle.load(pickle_starcraft)
    # print(starcraftMSD)
    pickle_traffic=open("./static/data/cache/motion/trafficMSD.pkl","rb")
    trafficMSD=pickle.load(pickle_traffic)
    # print(trafficMSD)
    flowMotion,flowRange,flowerCurve=motion.compare_video(MSDtest,flowersMSD)
    interMotion,interRange,interCurve=motion.compare_video(MSDtest,interviewMSD)
    movMotion,movRange,movCurve=motion.compare_video(MSDtest,movieMSD)
    musMotion,musRange,musCurve=motion.compare_video(MSDtest,musicvideoMSD)
    spoMotion,spoRange,spoCurve=motion.compare_video(MSDtest,sportsMSD)
    staMotion,staRange,staCurve=motion.compare_video(MSDtest,starcraftMSD)
    traMotion,traRange,traCurve=motion.compare_video(MSDtest,trafficMSD)

    # print('test motion return values', traRange, len(traCurve))

    flowN=1-(flowMotion/float(MOTION_NORM)) 
    interN=1-(interMotion/float(MOTION_NORM))
    movN=1-(movMotion/float(MOTION_NORM))
    musN=1-(musMotion/float(MOTION_NORM))
    spoN=1-(spoMotion/float(MOTION_NORM))
    staN=1-(staMotion/float(MOTION_NORM))
    traN=1-(traMotion/float(MOTION_NORM))

    motion_res = [(0, flowN, flowRange, flowerCurve), (1, interN, interRange, interCurve), (2, movN,movRange, movCurve), (3, musN,musRange, musCurve),
    (4,spoN,spoRange, spoCurve), (5, staN,staRange, staCurve), (6, traN,traRange, traCurve)]


    # for line in motion_res:
    #     print(line[:3])
    # '''end of motion part'''
    color_weight = 0.5
    motion_weight = 0.3
    audio_weight = 0.2

    res = []
    for i in range(7):
        similarity = color_weight * color_res[i][1] + motion_weight * motion_res[i][1] + audio_weight * audio_res[i][1];
        # similarity = color_weight * color_res[i][1] + audio_weight * audio_res[i][1]

        color_range = np.asarray(color_res[i][2])
        motion_range = np.zeros(600)
        motion_idx = motion_res[i][2]
        motion_range[motion_idx] = motion_res[i][3]
        similarity_range = color_weight * color_range + motion_weight * motion_range;
        # similarity_range = color_weight * color_range
        res.append((i, similarity, similarity_range))

    res.sort(key = operator.itemgetter(1), reverse=True)

    # Return top 3
    res = res[:3]
    result_video_path = []
    result_img_path = []
    result_video_name = []

    for r in res:
        result_name = index_to_name[r[0]]
        result_video_name.append(result_name)
        # print("result", r)
        # index = r[2]

        # print("index",index)
        # data = [0] * 600
        # data[index: index + 150] = [1] * 150
        data = r[2]
        result_img_path.append(generate_img(data, query_path, query_name, result_name))
        
        result_video_path.append(index_to_loc[r[0]] + '/' +index_to_name[r[0]] + '.mp4')

    subprocess.call("ffmpeg -pattern_type glob -y -r 30 -f image2 -i '" + query_path + "/*.jpg' -i " + query_path + "/" + query_name + ".wav" + " -c:v libx264 -c:a aac -b:a 192k " + query_path + "/" + query_name + ".mp4", shell = True)
    query_video_path = query_path + "/" + query_name + ".mp4"
    # print(query_video_path)
    # print(result_video_name)
    # print(result_video_path)
    # print(result_img_path)
    return (query_video_path, result_video_name, result_video_path, result_img_path)

def generate_img(data, saved_path, query_name, database_name):
    saved_file = saved_path + '/' + query_name + '_' + database_name + '.png'
    plt.figure(figsize=(7,1), dpi=50.2)
    plt.axis('off')
    plt.plot(data)
    plt.savefig(saved_file, bbox_inches='tight', pad_inches=0)
    # plt.show()
    return saved_file

if __name__ == '__main__':
    app.run(host='127.0.0.1', port = 51246, debug=True)




