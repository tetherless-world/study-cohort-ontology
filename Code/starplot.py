import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns # improves plot aesthetics
import pandas as pd
from ast import literal_eval as make_tuple
from matplotlib import colors as mcolors
import matplotlib.patches as mpatches
from matplotlib import rcParams
import os
rcParams.update({'figure.autolayout': True})

plotall_inone = False

def _invert(x, limits):
    """inverts a value x on a scale from
    limits[0] to limits[1]"""
    return limits[1] - (x - limits[0])

def _scale_data(data, ranges):
    """scales data[1:] to ranges[0],
    inverts if the scale is reversed"""
    for d, (y1, y2) in zip(data[1:], ranges[1:]):
        assert (y1 <= d <= y2) or (y2 <= d <= y1)
    x1, x2 = ranges[0]
    d = data[0]
    if x1 > x2:
        d = _invert(d, (x1, x2))
        x1, x2 = x2, x1
    sdata = [d]
    for d, (y1, y2) in zip(data[1:], ranges[1:]):
        if y1 > y2:
            d = _invert(d, (y1, y2))
            y1, y2 = y2, y1
        sdata.append((d-y1) / (y2-y1)
                     * (x2 - x1) + x1)
    return sdata

class ComplexRadar():
    def __init__(self, fig, variables, ranges,
                 n_ordinate_levels=6):
        angles = np.arange(0, 360, 360./len(variables))

        axes = [fig.add_axes([0.1,0.1,0.9,0.9],polar=True,
                label = "axes{}".format(i))
                for i in range(len(variables))]
        l, text = axes[0].set_thetagrids(angles,
                                         labels=variables)
        [txt.set_rotation(angle-90) for txt, angle
             in zip(text, angles)]
        for ax in axes[1:]:
            ax.patch.set_visible(False)
            ax.grid("off")
            ax.xaxis.set_visible(False)
        for i, ax in enumerate(axes):
            grid = np.linspace(*ranges[i],
                               num=n_ordinate_levels)
            gridlabel = ["{}".format(round(x,2))
                         for x in grid]
            if ranges[i][0] > ranges[i][1]:
                grid = grid[::-1] # hack to invert grid
                          # gridlabels aren't reversed
            gridlabel[0] = "" # clean up origin
            ax.set_rgrids(grid, labels=gridlabel,
                         angle=angles[i])
            #ax.spines["polar"].set_visible(False)
            ax.set_ylim(*ranges[i])
        # variables for plotting
        self.angle = np.deg2rad(np.r_[angles, angles[0]])
        self.ranges = ranges
        self.ax = axes[0]

    def plot(self, data, color, linestyle, *args, **kw):
        sdata = _scale_data(data, self.ranges)
        self.ax.plot(self.angle, np.r_[sdata, sdata[0]], color=color, linestyle=linestyle,*args, **kw)

    def fill(self, data, color, *args, **kw):
        sdata = _scale_data(data, self.ranges)
        print("SData ", sdata)
        print("SData ", sdata[0])
        self.ax.fill(self.angle, np.r_[sdata, sdata[0]], color=color, *args, **kw)

    def fill_between(self,data_point,lower_bound, upper_bound, color, *args, **kw):
        sdata = _scale_data(data_point, self.ranges)
        slower = _scale_data(lower_bound, self.ranges)
        shigher = _scale_data(upper_bound, self.ranges)
        self.ax.fill_between(sdata, slower, shigher, color = '#539caf', alpha = 0.4)


def starplot_viz(table1excelfilename:str, patientexcelfilename: str):
    '''
    Starplot to visualize the patient groups within population descriptions, and to see how patients align with these descriptions
    '''
    table1excel = pd.ExcelFile(table1excelfilename)
    table1_df = pd.read_excel(table1excel)
    data_rows = table1_df.groupby('cohort')[['age_mean','bmi_mean', 'sbp_mean', 'dbp_mean','A1c_median']].apply(lambda g: g.values.tolist()[0]).to_dict()
    #This can be changed to make the column selection automatic
    sd_rows =  table1_df.groupby('cohort')[['age_sd','bmi_sd','sbp_sd','dbp_sd','A1c_range']].apply(lambda g: g.values.tolist()[0]).to_dict()
    sd_lowerbound = {}
    sd_upperbound = {}

    patientexcel = pd.ExcelFile(patientexcelfilename)
    patient_df = pd.read_excel(patientexcel)
    patient_rows = patient_df.groupby('name')[['age','bmi', 'sbp', 'dbp','A1c']].apply(lambda g: g.values.tolist()[0]).to_dict()


    for cohort_key in sd_rows.keys():
        sd_lowerbound[cohort_key] = [data_rows[cohort_key][i] - sd_rows[cohort_key][i] if type(sd_rows[cohort_key][i]) != str else make_tuple(sd_rows[cohort_key][i])[0] for i in range(len(sd_rows[cohort_key]))]
        sd_upperbound[cohort_key] = [data_rows[cohort_key][i] + sd_rows[cohort_key][i] if type(sd_rows[cohort_key][i]) != str else make_tuple(sd_rows[cohort_key][i])[1] for i in range(len(sd_rows[cohort_key]))]
    print(sd_lowerbound, sd_upperbound, patient_rows)
    return (data_rows, sd_lowerbound, sd_upperbound, patient_rows)

