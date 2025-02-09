from cmd import IDENTCHARS
import random
from signal import ITIMER_PROF
from sqlite3 import Time
import tkinter
import cv2
import threading
import time
import os
from jinja2 import PrefixLoader
from torch import initial_seed
import win32com.client
import win32api
import pythoncom
from datetime import datetime
import sys

camwidth = 640
camheight = 480
toggle = 1;
recordingIndex = -999
run_onset = 0
cam_id = 0
user_initial = "(blank)"

numruns = 3
mindelay = 6
maxdelay = 10

fish_id = "Z1"
gender = "(blank)"
genotype = "(blank)"
notes = "(blank)"

pre_stimulus_time = 4
pre_reward_time = 4
reward_aversion_time = 4

post_reward_time = 5
tone_duration = 4

filename = "Sample.pptx"

tonePlaying = 0
videoPlaying = 0

now = datetime.now()
nowstr = now.strftime("%Y-%m-%d %H:%M:%S %p")
now = time.time()

forbidden = ["/","<",">",":",'"',"\\","|","?","*",
chr(0),chr(1),chr(2),chr(3),chr(4),chr(5),chr(6),chr(7),
chr(8),chr(9),chr(10),chr(11),chr(12),chr(13),chr(14),chr(15),
chr(16),chr(17),chr(18),chr(19),chr(20),chr(21),chr(22),chr(23),
chr(24),chr(25),chr(26),chr(27),chr(28),chr(29),chr(30),chr(31)]


class VideoRecorder():

    # Video class based on openCV
    def __init__(self, run, paradigm):

        self.open = True
        self.device_index = cam_id
        self.fps = 20  # fps should be the minimum constant  rate at which the camera can
        self.fourcc = "XVID"  # capture images (with no decrease in speed over time; testing is required)
        self.frameSize = (640, 480)  # video formats and sizes also depend and vary according to the camera used
        #self.video_filename = fish_id + "_run_" + str(run) + "_" + paradigm + ".avi"
        self.video_filename = str(fish_id)+"_"+str(datetime.today().strftime('%Y-%m-%d'))+"_"+str(paradigm)+".avi"
        self.video_cap = cv2.VideoCapture(self.device_index)
        self.video_writer = cv2.VideoWriter_fourcc(*self.fourcc)
        self.video_out = cv2.VideoWriter(self.video_filename, self.video_writer, self.fps, self.frameSize)
        self.frame_counts = 1
        self.start_time = time.time()
        self.font = cv2.FONT_HERSHEY_PLAIN
        self.xy = 10,10

    # Video starts being recorded
    def record(self):

        while (self.open == True):
            ret, video_frame = self.video_cap.read()
            if (tonePlaying==1):
                cv2.putText(video_frame, str(datetime.now()), (20,40),
                        self.font, 2, (0,0,0), 2, cv2.LINE_AA)
                cv2.circle(video_frame, (620, 20), 20, (0,0,255), -1)
            
            elif videoPlaying == 1:
                cv2.putText(video_frame, str(datetime.now()), (20, 40),
                            self.font, 2, (0, 0, 0), 2, cv2.LINE_AA)
                cv2.rectangle(video_frame, (580, 10), (620, 40), (255, 0, 0), -1)

            else:
                cv2.putText(video_frame, str(datetime.now()), (20,40),
                        self.font, 2, (255,255,255), 2, cv2.LINE_AA)
            
            if (ret == True):

                self.video_out.write(video_frame)
                self.frame_counts += 1
                time.sleep(0.05)
                gray = cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY)
                cv2.imshow('video_frame', gray)
                cv2.waitKey(1)

            else:
                break

    def markerOn(self):
        cv2.drawMarker()

    # Finishes the video recording therefore the thread too
    def stop(self):

        if self.open == True:

            self.open = False
            self.video_out.release()
            self.video_cap.release()
            cv2.destroyAllWindows()

        else:
            pass

    # Launches the video recording function using a thread
    def start(self):
        video_thread = threading.Thread(target=self.record)
        video_thread.start()

