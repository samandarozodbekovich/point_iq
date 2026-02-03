

def plot_heatmap(data, x, y, save_path=None):
    import seaborn as sns
    import matplotlib.pyplot as plt

    sns.kdeplot(x=data[x], y=data[y], fill=True)
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
