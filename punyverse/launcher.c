#include <stdlib.h>
#include <Windows.h>
#include <Python.h>

__declspec(dllexport) DWORD NvOptimusEnablement = 0x00000001;
__declspec(dllexport) int AmdPowerXpressRequestHighPerformance = 0x00000001;

#ifdef GUI
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow)
#else
int main()
#endif
{
#if PY_MAJOR_VERSION >= 3
	int argc;
	LPWSTR *argv = CommandLineToArgvW(GetCommandLineW(), &argc);
#else
    int argc = __argc;
    char **argv = __argv;
#endif

	Py_SetProgramName(argv[0]);
	Py_Initialize();
	PySys_SetArgvEx(argc, argv, 0);
	PyRun_SimpleString("from punyverse.main import main; main()");
	Py_Finalize();
    return 0;
}
