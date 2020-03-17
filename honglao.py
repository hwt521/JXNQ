# -*- coding: UTF-8 -*-
# 导入nc库
import netCDF4 as nc
import numpy as np
import datetime
import time
import cv2

filename = 'C:/Users/Zn/Desktop/ncdata/2019110110.nc'   # .nc文件名
f = nc.Dataset(filename)  # 读取.nc文件，传入f中。此时f包含了该.nc文件的全部信息

var_Pr = 'Pr24'
var_data_Pr = f[var_Pr][:]  # 获取变量的数据

var_data_Pr = np.array(var_data_Pr)  # 转化为np.array数组
Threshold1 = 100  # 输入阈值(每天)
Threshold2 = 150  # 输入阈值(每3天)
Threshold3 = 200  # 输入阈值(每5天)


def getTimeValue(self):

    dateTimeNumList = []  # 准备存储time的值
    dateTimeUnits = ''  # 准备记录初始时间
    for key in self.variables.keys():  # 在变量中筛选出time变量的全部信息
        if key.lower() in ['time', 't']:
            dateTimeNumList = self.variables[key][:]  # 获取time字段全部值
            dateTimeUnits = self.variables[key].units  # 获取初始时间信息
            break

    dateTimeStrList = []  # 该列表存储真实日期字符串
    dayValueList = []  # 该列表存储日值数据对应的time字段值

    # dateTimeUnits = 'hours since yyyymmddhhmmss'
    startDateTimeStr = ' '.join(dateTimeUnits.split()[-1:])  # -1提取日期

    stdt = datetime.datetime.strptime(
        startDateTimeStr, '%Y%m%d%H%M%S')  # stdt=真实起始时间

    if dateTimeUnits.split()[0] == 'hours':  # 0提取计时单位
        for dtn in dateTimeNumList:  # 逐一提取time字段值
            dt = stdt + datetime.timedelta(hours=dtn)  # 真实时间 = 起始时间 + 时间差
            ymdH = dt.strftime('%Y-%m-%d')  # 生成真实日期字符串
            H = dt.strftime('%H')  # 生成真实时间值
            dateTimeStrList.append(ymdH)

            # 取出每日20点的time字段值，并存入列表
            if int(H) % 24 == 20:
                dayValueList.append(dtn)

    # 分别返回：真实日期列表，逐日time值列表，全部time值列表
    return dateTimeStrList, dayValueList, dateTimeNumList


# 获取日值数据对应下标
timelist = getTimeValue(f)[1]
daylist = []
for day in timelist:
    day_in = np.argwhere(getTimeValue(f)[2] == day)  # week_in为np格式浮点数
    day_out = int(day_in[0])  # 转化为int整数
    daylist.append(day_out)
print(daylist)

# 获取降水15天的日值数据
Pr_daylist = []
for d in daylist:
    Pr_daylist.append(var_data_Pr[d][:])
print(np.shape(Pr_daylist))


# 判断每天Pr值与阈值关系，
# 并二值化：np.where(a>threshold, upper, lower)
honglao_list = []
for i in range(15):
    if i <= 10:
        condition_1 = np.where(Pr_daylist[i][:] >= Threshold1, 1, 0)
        condition_2 = np.where(
            (Pr_daylist[i][:]+Pr_daylist[i+1][:]+Pr_daylist[i+2][:]) >= Threshold2, 1, 0)
        condition_3 = np.where((Pr_daylist[i][:]+Pr_daylist[i+1][:]+Pr_daylist[i+2]
                                [:]+Pr_daylist[i+3][:]+Pr_daylist[i+4][:]) >= Threshold3, 1, 0)
        condition = condition_1 + condition_2 + condition_3
        condition = np.where(condition > 0, 1, 0)
        honglao_list.append(condition)

    elif i > 10 and i <= 12:
        condition_1 = np.where(Pr_daylist[i][:] >= Threshold1, 1, 0)
        condition_2 = np.where(
            (Pr_daylist[i][:]+Pr_daylist[i+1][:]+Pr_daylist[i+2][:]) >= Threshold2, 1, 0)
        condition = condition_1 + condition_2
        condition = np.where(condition > 0, 1, 0)
        honglao_list.append(condition)
    else:
        condition_1 = np.where(Pr_daylist[i][:] >= Threshold1, 1, 0)
        honglao_list.append(condition_1)

print(np.shape(honglao_list))

# 将15天二值数据求和叠加，再二值化
honglao_sum = np.zeros((17, 22))
for hl_perday in np.array(honglao_list, dtype=int):  # 遍历日值数据
    honglao_sum += hl_perday
honglao_ez = np.where(honglao_sum > 0, 255, 0)  # 二值化为灰阶图数据
print(np.shape(honglao_sum))
# 出图
honglao_ez = honglao_ez.astype(np.float32)
honglao_ez = cv2.resize(honglao_ez, (440, 340),
                        interpolation=cv2.INTER_NEAREST)
cv2.imwrite('C:/Users/Zn/Desktop/WORK/honglao/1.png', honglao_ez)
