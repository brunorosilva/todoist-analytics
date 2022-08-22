import matplotlib.pyplot as plt
import july


def histogram(data):
    fig, ax = plt.subplots(figsize=(15, 3), dpi=100)
    ax.hist(data, bins=20)
    ax.vlines(data.mean(), 0, ax.get_ylim()[1], color='r', linestyle='--')
    ax.set_xlabel(data.name)
    ax.set_ylabel("# Tasks")
    ax.legend(["Average ({})".format(round(data.mean(), 1)), "Total"])
    return fig, ax


def month_plot(counts, month):
    ax = july.month_plot(counts.index, counts.values, month=month, value_label=True)
    return ax.figure, ax


def calendar_plot(counts):
    ax = july.calendar_plot(counts.index, counts.values, title=False, value_label=True)
    if type(ax[0]) is list:
        return ax[0][0].figure, ax
    else:
        return ax[0].figure, ax


def heatmap_plot(counts):
    ax = july.heatmap(counts.index, counts.values, month_grid=True, colorbar=True)
    return ax.figure, ax


def category_pie(data, category):
    tasks_per_project_counts = data[category].value_counts()
    tasks_per_project_counts = tasks_per_project_counts[tasks_per_project_counts > 0]
    percent = ["{} ({:.0%})".format(name, val) for name, val in
               zip(tasks_per_project_counts.index, tasks_per_project_counts.values / tasks_per_project_counts.sum())]
    fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
    ax.pie(tasks_per_project_counts.values,
           labels=percent,
           wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'})
    return fig, ax


def category_plot(data, category):
    tasks_per_project_counts = data[category].value_counts()
    tasks_per_project_counts = tasks_per_project_counts[tasks_per_project_counts > 0]
    fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
    ax.bar(tasks_per_project_counts.index, tasks_per_project_counts.values)
    return fig, ax


def plot_with_average(data, x_label="", y_label="", figsize=(15, 3), labelrotation=0, ema=0):
    fig, ax = plt.subplots(figsize=figsize, dpi=100)
    ax.plot(data.index, data.values, 'mediumseagreen')
    ewm = 0
    mean = data.values.mean()
    if ema > 0:
        ewm = data.ewm(span=ema).mean()
        ax.plot(data.index, ewm, 'b')
    ax.axhline(mean, color='r', linestyle='--')
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.tick_params(axis='x', labelrotation=labelrotation)
    ax.set_ylim([0, ax.get_ylim()[1]])
    if ema > 0:
        ax.legend(["Total",
                   "EMA-{} ({})".format(ema, round(ewm[-2], 1)),
                   "Average ({})".format(round(mean, 1))])
        return fig, ax, ewm[-2]

    ax.legend(["Total", "Average ({})".format(round(mean, 1))])
    return fig, ax
