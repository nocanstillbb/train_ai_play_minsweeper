#ifndef REMOTE_VIEWMODEL_H
#define REMOTE_VIEWMODEL_H

#include <QObject>
#include <QImage>
#include <opencv2/opencv.hpp>
#include <models/label.h>
#include <prism/qt/core/hpp/prismModelListProxy.hpp>


#undef slots
#include "torch/script.h"
#define slots Q_SLOTS



class Remote_viewmodel : public QObject
{
    Q_OBJECT
    Q_PROPERTY(prism::qt::core::prismModelListProxy<MineCell>* mines READ mines WRITE setMines NOTIFY minesChanged)
    Q_PROPERTY(bool updateCells READ updateCells WRITE setUpdateCells NOTIFY updateCellsChanged)
public:
    explicit Remote_viewmodel(QObject *parent = nullptr);



    prism::qt::core::prismModelListProxy<MineCell> *mines() const;
    void setMines(prism::qt::core::prismModelListProxy<MineCell> *newMines);

    bool updateCells() const;
    void setUpdateCells(bool newUpdateCells);

public slots:

    void recognize(QImage* img,const QRect &rect);
    void saveClickPosLabel(QString filePath,double x,  double y, int cellsize);


private: //mehtods
    void loadResources();
    void loadModels();

    void letterbox(QImage* img);

private://fields
    std::map<int,cv::Mat> resources_;


    torch::jit::script::Module pt_model;


    prism::qt::core::prismModelListProxy<MineCell> *m_mines;

    bool m_updateCells;

signals:

    void minesChanged();
    void updateCellsChanged();
};

#endif // REMOTE_VIEWMODEL_H
