#include <opencv2/opencv.hpp>
#include "Simulator.h"
#include <fstream>

int main()
{
    std::cout << "GL Simulator starting ...\n" ;
    Window win;
    std::cout << "GL Simulator ...\n" ;
    try{
        win.initGui();
    }
    catch (std::exception &e){
        std::cout << "initGui returned exception: " << e.what() << std::endl;
        return 1;
    }

    bool running = true;
    while (running) {
        int k = cv::waitKey(1);
        if ((cv::getWindowProperty("GL Simulator", cv::WND_PROP_AUTOSIZE) == -1) || (k == 27)) {
            running = false;
        }
    }
    cv::destroyAllWindows();
    return 0;
}
