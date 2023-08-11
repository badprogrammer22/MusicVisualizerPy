from scipy.io import wavfile
import numpy as np
import pygame as py
from scipy.fft import fft, fftfreq
import matplotlib
from matplotlib import pyplot as plt
import math
import librosa



song = "telepatia.wav"
samplerate, data = wavfile.read(song)

#Debug - show samplerate
#print(samplerate)

duration_in_sec = librosa.get_duration(filename=song)


try:
    _, num_of_channels = data.shape
except:
    num_of_channels = 1

if num_of_channels == 1:
    ydata_for_line = list(data)
    ydata = list(np.array_split(data, 20 * duration_in_sec))

else:
    ydata_for_line = list(data[:,0])
    ydata = list(np.array_split(data[:,1], 20 * duration_in_sec))


start = 0
y_origin = 500


#Lists for x and y axi of frequency display
xf_list = []
yf_list = []

#Getting the frequency spectrum
for data in ydata:
    normalized_data = np.int16((data / data.max()) * 32767)
    N = data.size

    yf = list(np.abs(fft(normalized_data)))
    xf = list(fftfreq(N, 1 / samplerate))

    xf_list.append(xf)
    yf_list.append(yf)


#Debug - show frequency spectrum of an instant (0), on a plot
#plt.plot(np.resize(xf_list[0],15031), np.abs(yf_list[0]))
#plt.show()

#Debug - Show frequency range
#print(len(xf_list))


py.init()
py.mixer.init(samplerate, -16, 1, 1024)

screen = py.display.set_mode((600,600))

clock = py.time.Clock()


py.mixer.music.load(song)

count = 0

run = True

while run:
    screen.fill((0,0,0))

    for e in py.event.get():
        if e.type == py.QUIT:
            run = False


    #Frame count to move the visualization at the same rate the song plays
    count += 1/3
    
    #Get x and y axi of the specturm for the current instant
    xf, yf = xf_list[int(count)], yf_list[int(count)]

    #Drawing the raw data in points
    for i in range(1000):
        py.draw.circle(screen, (255,255,255), (10+xf[i]/20, 300-yf[i]/30000), 1)

    #Drawing the bars, which each are the average of five points
    for i in range(200):
        val = 0
        for j in range(5):
            val += yf[i+j]/30000
        val/=5
        py.draw.line(screen, (255,255,255), (10+xf[i]/4, 200-val), (10+xf[i]/4, 200), 10)

    #Drawing the bars but in a circle
    for i in range(200):
        val = 0
        for j in range(5):
            val += yf[i+j]/30000
        val/=5

        ag = xf[i]/4/100 * math.pi/2
        module_ = val

        py.draw.line(screen, (255,255,255), (300+math.cos(ag)*50,400+ math.sin(ag)*50), 
                        (300+math.cos(ag)*(50+val), 400+math.sin(ag)*(50+val)), 20)
        

    #Drawing the sound line
    start += int(samplerate/600)

    last_pos = (0,0)
    for i in range(1000):
        pos = (i*6, y_origin - ydata_for_line[(i+start)*10]/400) #pos_y is every 10th value, divided by 90 to fit
        py.draw.line(screen, (255,255,255), pos, last_pos, 1)

        last_pos = pos

    
    #Only start playing the song after the first display is done, so its synced
    if not py.mixer.music.get_busy():
        py.mixer.music.play()

    clock.tick(60)
    py.display.update()

