import pickle
import matplotlib.pyplot as plt
import numpy as np
import glob
from color import *
from decimal import Decimal, getcontext

NORM = 740




"""
print(sum(flowersMSD)/float(len(flowersMSD)))
print(sum(interviewMSD)/float(len(interviewMSD)))
print(sum(movieMSD)/float(len(movieMSD)))
print(sum(musicvideoMSD)/float(len(musicvideoMSD)))
print(sum(sportsMSD)/float(len(sportsMSD)))
print(sum(starcraftMSD)/float(len(starcraftMSD)))
print(sum(trafficMSD)/float(len(trafficMSD)))
"""

IMG_HEIGHT=288
IMG_WIDTH=352
"""
def read_img(path):
    res = []
    with open(path, 'rb') as f:
        res = f.read()
    
    r = np.zeros((IMG_HEIGHT, IMG_WIDTH))
    g = np.zeros((IMG_HEIGHT, IMG_WIDTH))
    b = np.zeros((IMG_HEIGHT, IMG_WIDTH))
    rgb = np.stack([r,g,b], 2)
    for k in range(3):
        for i in range(IMG_HEIGHT):
            for j in range(IMG_WIDTH):
                rgb[i][j][k] = ((res[k*IMG_WIDTH*IMG_HEIGHT + i*IMG_WIDTH + j]))
    
    rgb = rgb.astype('uint8')
    return rgb
"""

def test_video(image_test,a,b, num=149):
    name=glob.glob(image_test)
    Filename=sorted(name)
    redMSDtest=np.zeros((16,20))
    MSDtest=np.zeros((num))
    for x in range(a,b):
        k=4
        n=16
        #image1=read_img(Filename[x]) 
        #image2=read_img(Filename[x+1])
        image1=IMAGES[x]
        image2=IMAGES[x+1]
        for i in range(4,12):
            for j in range(5,15):
                SearchArea=np.sqrt(pow(image1[(n*i):(n*i+n+2*k),(n*j):(n*j+n+2*k),0],2)+pow(image1[(n*i):(n*i+n+2*k),(n*j):(n*j+n+2*k),1],2)+pow(image1[(n*i):(n*i+n+2*k),(n*j):(n*j+n+2*k),2],2))
                minMSD=0
                Macroblock=np.sqrt(pow(image2[(n*(i)+k):(n*(i)+n+k),(n*(j)+k):(n*(j)+n+k),0],2)+pow(image2[(n*(i)+k):(n*(i)+n+k),(n*(j)+k):(n*(j)+n+k),1],2)+pow(image2[(n*(i)+k):(n*(i)+n+k),(n*(j)+k):(n*(j)+n+k),2],2))
                for indx in range(2*k+1):
                    for indy in range(2*k+1):
                        Cblock=SearchArea[indx:(indx+n),indy:(indy+n)]
                        redSum=abs(Macroblock-Cblock)
                        Sum=redSum.sum()
                        if minMSD==0:
                            minMSD=Sum
                        if Sum<minMSD:
                            minMSD=Sum 
                redMSDtest[i][j]=minMSD
        MSDtest[x-a]=np.round(redMSDtest.sum())
    return (MSDtest)
  

def compare_video(MSDtest,MSD):
    Min=10000000000000
    #comparesum = [] 
    for z in range(451):
        ComMSD=MSD[z:(z+149)]

        Comparearray=abs(MSDtest-ComMSD)
        Compare=Comparearray.sum()
        #comparesum.append(Compare/149)
        if Compare<Min:
            Min=Compare
            Cindex=range(z,(z+149))
            Curve=(Comparearray)
    return Min,Cindex,Curve