def start_PPTrecording(filename):

    paradigm_slides = [['cf', 12], ['dfm', 7], ['ufm', 2]]
    all_runs = [['cf', 0], ['dfm', 0], ['ufm', 0]]

    global fixed_times
    fixed_times = [1, 6000, 1, 1]
    pythoncom.CoInitialize()
    app = win32com.client.Dispatch("PowerPoint.Application")
    app.Visible = 1
    app.Presentations.Open(FileName=filename)
    app.ActivePresentation.SlideShowSettings.Run()

    nov_test_len = 60
    print("Trial Onset:", nowstr)
    fixed = sum(fixed_times) / 1000
    vars = fixed + pre_stimulus_time + tone_duration + pre_reward_time + reward_aversion_time + post_reward_time
    if len(sys.argv) > 1:
        if sys.argv[1] == 'novel':
            vars += nov_test_len
    trial_min = (vars + mindelay) * numruns
    trial_max = (vars + maxdelay) * numruns
    print("Length of Trial:", round((trial_min / 60), 1), "-", round((trial_max / 60), 1), "minutes")

    # 6-min novel environment test
    if len(sys.argv) > 1:
        if sys.argv[1] == 'novel':
            novtest_vthread = VideoRecorder('novelenv', 'test')
            app.SlideShowWindows(1).View.GotoSlide(1)
            novtest_vthread.start()
            print("novel environment test")
            time.sleep(nov_test_len) #change to 360 for true trials
            novtest_vthread.stop()

    #loop through paradigm presentations and record from pre_stimulus_time to post reward_aversion_time
    for i in range(numruns):
        this_run = random.choice(paradigm_slides)
        iti = random.randint(mindelay, maxdelay)
        global run_onset
        run_onset = time.time()
        run_now = datetime.now().replace(microsecond=0)
        run_nowstr = '_'.join(str(run_now).split())

        print('run', i + 1, ':', this_run[0], 'ITI:', iti, "onset:", run_now)

        #with open("transcript.csv","a+") as wfile:
        #    wfile.write('run '+str(i + 1)+ ': '+ str(this_run[0])+ ' ITI:'+str(iti)+" onset:"+str(run_nowstr))

        video_thread = VideoRecorder(i, this_run[0])
        video_thread.start()

        win32api.Sleep((pre_reward_time * 1000) + 2000)  # pre-stimulus time
        app.SlideShowWindows(1).View.GotoSlide(this_run[1])  # advance to screen cue
        win32api.Sleep(fixed_times[0])  # fixed 1
        app.SlideShowWindows(1).View.Next()  # play screen cue
        win32api.Sleep(fixed_times[1])  # fixed 2
        app.SlideShowWindows(1).View.Next()  # advance to sound slide
        win32api.Sleep(fixed_times[2])  # fixed 3
        app.SlideShowWindows(1).View.Next()  # play CF/FM
        global tonePlaying
        tonePlaying = 1
        win32api.Sleep(tone_duration * 1000)  # Analysis Period
        tonePlaying = 0
        app.SlideShowWindows(1).View.Next()  # advance to black slide
        win32api.Sleep(pre_stimulus_time * 1000)  # pre_reward_time interval
        app.SlideShowWindows(1).View.Next()  # advance to video slide
        win32api.Sleep(fixed_times[3])  # fixed 5
        app.SlideShowWindows(1).View.Next()  # start video
        global videoPlaying
        videoPlaying = 1
        win32api.Sleep(reward_aversion_time * 1000)  # reward_aversion_time time
        videoPlaying = 0
        app.SlideShowWindows(1).View.Next()  # advance to black slide

        for y, j in enumerate(all_runs):
            if this_run[0] == j[0]:
                j[1] += 1
            if j[1] == numruns / 3:
                paradigm_slides.pop(y)
                all_runs.pop(y)

        time.sleep(post_reward_time)
        video_thread.stop()
        time.sleep(iti - post_reward_time)

        if len(all_runs) == 0:
            app.SlideShowWindows(1).View.GotoSlide(1)
            pythoncom.CoUninitialize()
            print("Presentation finished.")
            #with open("transcript.csv","a+") as wfile:
            #    wfile.write("Presentation finished.\n")
            break
        #with open("transcript.csv","a+") as wfile:
        #    wfile.write("Filename: "+video_thread.video_filename+"\n\n")


def main_():
    start_PPTrecording(filename)

def tkinter_start():
    top = tkinter.Tk()

    def action():
        global toggle
        toggle *= -1
        if(toggle==-1):
            #with open("transcript.csv","a+") as wfile:
            #    wfile.write("Emergency stop")
            print("Stopped Recording, exiting program")
            os._exit(0)
            cv2.destroyAllWindows()
            

    B = tkinter.Button(top, text ="Stop Recording", command = action)

    B.pack()
    top.mainloop()

def supermain():
    t1 = threading.Thread(target=main_)
    t2 = threading.Thread(target=tkinter_start)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

