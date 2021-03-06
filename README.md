# MOF Color ML

This repository contains code on data that was used to build models that can predict the color of MOFs using ML techniques. See the [preprint](https://chemrxiv.org/articles/preprint/A_Data-Driven_Perspective_on_the_Colours_of_Metal-Organic_Frameworks/13033217) for more details.

## Related repositories

- [The tool that was used to conduct the survey](https://github.com/kjappelbaum/colorjeopardy)
- [The results of the survey](https://zenodo.org/record/3831845)
- [A web app that uses the model](https://github.com/kjappelbaum/mofcolorizer) with is deployed at https://go.epfl.ch/mofcolorizer

Some files were moved in the cleanup process and paths within those files might be broken.

## Package

The code defining the models that we explored, as well as some utility code, can be found in the `colorml` package, which has the following subpackages:

- `BNN`: Implementing Bayesian Neural Networks (with variational inference)
- `dropoutmc`: Implementing DNN with uncertainity estimate with Dropout-Monte-Carlo (Gal, 2016)
- `GPR`: Implementing Gaussian Process Regression models
- `GBDT`: Implementing gradient boosted decision trees (with quantile regression). Those are the models that we used for the results presented in the main text of the paper
- `featurize`: Implements functions that take a `cif` and return a `pd.DataFrame` with the features
- `utils`: Implements utilities (also annealing functions for BNN) that are used throughout the package as well as some plotting functions

## Notebooks

The `legacy` folder contains notebooks that were used in the development but do not contain relevant results.

- `survey_eda.ipynb`: exploratory data analysis of the survey results. We run the survey using the [colorjeopardy flask app](https://github.com/kjappelbaum/colorjeopardy). Technical details about the survey can be found there. In the notebook we also perfom comparision to the xkcd results and drop entries with a particularly short or long response time.
- `color_csd_eda.ipynb`: counts the elemental distribution
- `test_featurization_code.ipynb`: contains examples of how to use the featurization code (and how it will fail if the structure is disordered/contains clashing atoms)
- `make_prediction_plot.ipynb`: used to generate the model evaluation plots for the paper.
- `summarize_metrics.ipynb`: comparing metrics of baseline models with those of the final model.
- `getting_some_baseline.ipynb`: here, we create with some baseline dummy models
- `plot_learning_curve.ipynb`: here, we plotted the learning curve
- `make_predictions_on_experimental_structures.ipynb`: here, we make the analysis on the experimental and hypothetical structures.
- `number_modifiers_color.ipynb`: count how many modifiers like 'intense' dark 'light' are in the names
- `feature_importance_analysis.ipynb`: do SHAP feature importance analysis
- `check_if_mof_74_in_db.ipynb`: Delete structures from the dataset that are close to the test structures, see also `split_data_for_development_excluding_colors.ipynb`
- `permutation_test.iynb`: Contains the permutation significance analysis of one model
- `augmentation_effect.ipynb`: Analysis the effect of using all color labels from the survey

### Notebooks that are not directly pertinent to the main content of the paper

- `ml_baseline.ipynb`: contains some first model building steps.
- `select_a_diverse_set_for_sfs.ipynb`: diverse set selection
- `mulitoutput_kernel.ipynb`: Playing with coregionalized GPR
- `get_smiles.ipynb`: Playing with the MOFid code and openbabel to generate some linker descriptors
- `bayesian_nets.ipynb`: Playing with BNN (with the probflow library)
- `augment.ipynb`: Initial attempts with data augmentation

## Data

- `backup_colorcrawler.csv`: snapshot of the colorjeopardy survey results
- `clean_survey.csv`: cleaned survey data in which we dropped results with short or long response times.
- `xkcd.tsv`: results from the xkcd survey which we downloaded on 24/2/2020 from https://xkcd.com/color/rgb.txt.
- `CoRE12K_testdata.csv` and `CoRE12K_traindata.csv`, train/test data as provided by S.M. Mosavi and used in his diversity study. Featurization explained there (columns include RACs, geometric features and also gas uptake properties).
- `annotated_df.csv` is the data extracted from the CSD which includes the color labels deposited there.
- `cleaned_survey_unweighted_mean.csv` is the mean aggregated cleaned survey data (string - mean rgb mapping).
- `cleaned_survey_unweighted_median.csv` is the median aggregated cleaned survey data (string - median rgb mapping).
- `color_feat_merged.csv` is the color data string from the CSD merged with the dataframe containing the descriptors.
- `augment_dict.pkl` contains the mapping from strings to RGB values which we got from the survey and use for data augmentation
- `holdout_set.csv` and `development_set.csv` are the test and train set that we obtained with iterative stratification.
- `diverse_set{,_2, _3000}.csv` are the diverse sets we utilized for initial explorations
- the `case_studies` directory contains descriptors that we used for some of the case studies in the paper.
- `color_threshold.pkl`: dictionary that contains the color names for different variance thresholds

Unweighted mean/median refers to the fact that we perform simple averaging in RGB space without taking into account that the percepetion of the human eye does not vary uniformly within this space.

## Conventions

- For commit messages, we try to use [conventional commits](https://www.conventionalcommits.org/en/v1.0.0-beta.2/). `feat` are also commits that introduce a new analysis step.
