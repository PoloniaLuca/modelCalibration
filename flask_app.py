import os
import subprocess
from pathlib import Path

## Development server requires we first copy all common libraries
if __name__ == "__main__":
    # subprocess.check_output('cp -nr ../../common/ .')
    f_path = Path(__file__)
    # source = os.path.join(f_path.parent.parent.parent, 'common/')
    # dest = str(f_path.parent) + '/'

    # output =subprocess.check_output(['rsync', '-a', '-v', source, dest])
    # print(output)

from utils.constants import constants

from ast import For
from flask import Flask, app, render_template, request, flash
from numpy import append
import pandas as pd
from pprint import pprint
import numpy as np
import pickle
import uuid

from calibration_framework import CalibrationFramework
calibration = CalibrationFramework()


from utils.plot import reliabilityplots
from utils.common import score_table, local_ecis_by_class, local_scores
from utils.common import create_intervals

path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, "uploads")
ALLOWED_FILES = {"txt"}
TEST_FOLDER = os.path.join(path, "testfiles/")
app = Flask(__name__)


if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ALLOWED_FILES"] = ALLOWED_FILES
app.config["SECRET_KEY"] = "f13783376341d2dddfaef175"
app.config["TEST_FOLDER"] = TEST_FOLDER

@app.context_processor
def inject_constants():
    return dict(constants=constants)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_FILES


per_page = 3

def allowed_strategy(bins):
    if bins.isdigit():
        bins = int(bins)
        return bins >= 1 and bins <= 20
    if bins == 'Automatic':
        return True
    if bins == 'True' or bins == True:
        return True
    return False

def allowed_uuid(value):
    try:
        uuid.UUID(str(value))

        return True
    except ValueError:
        return False

def uuid_to_path(id):
    path = "output/" + id + "classes_scores.pickle"
    return path

@app.route("/input", methods=["POST", "GET"])
def input(test=False):
    # If your shell script has shebang,
    # you can omit shell=True argument.
    subprocess.Popen(["bash", "./clean.sh"])    
    # print("#####")
    # for key, value in request.form.items():
    #     print(f"{key}: {value}")
    # print("#####")

    # Results page
    if request.method == "POST" or (test is True):

        classes_scores_uuid = request.form.get("classes_scores")

        # Page navigation
        if request.form.get("submit", False) == "navigate":
            if classes_scores_uuid == None or not allowed_uuid(classes_scores_uuid):
                flash("Invalid UUID provided for classes_scores.", category="danger")
                return render_template("input.html")

            classes_scores_filename = uuid_to_path(classes_scores_uuid)

            try:

                with open(classes_scores_filename, 'rb') as handle:

                    classes_scores = pickle.load(handle)
            except FileNotFoundError:
                flash("Your session expired, please submit the form again.", category="danger")
                return render_template("input.html")

            # print(classes_scores)

            # We let the render function to check the validity of strategy and start

            strategy = request.form.get("strategy")

            start = request.form.get("start")


            return render(classes_scores, strategy, start, navigating=True, classes_scores_uuid=classes_scores_uuid)


        # Results page for upload
        if request.form.get("submit", False) == "submit":

            y_true_file = request.files["y_true"]
            y_proba_file = request.files["y_proba"]
            y_pred_file = request.files["y_pred"]
            # print(app.config)
            # print(y_true_file)

            if y_true_file.filename == "":
                flash("y_true file is necessary!", category="warning")
                return render_template("input.html")

            if y_proba_file.filename == "":
                flash("y_proba file is necessary!", category="warning")
                return render_template("input.html")

            if (
                not allowed_file(y_true_file.filename)
                or not allowed_file(y_proba_file.filename)
                or ((y_pred_file.filename != "") and (not allowed_file(y_pred_file.filename)))
            ):
                flash("Input file needs .txt extension.", category="danger")
                return render_template("input.html")
            else:

                provided_pred = (y_pred_file.filename != "")

                try:
                    y_true = np.loadtxt(y_true_file)  # sarebbe y_ground_truth
                    y_proba = np.loadtxt(y_proba_file)  # sarebbe y confidence scores

                    y_pred = np.argmax(y_proba, 1) if (not provided_pred) else np.loadtxt(y_pred_file)
                except Exception as e:
                    print(e)
                    flash(
                        "Unable to read input data, incorrect data format in txt files, please check the data and try again",
                        category="danger",
                    )
                    return render_template("input.html")

                try:
                    if (y_true.ndim != 1):
                        raise Exception("y_true should have exactly one dimension (n rows)")

                    if (y_proba.ndim != 2):
                        raise Exception("y_proba should have exactly two dimensions (with n rows and c columns)")

                    if (y_proba.shape[0] != y_true.shape[0]):
                        raise Exception("y_true and y_proba should have the same number n of rows",)

                    if np.isnan(np.sum(y_true)) or np.isnan(np.sum(y_proba)):
                        raise Exception("y_true and y_proba must not have any missing values.")

                    if (provided_pred and np.isnan(np.sum(y_pred))):
                        raise Exception("y_pred must not have any missing values.")

                    if (provided_pred and y_proba.shape[0] != y_pred.shape[0]):
                        raise Exception("y_pred should have the same number n of rows as y_proba",)

                except Exception as e:
                    flash(
                        str(e),
                        category="danger",
                    )
                    return render_template("input.html")

                strategy = request.form.get("strategy")

                classes_scores = calibration.select_probability(y_true, y_proba, y_pred)

                start = "0"

                return render(classes_scores, strategy, start)


        if test is True:
            y_true = np.loadtxt(
                "./static/testfiles/y_true_vit_pathmnist.txt"
            )  # sarebbe y_ground_truth
            y_proba = np.loadtxt(
                "./static/testfiles/y_proba_vit_pathmnist.txt"
            )  # sarebbe y confidence scores

            y_pred = np.argmax(y_proba, 1)

            classes_scores = calibration.select_probability(y_true, y_proba, y_pred)

            ## no more uploaded files used after here
            strategy = request.args.get("strategy", "10")

            start = "0"

            return render(classes_scores, strategy, start)

    else:
        return render_template("input.html")


