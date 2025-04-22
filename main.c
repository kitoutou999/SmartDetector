#include <windows.h>
#include <stdio.h>

#define MEMORY_NAME "Global\\ScreenshotSharedMemory"
#define MUTEX_NAME "Global\\ScreenshotMutex"
#define SCREEN_WIDTH GetSystemMetrics(SM_CXSCREEN)
#define SCREEN_HEIGHT GetSystemMetrics(SM_CYSCREEN)
#define BYTES_PER_PIXEL 3
#define MEMORY_SIZE (SCREEN_WIDTH * SCREEN_HEIGHT * BYTES_PER_PIXEL)

HANDLE hMapFile;
LPVOID pBuf;
HANDLE hMutex;

void PrendreScreenshot() {
    HDC hScreenDC = GetDC(NULL);
    HDC hMemoryDC = CreateCompatibleDC(hScreenDC);
    HBITMAP hBitmap = CreateCompatibleBitmap(hScreenDC, SCREEN_WIDTH, SCREEN_HEIGHT);
    SelectObject(hMemoryDC, hBitmap);
    BitBlt(hMemoryDC, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, hScreenDC, 0, 0, SRCCOPY);

    BITMAPINFO bmi = {0};
    bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    bmi.bmiHeader.biWidth = SCREEN_WIDTH;
    bmi.bmiHeader.biHeight = -SCREEN_HEIGHT;
    bmi.bmiHeader.biPlanes = 1;
    bmi.bmiHeader.biBitCount = 24;
    bmi.bmiHeader.biCompression = BI_RGB;

    GetDIBits(hMemoryDC, hBitmap, 0, SCREEN_HEIGHT, pBuf, &bmi, DIB_RGB_COLORS);

    DeleteObject(hBitmap);
    DeleteDC(hMemoryDC);
    ReleaseDC(NULL, hScreenDC);
}

DWORD WINAPI CaptureLoop(LPVOID lpParam) {
    while (1) {
        WaitForSingleObject(hMutex, INFINITE);
        PrendreScreenshot();
        ReleaseMutex(hMutex);
        Sleep(16);  // ~60 FPS
    }
    return 0;
}

int main() {
    //secu de la zone memoire
    SECURITY_DESCRIPTOR sd;
    InitializeSecurityDescriptor(&sd, SECURITY_DESCRIPTOR_REVISION);
    SetSecurityDescriptorDacl(&sd, TRUE, NULL, FALSE);
    SECURITY_ATTRIBUTES sa = { sizeof(SECURITY_ATTRIBUTES), &sd, FALSE };

    //creation de la zone memoire
    hMapFile = CreateFileMapping(INVALID_HANDLE_VALUE, &sa, PAGE_READWRITE, 0, MEMORY_SIZE, MEMORY_NAME);
    pBuf = MapViewOfFile(hMapFile, FILE_MAP_WRITE, 0, 0, MEMORY_SIZE);

    //mutex
    hMutex = CreateMutex(NULL, FALSE, MUTEX_NAME);

    CaptureLoop(NULL);

    CloseHandle(hMutex);
    UnmapViewOfFile(pBuf);
    CloseHandle(hMapFile);
    return 0;
}