/*
**本文件来自~/autonomy_stack_go2/src/utilities/unitree_pkgs/go2_h264_repub/src/go2_h264_repub.cpp
用于学习GO2机器人的图像传输、话题包装


编译指令：
cd ~/unitree_sdk2_python
source /opt/ros/humble/setup.bash
cmake --build .vscode/build-go2 --target go2_h264_repub -j2

运行指令：
./.vscode/build-go2/go2_h264_repub --ros-args -p multicast_iface:=eth0
*/

#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>

class H264Repub : public rclcpp::Node {
public:
    // 构造函数
    H264Repub() : Node("h264_repub") {
        image_publisher_ = this->create_publisher<sensor_msgs::msg::Image>("/camera/image/raw", 10);

        std::string multicast_iface = "eth0";
        this->declare_parameter("multicast_iface", multicast_iface);
        this->get_parameter("multicast_iface", multicast_iface);

        std::string gstreamer_str = "udpsrc address=230.1.1.1 port=1720 multicast-iface=" + multicast_iface + " ! application/x-rtp, media=video, encoding-name=H264 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! video/x-raw,width=1280,height=720,format=BGR ! appsink drop=1";
        cap.open(gstreamer_str, cv::CAP_GSTREAMER);
        
        rclcpp::Rate rate(100);

        if (!cap.isOpened()) {
            RCLCPP_ERROR(this->get_logger(), "Failed to open video capture");
        } else {
            while (rclcpp::ok()) {
                cv::Mat frame;
                if (cap.read(frame)){
                // cv::imshow("repuber", frame);
                    // 发布ROS话题
                    auto ros_image = cv_bridge::CvImage(std_msgs::msg::Header(), "bgr8", frame).toImageMsg();
                    ros_image->header.frame_id = "camera";
                    ros_image->header.stamp = this->get_clock()->now();
                    image_publisher_->publish(*ros_image);
                    // std::cout << "pubed!" << std::endl;
                }
                cv::waitKey(10);
                // rate.sleep();
            }
        }
    }

private:
    // 用于发布图像 ROS 2 图像发布者的智能指针
    rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr image_publisher_; 
    // 读取视频。 它是 OpenCV 的 cv::VideoCapture 对象
    cv::VideoCapture cap;
    // 预留的 ROS 2 定时器指针
    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<H264Repub>();
    rclcpp::shutdown();
    return 0;
}