@app.route("/test")
def test():
    return input(test=True)

def render(classes_scores, strategy, start, navigating=False, classes_scores_uuid=None):

    # print("strategy", strategy)
    # print("start", start)

  # Validate and sanitise 'strategy'
    try:
        if not allowed_strategy(strategy):
            raise ValueError("Invalid strategy.")
        if strategy.isdigit():
            strategy = int(strategy)
        if strategy == 'Automatic':
            strategy = True
    except ValueError:
        flash("Invalid strategy provided .", category="danger")
        return render_template("input.html")


    classes_scores_id = str(uuid.uuid4()) if classes_scores_uuid is None else classes_scores_uuid
    classes_scores_path = uuid_to_path(classes_scores_id)

    hidden_fields = {"classes_scores": classes_scores_id, "strategy": strategy}


    try:
        if not os.path.exists(classes_scores_path):
            with open(classes_scores_path, 'wb') as handle:
                pickle.dump(classes_scores, handle, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            # just update last edited, to keep in cache
            os.utime(classes_scores_path)

        if strategy == "True":
                strategy = True
        rs, rs_bin = calibration.calibrationdiagnosis(
            classes_scores, strategy=strategy, undersampling=False
        )

        class_frequencies = [np.unique(data['y'], return_counts=True)[1][1] for classname,data in classes_scores.items()]

        global_metrics = calibration.classwise_calibration(rs)

        classes = rs.keys()

        class_list = list(classes)

        sorted_class_list = list(reversed([x for _, x in sorted(zip(class_frequencies, class_list))]))

    except Exception:
        flash("One or more errors were encountered: please check your data, or contact us if the issue persists.",category="danger")
        return render_template("input.html")

    # print(list(zip(class_frequencies, class_list)))
    # print(sorted_class_list)

    # Validate and sanitise 'start'
    try:
        if not start.isdigit():
            raise ValueError("Start must be numeric")
        start = int(start)
        if (start < 0 or start >= len(class_list)):
            raise ValueError
    except ValueError:
        start = 0

    classes_subset = sorted_class_list[start : start + per_page]

    # get the top per page

    classes_no=len(classes_subset)

    try:
        plot_filenames = reliabilityplots(
            classes_subset, classes_scores=classes_scores, strategy=strategy
        )

        global_scores_html = score_table(global_metrics)

        local_ecis_htmls = local_ecis_by_class(rs, rs_bin, classes_subset)
        local_scores_htmls = local_scores(rs, classes_subset)

        prev_start = max(start-per_page,0) if start > 0 else None
        next_start = start+per_page if  start+per_page < len(sorted_class_list) else None

        current_page = (start // per_page) +1

        total_pages = -(len(sorted_class_list) // -per_page)

    except Exception:
        flash("One or more errors were encountered: please check your data, or contact us if the issue persists.",category="danger")
        return render_template("input.html")

    return render_template(
        "results.html",
        rs=rs,
        hidden_fields=hidden_fields,
        classes_no=classes_no,
        prev_start=prev_start,
        next_start=next_start,
        current_page=current_page,
        total_pages=total_pages,
        start=start,
        navigating=navigating,
        classes_subset=classes_subset,
        global_scores_html=global_scores_html,
        local_ecis_htmls=local_ecis_htmls,
        local_scores_htmls=local_scores_htmls,
        plot_filenames=plot_filenames,
        filenames_tranne_primi_5=[],
    )

@app.route('/')
def home():
    return render_template('home.html')

@app.route("/deploy")
def deploy():
    output = subprocess.check_output('./lib/deploy.sh', stderr=subprocess.STDOUT).replace(b'\n', b'<br />')
    return output

## Development server
if __name__ == "__main__":
    app.run(debug=True, port=5002)
