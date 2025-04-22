import mmap
import numpy as np
import cv2
import win32event
import win32file

MEMORY_NAME = "Global\\ScreenshotSharedMemory"
MUTEX_NAME = "Global\\ScreenshotMutex"
SCREEN_WIDTH = 1920  
SCREEN_HEIGHT = 1080  
BYTES_PER_PIXEL = 3 
MEMORY_SIZE = SCREEN_WIDTH * SCREEN_HEIGHT * BYTES_PER_PIXEL  

aspect_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
window_width = 1280
window_height = int(window_width / aspect_ratio)

mutex = win32event.CreateMutex(None, False, MUTEX_NAME)
memory = mmap.mmap(-1, MEMORY_SIZE, MEMORY_NAME, access=mmap.ACCESS_READ)

cv2.namedWindow("ScreenLive", cv2.WINDOW_NORMAL)
cv2.resizeWindow("ScreenLive", window_width, window_height)

last_frame = None

print(MEMORY_SIZE)
while True:
    
    result = win32event.WaitForSingleObject(mutex, 100)
    if result == win32event.WAIT_OBJECT_0 :
        try:
            raw_data = memory.read(MEMORY_SIZE)  
            memory.seek(0)  
            
            if len(raw_data) == MEMORY_SIZE:
                current_frame = np.frombuffer(raw_data, dtype=np.uint8).reshape((SCREEN_HEIGHT, SCREEN_WIDTH, 3))
                cv2.imshow("ScreenLive", current_frame)
                last_frame = current_frame
        finally:
            win32event.ReleaseMutex(mutex)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
memory.close()
win32file.CloseHandle(mutex)