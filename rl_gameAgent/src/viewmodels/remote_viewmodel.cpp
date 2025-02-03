#include "remote_viewmodel.h"
#include <QFileInfo>
#include <QDir>
#include <QtConcurrent>
#include <prism/qt/ui/helper/cpp_utility.h>
#include <prism/container.hpp>
#include <QPainter>
#include <sstream>
#include <QColor>
#include <torch/torch.h>
#include <QImage>
#include <chrono>



namespace{
cv::Mat QImageToCvMat(const QImage &image);
const cv::Size TARGET_SIZE(480, 256);

}

Remote_viewmodel::Remote_viewmodel(QObject *parent) : QObject(parent)
{
    setMines(new prism::qt::core::prismModelListProxy<MineCell>());

    mines()->pub_beginResetModel();
    for(int i =0 ; i< 16*30; ++i)
        mines()->appendItemNotNotify(std::make_shared<MineCell>());
    mines()->pub_endResetModel();

    loadModels();
    loadResources();

}


cv::Mat letterbox_image(const cv::Mat& image) {
    int width = image.cols;
    int height = image.rows;
    float scale = std::min(TARGET_SIZE.width / (float)width, TARGET_SIZE.height / (float)height);
    int new_width = static_cast<int>(width * scale);
    int new_height = static_cast<int>(height * scale);

    cv::Mat resized_image;
    cv::resize(image, resized_image, cv::Size(new_width, new_height));

    cv::Mat padded_image(TARGET_SIZE, CV_8UC3, cv::Scalar(0, 0, 0));
    resized_image.copyTo(padded_image(cv::Rect(0, 0, new_width, new_height)));

    return padded_image;
}

void Remote_viewmodel::recognize(QImage* img,const QRect &rect)
{

    auto start = std::chrono::high_resolution_clock::now();

    QImage inputImg = img->copy(rect);
    cv::Mat mat = QImageToCvMat(inputImg);
    cv::Mat letterbox = letterbox_image(mat);

    auto preprocess_end = std::chrono::high_resolution_clock::now();

    qDebug()<< "preprocess  time (ms):" << std::chrono::duration_cast<std::chrono::milliseconds>(preprocess_end - start).count();

    torch::Device device(torch::kMPS); // macOS MPS 设备
    //mat.convertTo(mat, CV_32F, 1.0 / 255.0);
    letterbox.convertTo(letterbox, CV_32F, 1.0/255);
    torch::Tensor img_tensor = torch::from_blob(letterbox.data, {1,TARGET_SIZE.height, TARGET_SIZE.width, 3}).permute({0,3, 1, 2}).clone().to(device);

    torch::Tensor t = pt_model.forward({img_tensor}).toTensor().argmax(-1) - 1 ;

    auto infer_end = std::chrono::high_resolution_clock::now();

    qDebug()<< "infer  time (ms):" << std::chrono::duration_cast<std::chrono::milliseconds>(infer_end - preprocess_end).count();

    for(int row = 0; row < 16; ++row)
    {
        for(int col = 0; col<30 ; ++col)
        {
            //std::cout << std::setw(4) << t[0][row][col].item<int>();
            mines()->list()->at(row*30+col)->instance()->status = t[0][row][col].item<int>();
            //mines()->list()->at(row*30+col)->update();

        }
        //std::cout << std::endl;
    }
    //std::cout << std::endl;
    setUpdateCells(!updateCells());

    auto postprocess_end = std::chrono::high_resolution_clock::now();

    qDebug()<< "post process time (ms):" << std::chrono::duration_cast<std::chrono::milliseconds>(postprocess_end - infer_end).count();

}


