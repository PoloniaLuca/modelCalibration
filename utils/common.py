import numpy as np
import math 

from decimal import Decimal

def fexp(number):
    (sign, digits, exponent) = Decimal(number).as_tuple()
    return len(digits) + exponent - 1

def fman(number):
    return Decimal(number).scaleb(-fexp(number)).normalize()

def truncate(f, n):
    return math.floor(f * 10 ** n) / 10 ** n

def f_interval(intvl):
    #return str(np.round(intvl,10))
    #return ceil(log10(intvl))
    
    exponent = fexp(intvl)
    if exponent >= -3:
        value = truncate(intvl,3)
        if (value == 1):
            value = int(value)
    else:
        mantissa = fman(intvl).to_integral_value()
        value = "10<sup>" + str(exponent) + "</sup>"
        if mantissa != 1:
            value = str(mantissa) + "&middot;" + value
    
    return '<span class="interval_popover" data-trigger="hover click" data-placement="bottom" data-toggle="popover" data-content="' + str(intvl)  + '">' + str(value) + "</span>"
#.lstrip("0")

def create_intervals(bin_edges):
    # print(bin_edges)
    intervals = []
    for i in range(len(bin_edges) - 1):
        interval = f"{f_interval(bin_edges[i])} <span style='font-weight: normal'>-</span> {f_interval(bin_edges[i+1])}"
        intervals.append(interval)
    return intervals


def score_table(m):

    values = {
        "additional_headers": "",
        "brierLoss": "",
        "ECEacc": "%.3f" % (m["1-ece_acc"] if "1-ece_acc" in m else m["ece_acc"]),
        "ECIglobal": "%.3f" % m["ec_g"],
        "ECIbalance": "%.3f" % m["ec_dir"],
        "ECIover": "%.3f" % m["ec_overconf"],
        "ECIunder": "%.3f" % m["ec_underconf"]
    }


    if "brier_loss" in m:
        values["additional_headers"] = '<th scope="col">Brier loss</th>'
        values["brierLoss"] = "<td>%.3f</td>" % m["brier_loss"]

    return """\

        <table class="table mb-4">
    <thead>
        <tr>
        <th scope="col">ECE</th>
        <th scope="col">ECI<sub>global</sub></th>
        <th scope="col">ECI<sub>balance</sub></th>
        <th scope="col">ECI<sub>over</sub></th>
        <th scope="col">ECI<sub>under</sub></th>
        {additional_headers}
        
        </tr>
    </thead>
    <tbody>
        <tr>
        <td>{ECEacc}</th>
        <td>{ECIglobal}</td>
        <td>{ECIbalance}</td>
        <td>{ECIover}</td>
        <td>{ECIunder}</td>
        {brierLoss}
        </tr>
        
    </tbody>
    </table>\
    """.format(
        **values
    )


def local_ecis(rs, rs_bin, classname):
    intervals = create_intervals(rs_bin[classname]["bins"])
    #raise Exception
    headers = "".join(
        ['<th class="interval_limit" scope="col">' + interval + "</th>" for interval in intervals]
    )

    ecis = "".join(
        ["<td>" + "%.3f" % eci + "</th>" for eci in rs[classname]["ec_l_all"][:-1]]
    )

    frequencies = "".join(
        ["<td>" + "%.1f" % freq + "</th>" for freq in rs[classname]["relative-freq"][:-1]]
    )

    strings = {"ecis": ecis, "frequencies": frequencies, "headers": headers}

    return """\
        <div style="overflow-x: auto" class="mb-4">
        <table class="table">
    <thead>
        <tr>
        <th></th>
        {headers}
        </tr>
    </thead>
    <tbody>
        <tr>
        <th scope="row">ECI<sub>l</sub></th>{ecis}
        </tr>
        <tr>
        <th scope="row">Frequency (%)</td>{frequencies}
        </tr>
        
    </tbody>
    </table>
    </div>
    \
    """.format(
        **strings
    )


def local_ecis_by_class(rs, rs_bin, classes):
    tables = []

    for classname in classes:
        tables.append(local_ecis(rs, rs_bin, classname))

    return tables


def local_scores(rs, classes):
    tables = []

    for classname in classes:
        tables.append(score_table(rs[classname]))

    return tables
