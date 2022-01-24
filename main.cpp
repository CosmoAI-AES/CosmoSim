#include <opencv2/opencv.hpp>
#include <iostream>
#include <thread>

int window_size = 1001;
int R_e = 30;
int R = 40;
int x_pos = window_size / 2;
int y_pos = window_size / 2;
//int K_l = 1;
//int K_s = 2;
int dist_ratio = 2;
cv::Mat source;
cv::Mat image;


void point_mass_funct( int thread_begin, int thread_end) {
    // Evaluate each point in image plane ~ lens plane
    for (int i = thread_begin; i < thread_end; i++) {
        for (int j = 0; j <= source.cols; j++) {

            // set coordinate system with origin in middle and x right and y up
            int x = j - window_size / 2;
            int y = window_size / 2 - i;

            // calculate distance and angle of the point evaluated relative to center of lens (origin)
            double r = sqrt(x * x + y * y);
            double theta = atan2(y, x);

            int R_in_lens_plane = 1.3 * R_e;

            // Split the equation into three parts for simplicity. (eqn. 9 from "Gravitational lensing")
            // Find the point from the source corresponding to the point evaluated
            double frac = (R_e * R_e * r) / (r * r + R_in_lens_plane * R_in_lens_plane + 2 * r * R_in_lens_plane * cos(theta));
            //double x_ = dist_ratio * (x + frac * (r / R_in_lens_plane + cos(theta)));
            //double y_ = dist_ratio * (y + frac * (-sin(theta)));
            double x_ = r * cos(theta) + frac * (r / R_in_lens_plane + cos(theta));
            double y_ = r * sin(theta) - frac * sin(theta);

            // Translate to array index
            int source_row = window_size / 2 - (int)round(y_);
            int source_col = (int)round(x_) + window_size / 2;

            // If index within source , copy value to image
            if (std::max(source_col, source_row) < window_size && std::min(source_col, source_row) >= 0) {
                image.at<uchar>(i, j) = source.at<uchar>(source_row, source_col);
            }
        }
    }
}

// Add som lines to the image for reference
void refLines(){
    for (int i = 0; i < window_size; i++) {
//        source.at<uchar>(window_size/2, i) = 255;
//        source.at<uchar>(i, window_size/2) = 255;
        source.at<uchar>(i, window_size - 1) = 255;
        source.at<uchar>(i, 0) = 255;
        source.at<uchar>(window_size - 1, i) = 255;
        source.at<uchar>(0, i) = 255;
    }
}



static void update(int, void*){
    R = std::max(R, 1); // constrain R to positive numbers

    // Make a source with black background and a gaussian light source placed at x_pos, y_pos and radius R
    source = cv::Mat(window_size, window_size, CV_8UC1, cv::Scalar(0, 0, 0));
    cv::circle(source, cv::Point(x_pos, y_pos), 0, cv::Scalar(254, 254, 254), R);
    int kSize = (R / 2) * 2 + 1; // make sure kernel size is odd
    cv::GaussianBlur(source, source, cv::Size_<int>(kSize, kSize), R);
    //refLines();

    // Init a black image
    image = cv::Mat(window_size, window_size, CV_8UC1, cv::Scalar(0, 0, 0));

    // Run the point mass function for each pixel in image. (multi thread)
    unsigned int num_threads = std::thread::hardware_concurrency();
    std::cout << num_threads << std::endl;
    std::vector<std::thread> threads_vec;
    for (int k = 0; k < num_threads; k++) {
        unsigned int thread_begin = (source.rows / num_threads) * k;
        unsigned int thread_end = (source.rows / num_threads) * (k + 1);
        std::thread t(point_mass_funct, thread_begin, thread_end);
        threads_vec.push_back(std::move(t));
        }
    for (auto& thread : threads_vec) {
        thread.join();
    }

    // comment out the stuff above and uncomment the line below to run on single thread
//    point_mass_funct(0, window_size);  //for single thread


    // Some formatting of the images before plotting them
//    source = source(cv::Rect(100,100,source.cols - 200, source.rows - 200));
//    image = image(cv::Rect(100,100,image.cols - 200, image.rows - 200));

    cv::resize(source, source, cv::Size_<int>(701, 701));
    cv::resize(image, image, cv::Size_<int>(701, 701));

    cv::Mat matDst(cv::Size(source.cols*2,source.rows),source.type(),cv::Scalar::all(0));
    cv::Mat matRoi = matDst(cv::Rect(0,0,source.cols,source.rows));
    source.copyTo(matRoi);
    matRoi = matDst(cv::Rect(source.cols,0,source.cols,source.rows));
    image.copyTo(matRoi);

    cv::imshow("Window", matDst);
}

int main()
{
    cv::namedWindow("Window", cv::WINDOW_AUTOSIZE);
    cv::createTrackbar("x pos", "Window", &x_pos, window_size, update);
    cv::createTrackbar("y pos", "Window", &y_pos, window_size, update);
    cv::createTrackbar("Einstein", "Window", &R_e, 100, update);
    cv::createTrackbar("Radius", "Window", &R, 100, update);
    cv::waitKey(0);
    return 0;
}