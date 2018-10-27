from color import *
from Motion import *
from audio import *
import _pickle as cPickle
import time
import sys

MOTION_NORM = 25840*149

if __name__ == '__main__':
	start_time = time.time()

	path = "C:/Users/Alex Grieco/Desktop/CS576_final/query_vids/"+sys.argv[2]+'/'
	
	
	arr = return_info(path+sys.argv[1])

	for line in arr:
		print(line)
	#path for Angus's computer
	#voice_path = './databse_videos/*/*.wav'
	#saved_path = './voice_base/data.pkl'

	#path for Alex's computer
	voice_path = "C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/*/*.wav"
	saved_path = "C:/Users/Alex Grieco/Desktop/CS576_final/voice_base/data.pkl"

	filenames_dict = {'flowers': 0, 'interview': 1, 'movie': 2, 'musicvideo': 3, 'sports': 4, 'starcraft': 5, 'traffic': 6}
	if not os.path.exists(saved_path):
		print('executing processing the whole database videos')
		save_voiceprint(voice_path, saved_path, filenames_dict)

	#change this
	#query_path = "C:/Users/Alex Grieco/Desktop/CS576_final/query_vids/first/first.wav"
	query_path = path+sys.argv[1]+'.wav'
	print('the results for the query are')
	result = audio_interface(query_path, saved_path)
	for item in result:
		print(item)

	
	#MSDtest=test_video('C:/Users/Alex Grieco/Desktop/CS576_final/query_vids/first/first*.rgb',0,149)
	MSDtest=test_video(path+sys.argv[1]+'*.rgb',0,149)
	#test_pkl=open("C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/testMSD.pkl","rb") 
	#MSDtest = pickle.load(test_pkl)
	#print (MSDtest) 

	flowMotion,flowRange,flowerCurve=compare_video(MSDtest,flowersMSD)
	interMotion,interRange,interCurve=compare_video(MSDtest,interviewMSD)
	movMotion,movRange,movCurve=compare_video(MSDtest,movieMSD)
	musMotion,musRange,musCurve=compare_video(MSDtest,musicvideoMSD)
	spoMotion,spoRange,spoCurve=compare_video(MSDtest,sportsMSD)
	staMotion,staRange,staCurve=compare_video(MSDtest,starcraftMSD)
	traMotion,traRange,traCurve=compare_video(MSDtest,trafficMSD)

	flowN=1-(flowMotion/float(MOTION_NORM)) 
	interN=1-(interMotion/float(MOTION_NORM))
	movN=1-(movMotion/float(MOTION_NORM))
	musN=1-(musMotion/float(MOTION_NORM))
	spoN=1-(spoMotion/float(MOTION_NORM))
	staN=1-(staMotion/float(MOTION_NORM))
	traN=1-(traMotion/float(MOTION_NORM))
	
	print ("flowers motion =",flowN,flowRange)
	print ("interview motion =",interN,interRange)
	print ("movie motion =",movN,movRange)
	print ("musicvideo motion =",musN,musRange)
	print ("sports motion =",spoN,spoRange)
	print ("starcraft motion =",staN,staRange)
	print ("traffic motion =",traN,traRange)


	elapsed_time = time.time() - start_time
	print(elapsed_time)