"""
MSD = test_video('C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/flowers/flowers*.rgb',0,599, 599)
cPickle.dump(MSD, open("C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/flowersMSD.pkl", "wb"))


MSD = test_video('C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/interview/interview*.rgb',0,599, 599)
cPickle.dump(MSD, open("C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/interviewMSD.pkl", "wb"))


MSD = test_video('C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/movie/movie*.rgb',0,599, 599)
cPickle.dump(MSD, open("C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/movieMSD.pkl", "wb"))


MSD = test_video('C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/musicvideo/musicvideo*.rgb',0,599, 599)
cPickle.dump(MSD, open("C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/musicvideoMSD.pkl", "wb"))


MSD = test_video('C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/sports/sports*.rgb',0,599, 599)
cPickle.dump(MSD, open("C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/sportsMSD.pkl", "wb"))


MSD = test_video('C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/starcraft/starcraft*.rgb',0,599, 599)
cPickle.dump(MSD, open("C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/starcraftMSD.pkl", "wb"))


MSD = test_video('C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/traffic/traffic*.rgb',0,599, 599)
cPickle.dump(MSD, open("C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/trafficMSD.pkl", "wb"))
"""


# change the path and the parameters of the quaryvideo to ("/path/*.rgb",a,b) a is the start frame,b is the end frame.If they just have 150 frames, the range should be (0,149)
#MSDtest=test_video('C:/Users/Alex Grieco/Desktop/CS576_final/query_vids/first/first*.rgb',0,149)
#print (MSDtest) 
#test_pkl=open("C:/Users/Alex Grieco/Desktop/CS576_final/databse_vids/testMSD.pkl","rb") 
#MSDtest = pickle.load(test_pkl)
#flowMotion,flowRange,flowerCurve=compare_video(MSDtest,flowersMSD)
"""print (flowRange)
plt.plot(flowerCurve)
plt.title('match Score')
plt.ylabel('Difference')
plt.xlabel('frame')
plt.show()
interMotion,interRange,interCurve=compare_video(MSDtest,interviewMSD)
print (interRange)
plt.plot(interCurve)
plt.title('interview match Score')
plt.ylabel('Difference')
plt.xlabel('frame')
plt.show()
movMotion,movRange,movCurve=compare_video(MSDtest,movieMSD)
print (movRange)
plt.plot(movCurve)
plt.title('movie match Score')
plt.ylabel('Difference')
plt.xlabel('frame')
plt.show()
musMotion,musRange,musCurve=compare_video(MSDtest,musicvideoMSD)
print (musRange)
plt.plot(musCurve)
plt.title('musicvideo match Score')
plt.ylabel('Difference')
plt.xlabel('frame')
plt.show()
spoMotion,spoRange,spoCurve=compare_video(MSDtest,sportsMSD)
print (spoRange)
plt.plot(spoCurve)
plt.title('sport match Score')
plt.ylabel('Difference')
plt.xlabel('frame')
plt.show()
staMotion,staRange,staCurve=compare_video(MSDtest,starcraftMSD)
print (staRange)
plt.plot(staCurve)
plt.title('starcraft match Score')
plt.ylabel('Difference')
plt.xlabel('frame')
plt.show()
traMotion,traRange,traCurve=compare_video(MSDtest,trafficMSD)
print (traRange)
plt.plot(traCurve)
plt.title('traffic match Score')
plt.ylabel('Difference')
plt.xlabel('frame')
plt.show()
# the return similarity is more approach to 1, it means more similar
De=max(flowMotion,interMotion,movMotion,musMotion,spoMotion,staMotion,traMotion)
flowN=1-(flowMotion/De)
interN=1-(interMotion/De)
movN=1-(movMotion/De)
musN=1-(musMotion/De)
spoN=1-(spoMotion/De)
staN=1-(staMotion/De)
traN=1-(traMotion/De)
print ("flowers motion =",flowN,flowRange)
print ("interview motion =",interN,interRange)
print ("movie motion =",movN,movRange)
print ("musicvideo motion =",musN,musRange)
print ("sports motion =",spoN,spoRange)
print ("starcraft motion =",staN,staRange)
print ("traffic motion =",traN,traRange)
"""
