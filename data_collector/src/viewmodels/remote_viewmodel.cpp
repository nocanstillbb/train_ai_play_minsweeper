#include "remote_viewmodel.h"
#include <QFileInfo>
#include <QDir>
#include <QtConcurrent>
#include <prism/qt/ui/helper/cpp_utility.h>
#include <prism/container.hpp>
#include <sstream>


namespace{
cv::Mat QImageToCvMat(const QImage &image);

}

Remote_viewmodel::Remote_viewmodel(QObject *parent) : QObject(parent)
{
    loadResources();

}

//#define COLLECT_DATA
void Remote_viewmodel::save(QImage *img, const QString &filePath, const QRect &rect, const bool &async)
{
    QFileInfo fileInfo(filePath);
    QDir dir(fileInfo.dir().dirName());
    if (!dir.exists())
    {
        qDebug()<< "create dir:" << fileInfo.dir().dirName();
        dir.mkpath(fileInfo.dir().dirName());
    }


    if(!img->isNull())
    {
        auto lambda = [=](){
            auto imgcopy = img->copy(rect);
            imgcopy.save(filePath+".png");

#ifdef COLLECT_DATA
            //仅在调试时保存图片查看
            QString splitDir = fileInfo.dir().dirName() +"/"+fileInfo.baseName() + "_split";
            QDir dir2(splitDir); if (!dir2.exists()) {

                qDebug()<< "create dir:" << splitDir;
                dir2.mkpath(splitDir);
            }
#endif


            StatusLabel label;

            for(int row=0;row<16;++row)
            {
                for(int col = 0;col<30;++col)
                {
                    QRect clip_cell;
                    clip_cell.setX(col*26 + 3);
                    clip_cell.setY(row*26 + 2);
                    clip_cell.setWidth(20);
                    clip_cell.setHeight(20);



#ifdef COLLECT_DATA
                    //仅在调试时保存图片查看
                    QString cellpath = QString("%1/%2_%3.png")
                        .arg(splitDir)
                        .arg(row)
                        .arg(col);
                    qDebug()<< "cell save path;" << cellpath;
                    imgcopy.copy(clip_cell).save(cellpath);
#endif



#ifndef COLLECT_DATA
                    //匹配,计算最匹配的格式名称
                    QImage cell_img = imgcopy.copy(clip_cell);
                    cv::Mat cell_mat = QImageToCvMat(cell_img);
                    double diffnum = 9999;
                    int bestIndex = -1;

                    for(const auto& [k,v]:resources_)
                    {
                        // 计算差值
                        cv::Mat diff;
                        cv::absdiff(cell_mat, v, diff); // 逐像素求差值
                        // 检查差值是否全为 0
                        int diffnum_ = cv::countNonZero(diff.reshape(1));
                        if(diffnum > diffnum_)
                        {
                            diffnum = diffnum_;
                            bestIndex = k;
                        }

                    }
                    label.minsRows[row][col] = bestIndex;
#endif

                }

            }

#ifndef COLLECT_DATA
            for(const auto& row : label.minsRows)
            {
                for(const auto& col : row)
                {
                    std::cout << std::setw(4)   << std::setfill(' ')<< col ;
                }
                std::cout << std::endl;
            }

            QString labelPath = filePath + "_label_status.json";
            QFile file(labelPath);
            if (file.open(QIODevice::WriteOnly | QIODevice::Text)) {
                QTextStream out(&file);
                out << QString::fromStdString(prism::json::toJsonString(label));
                file.close();
            } else {
                qWarning() << "无法打开文件:" << file.errorString();
            }



#endif

        };
        if(async)
        {
            qDebug()<< "async save image " << rect << " to " << filePath;
            QtConcurrent::run(lambda);
        }
        else
        {
            qDebug()<< "sync save image " << rect << " to " << filePath;
            lambda();
        }

    }

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

        cv::Mat image = imread(info.absoluteFilePath().toStdString(), cv::IMREAD_COLOR);
        qDebug() << "iamge path:" << info.absoluteFilePath() << "    image size:" << image.rows << "x" << image.cols;

        resources_[info.baseName().toInt()] = image;
    }

    for(const auto& [k,v] : resources_)
    {
        qDebug()<< "key:" << k ;
    }

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


