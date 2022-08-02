import matplotlib.pyplot as plt


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


def plot_with_average(data, x_label="", y_label="", figsize=(15, 3)):
    fig, ax = plt.subplots(figsize=figsize, dpi=100)
    ax.plot(data.index, data.values, 'mediumseagreen')
    ax.axhline(data.values.mean(), color='r', linestyle='--')
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    ax.set_ylim([0, ax.get_ylim()[1]])
    ax.legend(["Total", "Average ({})".format(round(data.values.mean(), 1))])
    return fig, ax