def startup():
    
    top1 = tkinter.Tk()
    top1.title("Zfish Interface")
    mainpanel = tkinter.PanedWindow(orient=tkinter.VERTICAL)
    mainpanel.pack(fill=tkinter.BOTH,expand = 1)
    panel1 = tkinter.PanedWindow(mainpanel)
    panel1.pack(fill=tkinter.BOTH, expand=1)

    top1.geometry('360x440')    
    def c():  
        if(not os.path.exists("transcript.csv")):   
            with open("transcript.csv","a+") as wfile:
                wfile.write("Fish ID, Gender, Date, Time, Initials, Num Runs, Min ITI, Max ITI, Post-reward Time, Tone Duration, Camera ID, Gender, Notes, Pre-stimulus Time, Pre-reward Time, Reward/Aversion Time\n")
        with open("transcript.csv", "a+") as wfile:
            global fish_id 
            if(not(txt7.get()=="")):
                fish_id  = txt7.get()
                wfile.write(str(fish_id)+",")
            else:
                wfile.write("Z1,")           

            global gender
            if(not(txt8.get()=="")):
                gender = txt8.get()
            
                wfile.write(str(gender)+",")
            else:
                wfile.write("(blank),") 
            
            wfile.write(str( datetime.today().strftime('%Y-%m-%d'))+",")
            wfile.write(str(datetime.now().strftime('%H:%M:%S'))+",")
            
            
            
            global user_initial
            user_initial = txt3.get()
            if(not(txt3.get()=="")):
                wfile.write(str(user_initial)+",")
            else:
                wfile.write("(blank),")

            global numruns
            if(not(txt4.get()=="")):
                numruns = int(txt4.get())
                wfile.write(str(numruns)+",")
            else:
                wfile.write("3,")

            global mindelay
            if(not(txt5.get()=="")):
                mindelay = int(txt5.get())
                wfile.write(str(mindelay)+" seconds,")
            else:
                wfile.write("6 seconds,")

            global maxdelay
            if(not(txt51.get()=="")):
                maxdelay = int(txt51.get())
                wfile.write(str(maxdelay)+" seconds,")
            else:
                wfile.write("10 seconds,")

            global post_reward_time
            if(not(txt100.get()=="")):
                post_reward_time = int(txt100.get())
                wfile.write(str(post_reward_time)+",")
            else:
                wfile.write("5,") 


            global tone_duration
            if(not(txt101.get()=="")):
                tone_duration = int(txt101.get())
                wfile.write(str(tone_duration)+",")
            else:
                wfile.write("4,")


            global cam_id    
            if(not(txt1.get()=="")):    
                cam_id = int(txt1.get())    
                wfile.write(str(cam_id)+",")  
            else:   
                wfile.write("0,") 

            global genotype
            if(not(txt9.get()=="")):
                genotype = txt9.get()
            
                wfile.write(str(genotype)+",")
            else:
                wfile.write("(blank),")

            global notes
            if(not(txt10.get()=="")):
                notes = txt10.get()
            
                wfile.write(str(notes)+",")
            else:
                wfile.write("(blank),")

            global pre_stimulus_time
            if(not(txt52.get()=="")):
                pre_stimulus_time = txt52.get()
                wfile.write(str(pre_stimulus_time)+",")
            else:
                wfile.write("4,")

            global pre_reward_time
            if(not(txt53.get()=="")):
                pre_reward_time = txt53.get()
                wfile.write(str(pre_reward_time)+",")
            else:
                wfile.write("4,")

            global reward_aversion_time
            if(not(txt54.get()=="")):
                reward_aversion_time = txt54.get()
                wfile.write(str(reward_aversion_time)+",")
            else:
                wfile.write("4,")
            wfile.write("\n")
            top1.destroy()
            #wfile.write("-"*50+"\n")
            return 1
    def val(char):
        if str.isdigit(char) or char == "":
            return True
        else:
            return False

    def valfn(char):
        if char in forbidden:
            return False
        else:
            return True
    val2 = (top1.register(val))
    valfn2 = (top1.register(valfn))

    panel2 = tkinter.PanedWindow(mainpanel,orient=tkinter.VERTICAL)
    panel2.pack()

    panel1 = tkinter.PanedWindow(panel2,orient=tkinter.HORIZONTAL)
    panel1.pack(anchor="w")
    label1 = tkinter.Label(top1, text="Cam Id: ",anchor="w",font=("Arial", 12))
    panel1.add(label1)
    txt1 = tkinter.Entry(top1, validate='all', validatecommand=(val2, '%P')) 
    panel1.add(txt1)

    panel3 = tkinter.PanedWindow(panel2,orient=tkinter.HORIZONTAL)
    panel3.pack(anchor="w")
    label3 = tkinter.Label(top1, text="User Initials: ",anchor="w",font=("Arial", 12))
    panel3.add(label3)
    txt3 = tkinter.Entry(top1, validate='all') 
    panel3.add(txt3)

    panel4 = tkinter.PanedWindow(panel2,orient=tkinter.HORIZONTAL)
    panel4.pack(anchor="w")
    label4 = tkinter.Label(top1, text="Number of Runs/Recordings: ",anchor="w",font=("Arial", 12))
    panel4.add(label4)
    txt4 = tkinter.Entry(top1, validate='all', validatecommand=(val2, '%P')) 
    panel4.add(txt4)

    panel5 = tkinter.PanedWindow(panel2,orient=tkinter.HORIZONTAL)
    panel5.pack(anchor="w")
    label5 = tkinter.Label(top1, text="ITI min (sec): ",anchor="w",font=("Arial", 12))
    panel5.add(label5)
    txt5 = tkinter.Entry(top1, validate='all', validatecommand=(val2, '%P')) 
    panel5.add(txt5)

    panel51 = tkinter.PanedWindow(panel2,orient=tkinter.HORIZONTAL)
    panel51.pack(anchor="w")
    label51 = tkinter.Label(top1, text="ITI max (sec): ",anchor="w",font=("Arial", 12))
    panel51.add(label51)
    txt51 = tkinter.Entry(top1, validate='all', validatecommand=(val2, '%P')) 
    panel51.add(txt51)
    
    panel52 = tkinter.PanedWindow(panel2,orient=tkinter.HORIZONTAL)
    panel52.pack(anchor="w")
    label52 = tkinter.Label(top1, text="Pre-stimulus Time: ",anchor="w",font=("Arial", 12))
    panel52.add(label52)
    txt52 = tkinter.Entry(top1, validate='all', validatecommand=(val2, '%P')) 
    panel52.add(txt52)

    panel53 = tkinter.PanedWindow(panel2,orient=tkinter.HORIZONTAL)
    panel53.pack(anchor="w")
    label53 = tkinter.Label(top1, text="Pre-reward Time: ",anchor="w",font=("Arial", 12))
    panel53.add(label53)
    txt53 = tkinter.Entry(top1, validate='all', validatecommand=(val2, '%P')) 
    panel53.add(txt53)





    panel54 = tkinter.PanedWindow(panel2,orient=tkinter.HORIZONTAL)
    panel54.pack(anchor="w")
    label54 = tkinter.Label(top1, text="Reward/Aversion Time: ",anchor="w",font=("Arial", 12))
    panel54.add(label54)
    txt54 = tkinter.Entry(top1, validate='all', validatecommand=(val2, '%P')) 
    panel54.add(txt54)



    panel100 = tkinter.PanedWindow(panel2,orient=tkinter.HORIZONTAL)
    panel100.pack(anchor="w")
    label100 = tkinter.Label(top1, text="Post-reward time: ",anchor="w",font=("Arial", 12)) 
    panel100.add(label100)
    txt100 = tkinter.Entry(top1, validate='all', validatecommand=(val2, '%P')) 
    panel100.add(txt100)


    panel101 = tkinter.PanedWindow(panel2,orient=tkinter.HORIZONTAL)
    panel101.pack(anchor="w")
    label101 = tkinter.Label(top1, text="Tone Duration: ",anchor="w",font=("Arial", 12))
    panel101.add(label101)
    txt101 = tkinter.Entry(top1, validate='all', validatecommand=(val2, '%P')) 
    panel101.add(txt101)

    panel6 = tkinter.PanedWindow(panel2,orient=tkinter.VERTICAL)
    panel6.pack(anchor="w")
    label6 = tkinter.Label(top1, text="Fish Information: ",anchor='center',font=("Arial", 12))
    label6.pack(anchor='center')
    label6.config(font=("Arial", 24))
    panel6.add(label6)

    panel7 = tkinter.PanedWindow(panel2,orient=tkinter.HORIZONTAL)
    panel7.pack(anchor="w")
    label7 = tkinter.Label(top1, text="Fish ID: ",anchor="w",font=("Arial", 12))
    panel7.add(label7)
    txt7 = tkinter.Entry(top1, validate='all',validatecommand=(valfn2,'%P')) 
    panel7.add(txt7)

    panel8 = tkinter.PanedWindow(panel2,orient=tkinter.HORIZONTAL)
    panel8.pack(anchor="w")
    label8 = tkinter.Label(top1, text="Gender (M/F): ",anchor="w",font=("Arial", 12))
    panel8.add(label8)
    txt8 = tkinter.Entry(top1, validate='all') 
    panel8.add(txt8)

    panel9 = tkinter.PanedWindow(panel2,orient=tkinter.HORIZONTAL)
    panel9.pack(anchor="w")
    label9 = tkinter.Label(top1, text="Genotype (W/M/T): ",anchor="w",font=("Arial", 12))
    panel9.add(label9)
    txt9 = tkinter.Entry(top1, validate='all') 
    panel9.add(txt9)

    panel10 = tkinter.PanedWindow(panel2,orient=tkinter.HORIZONTAL)
    panel10.pack(anchor="w")
    label10 = tkinter.Label(top1, text="Notes: ",anchor="w",font=("Arial", 12))
    panel10.add(label10)
    txt10 = tkinter.Entry(top1, validate='all') 
    panel10.add(txt10)


    C = tkinter.Button(top1, text ="GO", command = c)
    C.pack(side = tkinter.BOTTOM)
    top1.mainloop()

startup()
supermain()
