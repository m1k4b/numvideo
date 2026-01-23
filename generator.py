import cv2
import os

filepath=None
first_time=True

while filepath is None or not os.path.exists(filepath):
    if not first_time:
        print('Please enter a valid path')
    filepath=input('Enter the path of your video: ')
    quality_score=None
    first_time=False

resolution_quality=int(input('Resolution quality (low=good, high=bad): '))
color_quality=float(input('Color quality (low=good, high=bad): '))
duration=input('Duration in seconds (blank for full video): ')
if duration== '':
    duration=None
else:
    duration=float(duration)

size=(320//resolution_quality,222//resolution_quality)

video = cv2.VideoCapture(filepath)
fps=video.get(cv2.CAP_PROP_FPS)
video.set(cv2.CAP_PROP_POS_FRAMES,0)

converted_frames=[]

divide_fps=int(input('FPS splitter (low=good high=bad): '))

index=0

while True:
    ret, frame = video.read()
    if not ret:
        break
    if index % divide_fps != 0:
        index += 1
        continue
    if duration is not None and index>fps*duration:
        break
    inv_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    inv_frame=cv2.resize(inv_frame,size)
    height, width, _ = inv_frame.shape
    converted=""
    for y in range(height):
        for x in range(width):
            r,g,b=int(inv_frame[y][x][0]),int(inv_frame[y][x][1]),int(inv_frame[y][x][2])
            hex_code=str(format((r+g+b)//3,'02x'))
            converted+=hex_code
    index += 1
    converted_frames.append(converted)

part_len=1
parts_numb=len(converted_frames)//part_len
parts=[]
for i in range(parts_numb):
    parts.append(''.join(converted_frames[i*part_len:(i+1)*part_len]))
if len(converted_frames)%part_len != 0:
    parts.append(''.join(converted_frames[len(converted_frames)-len(converted_frames)%part_len:]))

text_parts=""
for part in parts:
    text_parts += f'part=decode("{part}")\nlast_frame=read(part,last_frame)\n'

embed=f"""
import kandinsky as kd
import time

def sim(color1,color2):
    return sum([abs(c-c1) for c,c1 in zip(color1,color2)])

size=({size[0]},{size[1]})

frame_size=size[0]*size[1]*2

def decode(video):
    converted_video=[]
    frames=[]
    for i in range(0,len(video),frame_size):
        frames.append(video[i:i+frame_size])
    for frame in frames:
        decoded_frame={{}}
        for x in range(size[0]+1):
            decoded_frame[x]=[]
            for y in range(size[1]+1):
                decoded_frame[x].append(0)
        for i in range(0,len(frame),2):
            x,y=(i//2)%size[0],(i//2)//size[0]
            decoded_frame[x][y]=(int(frame[i:i+2],16),)*3
        converted_video.append(decoded_frame)
    return converted_video

def read(video,last_frame_):
    color_quality={color_quality}
    fps={fps/divide_fps}

    p_size=(320//size[0],222//size[1])

    index=0

    while True:
        if index>=len(video):
            break
        frame=video[index]
        start = time.monotonic()
        for x in range(size[0]):
            for y in range(size[1]):
                color = frame[x][y]
                if last_frame_ is not None:
                    if sim(color,last_frame_[x][y])<color_quality:
                        continue
                kd.fill_rect(int(x*p_size[0]),int(y*p_size[1]),int(p_size[0]),int(p_size[1]),color)
        end = time.monotonic()
        pause = (1 / fps) - (end - start)
        if pause > 0:
            time.sleep(pause)
        else:
            jump=int(abs(pause)/(1/fps))
            index+=jump
        last_frame_=dict(frame)
        index+=1
    return last_frame_

last_frame=None
{text_parts}

while True:
    pass
"""

open('embed.py','w',encoding='utf-8').write(embed)
