import win32com.client
import win32api
import random
import time


def main():
    path = r'C:\Users\josep\anaconda3\envs\ZF_attention_project\ppt_method\paradigms.pptx'

    runs = 6
    rand_iti_start = 5
    rand_iti_stop = 10
    iti = random.randrange(rand_iti_start, rand_iti_stop)

    paradigm_slides = [['cf', 12], ['dfm', 7], ['ufm', 2]]
    all_runs = [['cf', 0], ['dfm', 0], ['ufm', 0]]

    app = win32com.client.Dispatch("PowerPoint.Application")
    app.Visible = 1
    app.Presentations.Open(FileName=path)
    app.ActivePresentation.SlideShowSettings.Run()

    for i in range(runs+1):
        this_run = random.choice(paradigm_slides)
        print("this run", this_run[0])

        app.SlideShowWindows(1).View.GotoSlide(this_run[1])
        win32api.Sleep(2000)
        app.SlideShowWindows(1).View.Next()
        win32api.Sleep(2000)
        app.SlideShowWindows(1).View.Next()
        win32api.Sleep(2000)
        app.SlideShowWindows(1).View.Next()
        win32api.Sleep(2000)
        app.SlideShowWindows(1).View.Next()
        win32api.Sleep(2000)
        app.SlideShowWindows(1).View.Next()
        win32api.Sleep(2000)
        app.SlideShowWindows(1).View.Next()
        win32api.Sleep(2000)
        app.SlideShowWindows(1).View.Next()

        for x, j in enumerate(all_runs):
            if this_run[0] == j[0]:
                j[1] += 1
            if j[1] == runs / 3:
                paradigm_slides.pop(x)
                all_runs.pop(x)

        time.sleep(iti)

        if len(all_runs) == 0:
            app.SlideShowWindows(1).View.GotoSlide(1)
            break

if __name__ == '__main__':
    main()

#add timer and trial number