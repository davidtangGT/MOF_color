# -*- coding: utf-8 -*-
"""Code to train BNN with probflow using variational inference"""
from __future__ import absolute_import

from functools import partial

import probflow as pf
import tensorflow as tf
from comet_ml import Experiment  # pylint:disable=unused-import
from numpy.random import seed
from probflow.callbacks import (EarlyStopping, KLWeightScheduler, LearningRateScheduler, MonitorELBO, MonitorMetric)
from scipy import stats
from six.moves import range, zip

import tensorflow_addons as tfa

from ..utils.clr import cyclic_learning_rate
from .utils.kl_anneal import (cycle_kl_anneal, linear_kl_anneal, monotonical_kl_anneal)
from .utils.utils import mapping_to_target_range


class DenseNetworkConstrained(pf.Module):
    """
    Defines a dense NN in which the last activation function is constrained to a range
    """

    def __init__(self, dims, activation=tf.keras.activations.relu):
        number_layers = len(dims) - 1
        self.layers = [pf.modules.Dense(dims[i], dims[i + 1]) for i in range(number_layers)]
        self.activations = (number_layers - 1) * [activation] + [mapping_to_target_range]

    def __call__(self, x):
        for layer, activation in zip(self.layers, self.activations):
            x = layer(x)
            x = activation(x)
        return x


class DenseNetwork(pf.Module):
    """
    Defines a dense NN.
    """

    def __init__(self, dims, activation=tf.keras.activations.relu):
        number_layers = len(dims) - 1
        self.layers = [pf.modules.Dense(dims[i], dims[i + 1]) for i in range(number_layers)]
        self.activations = (number_layers - 1) * [activation] + [lambda x: x]

    def __call__(self, x):
        for layer, activation in zip(self.layers, self.activations):
            x = layer(x)
            x = activation(x)
        return x


class TwoHeadedNet(pf.ContinuousModel):

    def __init__(self, units, head_units, activation=tf.keras.activations.relu, batch_norm=True):
        self.core = DenseNetwork(units, activation)
        self.mean = DenseNetworkConstrained(head_units, activation)
        self.std = DenseNetwork(head_units, activation)
        if batch_norm:
            self.batch_norm = pf.modules.BatchNormalization([units[-1]])  # use batchnorm between core and head units
        else:
            self.batch_norm = None

    def __call__(self, x):
        x = self.core(x)

        if self.batch_norm is not None:
            x = self.batch_norm(x)

        return pf.Cauchy(self.mean(x), tf.exp(self.std(x)))


def build_model(units: list, head_units: list, activation: str = 'relu', batch_norm: bool = True):
    if activation == 'relu':
        activation = tf.keras.activations.relu
    elif activation == 'elu':
        activation = tf.keras.activations.elu
    elif activation == 'selu':
        activation = tf.keras.activations.selu
    else:
        raise NotImplementedError
    model = TwoHeadedNet(units, head_units, activation, batch_norm)

    return model


def train_model(
    experiment,
    model,
    train_data: tuple,
    valid_data: tuple,
    logger,
    early_stopping_patience: int = 10,
    random_seed: int = 821996,
    lr: float = None,
    epochs: int = 200,
    batch_size: int = 268,
    cycling_lr: bool = False,
    kl_annealing: bool = True,
):
    with experiment.train():
        seed(random_seed)
        tf.random.set_seed(random_seed)
        X_train, y_train = train_data
        X_valid, y_valid = valid_data

        assert len(X_train) == len(y_train)
        assert len(X_valid) == len(y_valid)

        # We normalize y for now
        assert y_train.max() <= 1
        assert y_train.min() >= 0
        assert y_valid.max() <= 1
        assert y_valid.min() >= 0

        assert X_train.shape[1] == X_valid.shape[1]

        logger.info('Will now start training.')
        callbacks = []
        monitor_mae = MonitorMetric('mae', X_valid, y_valid, verbose=True)
        callbacks.append(monitor_mae)

        if early_stopping_patience is not None:
            logger.info('Will use early stopping.')
            assert early_stopping_patience % 1 == 0
            early_stopping = EarlyStopping(lambda: monitor_mae.current_metric, patience=early_stopping_patience)
            callbacks.append(early_stopping)

        if cycling_lr:
            logger.info('Will use cycling learning rate')
            cycling_learning_rate = LearningRateScheduler(cyclic_learning_rate)
            callbacks.append(cycling_learning_rate)

        if kl_annealing is not None:
            logger.info('Will use KL annealing')
            if kl_annealing['method'] == 'tanh':
                kl_annealer = KLWeightScheduler(partial(monotonical_kl_anneal, M=kl_annealing['constant']))
                callbacks.append(kl_annealer)
            elif kl_annealing['method'] == 'linear':
                kl_annealer = KLWeightScheduler(partial(linear_kl_anneal, M=kl_annealing['constant']))
                callbacks.append(kl_annealer)
            elif kl_annealing['method'] == 'cycling':
                kl_annealer = KLWeightScheduler(partial(cycle_kl_anneal, M=kl_annealing['constant']))
                callbacks.append(kl_annealer)

        model.fit(
            X_train,
            y_train,
            callbacks=callbacks,
            batch_size=batch_size,
            epochs=epochs,
            lr=lr,
        )

    return model