void Remote_viewmodel::saveClickPosLabel(QString filePath,double x,  double y, int cellsize)
{
    ActionLabel label;
    size_t clicked_row =  y / cellsize;
    size_t clicked_col =  x / cellsize;
    label.clicked_x = clicked_row;
    label.clicked_y = clicked_col;
    for(size_t row = 0 ; row < label.clickedPosOnehot.size(); ++ row)
    {
        for(size_t col = 0 ; col <  label.clickedPosOnehot[row].size(); ++ col)
        {
            if(clicked_row == row && clicked_col == col)
                label.clickedPosOnehot[row][col] = 1;
            else
                label.clickedPosOnehot[row][col] = 0;
        }
    }
    QString json = QString::fromStdString(prism::json::toJsonString(label)) ;
    qDebug()<< "x:" << x << "  y:" << y << "  clicked_row:" << clicked_row << "  clicked_col:" << clicked_col;

    QFileInfo fileInfo(filePath);
    QDir dir(fileInfo.dir().dirName());
    if (!dir.exists())
        dir.mkpath(fileInfo.dir().dirName());
    QFile file(filePath);
    if (file.open(QIODevice::WriteOnly | QIODevice::Text)) {
        QTextStream out(&file);
        out << json;
        file.close();
    } else {
        qWarning() << "无法打开文件:" << file.errorString();
    }


}

void Remote_viewmodel::loadResources()
{

    QDir dir("./resources");

    if(!dir.exists())
    {
        qDebug()<< "目录不存在";
        return;
    }

    for(const QFileInfo& info : dir.entryInfoList(QDir::Files|QDir::NoDotAndDotDot))
    {

        if(info.baseName().startsWith("mouse"))
            continue;
        cv::Mat image = imread(info.absoluteFilePath().toStdString(), cv::IMREAD_COLOR);
        qDebug() << "iamge path:" << info.absoluteFilePath() << "    image size:" << image.rows << "x" << image.cols;

        resources_[info.baseName().toInt()] = image;
    }

    for(const auto& [k,v] : resources_)
    {
        qDebug()<< "key:" << k ;
    }

}

void Remote_viewmodel::loadModels()
{
    // 1. 加载 TorchScript 模型
    //std::string model_path = "epo999_acc0.9998model.pt";
    std::string model_path = "model_scripted.pt";

    try {
        pt_model = torch::jit::load(model_path);
    } catch (const c10::Error& e) {
        qDebug()<< "模型加载失败！" ;
        return;
    }
    qDebug()<< "模型加载成功！" ;

    // 2. 设置设备为 MPS (Metal Performance Shaders)
    torch::Device device(torch::kMPS); // macOS MPS 设备
    pt_model.to(device);
    pt_model.eval();


}





namespace{
cv::Mat QImageToCvMat(const QImage &image) {
    switch (image.format()) {
    case QImage::Format_RGB32:
    {
        cv::Mat mat(image.height(), image.width(), CV_8UC4, const_cast<uchar*>(image.bits()), image.bytesPerLine());
        cv::cvtColor(mat,mat,cv::COLOR_BGRA2BGR);
        return mat.clone(); // 深拷贝以避免 QImage 数据被释放
    }
    case QImage::Format_Grayscale8: {
        cv::Mat mat(image.height(), image.width(), CV_8UC1, const_cast<uchar*>(image.bits()), image.bytesPerLine());
        return mat.clone();
    }
    default:
        qWarning("Unsupported QImage format");
        return cv::Mat();
    }
}

}



prism::qt::core::prismModelListProxy<MineCell> *Remote_viewmodel::mines() const
{
    return m_mines;
}

void Remote_viewmodel::setMines(prism::qt::core::prismModelListProxy<MineCell> *newMines)
{
    if (m_mines == newMines)
        return;
    m_mines = newMines;
    emit minesChanged();
}

bool Remote_viewmodel::updateCells() const
{
    return m_updateCells;
}

void Remote_viewmodel::setUpdateCells(bool newUpdateCells)
{
    if (m_updateCells == newUpdateCells)
        return;
    m_updateCells = newUpdateCells;
    emit updateCellsChanged();
}