(table1part, table1partlowerbound, table1partupperbound, patient_rows) = starplot_viz("../data/chapter8_citation32_table1.xlsx", "../NHANESPatientData/nhanes-sample-patient.xlsx")
# example data
variables = ('Age','BMI', 'Systolic BP', 'Diastolic BP','HbA1C')
data = list(table1part.values())
data_lb = list(table1partlowerbound.values())
data_ub = list(table1partupperbound.values())
patient_data = list(patient_rows.values())
print((data, data_lb, data_ub))
ranges = [(10, 80), (15, 40),
         (110, 164), (55, 90), (5, 10)]


colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)

# Sort colors by hue, saturation, value and name.
by_hsv = sorted((tuple(mcolors.rgb_to_hsv(mcolors.to_rgba(color)[:3])), name)
                for name, color in colors.items())
sorted_cnames = [name for hsv, name in by_hsv]
#Getting random colours for each row
color_indices = list(np.random.choice(len(sorted_cnames), size=len(data), replace=False))

# plotting





colors = ['red', 'blue', 'yellow', 'green']
ligther_colors = ['lavenderblush','azure','papayawhip','honeydew']
mng = plt.get_current_fig_manager()
mng.full_screen_toggle()

patient_groupnames = list(table1part.keys())
legend_patches = [(mpatches.Patch(color=colors[i], label=patient_groupnames[i])) for i in range(len(data))]


def plot_asindividual(patientgroupsmean, patientgroupslower, patientgroupsupper):
    for data_count in range(len(data)):
        fig = plt.figure()
        title_fig = ''.join(x for x in patient_groupnames[data_count]).title()
        ranges = [(10, 80), (15, 40),
         (110, 164), (55, 90), (5, 10)]
        radar = ComplexRadar(fig, variables, ranges)
        radar.fill(patientgroupsupper[data_count],ligther_colors[data_count], alpha=1)
        radar.fill(patientgroupslower[data_count], 'white', alpha=1)
        radar.plot(patientgroupsmean[data_count], colors[data_count],"-",label=title_fig)
        #radar.fill_between(data[data_count], data_lb[data_count],data_ub[data_count])
        #sorted_cnames[color_indices[data_count]]
        radar.plot(data_lb[data_count],colors[data_count], "--")
        radar.plot(data_ub[data_count], colors[data_count], "--")
        #For now plotting 3rd patient
        print(patient_data[2])
        radar.plot(patient_data[2], 'dodgerblue',"-",label="Patient Datapoint")
        #radar.fill(patient_data[2], 'lightblue', alpha = 1)
        plt.title(title_fig)
        #plt.legend(handles=[mpatches.Patch(color= colors[data_count],label=title_fig)])
        os.makedirs("../data/output_files/",exist_ok=True)
        plt.savefig('../data/output_files/' + title_fig + '.png')
        plt.show()

def plot_asindividuallinechart(patientgroupsmean, patientgroupslower, patientgroupsupper):
    plt.clf()
    print("Lower ", patientgroupslower)
    # using some dummy data for this example
    xs = np.arange(0,5,1)
    ys = np.random.normal(loc=3, scale=0.4, size=5)
    # 'bo-' means blue color, round points, solid lines
    plt.plot(xs,ys,'bo-')
    # zip joins x and y coordinates in pairs
    for x,y in zip(xs,ys):
        print("X ", x, "Y ", y)
        label = "{:.2f}".format(y)

        plt.annotate(label, # this is the text
                 (x,y), # this is the point to label
                 textcoords="offset points", # how to position the text
                 xytext=(0,10), # distance from text to points (x,y)
                 ha='center') # horizontal alignment can be left, right or center
    print(" Variables ", variables)
    plt.xticks(xs, variables)
    plt.yticks(np.arange(0,7,0.5))

    plt.show()

def plot_all(patientgroupsmean, patientgroupslower,patientgroupsupper):
    fig = plt.figure()
    for data_count in range(len(data)):
        title_fig = ''.join(x for x in patient_groupnames[data_count]).title()
        print("Title ", title_fig)
        radar = ComplexRadar(fig, variables, ranges)
        radar.fill(patientgroupsupper[data_count],ligther_colors[data_count], alpha=1)
        radar.fill(patientgroupslower[data_count], 'white', alpha=1)
        radar.plot(patientgroupsmean[data_count], colors[data_count],"-",label = title_fig )
        #radar.fill_between(data[data_count], data_lb[data_count],data_ub[data_count])
        #sorted_cnames[color_indices[data_count]]
        radar.plot(data_lb[data_count],colors[data_count], "--")
        radar.plot(data_ub[data_count], colors[data_count],"--")
        #For now plotting 3rd patient
        print(patient_data[2])
        radar.plot(patient_data[2], 'dodgerblue',"-",label="Patient Datapoint")
        #Testing how this looks
        #radar.fill(patient_data[2], 'lightblue', alpha = 1)
        #This will become the legend key portion
    #plt.legend(handles=legend_patches,loc="upperright")
    #Only create new directory if it doesn't exist
    os.makedirs("../data/output_files/",exist_ok=True)
    plt.savefig('../data/output_files/alltogetherpatientgroups.png')
    plt.show()


if plotall_inone == True:
    plot_all(data, data_lb, data_ub)
else:
    plot_asindividual(data, data_lb, data_ub)
