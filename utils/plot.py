from matplotlib.gridspec import GridSpec
import matplotlib
matplotlib.use('agg')
import numpy as np
import matplotlib.pyplot as plt
import uuid

from calibration_framework import CalibrationFramework
calibration = CalibrationFramework()

def reliabilityplot(classes_scores, strategy= 15, classes = '0'):
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.size"] = 10
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.rcParams['legend.title_fontsize'] = 'xx-small'
    fig = plt.figure(figsize=(6,5))
    gs = GridSpec(4,2)
    conta = 0
    ax_joint = fig.add_subplot(gs[1:4,0:3])
    ax_marg_x = fig.add_subplot(gs[0,0:3])
    prob_true, prob_pred, bins_dict = calibration.calibrationcurve(classes_scores[classes]['y'],classes_scores[classes]['proba'],strategy=strategy, adaptive=False)
    conta += 1
    ax_joint.plot(prob_pred, prob_true, label = f'Class {classes}, N = {np.unique(classes_scores[classes]["y"], return_counts=True)[1][1]}', linestyle='-', markersize=2, alpha=0.8)
    ax_joint.plot([0, 1], [0, 1], linestyle='-', color='black')
    ax_joint.legend(loc='upper left',fancybox=True, shadow=True,ncol=3,fontsize=7)
    ax_marg_x.bar(prob_pred, bins_dict['binfr']*100, width=0.05, alpha=0.6)
    
    ax_marg_x.grid(linestyle=':')
    plt.setp(ax_marg_x.get_xticklabels(), visible=False)
    ax_joint.grid(linestyle=':')
    ax_marg_x.set_ylabel('RF (%)', fontsize=7)
    ax_marg_x.set_yticks(np.arange(0, 100, 20))
    ax_joint.set_xlabel('Predicted Probability')
    ax_joint.set_ylabel('Estimated Probability')
    ax_joint.legend(loc='upper left',fancybox=True, shadow=True,ncol=3,fontsize=5)
    plt.tight_layout()

    ## Start export via file, not via plt.show()
    id = str(uuid.uuid4())
    filename = "output_images/" + id + "reliability.png"
    path = "static/" + filename
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    return filename


def reliabilityplots(classes, classes_scores, strategy):
    plot_filenames = []

    for classname in classes: 
        plot_filenames.append(reliabilityplot(classes_scores, strategy, classname))

    return plot_filenames
    