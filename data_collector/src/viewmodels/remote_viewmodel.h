#ifndef REMOTE_VIEWMODEL_H
#define REMOTE_VIEWMODEL_H

#include <QObject>
#include <QImage>
#include <opencv2/opencv.hpp>
#include <models/label.h>

class Remote_viewmodel : public QObject
{
    Q_OBJECT
public:
    explicit Remote_viewmodel(QObject *parent = nullptr);



public slots:

    void save(QImage* img,const QString &filePath, const QRect &rect,const bool& async);
    void saveClickPosLabel(QString filePath,double x,  double y, int cellsize);


private: //mehtods
    void loadResources();

private://fields
    std::map<int,cv::Mat> resources_;


signals:

};

#endif // REMOTE_VIEWMODEL_H
