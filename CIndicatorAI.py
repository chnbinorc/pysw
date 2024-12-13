import os.path
from sklearn.linear_model import LinearRegression
# from LinearUnit import LinearUnit
from sklearn.feature_extraction.image import grid_to_graph
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans
from sklearn import datasets
import joblib
import numpy as np
from matplotlib.collections import LineCollection
import pandas as pd
from sklearn.decomposition import PCA
from sklearn import cluster, covariance, manifold
import warnings
import numpy
import matplotlib.pyplot as plt
from tslearn.clustering import KShape
from tslearn.datasets import CachedDatasets
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
import sys
from CCommon import log, warning, error

warnings.filterwarnings('ignore')

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', 10000)
pd.set_option('display.width', 10000)

np.set_printoptions(threshold=np.inf)


class CIndicatorAI:
    def __init__(self):
        return

    def fit_kshape(self,data):
        filename = 'd:/temp/kshape_day_10.pkl'
        if not os.path.exists(filename):
            log('kshape_day_10.pkl 文件不存在')
            return None

        scaler = TimeSeriesScalerMeanVariance()
        data_scaled = scaler.fit_transform(data)
        kshape_model = KShape.from_pickle(filename)
        labels = kshape_model.fit_predict(data_scaled)
        return labels

    def test_kshape(self, draw=False):
        seed = 0
        numpy.random.seed(seed)
        df = pd.read_csv('D:/temp/bbidata.csv').copy()
        if 'label' in df.columns:
            df = df.drop(columns=['quaprice', 'quavol', 'days', 'income', 'ts_code', 'trade_date', 'label'])
        else:
            df = df.drop(columns=['quaprice', 'quavol', 'days', 'income', 'ts_code', 'trade_date'])
        data = np.array(df).reshape(-1, 12, 1)
        # numpy.random.shuffle(data)

        scaler = TimeSeriesScalerMeanVariance()
        data_scaled = scaler.fit_transform(data)
        sz = data.shape[1]

        n_clusters = 10
        filename = 'd:/temp/kshape_day_10.pkl'

        if os.path.exists(filename):
            kshape_model = KShape.from_pickle(filename)
            labels = kshape_model.fit_predict(data_scaled)
        else:
            kshape_model = KShape(n_clusters=n_clusters, verbose=False, random_state=42)
            labels = kshape_model.fit_predict(data_scaled)
            kshape_model.to_pickle(filename)
        dbsource = pd.read_csv('D:/temp/bbidata.csv')
        dbsource['label'] = labels
        dbsource.to_csv('D:/temp/bbidata.csv', index=False)

        if draw:
            plt.figure()
            for yi in range(10):
                print(len(data[labels == yi]))
                for xx in data[labels == yi]:
                    plt.plot(xx.ravel(), "k-", alpha=.2)
                plt.plot(kshape_model.cluster_centers_[yi].ravel(), "r-")
                plt.xlim(-1, sz)
                plt.ylim(-2, 2)
                plt.tight_layout()
                filename = f'd:/temp/bbidata_{yi}.png'
                plt.savefig(filename, bbox_inches='tight')
                plt.cla()

    def test_make_kshape_day_10(self):
        db = pd.read_csv('d:/temp/bbidata.csv')
        cols = ['quaprice', 'quavol', 'label', 'succeed', 'fail', 'simples']
        dbStd = pd.DataFrame(columns=cols)
        for i in range(5):
            for j in range(5):
                for k in range(10):
                    cond = f'quaprice == {i} and quavol == {j} and label=={k}'
                    # print(cond)
                    dk = db.query(cond).copy()
                    if len(dk) == 0:
                        print(
                            f'条件：价格区间：{i} 成交量区间:{j} 标签区间:{k}  样本为 0')
                    else:
                        d1 = dk.query('income > 0')
                        d2 = dk.query('income < 0')
                        dbStd.loc[len(dbStd)] = [i, j, k, round(len(d1) / len(dk), 3), round(len(d2) / len(dk), 3),
                                                 len(dk)]
                        # print(
                        #     f'条件：价格区间：{i} 成交量区间:{j} 标签区间:{k}  总数： {len(dk)} , 成功：{round(len(d1) / len(dk), 3)}, 失败：{round(len(d2) / len(dk), 3)}')
                print('==========================================================')
        dbStd.to_csv('d:/temp/bbidata_kshape_day_10_std.csv', index=False)
        print(dbStd.query('succeed > 0.6'))
        print(dbStd)
