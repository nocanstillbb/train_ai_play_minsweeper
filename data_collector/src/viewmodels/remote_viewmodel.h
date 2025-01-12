#ifndef REMOTE_VIEWMODEL_H
#define REMOTE_VIEWMODEL_H

#include <QObject>

class Remote_viewmodel : public QObject
{
    Q_OBJECT
public:
    explicit Remote_viewmodel(QObject *parent = nullptr);

signals:

};

#endif // REMOTE_VIEWMODEL_H
