#ifndef LABEL_H
#define LABEL_H

#include <vector>
#include <prism/qt/core/hpp/prismQt.hpp>
#include <prism/prismJson.hpp>
#include <vector>

struct ActionLabel
{
    double clicked_x = 0;
    double clicked_y = 0;
    std::vector<std::vector<int>> clickedPosOnehot = std::vector<std::vector<int>>(16,std::vector<int>(30));
};

PRISMQT_CLASS(ActionLabel)
PRISM_FIELDS(ActionLabel,clicked_x,clicked_y,clickedPosOnehot)


struct StatusLabel
{
    std::vector<std::vector<int>>  minsRows = std::vector<std::vector<int>> (16,std::vector<int>(30));
};
PRISMQT_CLASS(StatusLabel)
PRISM_FIELDS(StatusLabel,minsRows)

#endif // LABEL_H
