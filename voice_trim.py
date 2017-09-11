#coding=utf-8
"""
本程序用来实现语音信号的截取，将本程序放在语音文件目录下，请在Python3 环境下运行！
版本：1.0
"""
import os
import wave
import matplotlib.pyplot as plt
import numpy as np
import struct
import sys
#########################################子函数##############################################
def arrsum(arr,startpoint,num=800):#计算特定长度的列表的和
    summ=0
    for i in range(0,num):
        summ=summ+abs(arr[startpoint+i])
    return summ

def trim(file="7.wav"):
    print("现在正在截取%s,请耐心等待..."%file)
    voice_file=wave.open(curdir+file)
    params=voice_file.getparams()#获得音频参数
    nchannels,sampwidth,framerate,nframes=params[:4]#声道数，量化位数（byte），采样频率，采样点数
    strData=voice_file.readframes(nframes)#读取音频
    waveData = np.fromstring(strData,dtype=np.int16)#将字符串转化为int
    origData=waveData#将原始幅值的音频保留
    waveData = waveData*1.0/(max(abs(waveData)))#wave幅值归一化
    
    #找到音频边界:
    start_loc=[0]*10#存储音频边界索引
    end_loc=[0]*10#存储音频边界索引
    index=0
    mode=0#设置当前状态，初始状态为噪声
    i=0#对整个声音文件进行索引
    while i<nframes:#采样点数
        
        if (mode==0 and abs(waveData[i]>0.10)):#当前状态为噪声态
            if 1.6*arrsum(waveData,i-1000)<arrsum(waveData,i):
                mode=1
                start_loc[index]=i-500#500为实验值

        if mode==1:#当前状态为信号状态
            count=0
            for j in range(0,1000):
                if abs(waveData[i+j])<0.10:
                    count=count+1
                else:
                    count=0
            if count>950:
                mode=0
                end_loc[index]=i+1200#1200为实验值
                i=end_loc[index]
                if arrsum(waveData,start_loc[index],end_loc[index]-start_loc[index])>150:
                    index=index+1
        i=i+1
        
    #print(start_loc)显示起止索引
    #print(end_loc)
        
    # 绘制波形图
    time = np.arange(0,nframes)#时间轴
    plt.figure()
    plt.plot(time,waveData)
    plt.xlabel("Sample point")#采样点
    plt.ylabel("amplitude")#幅值
    plt.title("%s"%file)
    for i in start_loc:
        plt.vlines(i,-1,1,color='g')#起始位置
    for i in end_loc:
        plt.vlines(i,-1,1,color='r')#终止位置

    #存储音频文件
    outPath=curdir+file.rstrip(".wav")#去掉尾部.wav
    if not(os.path.exists(outPath)):#如果不存在文件夹
        os.mkdir(outPath)
    for index in range(0,10):
        outData=origData[start_loc[index]:end_loc[index]]
        outFile=outPath+"\\%d.wav"%index
        outWave=wave.open(outFile,'wb')#定义存储轮径及文件名
        data_size=len(outData)
        comptype = "NONE"
        compname = "not compressed"
        outWave.setparams((nchannels,sampwidth,framerate,data_size,comptype, compname))
        
        for v in outData:
            outWave.writeframes(struct.pack('h', v))#outData:16位，-32767~32767，注意不要溢出
        outWave.close()

##########################################主程序部分################################################
    
curdir=os.getcwd()+"\\"
filenames=[fname for fname in os.listdir(curdir) if os.path.isfile(fname) if fname.endswith('.wav')]

if np.size(filenames)!=11:
    print("输入的文件数量有误，请检查当前文件夹！！\n\t  Sorry,Good bye!!")
    sys.exit(); 
else:
    for file in filenames:
       trim(file)
plt.show()
