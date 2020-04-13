# -*- coding: utf-8 -*-
"""
Filename: /home/kevin/Dropbox (LSMO)/proj75_mofcolor/ml/code/utils.py
Path: /home/kevin/Dropbox (LSMO)/proj75_mofcolor/ml/code
Created Date: Monday, February 24th 2020, 4:42:56 pm
Author: Kevin Jablonka

Copyright (c) 2020 Kevin Jablonka
"""

import os
import collections
import pickle
import random
import numpy as np
import keras.backend as K
import matplotlib.patches as mpatch
from webcolors import rgb_to_hex
import matplotlib.pyplot as plt
from comet_ml import Experiment
from typing import Union
import time
import tensorflow as tf
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from keras import backend as BK
import pandas as pd
import ruamel.yaml as yaml
from .descriptornames import *
from numpy.random import seed
import joblib


def augment_data(
    df, augment_dict, r_col="r", g_col="g", b_col="b", name_col="color_cleaned"
):
    df_ = df.copy()

    new_rows = []
    for i, row in df.iterrows():
        color = row[name_col]
        r_ = row.copy()
        for rgb in augment_dict[color]:
            r_[r_col] = rgb[0]
            r_[g_col] = rgb[1]
            r_[b_col] = rgb[2]
            new_rows.append(r_)

    new_df = pd.concat([df, pd.DataFrame(new_rows)])
    return new_df


def augment_random(colorname, augment_dict):
    possible_colors = augment_dict[colorname]
    chosen_color = random.choice(possible_colors)
    return np.array(chosen_color)


def tf_augment_random():
    raise NotImplementedError


def read_pickle(file):
    with open(file, "rb") as fh:
        result = pickle.load(fh)
    return result


def huber_fn(y_true, y_pred):
    error = y_true - y_pred
    is_small_error = (
        tf.abs(error) < 1
    )  # replace `tf` with `K` where `K = keras.backend`
    squared_loss = tf.square(error) / 2  # replace `tf` with `K`
    linear_loss = tf.abs(error) - 0.5  # replace `tf` with `K`
    return tf.where(is_small_error, squared_loss, linear_loss)


def get_timestamp_string():
    t = time.localtime()
    timestamp = time.strftime("%b-%d-%Y_%H%M", t)
    return timestamp


def mapping_to_target_range(x, target_min=0, target_max=1):
    """Linear activation function that constrains output to a range
    
    Arguments:
        x {tensor} -- input tensor
    
    Keyword Arguments:
        target_min {float} -- minimum output (default: {0})
        target_max {float} -- maximum output (default: {1})
    
    Returns:
        tensor -- constrained linear activation
    """
    x02 = x + 1  # x in range(0,2)
    scale = (target_max - target_min) / 2.0
    return x02 * scale + target_min


def mapping_to_target_range_sig(x, target_min=0, target_max=255):
    """Sigmoid activation function that constrains output to a range
    
    Arguments:
        x {tensor} -- input tensor
    
    Keyword Arguments:
        target_min {float} -- minimum output (default: {0})
        target_max {float} -- maximum output (default: {255})
    
    Returns:
        tensor -- constrained Sigmoid activation
    """
    x02 = BK.sigmoid(x) + 1  # x in range(0,2)
    scale = (target_max - target_min) / 2.0
    return x02 * scale + target_min


def plot_predictions(predictions, labels, names, sample=100, outname=None):
    """Plot figure that compares color of predictions versus acutal colors.
    
    Arguments:
        predictions {iterable} -- iterable of rgb colors
        labels {iterable} -- iterable of rgb colors
        names {iterable} -- iterable of strings
    
    Keyword Arguments:
        sample {int} -- how many samples to plot (default: {100})
        outname {string} -- path to which figure is saved (default: {None})
    """
    fig = plt.figure(figsize=[4.8, 16])
    ax = fig.add_axes([0, 0, 1, 1])

    predictions = predictions[:sample]
    names = names[:sample]
    labels = labels[:sample]

    predictions = [rgb_to_hex((int(c[0]), int(c[1]), int(c[2]))) for c in predictions]
    true = [rgb_to_hex((int(c[0]), int(c[1]), int(c[2]))) for c in labels]

    for i in range(len(predictions)):
        r1 = mpatch.Rectangle((0, i), 1, 1, color=predictions[i])
        r2 = mpatch.Rectangle((1, i), 1, 1, color=true[i])
        txt = ax.text(2, i + 0.5, "  " + names[i], va="center", fontsize=10)

        ax.add_patch(r1)
        ax.add_patch(r2)
        ax.axhline(i, color="k")

    ax.text(0.5, i + 1.5, "prediction", ha="center", va="center")
    ax.text(1.5, i + 1.5, "median RGB for label", ha="center", va="center")
    ax.set_xlim(0, 3)
    ax.set_ylim(0, i + 2)
    ax.axis("off")

    fig.tight_layout()

    if outname is not None:
        fig.savefig(outname, bbox_inches="tight")


def flatten(d, parent_key="", sep="_"):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def parse_config(yml_file):
    with open(yml_file, "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return config


def make_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def select_features(selection: list):
    selected_features = []
    for feature in selection:
        selected_features.extend(descriptor_dict[feature])

    return selected_features


def rgb_to_hex_round(c):
    return rgb_to_hex((int(c[0]), int(c[1]), int(c[2])))


def plot_prediction_dist(
    predictions_dist,
    label_names,
    label_dict: dict,
    sample: int = 100,
    outname: str = None,
    centrality: str = "median",
    n_samples: int = 10,
    width: float = 0.2,
    figsize: tuple = (8.16),
):
    """Plot figure that compares color of predictions versus acutal colors.
    
    Arguments:
        predictions_dist {iterable} -- iterable of rgb colors, assumes (samples, 1, structures, 3) shape 
        labels {iterable} -- iterable of rgb colors of length structures
        label_dict {dict} -- dictionary mapping the strings from the labels array to the RGB colors 
            form the survey

    Keyword Arguments:
        sample {int} -- how many samples to plot (default: {100})
        outname {string} -- path to which figure is saved (default: {None})
        centrality {string} -- method that is used to calculate the centrality of the color distributions (mean or median) (default: {median})
        n_samples {int} -- number of random samples that are drawn from the distributions and plotted in the figure
        width {float} -- width of the rectangles for the random samples from the distribution
        figsize {tuple} -- size of the full figure
    """
    fig = plt.figure(figsize=figsize)
    ax = fig.add_axes([0, 0, 1, 1])

    predictions = predictions_dist[:, 0, :sample]
    label_names = label_names.values[:sample]
    label_names_set = set(label_names)

    if centrality == "median":
        prediction_centrality = np.median(predictions, axis=0)
        label_centrality_dict = {}
        for color in label_names_set:
            label_centrality_dict[color] = np.median(label_dict[color], axis=0)
    elif centrality == "mean":
        prediction_centrality = np.mean(predictions, axis=0)
        label_centrality_dict = {}
        for color in label_names_set:
            label_centrality_dict[color] = np.mean(label_dict[color], axis=0)

    for i in range(len(label_names)):
        colorname = label_names[i]
        r1 = mpatch.Rectangle(
            (0, i), 1, 1, color=rgb_to_hex_round(prediction_centrality[i])
        )
        r2 = mpatch.Rectangle(
            (1, i), 1, 1, color=rgb_to_hex_round(label_centrality_dict[colorname])
        )

        ax.add_patch(r1)
        ax.add_patch(r2)

        for j in range(n_samples):
            choice = np.random.randint(0, len(predictions_dist))
            choice2 = np.random.randint(0, len(label_dict[colorname]))
            r3 = mpatch.Rectangle(
                (-0.5 - width * j, i),
                0.5,
                1,
                color=rgb_to_hex_round(predictions[choice][i]),
            )
            r4 = mpatch.Rectangle(
                (2 + width * j, i),
                0.5,
                1,
                color=rgb_to_hex_round(label_dict[colorname][choice2]),
            )
            ax.add_patch(r3)
            ax.add_patch(r4)

        ax.axhline(i, color="k")

    ax.text(0.5, i + 1.5, "prediction {}".format(centrality), ha="center", va="center")
    ax.text(1.5, i + 1.5, "label {}".format(centrality), ha="center", va="center")

    ax.text(
        0.5 - n_samples * 3 / 4 * width,
        i + 1.5,
        "prediction samples",
        ha="center",
        va="center",
    )
    ax.text(
        1.5 + n_samples * 3 / 4 * width,
        i + 1.5,
        "colorjeopardy samples",
        ha="center",
        va="center",
    )

    ax.set_xlim(0 - n_samples * width, 2 + n_samples * width)
    ax.set_ylim(0, i + 2)
    ax.axis("off")

    fig.tight_layout()

    if outname is not None:
        fig.savefig(outname, bbox_inches="tight")


def predict_with_uncertainty(
    mlp, x: np.array, n_iter: int = 1000, centrality: str = "median"
) -> Union[np.array, np.array, np.array]:
    """Use dropout sampling
    
    Args:
        mlp ([type]): keras model
        x (np.array): feature matrix
        n_iter (int, optional): Number of samples from the predictive distribution. 
            Defaults to 1000.
        centrality (str, optional): Method used to calculate the center of the predictive distribution. 
            Defaults to "median".
    
    Returns:
        Union[np.array, np.array, np.array]: All samples from the predictive distribution, centrality measures, variancesƒ
    """
    result = []

    f = K.function([mlp.layers[0].input, K.learning_phase()], [mlp.layers[-1].output])

    for i in range(n_iter):
        result.append(f([x, 1]))

    result = np.array(result)

    if centrality == "median":
        prediction = np.median(result, axis=0)
    elif centrality == "mean":
        prediction = np.mean(result, axis=0)
    uncertainty = result.var(axis=0)
    return result, prediction, uncertainty


def measure_performance(model, X, y_true):
    mae = model.metric("mae", X, y_true)
    mse = model.metric("mse", X, y_true)
    prediction = model.predict(X)

    stdev = prediction.std()

    corr0 = stats.pearsonr(prediction[:, 0], y_true[:, 0])[0]
    corr1 = stats.pearsonr(prediction[:, 1], y_true[:, 1])[0]
    corr2 = stats.pearsonr(prediction[:, 2], y_true[:, 2])[0]

    return {
        "mae": mae,
        "mse": mse,
        "std": stdev,
        "mae_std_ratio": mae / stdev,
        "pearson_corr0": corr0,
        "pearson_corr1": corr1,
        "pearson_corr2": corr2,
    }
